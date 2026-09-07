# AGENTS.md - soia-open-env-skills

Rules for agents editing this public environment-tools skill repository.

## 规则适用与任务完成

- 宿主实际加载的全局规则、父目录规则与本文件共同适用；本文件补充本仓事实和边界，不把共享贡献手册的旧示例当作新的授权。遇到无法按层级消解的实质冲突，指出具体条款，仅暂停受影响动作。
- 解释、诊断或审阅只读取相关规则与证据，不自动授权修复、安装或发布；明确要求实施且范围已清楚时，完成修改、适度验证和结果交付，不只返回计划。
- 已批准范围内的常规补丁、相关只读检查和验证连续推进；只在缺少会实质改变结果的信息、重叠改动无法安全保留，或下一步超出授权时询问。已确认且目标与影响未变的计划不重复确认。
- 未提交改动属于原作者；不清理、不混入提交、不覆盖。无关脏文件不阻断可隔离工作，真实重叠只暂停冲突部分。
- 不因仓名或“完整交付”默认启动多模型、子 Agent、全生态扫描、全量安装或产品治理流程；仅在用户要求、适用项目角色规则或任务风险明确需要时采用对应流程。
- 提交、远端写入、合并、部署、发布、发送消息、权限变更、凭据操作及重要数据删除仍遵守各自授权门；本地修改完成不代表这些后续动作已获授权。
- 交付说明实际改动、验证结果、未验证项及阻塞。要求实施的任务应做到授权边界内可验证的完成；区分本次已请求但待批的剩余步骤与未请求的后续动作；未请求的发布/安装不属于本次未完成工作。

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

## Validation

日常修改按影响面验证；纯指令文档先核对 diff、链接和规则一致性，行为变化运行受影响测试。涉及技能行为、脚本、依赖或公共工具的提交前执行以下完整门禁；纯指令/说明文档提交不机械套用全仓测试，但 CI/正式发布明确要求的检查不得省略：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py
git diff --check
```

修改技能时补充兼容的 quick validator；若仅因本仓必需的扩展 frontmatter 不受支持而失败，记录限制并以本仓 audit 判定，不删除必需字段。其他真实校验错误仍须处理。

## Git Workflow

- **Branch off `main`** (the latest formal release), then open the PR against
  `dev` and wait for the `audit` check. Verify the expected `main` → `dev`
  ancestry and actual merge conflicts; ancestry alone is not proof of a clean merge. Branch off `dev` only when your change
  genuinely builds on unreleased work, and say so in the PR body.
- `main` never receives PRs. It moves only by **fast-forward from `dev`** during
  a formal release driven by `soia-meta-skill-release`, so `main` and `dev` then
  point at the same commit. 普通开发不直接 push `main` 或 `dev`；唯一例外是已获本次发布授权、通过 CI 且祖先关系校验成立后，由发布流程快进 `dev` → `main`。
- Plugin manifests on `dev` carry a `-SNAPSHOT` version naming the next release
  target. Do not change manifest versions in feature PRs; versions move only
  during a release.

## 维护本仓技能

技能契约、调试安装、新增/改名/拆分/删除的完整流程，以及插件市场发布步骤，统一见
元仓的 [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md)。
本文件只保留本仓特有的用途、边界与验证命令。
