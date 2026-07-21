#!/usr/bin/env python3
"""Check that every real skill under skills/ is mentioned in the top-level README.md.

Scope, on purpose: this is a literal substring presence check only. It answers
one narrow question -- "does this skill name appear anywhere in README.md's
text?" -- and nothing else. It does not check whether the description is
accurate, whether the status marker (checked/warning) is correct, or whether
the skill is filed under the right section. That kind of semantic review is
expensive to automate reliably and produces high false-positive rates as the
README's prose evolves; a human (or a doc-sync skill) is the right tool for
that job. This script only guards against the cheapest, highest-value failure
mode: a skill quietly shipped or renamed and the top-level README never
mentions it at all.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` looking for a directory containing `.git`.

    Falls back to `start` itself when no `.git` directory is found, so the
    script still runs (against whatever directory it was pointed at) instead
    of failing outright in environments without a full git checkout.
    """
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def discover_skill_names(repo_root: Path) -> list[str]:
    """Return the real skill names: subdirectories of skills/ that have a SKILL.md.

    Skips anything under skills/ without a SKILL.md -- for example
    skills/README.md (a file, not a directory) or any stray non-skill entry.
    """
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return []
    names = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            names.append(entry.name)
    return names


def find_missing(skill_names: list[str], readme_text: str) -> list[str]:
    """Return skill names that do not appear as a literal substring of readme_text."""
    return [name for name in skill_names if name not in readme_text]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that every skills/<name>/SKILL.md skill is mentioned in the top-level README.md."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to check. Defaults to the nearest ancestor of the current "
        "directory that contains .git, or the current directory if none is found.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root(Path.cwd())
    readme_path = repo_root / "README.md"

    skill_names = discover_skill_names(repo_root)
    if not skill_names:
        print(f"no skills with SKILL.md found under {repo_root / 'skills'}", file=sys.stderr)
        return 1

    if not readme_path.is_file():
        print(f"missing {readme_path}", file=sys.stderr)
        return 1

    readme_text = readme_path.read_text(encoding="utf-8")
    missing = find_missing(skill_names, readme_text)

    if missing:
        for name in missing:
            print(name)
        return 1

    print(f"✓ 全部 {len(skill_names)} 个技能都在 README.md 里被提及")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
