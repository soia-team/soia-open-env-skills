---
name: soia-env-ai-cli-upgrade
description: 审计并按授权升级多款 AI CLI，先预演并核验结果。触发：「升级 AI CLI」「更新 Claude/Kimi」「检查 CLI 版本」。
version: 2.3.0
created_at: 2026-07-09 07:45:34
updated_at: 2026-08-08 15:20:00
created_by: claude opus 4.6
updated_by: claude-fable-5
---

# soia-env-ai-cli-upgrade

Use this skill when the user asks to audit, dry-run, or upgrade local AI and
developer CLIs in a repeatable way.

Do not use it when the user only asks how to install one known CLI and no
version audit or batch workflow is needed.

> **引擎（v2.2.0）**：纯 Python 标准库单文件 `scripts/upgrade_ai_clis.py`。
> 由同名 bash 引擎逐行为移植而来，对外契约（环境变量、表格列、状态字、退出码、
> 日志命名与轮转）由仓级契约测试双引擎锁定后完成切换；真机全量 dry-run 逐行
> 对照仅存在一处**有意差异**：新增 `~/.opencode/bin` 原生安装探测回退
> （2026-08-08 真机实跑发现旧 shell PATH 缺失时误报未安装）。纯 Python 也是
> 外部技能市场文件白名单（不收 .sh）的硬前提。

## 客户可读说明

### 这个技能可以做什么

Audit and upgrade AI/developer CLIs (codex, claude, Antigravity/agy,
Gemini's supported non-consumer lanes, kimi, qwen, opencode, cursor,
deepcode, pi, etc.)
with dry-run reports and logs.

进阶维护工具：面向已装多套 AI CLI 的用户，与本仓其他面向小白的单工具安装技能定位不同。

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 完成本技能覆盖的工作 | 读取用户请求、必要上下文和本技能正文流程，执行最小可靠步骤 | 客户会看到执行计划、命令输出摘要、代码/文档变更、验证结果和风险说明。 |
| 缺少依赖、权限、配置或 key | 停止需要外部状态的动作，明确指出缺什么 | 安装命令、申请地址、配置路径或需要客户确认的问题 |
| 执行完成 | 汇总成功、跳过、失败、文件变更和验证结果 | 一段可复制进工单/日志的完成回执 |

### 客户如何使用

1. 用自然语言说明目标，并提供必要输入：文件、URL、repo、workspace、proposal、vault 或平台账号状态。
2. 能 dry-run 或预览的动作先给预览；涉及删除、覆盖、发送、发布、写远端状态时先征求客户确认。

### 依赖与安装

安装（推荐：装整个领域插件，一次装好本仓全部技能）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-env@soia
```

只要这一个技能时，可用 npx 路线。注意技能会落进共享真源 `~/.agents/skills`；若同时装了插件，同一技能会出现两份索引且各自漂移，建议二选一：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-ai-cli-upgrade -y
```

国内网络环境提示：npm 通道安装或升级 CLI 超时、下载失败时，可先切换 npmmirror 国内镜像源再重试，完成后按需切回官方源：

```bash
npm config set registry https://registry.npmmirror.com   # 切国内镜像
npm config set registry https://registry.npmjs.org       # 切回官方源
```

配置约定：

```text
~/.config/soia-skills/soia-env-ai-cli-upgrade/config.yml
SOIA_ENV_AI_CLI_UPGRADE_CONFIG_FILE=<custom-config-path>
```

- 如果本技能不需要私有配置，可以不创建 `config.yml`。
- 配置文件使用 `schema_version: 2`；脚本优先读取新路径，只有新路径不存在时才回退读取旧版配置位置。
- 如果需要 API key、cookie、session、provider home 或本机路径，只能放进私有 `config.yml`、进程环境或 provider 自己的登录态里，不能写进仓库、vault 正文或日志。
- **日志位置与保留**：升级日志定位为**用完即弃**——当次报告看完即无价值，默认落系统临时区 `${TMPDIR:-/tmp}/soia-env-ai-cli-upgrade/logs/`（macOS 的 $TMPDIR 约 3 天自动清、/tmp 重启清），同日多次运行由 `LOG_KEEP`（默认 10）轮转防堆积。若确需留审计追溯（例如排查"哪天升了什么版本导致行为变化"），设 `LOG_DIR` 改道到持久位置（如 `~/.local/state/...`）。
- 第三方 skill 只能声明依赖和安装方式，不直接修改第三方 skill 文件。

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### 日志与完成回执

每次执行都要让客户看见过程和结果。最低回执格式：

客户可见结果中的 `更新时间` 在最终版本验证完成后记录，使用带时区的 RFC 3339 时间。

```markdown
完成：<一句话说明本次完成了什么>。

日志摘要：
- started: <检查到的输入/配置/依赖，不打印秘密值>
- processed: <数量或范围>
- created/updated: <数量或路径>
- skipped/failed: <数量和原因>

文件变化：
- <绝对路径或“未改动文件”>

验证：
- <运行过的检查、命令或人工核对点>

问题与下一步：
- <缺 key / 缺依赖 / 需要客户确认 / 建议下一条命令；没有则写“无”>
```

## Tools Covered

| Tool | Command | Default upgrade method |
|---|---|---|
| Codex | `codex` | `codex update` (auto-detects native/brew-cask/npm internally); installs via `curl https://chatgpt.com/codex/install.sh`, `brew install --cask codex`, or `npm install -g @openai/codex`; **⚑ npm path**: NOTE column shows curl recommendation |
| Claude Code | `claude` | auto-detected: native → `claude update`; Homebrew defaults to preserving the installed cask, while authorized `CLAUDE_CHANNEL=latest` safely migrates `claude-code` → `claude-code@latest` with prefetch and rollback; npm (legacy) → `npm install -g @anthropic-ai/claude-code`; Desktop-managed → skip (MANUAL) |
| Antigravity CLI (consumer Google accounts) | `agy` | Official successor to Gemini CLI consumer Google login; native `agy update`; missing-command install is gated by `AGY_INSTALL=1` |
| Gemini CLI (non-consumer lanes) | `gemini` | auto-detected: brew formula (`brew install gemini-cli`) → `brew upgrade <formula>`; npm → `npm install -g @google/gemini-cli`; native → `gemini update`; explicit opt-in with `TOOLS=gemini` |
| Qwen Code | `qwen` | auto-detected: brew formula (`brew install qwen-code`) → `brew upgrade <formula>`; npm → `npm install -g @qwen-code/qwen-code`; native (curl) → `qwen update`; **⚑ npm path**: NOTE column shows curl recommendation |
| MiniMax CLI | `mmx` | `mmx update` (wraps npm internally); npm-only: `npm install -g mmx-cli` |
| Kimi Code | `kimi` | auto-detected: Homebrew formula, including relative `bin` symlinks, → `brew upgrade <formula>`; npm → `npm install -g @moonshot-ai/kimi-code`; native (curl) → `kimi upgrade`; Homebrew failures are reported instead of being treated as “already latest” |
| OpenCode | `opencode` | auto-detected: brew formula (`brew install opencode`) → `brew upgrade <formula>`; npm → `npm install -g opencode-ai`; native (curl) → MANUAL (re-run `curl -fsSL https://opencode.ai/install \| bash`); **⚑ npm path**: NOTE column shows curl recommendation |
| Qoder CLI | `qodercli` | `qodercli update` |
| DeepCode Agent CLI | `deepcode` | npm → `npm install -g deepcode`（@vegamo/deepcode-cli 已装时更新包名） |
| Pi (pi-coding-agent) | `pi` | `pi update --self`（npm 包 `@earendil-works/pi-coding-agent`） |
| Cursor | `cursor` | version audit only unless `CURSOR_UPGRADE_CMD` is set |

Why both rows remain: `agy` is the replacement for Gemini CLI's consumer
Google-login path. `gemini` stays only so this skill can audit explicitly
supported Standard/Enterprise, API Key, and Vertex AI installations; it is no
longer part of the default batch.

## Safety Model

- Start with `DRY_RUN=1` unless the user explicitly asked to upgrade.
- Preserve Claude's installed Homebrew cask by default. Set
  `CLAUDE_CHANNEL=latest` only after the user separately authorizes changing
  from `claude-code` to `claude-code@latest`; fetch the target before removing
  the stable cask and attempt restoration if installation fails.
- Never edit shell profiles or PATH files automatically.
- Missing `agy` is installed only when `AGY_INSTALL=1`. The helper downloads
  Google's HTTPS installer to a temporary directory, syntax-checks it, and runs
  it with an isolated temporary `HOME`; `--dir` places the native binary in
  `AGY_INSTALL_DIR` without letting vendor setup edit the user's real profiles.
- Never write API keys, tokens, cookies, or login material to logs.
- Treat `CURSOR_UPGRADE_CMD` as user-supplied code. Only run it when the user
  has explicitly provided or approved that command.
- If an updater requires interactive login or privileged access, stop and report
  the blocker instead of guessing.

## Configuration

The script uses environment variables. If persistent local configuration is
needed, keep it in the skill-specific private `config.yml`:

```text
~/.config/soia-skills/soia-env-ai-cli-upgrade/config.yml
```

Example:

```yaml
schema_version: 2
env:
  LOG_DIR: "$HOME/.local/state/soia-env-ai-cli-upgrade/logs"
  TOOLS: "codex,claude,agy"
  NPM_PREFIX: "$HOME/.npm-global"
  CLAUDE_CHANNEL: "preserve"
  AGY_INSTALL: "0"
  AGY_INSTALL_DIR: "$HOME/.local/bin"
```

Supported variables:

| Variable | Purpose | Default |
|---|---|---|
| `DRY_RUN=1` | Print current versions without upgrading | `0` |
| `TOOLS="codex,claude,agy"` | Limit the tool list | consumer-safe default set; `gemini` is opt-in |
| `NPM_PACKAGES="codex,claude"` | Backward-compatible alias for `TOOLS`; ignored when `TOOLS` is set | unset |
| `NPM_PREFIX=<path>` | npm global prefix for npm-based CLIs | `$HOME/.npm-global` |
| `CLAUDE_CHANNEL=preserve|latest` | Preserve the installed Claude Homebrew cask, or explicitly migrate the stable cask to `claude-code@latest` | `preserve` |
| `AGY_INSTALL=1` | Allow a missing `agy` to be installed from Google's fixed official HTTPS endpoint | `0` |
| `AGY_INSTALL_DIR=<path>` | Native `agy` installation and fallback detection directory | `$HOME/.local/bin` |
| `LOG_DIR=<path>` | Upgrade log directory | `${TMPDIR:-/tmp}/soia-env-ai-cli-upgrade/logs` |
| `CURSOR_UPGRADE_CMD=<command>` | Optional Cursor updater command | unset |

## Standard Workflow

From this repository:

```bash
# Version audit only
DRY_RUN=1 python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# Upgrade all supported tools
python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# Upgrade a consumer-safe subset
TOOLS="codex,claude,agy" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# After separate channel-switch authorization, migrate Homebrew Claude to @latest
CLAUDE_CHANNEL=latest TOOLS="claude" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# Upgrade Gemini CLI only after confirming a supported non-consumer lane
TOOLS="gemini" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# Explicitly install agy if it is missing; this does not perform login
AGY_INSTALL=1 TOOLS="agy" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py
```

From an installed skill:

```bash
DRY_RUN=1 python3 ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py
```

The script writes one timestamped log file and prints a table:

| Column | Meaning |
|---|---|
| `TOOL` | logical tool name |
| `COMMAND` | executable checked |
| `OLD` | version before upgrade or current version in dry-run |
| `NEW` | version after upgrade, or `N/A` in dry-run |
| `STATUS` | `INSTALLED`, `UPDATED`, `ALREADY_LATEST`, `NOT_INSTALLED`, `SKIP_DRY_RUN`, `MANUAL`, `FAILED` |
| `NOTE` | short reason or next action |

`MANUAL` for `agy` can mean installation or update succeeded but the resolved
binary directory is absent from PATH, or PATH resolves to a different binary.
The script reports the absolute resolved path and never edits PATH itself.

## 样例：一次真实的 dry-run 审计

2026-08-08 在 macOS（arm64）真机运行 `DRY_RUN=1 python3 scripts/upgrade_ai_clis.py`
的实际输出（用户主目录已脱敏为 `~`，数据逐字保留）：

| TOOL | OLD | NEW | STATUS | NOTE |
|---|---|---|---|---|
| codex | 0.147.0 | N/A | SKIP_DRY_RUN | path=/opt/homebrew/bin/codex; no upgrade |
| claude | 2.1.224 | N/A | SKIP_DRY_RUN | path=/opt/homebrew/bin/claude; no upgrade; channel=claude-code@latest |
| agy | 1.1.11 | N/A | SKIP_DRY_RUN | path=~/.local/bin/agy; no upgrade |
| kimi | 0.34.0 | N/A | SKIP_DRY_RUN | path=/opt/homebrew/bin/kimi; no upgrade |
| mmx | 1.0.16 | N/A | SKIP_DRY_RUN | path=~/.npm-global/bin/mmx; no upgrade |
| qwen | 0.21.6 | N/A | SKIP_DRY_RUN | path=/opt/homebrew/bin/qwen; no upgrade |
| opencode | 1.18.15 | N/A | SKIP_DRY_RUN | path=~/.opencode/bin/opencode; no upgrade |
| qodercli | 1.1.17 | N/A | SKIP_DRY_RUN | path=~/.local/bin/qodercli; no upgrade |
| cursor | UNKNOWN | N/A | SKIP_DRY_RUN | path=~/.local/bin/cursor; no upgrade |
| deepcode | 0.1.34 | N/A | SKIP_DRY_RUN | path=~/.npm-global/bin/deepcode; no upgrade |
| pi | 0.84.1 | N/A | SKIP_DRY_RUN | path=~/.npm-global/bin/pi; no upgrade |

读法：这台机器装了 11 款 AI CLI；dry-run 只审计不动手，`OLD` 列即当前版本。
`cursor` 是桌面应用，CLI 无版本命令故显示 `UNKNOWN`（属预期，见能力边界）。
`opencode` 由 v2.2.0 新增的 `~/.opencode/bin` 原生目录回退探测到——不在当前
shell 的 PATH 上也不会误报未安装。安装通道与官方推荐不一致时（如 npm 装的
codex），`NOTE` 列会附上可直接复制的迁移命令；本机各工具已迁到推荐通道故无此提示。

## 不负责什么（能力边界）

- **不首次安装缺失的 CLI**：没装的工具只报 `NOT_INSTALLED`，不代装（唯一例外是
  `agy`，且必须显式 `AGY_INSTALL=1` 授权）；安装请走各工具官方渠道或对应安装技能
- **不改 shell profile、PATH、登录态**：升级后需要重新登录时如实报告并停下，
  不代客户完成任何认证流程
- **不升级桌面应用**：Cursor 只做版本审计，除非客户自己提供 `CURSOR_UPGRADE_CMD`
- **不判断新版本是否更好**：只做版本对齐与结果核验；是否回滚、锁版本归客户决策
- **不碰秘密**：API key、token、cookie 一律不读取、不记录、不回显
- **平台范围**：macOS 与 Linux（含 WSL）完整支持；**原生 Windows 自 2.3.0 起
  实验性支持**——引擎平台化（os.pathsep、Windows npm 全局布局 `%AppData%\npm`、
  平台 shell），契约测试在 GitHub Actions windows-latest 真机回归。已知限制：
  `agy` 官方安装器是 bash 脚本，原生 Windows 下如实报 MANUAL（请走 WSL）；
  brew 通道在 Windows 天然缺席时自动跳过

## 私密信息与中间数据

- 配置只保存非秘密偏好和用户选择的路径；API key、token、cookie、session 与登录凭据继续由各 CLI 的官方登录流程或系统凭据库管理。
- 默认日志位于系统临时目录并按 `LOG_KEEP` 轮转；若用户明确选择持久 `LOG_DIR`，只记录脱敏后的版本、状态与错误摘要，不记录账号、凭据、认证 URL 或私有路径。
- dry-run 只读检查不创建持久 state；真实升级的客户回执必须标明工具、旧/新版本、结果与带时区的 `更新时间`。

## Output Checklist

Before final response:

- Say whether the run was dry-run or live.
- Include the log file path.
- Summarize each tool status.
- Call out any `FAILED`, `MANUAL`, or interactive-login blockers.
- For Homebrew Claude, report the actual cask channel. Treat
  `ALREADY_LATEST` as “latest in the preserved channel,” not proof that another
  authorized channel has no newer build.
- Treat a non-zero script exit as at least one true `FAILED` row; the script
  still processes the remaining selected tools before returning failure.
- State that authentication was not checked unless an explicit PTY login flow
  was completed by the user. Use `blocked_user_action` while waiting.
- When model discovery was requested, report `model_source=runtime_account_scoped`
  and the display names returned by `agy models`; do not invent stable model ids,
  aliases, a default, or plan eligibility from that output.
- If live upgrades were run, report old and new versions where available.

## 分流程手册

以下流程互斥，一次任务只会走其中一条；按需读取对应文件即可。

- **Gemini consumer migration and Antigravity authentication** — [antigravity-migration.md](references/antigravity-migration.md)
- **Antigravity diagnosis** — [antigravity-diagnosis.md](references/antigravity-diagnosis.md)
