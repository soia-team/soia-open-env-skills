#!/usr/bin/env python3
"""Build a machine-readable SOIA skill-install plan without changing a host."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
AGENTS = ("claude", "codex", "workbuddy")
TARGET_KINDS = ("skill", "domain", "all")
SCOPES = ("project", "global")

# These are capability facts, not install commands.  The commands and their
# current syntax live in references/capabilities.md and are checked before use.
CAPABILITIES = {
    "claude": {
        "project": {"skill": "supported", "domain": "capability_check", "all": "capability_check"},
        "global": {"skill": "supported", "domain": "supported", "all": "supported"},
    },
    "codex": {
        "project": {"skill": "supported", "domain": "capability_check", "all": "capability_check"},
        "global": {"skill": "supported", "domain": "supported", "all": "supported"},
    },
    "workbuddy": {
        "project": {"skill": "unsupported", "domain": "unsupported", "all": "unsupported"},
        "global": {"skill": "supported", "domain": "supported", "all": "supported"},
    },
}


def _as_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_agents(value: Any) -> tuple[list[str], list[str]]:
    raw = []
    for item in _as_list(value):
        raw.extend(str(item).split(","))
    names = []
    errors = []
    for item in raw:
        name = item.strip().lower().replace("-", "_")
        aliases = {"claude_code": "claude", "claude-code": "claude", "work_buddy": "workbuddy", "*": "*"}
        name = aliases.get(name, name)
        if name == "*":
            names = list(AGENTS)
            continue
        if name not in AGENTS:
            errors.append(f"unknown agent: {item}")
        elif name not in names:
            names.append(name)
    return names, errors


def normalize_target(selection: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    target = selection.get("target", {})
    if isinstance(target, str):
        target = {"kind": target}
    if not isinstance(target, dict):
        return {"kind": None, "name": None}, ["target must be an object or target kind string"]
    kind = selection.get("target_kind", target.get("kind"))
    name = selection.get("target_name", target.get("name", target.get("id")))
    kind = str(kind).lower() if kind is not None else None
    errors = []
    if kind not in TARGET_KINDS:
        errors.append("target kind is required: skill, domain, or all")
    if kind in {"skill", "domain"} and not str(name or "").strip():
        errors.append(f"target name is required for {kind}")
    return {"kind": kind, "name": str(name).strip() if name else None}, errors


def normalize_selection(selection: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    scope = selection.get("scope")
    scope = str(scope).lower() if scope is not None else None
    errors = []
    if scope not in SCOPES:
        errors.append("scope is required: project or global")
    agents, agent_errors = normalize_agents(selection.get("agents"))
    errors.extend(agent_errors)
    if not agents:
        errors.append("at least one agent is required: claude, codex, or workbuddy")
    target, target_errors = normalize_target(selection)
    errors.extend(target_errors)
    confirmed = bool(selection.get("confirmed", False))
    return {"scope": scope, "agents": agents, "target": target, "confirmed": confirmed}, errors


def build_plan(selection: dict[str, Any]) -> dict[str, Any]:
    normalized, errors = normalize_selection(selection)
    missing = bool(errors)
    target = normalized["target"]
    kind = target["kind"]
    matrix = []
    for agent in normalized["agents"]:
        capability = CAPABILITIES[agent][normalized["scope"]][kind] if kind in TARGET_KINDS and normalized["scope"] else "selection_required"
        if capability == "supported":
            status = "planned"
            reason = "capability is available; this output is plan-only"
        elif capability == "capability_check":
            status = "blocked"
            reason = "project aggregate install requires a host-specific installer capability check"
        elif capability == "unsupported":
            status = "blocked"
            reason = "this host's supported installer writes a global/user store, not a project scope"
        else:
            status = "selection_required"
            reason = "scope, agent, and target must be selected first"
        matrix.append({
            "scope": normalized["scope"],
            "agent": agent,
            "target_kind": kind,
            "target_name": target["name"],
            "capability": capability,
            "status": status,
            "reason": reason,
        })
    pending = missing or not normalized["confirmed"]
    if missing:
        state = "selection_required"
    elif any(row["status"] == "blocked" for row in matrix):
        state = "capability_blocked"
    elif not normalized["confirmed"]:
        state = "confirmation_required"
    else:
        state = "ready"
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": normalized["scope"],
        "agents": normalized["agents"],
        "target": target,
        "target_kind": kind,
        "target_name": target["name"],
        "selection_required": missing,
        "pending": pending,
        "pending_reason": errors if errors else (["explicit confirmation required before installation"] if pending else []),
        "state": state,
        "confirmed": normalized["confirmed"],
        "dry_run": True,
        "plan_only": True,
        "matrix": matrix,
    }


def run_selftest() -> None:
    missing = build_plan({})
    if not missing["selection_required"] or missing["matrix"] or missing["state"] != "selection_required":
        raise AssertionError("missing selection did not fail closed")
    project = build_plan({"scope": "project", "agents": ["codex"], "target": {"kind": "skill", "name": "example"}})
    if project["selection_required"] or project["matrix"][0]["status"] != "planned" or not project["pending"]:
        raise AssertionError("project single-skill plan is incorrect")
    global_all = build_plan({"scope": "global", "agents": ["*"], "target": {"kind": "all"}, "confirmed": True})
    if global_all["agents"] != list(AGENTS) or len(global_all["matrix"]) != 3 or not global_all["plan_only"]:
        raise AssertionError("explicit global all plan is incorrect")
    selected = build_plan({"scope": "global", "agents": ["claude"], "target": {"kind": "domain", "name": "soia-dev"}})
    if [row["agent"] for row in selected["matrix"]] != ["claude"]:
        raise AssertionError("selected-agent plan affected another host")
    blocked = build_plan({"scope": "project", "agents": ["workbuddy"], "target": {"kind": "skill", "name": "example"}})
    if blocked["matrix"][0]["status"] != "blocked":
        raise AssertionError("unsupported project capability was not blocked")
    print("selftest: passed (selection gate, scope/target matrix, explicit all, host isolation, capability gap)")


def load_json(path: str) -> dict[str, Any]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("selection JSON must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Selection JSON file, or - for stdin.")
    parser.add_argument("--scope", choices=SCOPES)
    parser.add_argument("--agents", help="Comma-separated agents or *.")
    parser.add_argument("--target-kind", choices=TARGET_KINDS)
    parser.add_argument("--target-name")
    parser.add_argument("--confirmed", action="store_true", help="Record that the customer confirmed this plan; never installs.")
    parser.add_argument("--selftest", action="store_true", help="Run plan-only checks without invoking an installer.")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            run_selftest()
            return 0
        selection = load_json(args.input) if args.input else {}
        for key, value in (("scope", args.scope), ("agents", args.agents), ("target_kind", args.target_kind), ("target_name", args.target_name)):
            if value is not None:
                selection[key] = value
        if args.confirmed:
            selection["confirmed"] = True
        print(json.dumps(build_plan(selection), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
