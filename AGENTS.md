# AGENTS.md - soia-open-env-skills

Rules for agents editing this public environment-tools skill repository.

## Purpose

This repository publishes beginner-friendly, cross-platform skills for diagnosing
network issues and installing/verifying common development tools. It must work
for users who do not share the maintainer's machine, shell, accounts, paths, or
private configuration.

## Public repository contract

- Real skills live only under `skills/<skill-name>/`.
- Every skill has `SKILL.md` with `name`, `description`, `version`, timestamps,
  and author fields in frontmatter, plus customer-readable setup and receipt
  sections.
- Read `DATA_STORAGE_SPEC.md` before adding configuration, credentials, logs,
  cache, temporary files, or machine-readable receipts.
- Keep required workflow in `SKILL.md`; put provider/version facts in that
  skill's own `references/` directory.
- Never commit API keys, access tokens, cookies, passwords, private config,
  local absolute paths, or user-specific machine details.
- Examples use placeholders such as `<path>`, `<YOUR_KEY>`, and `<repo>`.
- New scripts must use portable path APIs and must not hardcode Unix-only
  temporary or config paths.
- Customer-facing status tables must include a runtime `更新时间`; structured
  receipts use timezone-aware RFC 3339 `checked_at`. These are not the
  frontmatter source-code timestamps.
- Store provider credentials in provider-owned login flows or the OS keychain.
  Ordinary SOIA config files contain non-secret settings and paths only.
- Separate persistent audit state, disposable cache, and per-run temporary
  files according to `DATA_STORAGE_SPEC.md`; read-only skills write nothing by
  default.

## Beginner safety boundary

- Detect OS, architecture, shell, package manager, and existing versions before
  proposing installation.
- Prefer official vendor download pages and signed installers; do not use
  `curl | bash`, opaque third-party installers, or guessed package commands.
- Diagnose network access read-only first. Do not silently modify proxies, DNS,
  certificates, firewall rules, shell profiles, or system-wide settings.
- Before installing, uninstalling, changing PATH, or using administrator
  privileges, show the exact plan and obtain confirmation for that state change.
- Version discovery never authorizes an update. By default, report the current
  and available versions without changing the machine. Run an updater only when
  the customer explicitly asks to update or upgrade to the latest version;
  ambiguous requests such as "update X" stop after the version report and ask
  whether the customer wants the latest version.
- During an authorized installation or update, show each phase to the customer
  as it happens and append a redacted progress event to the skill's private state
  directory. At minimum record checking, planning/confirmation, execution,
  verification, and completed/failed/blocked. Read-only checks remain stateless.
- The customer should not need to operate a terminal. The agent may run safe
  checks; the customer performs browser login, CAPTCHA, OS security prompts, and
  product consent in the official UI.
- Never request or print passwords, API keys, tokens, or session strings.

## Three-repository cooperation

This repository owns environment readiness only. It may recommend or hand off
to:

- `soia-open-skills`: public PKM, cloud-drive, and knowledge-base workflows;
- `soia-private-skills`: private SOIA governance and internal execution skills.

Do not copy or modify skills from either repository. Check availability, state
the dependency, and pass only portable outputs such as OS/tool/version/status.
Environment setup must finish with a machine-readable readiness summary that a
downstream skill can consume.

## Validation

Before committing:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py
git diff --check
```

For changed skills, run the available quick validator as an additional check.

## GitHub workflow

Develop on a short-lived branch, open a PR to `main`, wait for the `audit`
status check, and merge through GitHub. Keep `main` protected and require the
repository audit workflow for pull requests.

## 维护本仓技能

技能契约、调试安装、新增/改名/拆分/删除的完整流程，以及插件市场发布步骤，统一见
元仓的 [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md)。
本文件只保留本仓特有的用途、边界与验证命令。
