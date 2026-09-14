# 环境技能边界细则

仅编写或执行环境诊断、安装、更新技能时按需阅读；普通规则文案不探测机器、不写机器状态。

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

本节仅适用于技能实际执行环境诊断、安装或机器变更，不要求普通文档维护先探测或改动本机环境。

- Detect OS, architecture, shell, package manager, and existing versions before
  proposing installation.
- Prefer official vendor download pages and signed installers; do not use
  `curl | bash`, opaque third-party installers, or guessed package commands.
- Diagnose network access read-only first. Do not silently modify proxies, DNS,
  certificates, firewall rules, shell profiles, or system-wide settings.
- Before installing, uninstalling, changing PATH, or using administrator
  privileges, show the exact plan and obtain confirmation for that state change.
  已确认计划包含目标、范围、版本策略和影响时直接按计划执行，不为同一步重复询问；目标或影响变化才重新确认。
- Version discovery never authorizes an update. 只问版本时只报告，不改机器。
  明确要求更新且已确认目标、范围与版本策略时完成更新及验证；仅当这些信息缺失会实质影响结果，或涉及未批准的跨大版本/安装范围变化时询问。不把所有 "update X" 一律视为必须再问一次，但仍保留上条具体安装计划的确认门。
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

- `soia-env-open-skills-install` (this repo): installs SOIA open-skill plugins across hosts after CLIs are ready;
- `soia-open-skills`: ecosystem discovery, installation routing and release coordination; PKM workflows belong to their corresponding domain repository;
- `soia-private-skills`: private SOIA governance and internal execution skills.

本仓维护不自动授权复制或修改其他仓库技能；用户明确指定的跨仓任务按各仓边界分别处理。Check availability, state
the dependency, and pass only portable outputs such as OS/tool/version/status.
实际环境 setup 完成后提供下游可消费的 machine-readable readiness summary；普通说明、代码审阅和本仓文档维护不生成机器配置回执。
