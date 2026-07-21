#!/usr/bin/env python3
"""Append privacy-safe installation progress to the current skill's state directory."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


REPO_NAME = "soia-open-env-skills"
SKILL_TYPE = "soia-env"
MARKER_NAME = ".soia-managed-storage.json"
ACTIONS = {"install", "update", "repair"}
STAGES = {
    "checking",
    "planning",
    "waiting_confirmation",
    "installing",
    "updating",
    "verifying",
    "completed",
    "failed",
    "blocked",
}
STATUSES = {"in_progress", "waiting", "completed", "failed", "blocked"}
STAGE_LABELS = {
    "checking": "检查",
    "planning": "计划",
    "waiting_confirmation": "等待确认",
    "installing": "安装",
    "updating": "更新",
    "verifying": "验证",
    "completed": "完成",
    "failed": "失败",
    "blocked": "被阻塞",
}
STATUS_LABELS = {
    "in_progress": "进行中",
    "waiting": "等待",
    "completed": "已完成",
    "failed": "失败",
    "blocked": "被阻塞",
}
ALLOWED_TRANSITIONS = {
    "checking": {"checking", "planning", "failed", "blocked"},
    "planning": {"planning", "waiting_confirmation", "installing", "updating", "failed", "blocked"},
    "waiting_confirmation": {"waiting_confirmation", "planning", "installing", "updating", "failed", "blocked"},
    "installing": {"installing", "verifying", "failed", "blocked"},
    "updating": {"updating", "verifying", "failed", "blocked"},
    "verifying": {"verifying", "completed", "failed", "blocked"},
}
RESULT_CODES = {
    "checking_started": ("checking", "正在检查环境与安装来源"),
    "plan_ready": ("planning", "已生成安装或更新方案"),
    "waiting_customer_confirmation": (
        "waiting_confirmation",
        "正在等待客户确认风险动作",
    ),
    "installation_started": ("installing", "安装已开始"),
    "update_started": ("updating", "更新已开始"),
    "verification_started": ("verifying", "正在验证安装或更新结果"),
    "operation_completed": ("completed", "操作已完成并通过验证"),
    "operation_failed": ("failed", "操作失败，已保留原有环境"),
    "operation_blocked": ("blocked", "操作被阻塞，未继续变更"),
}
SKILL_NAME_RE = re.compile(r"^soia-env-[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{7,127}$")


class ProgressError(ValueError):
    """Raised when a progress record would violate the audit contract."""


def now_rfc3339() -> str:
    """Return the recorder's current time; callers cannot backfill timestamps."""

    return datetime.now().astimezone().isoformat(timespec="microseconds")


def parse_rfc3339(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ProgressError("progress record contains an invalid checked_at") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProgressError("progress record contains an invalid checked_at")
    return parsed


def state_directory(
    skill_name: str,
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path:
    values = os.environ if env is None else env
    user_home = Path.home() if home is None else home
    platform_id = sys.platform if platform_name is None else platform_name
    configured = values.get("SOIA_SKILLS_STATE_HOME")
    if configured:
        base = Path(configured).expanduser()
    elif platform_id.startswith("win"):
        base = Path(
            values.get("LOCALAPPDATA", user_home / "AppData" / "Local")
        ) / "soia-skills" / "state"
    else:
        base = Path(
            values.get("XDG_STATE_HOME", user_home / ".local" / "state")
        ) / "soia-skills"
    if not base.is_absolute():
        raise ProgressError("state root must be an absolute path")
    return base / REPO_NAME / SKILL_TYPE / skill_name


def ensure_marker(directory: Path, skill_name: str) -> None:
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ProgressError("skill state directory is not a regular directory")
    directory.mkdir(parents=True, exist_ok=True)
    try:
        directory.chmod(0o700)
    except OSError:
        pass
    marker = directory / MARKER_NAME
    expected = {
        "schema_version": 1,
        "owner_skill": skill_name,
        "data_class": "audit_state",
        "retention_days": 30,
        "cleanup_allowed": True,
    }
    if marker.exists() or marker.is_symlink():
        if marker.is_symlink() or not marker.is_file():
            raise ProgressError("managed-state marker is not a regular file")
        try:
            current = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProgressError("managed-state marker is invalid") from exc
        if current != expected:
            raise ProgressError("managed-state marker does not match this skill")
        return
    try:
        with marker.open("x", encoding="utf-8") as handle:
            json.dump(expected, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        marker.chmod(0o600)
    except FileExistsError:
        ensure_marker(directory, skill_name)


def last_event(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ProgressError("progress record is not a regular file")
    latest: dict[str, Any] | None = None
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ProgressError("progress record contains a non-object event")
                    latest = value
    except (OSError, json.JSONDecodeError) as exc:
        raise ProgressError("progress record is unreadable") from exc
    return latest


def append_event(
    *,
    skill_name: str,
    run_id: str,
    action: str,
    stage: str,
    status: str,
    result_code: str,
    customer_requested_latest: bool = False,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> tuple[dict[str, Any], Path]:
    if not SKILL_NAME_RE.fullmatch(skill_name):
        raise ProgressError("skill name must be a canonical soia-env name")
    if not RUN_ID_RE.fullmatch(run_id):
        raise ProgressError("run_id must be an opaque 8-128 character identifier")
    if action not in ACTIONS or stage not in STAGES or status not in STATUSES:
        raise ProgressError("action, stage, or status is unsupported")
    if action != "update" and customer_requested_latest:
        raise ProgressError("latest-version authorization applies only to updates")
    expected_stage = RESULT_CODES.get(result_code, (None, None))[0]
    if expected_stage != stage:
        raise ProgressError("result_code does not match the progress stage")
    if stage == "completed" and status != "completed":
        raise ProgressError("completed stage requires completed status")
    if stage == "failed" and status != "failed":
        raise ProgressError("failed stage requires failed status")
    if stage == "blocked" and status != "blocked":
        raise ProgressError("blocked stage requires blocked status")
    if stage == "waiting_confirmation" and status != "waiting":
        raise ProgressError("waiting_confirmation stage requires waiting status")
    if status == "waiting" and stage != "waiting_confirmation":
        raise ProgressError("waiting status requires the waiting_confirmation stage")
    if stage in {"checking", "planning", "installing", "updating", "verifying"}:
        if status != "in_progress":
            raise ProgressError("active progress stages require in_progress status")
    if action == "update" and stage == "installing":
        raise ProgressError("update action must use the updating stage")
    if action != "update" and stage == "updating":
        raise ProgressError("updating stage requires the update action")
    if action == "update" and stage in {"updating", "verifying", "completed"}:
        if not customer_requested_latest:
            raise ProgressError(
                "update execution requires an explicit customer request for the latest version"
            )

    directory = state_directory(
        skill_name, env=env, home=home, platform_name=platform_name
    )
    progress_dir = directory / "installation-progress"
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ProgressError("skill state directory is not a regular directory")
    if progress_dir.is_symlink() or (
        progress_dir.exists() and not progress_dir.is_dir()
    ):
        raise ProgressError("progress directory is not a regular directory")
    path = progress_dir / f"{run_id}.jsonl"
    previous = last_event(path)
    if previous is None and stage != "checking":
        raise ProgressError("the first progress stage must be checking")
    if previous and previous.get("status") in {"completed", "failed", "blocked"}:
        raise ProgressError("cannot append after a terminal progress event")
    if previous:
        if previous.get("run_id") != run_id or previous.get("skill") != skill_name:
            raise ProgressError("progress record identity changed within one run")
        if previous.get("action") != action:
            raise ProgressError("progress action changed within one run")
        previous_stage = str(previous.get("stage", ""))
        if stage not in ALLOWED_TRANSITIONS.get(previous_stage, set()):
            raise ProgressError(
                f"invalid progress transition from {previous_stage or '<missing>'} to {stage}"
            )
    if path.is_symlink():
        raise ProgressError("progress record must not be a symlink")

    recorded_at = parse_rfc3339(now_rfc3339())
    if previous:
        previous_at = parse_rfc3339(str(previous.get("checked_at", "")))
        if recorded_at <= previous_at:
            recorded_at = previous_at + timedelta(microseconds=1)
    safe_checked_at = recorded_at.isoformat(timespec="microseconds")

    ensure_marker(directory, skill_name)
    if progress_dir.is_symlink() or (
        progress_dir.exists() and not progress_dir.is_dir()
    ):
        raise ProgressError("progress directory is not a regular directory")
    progress_dir.mkdir(parents=True, exist_ok=True)
    try:
        progress_dir.chmod(0o700)
    except OSError:
        pass

    event = {
        "schema_version": 1,
        "run_id": run_id,
        "skill": skill_name,
        "action": action,
        "stage": stage,
        "status": status,
        "checked_at": safe_checked_at,
        "customer_requested_latest": bool(customer_requested_latest),
        "result_code": result_code,
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return event, path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-name", default=Path(__file__).resolve().parents[1].name)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS))
    parser.add_argument("--stage", required=True, choices=sorted(STAGES))
    parser.add_argument("--status", required=True, choices=sorted(STATUSES))
    parser.add_argument("--result-code", required=True, choices=sorted(RESULT_CODES))
    parser.add_argument("--customer-requested-latest", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        event, _path = append_event(
            skill_name=args.skill_name,
            run_id=args.run_id,
            action=args.action,
            stage=args.stage,
            status=args.status,
            result_code=args.result_code,
            customer_requested_latest=args.customer_requested_latest,
        )
    except ProgressError as exc:
        print(
            json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    if args.json:
        print(json.dumps(event, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("| 阶段 | 当前状态 | 更新时间 | 处理结果 |")
        print("|---|---|---|---|")
        print(
            f"| {STAGE_LABELS[event['stage']]} | {STATUS_LABELS[event['status']]} | "
            f"{event['checked_at']} | {RESULT_CODES[event['result_code']][1]} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
