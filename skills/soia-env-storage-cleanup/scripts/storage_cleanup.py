#!/usr/bin/env python3
"""Scan and clean SOIA-managed storage with an immutable authorization plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import uuid
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PLAN_SCHEMA_VERSION = 1
RECEIPT_SCHEMA_VERSION = 1
PLAN_TTL_MINUTES = 30
ACKNOWLEDGEMENT = "CUSTOMER_APPROVED_IRREVERSIBLE_DELETE"
MANAGED_MARKER = ".soia-managed-storage.json"
ROOT_MARKER = ".soia-storage-root.json"
ACTIVE_MARKER = ".soia-active"
STATE_CLASSES = {"audit_state"}
AUTHORIZATION_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
ROOT_ENVIRONMENTS = {
    "config": "SOIA_SKILLS_CONFIG_HOME",
    "state": "SOIA_SKILLS_STATE_HOME",
    "cache": "SOIA_SKILLS_CACHE_HOME",
    "temp": "SOIA_SKILLS_TEMP_HOME",
}


class CleanupError(ValueError):
    """Raised when a cleanup safety gate fails closed."""


def now_rfc3339() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def aware_datetime(value: str, label: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except (TypeError, ValueError) as exc:
        raise CleanupError(f"{label} must be RFC3339 with an explicit timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CleanupError(f"{label} must be RFC3339 with an explicit timezone")
    return parsed


def configured_path(env: Mapping[str, str], name: str) -> Path | None:
    value = env.get(name)
    return Path(value).expanduser().absolute() if value else None


def managed_roots(
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
    temp_root: Path | None = None,
) -> dict[str, Path]:
    """Resolve the four SOIA-owned roots without creating them."""

    values = os.environ if env is None else env
    user_home = Path.home() if home is None else home
    platform_id = sys.platform if platform_name is None else platform_name
    is_windows = platform_id.startswith("win")
    is_macos = platform_id == "darwin"

    config = configured_path(values, "SOIA_SKILLS_CONFIG_HOME")
    if config is None:
        if is_windows:
            config = Path(values.get("APPDATA", user_home / "AppData" / "Roaming")) / "soia-skills"
        else:
            config = Path(values.get("XDG_CONFIG_HOME", user_home / ".config")) / "soia-skills"

    state_root = configured_path(values, "SOIA_SKILLS_STATE_HOME")
    if state_root is None:
        if is_windows:
            state_root = Path(values.get("LOCALAPPDATA", user_home / "AppData" / "Local")) / "soia-skills" / "state"
        else:
            state_root = Path(values.get("XDG_STATE_HOME", user_home / ".local" / "state")) / "soia-skills"

    cache = configured_path(values, "SOIA_SKILLS_CACHE_HOME")
    if cache is None:
        if is_windows:
            cache = Path(values.get("LOCALAPPDATA", user_home / "AppData" / "Local")) / "soia-skills" / "Cache"
        elif is_macos:
            cache = user_home / "Library" / "Caches" / "soia-skills"
        else:
            cache = Path(values.get("XDG_CACHE_HOME", user_home / ".cache")) / "soia-skills"

    temporary = configured_path(values, "SOIA_SKILLS_TEMP_HOME")
    if temporary is None:
        temporary = Path(tempfile.gettempdir()) / "soia-skills" if temp_root is None else temp_root

    return {
        "config": config.absolute(),
        "state": state_root.absolute(),
        "cache": cache.absolute(),
        "temp": temporary.absolute(),
    }


def validate_custom_roots(roots: Mapping[str, Path], env: Mapping[str, str] | None = None) -> None:
    """Require an explicit marker before trusting an overridden root."""

    values = os.environ if env is None else env
    for kind, variable in ROOT_ENVIRONMENTS.items():
        if not values.get(variable):
            continue
        root = roots[kind].absolute()
        marker = root / ROOT_MARKER
        if marker.is_symlink() or not marker.is_file():
            raise CleanupError(
                f"custom {kind} root requires {ROOT_MARKER}; refuse to claim an unmarked directory"
            )
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CleanupError(f"custom {kind} root marker is invalid") from exc
        if not isinstance(data, dict) or data != {
            "schema_version": 1,
            "managed_by": "soia-skills",
            "root_kind": kind,
        }:
            raise CleanupError(f"custom {kind} root marker does not match the resolved root kind")


def digest_mapping(value: Mapping[str, Any], digest_key: str) -> str:
    payload = {key: item for key, item in value.items() if key != digest_key}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_descendant(path: Path, root: Path) -> bool:
    try:
        path.absolute().relative_to(root.absolute())
    except ValueError:
        return False
    return path.absolute() != root.absolute()


def symlink_in_chain(path: Path, root: Path) -> bool:
    current = path
    while current != root:
        if current.is_symlink():
            return True
        if current.parent == current:
            return True
        current = current.parent
    return root.is_symlink()


def active_marker(path: Path, root: Path, now_timestamp: float) -> Path | None:
    current = path.parent
    cutoff = now_timestamp - 24 * 60 * 60
    while True:
        marker = current / ACTIVE_MARKER
        try:
            if marker.is_file() and not marker.is_symlink() and marker.stat().st_mtime >= cutoff:
                return marker
        except OSError:
            return marker
        if current == root or current.parent == current:
            return None
        current = current.parent


def read_state_policy(path: Path, root: Path, default_days: int) -> dict[str, Any] | None:
    current = path.parent
    while True:
        marker = current / MANAGED_MARKER
        if marker.exists():
            if marker.is_symlink() or not marker.is_file():
                return None
            try:
                data = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
            if not isinstance(data, dict):
                return None
            owner = data.get("owner_skill")
            data_class = data.get("data_class")
            allowed = data.get("cleanup_allowed") is True
            retention = data.get("retention_days", default_days)
            if (
                not isinstance(owner, str)
                or not owner.startswith("soia-")
                or data_class not in STATE_CLASSES
                or not allowed
                or not isinstance(retention, int)
                or retention < 0
            ):
                return None
            return {
                "marker_path": str(marker.absolute()),
                "marker_sha256": file_sha256(marker),
                "owner_skill": owner,
                "data_class": data_class,
                "retention_days": max(default_days, retention),
            }
        if current == root or current.parent == current:
            return None
        current = current.parent


def walk_regular_files(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    files: list[dict[str, Any]] = []
    blocked: list[dict[str, str]] = []
    if not root.exists():
        return files, blocked
    if root.is_symlink() or not root.is_dir():
        blocked.append({"path": str(root), "reason": "managed_root_is_not_a_regular_directory"})
        return files, blocked

    def onerror(error: OSError) -> None:
        blocked.append({"path": str(getattr(error, "filename", root)), "reason": type(error).__name__})

    for current_text, directories, filenames in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        current = Path(current_text)
        safe_directories: list[str] = []
        for name in directories:
            candidate = current / name
            if candidate.is_symlink():
                blocked.append({"path": str(candidate), "reason": "symlink_directory"})
            else:
                safe_directories.append(name)
        directories[:] = safe_directories

        for name in filenames:
            path = current / name
            try:
                metadata = path.lstat()
            except OSError as exc:
                blocked.append({"path": str(path), "reason": type(exc).__name__})
                continue
            if stat.S_ISLNK(metadata.st_mode):
                blocked.append({"path": str(path), "reason": "symlink_file"})
                continue
            if not stat.S_ISREG(metadata.st_mode):
                blocked.append({"path": str(path), "reason": "not_regular_file"})
                continue
            files.append(
                {
                    "path": str(path.absolute()),
                    "size": metadata.st_size,
                    "mtime_ns": metadata.st_mtime_ns,
                    "mtime": datetime.fromtimestamp(metadata.st_mtime, timezone.utc).isoformat(),
                }
            )
    return files, blocked


def build_plan(
    roots: Mapping[str, Path],
    *,
    temp_days: int = 1,
    cache_days: int = 7,
    state_days: int = 30,
    state_max_files: int = 100,
    state_max_bytes: int = 10 * 1024 * 1024,
    cache_max_bytes: int = 512 * 1024 * 1024,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a read-only cleanup plan. No file is modified."""

    for label, value in (
        ("temp_days", temp_days),
        ("cache_days", cache_days),
        ("state_days", state_days),
        ("state_max_files", state_max_files),
        ("state_max_bytes", state_max_bytes),
        ("cache_max_bytes", cache_max_bytes),
    ):
        if not isinstance(value, int) or value < 0:
            raise CleanupError(f"{label} must be a non-negative integer")

    current = now or datetime.now().astimezone()
    if current.tzinfo is None or current.utcoffset() is None:
        raise CleanupError("now must include a timezone")
    now_timestamp = current.timestamp()
    candidates: list[dict[str, Any]] = []
    blocked: list[dict[str, str]] = []
    summaries: dict[str, dict[str, Any]] = {}
    entries_by_kind: dict[str, list[dict[str, Any]]] = {}

    for kind in ("config", "state", "cache", "temp"):
        root = roots[kind].absolute()
        entries, root_blocked = walk_regular_files(root)
        entries_by_kind[kind] = entries
        blocked.extend({**item, "root_kind": kind} for item in root_blocked)
        summaries[kind] = {
            "exists": root.is_dir() and not root.is_symlink(),
            "files": len(entries),
            "bytes": sum(int(item["size"]) for item in entries),
            "candidate_files": 0,
            "candidate_bytes": 0,
            "cleanup_allowed": kind in {"state", "cache", "temp"},
        }

    selected: dict[str, dict[str, Any]] = {}

    def select(kind: str, entry: dict[str, Any], reason: str, risk: str, policy: dict[str, Any] | None = None) -> None:
        path = str(entry["path"])
        item = selected.get(path)
        if item is None:
            item = {
                **entry,
                "root_kind": kind,
                "reasons": [],
                "risk": risk,
            }
            if policy:
                item["state_policy"] = policy
            selected[path] = item
        if reason not in item["reasons"]:
            item["reasons"].append(reason)

    for kind, retention_days, reason, risk in (
        ("temp", temp_days, "temp_expired", "medium"),
        ("cache", cache_days, "cache_expired", "medium"),
    ):
        root = roots[kind].absolute()
        cutoff = now_timestamp - retention_days * 24 * 60 * 60
        for entry in entries_by_kind[kind]:
            path = Path(str(entry["path"]))
            if path.name in {ACTIVE_MARKER, MANAGED_MARKER, ROOT_MARKER}:
                continue
            if active_marker(path, root, now_timestamp) is not None:
                blocked.append({"path": str(path), "root_kind": kind, "reason": "active_run_marker"})
                continue
            if entry["mtime_ns"] / 1_000_000_000 < cutoff:
                select(kind, entry, reason, risk)

    state_root = roots["state"].absolute()
    state_groups: dict[str, dict[str, Any]] = {}
    for entry in entries_by_kind["state"]:
        path = Path(str(entry["path"]))
        if path.name in {ACTIVE_MARKER, MANAGED_MARKER, ROOT_MARKER}:
            continue
        policy = read_state_policy(path, state_root, state_days)
        if policy is None:
            continue
        if active_marker(path, state_root, now_timestamp) is not None:
            blocked.append({"path": str(path), "root_kind": "state", "reason": "active_run_marker"})
            continue
        group = state_groups.setdefault(
            str(policy["marker_path"]),
            {"policy": policy, "entries": []},
        )
        group["entries"].append(entry)
        cutoff = now_timestamp - int(policy["retention_days"]) * 24 * 60 * 60
        if entry["mtime_ns"] / 1_000_000_000 < cutoff:
            select("state", entry, "state_expired", "high", policy)

    for group in state_groups.values():
        policy = group["policy"]
        entries = sorted(
            group["entries"],
            key=lambda item: (int(item["mtime_ns"]), str(item["path"])),
        )
        remaining = [entry for entry in entries if str(entry["path"]) not in selected]
        remaining_bytes = sum(int(entry["size"]) for entry in remaining)
        while len(remaining) > state_max_files or remaining_bytes > state_max_bytes:
            entry = remaining.pop(0)
            reasons: list[str] = []
            if len(remaining) + 1 > state_max_files:
                reasons.append("state_count")
            if remaining_bytes > state_max_bytes:
                reasons.append("state_capacity")
            for reason in reasons:
                select("state", entry, reason, "high", policy)
            remaining_bytes -= int(entry["size"])

    cache_entries = entries_by_kind["cache"]
    cache_total = sum(int(entry["size"]) for entry in cache_entries)
    selected_cache_bytes = sum(
        int(item["size"]) for item in selected.values() if item["root_kind"] == "cache"
    )
    remaining_cache = cache_total - selected_cache_bytes
    if remaining_cache > cache_max_bytes:
        unselected = sorted(
            (entry for entry in cache_entries if str(entry["path"]) not in selected),
            key=lambda item: (int(item["mtime_ns"]), str(item["path"])),
        )
        for entry in unselected:
            path = Path(str(entry["path"]))
            if path.name in {ACTIVE_MARKER, MANAGED_MARKER, ROOT_MARKER}:
                continue
            if active_marker(path, roots["cache"].absolute(), now_timestamp) is not None:
                blocked.append({"path": str(path), "root_kind": "cache", "reason": "active_run_marker"})
                continue
            select("cache", entry, "cache_capacity", "medium")
            remaining_cache -= int(entry["size"])
            if remaining_cache <= cache_max_bytes:
                break

    candidates = sorted(selected.values(), key=lambda item: (item["root_kind"], item["path"]))
    for item in candidates:
        summary = summaries[item["root_kind"]]
        summary["candidate_files"] += 1
        summary["candidate_bytes"] += int(item["size"])

    created_at = current.replace(microsecond=0).isoformat()
    expires_at = (current + timedelta(minutes=PLAN_TTL_MINUTES)).replace(microsecond=0).isoformat()
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "plan_id": f"cleanup-{current.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "created_at": created_at,
        "expires_at": expires_at,
        "authorization_required": True,
        "risk_warning": "Deletion is irreversible. Review the complete candidate summary and obtain explicit customer approval before execution.",
        "roots": {kind: str(path.absolute()) for kind, path in roots.items()},
        "policy": {
            "temp_days": temp_days,
            "cache_days": cache_days,
            "state_days": state_days,
            "state_max_files": state_max_files,
            "state_max_bytes": state_max_bytes,
            "cache_max_bytes": cache_max_bytes,
        },
        "summary": summaries,
        "candidate_files": len(candidates),
        "candidate_bytes": sum(int(item["size"]) for item in candidates),
        "candidates": candidates,
        "blocked": blocked,
    }
    plan["plan_digest"] = digest_mapping(plan, "plan_digest")
    return plan


def ensure_private_parent(path: Path, state_root: Path) -> None:
    if not is_descendant(path, state_root):
        raise CleanupError("plan and receipt files must stay inside the managed state root")
    current = path.parent
    while current != state_root and current.parent != current:
        if current.exists() and current.is_symlink():
            raise CleanupError("plan or receipt parent must not be a symlink")
        current = current.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass


def atomic_write_private_json(path: Path, value: Mapping[str, Any], state_root: Path) -> None:
    ensure_private_parent(path, state_root)
    if path.exists() or path.is_symlink():
        raise CleanupError("refusing to overwrite an existing plan or receipt")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CleanupError(f"unable to read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise CleanupError(f"{label} must be a JSON object")
    return value


def validate_plan(plan: Mapping[str, Any], roots: Mapping[str, Path], expected_digest: str, now: datetime) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise CleanupError("unsupported cleanup plan schema")
    actual_digest = digest_mapping(plan, "plan_digest")
    if plan.get("plan_digest") != actual_digest or expected_digest != actual_digest:
        raise CleanupError("cleanup plan digest mismatch; generate and approve a new plan")
    expected_roots = {kind: str(path.absolute()) for kind, path in roots.items()}
    if plan.get("roots") != expected_roots:
        raise CleanupError("cleanup plan roots do not match the current managed roots")
    created_at = aware_datetime(str(plan.get("created_at", "")), "plan.created_at")
    expires_at = aware_datetime(str(plan.get("expires_at", "")), "plan.expires_at")
    if expires_at <= created_at or now > expires_at:
        raise CleanupError("cleanup plan expired; scan again and request fresh customer approval")
    if not plan.get("authorization_required"):
        raise CleanupError("cleanup plan does not contain the authorization gate")


def validate_candidate(
    candidate: Mapping[str, Any],
    roots: Mapping[str, Path],
    policy: Mapping[str, Any],
    now: datetime,
) -> tuple[Path, os.stat_result]:
    kind = candidate.get("root_kind")
    if kind not in {"state", "cache", "temp"}:
        raise CleanupError("candidate is not in a cleanable storage class")
    root = roots[str(kind)].absolute()
    path = Path(str(candidate.get("path", ""))).absolute()
    if not is_descendant(path, root) or symlink_in_chain(path, root):
        raise CleanupError("candidate escaped its managed root or crossed a symlink")
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        raise CleanupError("candidate no longer exists")
    if not stat.S_ISREG(metadata.st_mode):
        raise CleanupError("candidate is no longer a regular file")
    if metadata.st_size != candidate.get("size") or metadata.st_mtime_ns != candidate.get("mtime_ns"):
        raise CleanupError("candidate changed after planning")
    if path.name in {ACTIVE_MARKER, MANAGED_MARKER, ROOT_MARKER}:
        raise CleanupError("safety marker files are never cleanup candidates")
    if active_marker(path, root, now.timestamp()) is not None:
        raise CleanupError("candidate belongs to an active run")

    age_days = (now.timestamp() - metadata.st_mtime) / (24 * 60 * 60)
    reasons = candidate.get("reasons")
    if not isinstance(reasons, list) or not reasons:
        raise CleanupError("candidate has no cleanup reason")
    if kind == "temp" and "temp_expired" in reasons and age_days < int(policy["temp_days"]):
        raise CleanupError("temporary candidate is no longer expired")
    if kind == "cache" and "cache_expired" in reasons and age_days < int(policy["cache_days"]):
        raise CleanupError("cache candidate is no longer expired")
    if kind == "state":
        state_policy = candidate.get("state_policy")
        if not isinstance(state_policy, dict):
            raise CleanupError("state candidate lacks a managed cleanup policy")
        marker = Path(str(state_policy.get("marker_path", ""))).absolute()
        if not marker.is_file() or marker.is_symlink() or file_sha256(marker) != state_policy.get("marker_sha256"):
            raise CleanupError("state cleanup policy changed after planning")
        current_policy = read_state_policy(path, root, int(policy["state_days"]))
        if current_policy is None or current_policy.get("marker_sha256") != state_policy.get("marker_sha256"):
            raise CleanupError("state candidate is no longer covered by an approved marker")
        state_reasons = set(str(reason) for reason in reasons)
        if "state_expired" in state_reasons and age_days < int(current_policy["retention_days"]):
            raise CleanupError("state candidate is no longer expired")
        if state_reasons <= {"state_count", "state_capacity"}:
            marker_root = marker.parent
            group_entries, _ = walk_regular_files(marker_root)
            ordinary = [
                item
                for item in group_entries
                if Path(str(item["path"])).name not in {ACTIVE_MARKER, MANAGED_MARKER, ROOT_MARKER}
            ]
            over_count = len(ordinary) > int(policy["state_max_files"])
            over_capacity = sum(int(item["size"]) for item in ordinary) > int(policy["state_max_bytes"])
            if not over_count and not over_capacity:
                raise CleanupError("state directory is already below its count and capacity limits")
    return path, metadata


def remove_empty_parents(path: Path, root: Path) -> list[str]:
    removed: list[str] = []
    current = path.parent
    while current != root and is_descendant(current, root):
        if current.is_symlink():
            break
        try:
            current.rmdir()
        except OSError:
            break
        removed.append(str(current))
        current = current.parent
    return removed


def default_state_dir(state_root: Path) -> Path:
    return state_root / "soia-open-env-skills" / "soia-env" / "soia-env-storage-cleanup"


def execute_plan(
    plan_path: Path,
    roots: Mapping[str, Path],
    *,
    expected_digest: str,
    confirmed_plan_id: str,
    authorization_id: str,
    authorized_at: str,
    acknowledgement: str,
    receipt_path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Delete exactly the unchanged files in a fresh, customer-authorized plan."""

    if acknowledgement != ACKNOWLEDGEMENT:
        raise CleanupError("risk acknowledgement missing; deletion was not authorized")
    if not AUTHORIZATION_ID_RE.fullmatch(authorization_id):
        raise CleanupError("authorization_id must be an opaque 8-128 character identifier")
    current = now or datetime.now().astimezone()
    if current.tzinfo is None or current.utcoffset() is None:
        raise CleanupError("now must include a timezone")
    authorization_time = aware_datetime(authorized_at, "authorized_at")
    if authorization_time > current + timedelta(minutes=5):
        raise CleanupError("authorized_at is in the future")

    state_root = roots["state"].absolute()
    if not is_descendant(plan_path.absolute(), state_root):
        raise CleanupError("cleanup plan must be stored inside the managed state root")
    plan = load_json_object(plan_path, "cleanup plan")
    validate_plan(plan, roots, expected_digest, current)
    if confirmed_plan_id != plan.get("plan_id"):
        raise CleanupError("customer-confirmed plan_id does not match the cleanup plan")
    created_at = aware_datetime(str(plan["created_at"]), "plan.created_at")
    if authorization_time < created_at:
        raise CleanupError("customer authorization predates the cleanup plan")

    disk_anchor = next((path for path in roots.values() if path.exists()), Path.home())
    free_before = shutil.disk_usage(disk_anchor).free
    deleted: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    removed_directories: list[str] = []
    policy = plan.get("policy")
    if not isinstance(policy, dict):
        raise CleanupError("cleanup plan policy is missing")

    cache_remaining = sum(int(item["size"]) for item in walk_regular_files(roots["cache"])[0])
    for candidate in plan.get("candidates", []):
        if not isinstance(candidate, dict):
            skipped.append({"path": "<invalid>", "reason": "candidate_not_an_object"})
            continue
        try:
            if (
                candidate.get("root_kind") == "cache"
                and candidate.get("reasons") == ["cache_capacity"]
                and cache_remaining <= int(policy["cache_max_bytes"])
            ):
                raise CleanupError("cache is already below the configured capacity")
            path, metadata = validate_candidate(candidate, roots, policy, current)
            path.unlink()
            if path.exists():
                raise CleanupError("candidate still exists after deletion")
            deleted.append(
                {
                    "path": str(path),
                    "root_kind": candidate["root_kind"],
                    "bytes": metadata.st_size,
                    "reasons": candidate["reasons"],
                }
            )
            if candidate["root_kind"] == "cache":
                cache_remaining -= metadata.st_size
            removed_directories.extend(remove_empty_parents(path, roots[str(candidate["root_kind"])].absolute()))
        except (CleanupError, OSError) as exc:
            skipped.append({"path": str(candidate.get("path", "<invalid>")), "reason": str(exc)})

    free_after = shutil.disk_usage(disk_anchor).free
    completed_at = current.replace(microsecond=0).isoformat()
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "status": "completed" if not skipped else "completed_with_skips",
        "plan_id": plan["plan_id"],
        "confirmed_plan_id": confirmed_plan_id,
        "plan_digest": plan["plan_digest"],
        "authorization_id": authorization_id,
        "authorized_at": authorization_time.replace(microsecond=0).isoformat(),
        "checked_at": completed_at,
        "deleted_files": len(deleted),
        "deleted_bytes": sum(int(item["bytes"]) for item in deleted),
        "deleted": deleted,
        "removed_empty_directories": removed_directories,
        "skipped": skipped,
        "disk_free_before": free_before,
        "disk_free_after": free_after,
        "disk_free_delta": free_after - free_before,
    }
    receipt["receipt_digest"] = digest_mapping(receipt, "receipt_digest")
    destination = receipt_path or default_state_dir(state_root) / "receipts" / f"{plan['plan_id']}.receipt.json"
    atomic_write_private_json(destination.absolute(), receipt, state_root)
    receipt["receipt_path"] = str(destination.absolute())
    return receipt


def verify_receipt(receipt_path: Path, roots: Mapping[str, Path]) -> dict[str, Any]:
    state_root = roots["state"].absolute()
    if not is_descendant(receipt_path.absolute(), state_root):
        raise CleanupError("cleanup receipt must be stored inside the managed state root")
    receipt = load_json_object(receipt_path, "cleanup receipt")
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise CleanupError("unsupported cleanup receipt schema")
    if receipt.get("receipt_digest") != digest_mapping(receipt, "receipt_digest"):
        raise CleanupError("cleanup receipt digest mismatch")
    present = [item["path"] for item in receipt.get("deleted", []) if Path(str(item.get("path", ""))).exists()]
    result = {
        "valid": not present,
        "checked_at": now_rfc3339(),
        "deleted_files": receipt.get("deleted_files", 0),
        "deleted_bytes": receipt.get("deleted_bytes", 0),
        "reappeared_files": present,
    }
    return result


def human_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def print_plan_summary(plan: Mapping[str, Any]) -> None:
    print("| 数据类别 | 当前大小 | 可清理大小 | 候选文件 | 风险 |")
    print("|---|---:|---:|---:|---|")
    for kind, label, risk in (
        ("config", "配置", "禁止清理"),
        ("state", "审计状态", "高"),
        ("cache", "缓存", "中"),
        ("temp", "临时文件", "中"),
    ):
        item = plan["summary"][kind]
        print(
            f"| {label} | {human_bytes(int(item['bytes']))} | "
            f"{human_bytes(int(item['candidate_bytes']))} | {item['candidate_files']} | {risk} |"
        )
    print(f"plan_id={plan['plan_id']}")
    print(f"plan_digest={plan['plan_digest']}")
    print("风险提醒：删除不可撤销。必须先向客户展示本清单并取得明确授权，才能运行 clean --execute。")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    def add_policy(target: argparse.ArgumentParser) -> None:
        target.add_argument("--temp-days", type=int, default=1)
        target.add_argument("--cache-days", type=int, default=7)
        target.add_argument("--state-days", type=int, default=30)
        target.add_argument("--state-max-files", type=int, default=100)
        target.add_argument("--state-max-bytes", type=int, default=10 * 1024 * 1024)
        target.add_argument("--cache-max-bytes", type=int, default=512 * 1024 * 1024)
        target.add_argument("--json", action="store_true")

    scan = subparsers.add_parser("scan", help="Read-only scan; never writes or deletes files.")
    add_policy(scan)

    plan = subparsers.add_parser("plan", help="Write an immutable cleanup plan inside managed state.")
    add_policy(plan)
    plan.add_argument("--output", help="Plan path inside the managed state root.")

    clean = subparsers.add_parser("clean", help="Execute a fresh, explicitly authorized cleanup plan.")
    clean.add_argument("--plan", required=True)
    clean.add_argument("--plan-digest", required=True)
    clean.add_argument("--confirmed-plan-id", required=True)
    clean.add_argument("--authorization-id", required=True)
    clean.add_argument("--authorized-at", required=True)
    clean.add_argument("--acknowledge-risk", required=True)
    clean.add_argument("--receipt", help="Receipt path inside the managed state root.")
    clean.add_argument("--execute", action="store_true")
    clean.add_argument("--json", action="store_true")

    verify = subparsers.add_parser("verify", help="Verify that a cleanup receipt remains valid.")
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    roots = managed_roots()
    try:
        validate_custom_roots(roots)
        if args.command in {"scan", "plan"}:
            plan = build_plan(
                roots,
                temp_days=args.temp_days,
                cache_days=args.cache_days,
                state_days=args.state_days,
                state_max_files=args.state_max_files,
                state_max_bytes=args.state_max_bytes,
                cache_max_bytes=args.cache_max_bytes,
            )
            if args.command == "plan":
                destination = (
                    Path(args.output).expanduser().absolute()
                    if args.output
                    else default_state_dir(roots["state"]) / "plans" / f"{plan['plan_id']}.json"
                )
                atomic_write_private_json(destination, plan, roots["state"])
                plan["plan_path"] = str(destination)
            if args.json:
                print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print_plan_summary(plan)
            return 0

        if args.command == "clean":
            if not args.execute:
                raise CleanupError("clean requires --execute after explicit customer authorization")
            receipt = execute_plan(
                Path(args.plan).expanduser().absolute(),
                roots,
                expected_digest=args.plan_digest,
                confirmed_plan_id=args.confirmed_plan_id,
                authorization_id=args.authorization_id,
                authorized_at=args.authorized_at,
                acknowledgement=args.acknowledge_risk,
                receipt_path=Path(args.receipt).expanduser().absolute() if args.receipt else None,
            )
            if args.json:
                print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(
                    f"status={receipt['status']} deleted_files={receipt['deleted_files']} "
                    f"deleted_bytes={receipt['deleted_bytes']} skipped={len(receipt['skipped'])} "
                    f"checked_at={receipt['checked_at']}"
                )
            return 0 if not receipt["skipped"] else 1

        result = verify_receipt(Path(args.receipt).expanduser().absolute(), roots)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"valid={str(result['valid']).lower()} deleted_files={result['deleted_files']} "
                f"reappeared={len(result['reappeared_files'])} checked_at={result['checked_at']}"
            )
        return 0 if result["valid"] else 1
    except CleanupError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
