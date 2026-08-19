---
name: soia-env-ai-cli-upgrade
description: 审计并按授权升级多款 AI CLI，先预演并核验结果。触发：「升级 AI CLI」「更新 Claude/Kimi」「检查 CLI 版本」。
version: 2.3.4
created_at: 2026-07-09 07:45:34
updated_at: 2026-08-19 14:10:00
created_by: claude opus 4.6
updated_by: claude-fable-5
---

# soia-env-ai-cli-upgrade

Use this skill when the user asks to audit, dry-run, or upgrade local AI and
developer CLIs in a repeatable way. Do not use it when the user only asks how
to install one known CLI and no version audit or batch workflow is needed.

> **引擎**：纯 Python 标准库单文件 `scripts/upgrade_ai_clis.py`（v2.2.0 由同名
> bash 引擎逐行移植，对外契约由仓级契约测试双引擎锁定；纯 Python 也是外部技能
> 市场文件白名单的硬前提）。

## 客户可读说明

### 这个技能可以做什么

进阶维护工具：面向已装多套 AI CLI 的用户，与本仓面向小白的单工具安装技能定位不同。

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 盘点本机 AI CLI 版本 | `DRY_RUN=1` 只读审计，不动任何东西 | 七列状态表 + 日志路径 |
| 升级全部或指定工具 | 明确授权后按检测到的安装通道升级 | 每款工具旧/新版本与结果 |
| 安装通道不合官方推荐 | 不代迁移，`NOTE` 列给出建议 | 「下载 → 审阅 → 本地执行」三段式迁移指引 |

覆盖 codex、claude、agy、gemini（非消费者通道，显式 opt-in）、qwen、kimi、mmx、
opencode、qodercli、deepcode、pi、cursor（仅审计）。各工具安装通道与默认升级方式
见 [tools-covered.md](references/tools-covered.md)。

### 客户如何使用

1. 说人话即可：「升级 AI CLI」「检查 CLI 版本」「我的 codex 该更新吗」。默认先
   dry-run 只读盘点，客户圈定后才真升级。
2. 涉及换安装通道、安装缺失工具等动作，先展示计划并单独征求确认。

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

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

私有配置（可选，不建也行）与全部环境变量见
[configuration.md](references/configuration.md)。

### 私密信息与中间数据

- 配置只保存非秘密偏好与路径；key、token、cookie、登录凭据由各 CLI 官方登录流程
  或系统凭据库管理，一律不读取、不记录、不回显。
- 默认日志落系统临时目录并按 `LOG_KEEP` 轮转；持久 `LOG_DIR` 下也只记脱敏后的
  版本、状态与错误摘要。
- dry-run 只读检查不创建持久 state。

### 日志与完成回执

```markdown
完成：<一句话说明本次完成了什么>。

日志摘要：
- started / processed / created/updated / skipped/failed

文件变化：
- <绝对路径或“未改动文件”>

验证：
- <运行过的检查、命令或人工核对点>

问题与下一步：
- <缺依赖 / 需客户确认 / 建议下一条命令；没有则写“无”>
```

真实升级的回执须标明工具、旧/新版本、结果与带时区的 `更新时间`。

## 快速用法

```bash
# 只读审计（默认姿势）
DRY_RUN=1 python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 授权后升级全部受支持工具
python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 指定子集
TOOLS="codex,claude,agy" python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py
```

输出七列状态表（TOOL / COMMAND / OLD / NEW / STATUS / NOTE），`STATUS` 语义见
[configuration.md](references/configuration.md)，更多命令变体与回执核对清单见
[workflows.md](references/workflows.md)。

## 安全模型

- 未获明确升级授权时一律 `DRY_RUN=1` 起步。
- **不输出、不执行 pipe-to-shell 形式的命令**：安装建议一律「下载脚本 → 人工审阅
  → 本地执行」三段式表述；包内不含任何真实凭据。
- 不自动改 shell profile、PATH 或登录态；升级后需重新登录时如实报告并停下。
- Homebrew Claude 默认保留已装 cask；`CLAUDE_CHANNEL=latest` 迁移须客户单独授权，
  先预取目标再移除稳定版，失败尝试恢复。
- 缺失的 `agy` 仅在 `AGY_INSTALL=1` 时安装：固定官方 HTTPS 域名、下载到独立临时
  目录、语法校验、隔离 HOME 执行，不直接执行网络响应。
- `CURSOR_UPGRADE_CMD` 视为用户自供代码，仅在客户明确提供或批准后运行。
- 更新器要求交互登录或特权时，停下报告阻塞，不猜测。

## 样例：一次真实的 dry-run 审计

2026-08-08 在 macOS（arm64）真机运行 `DRY_RUN=1 python3 scripts/upgrade_ai_clis.py`
的实际输出（用户主目录脱敏为 `~`，数据逐字保留）：

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
`cursor` 是桌面应用，CLI 无版本命令故显示 `UNKNOWN`（属预期）。`opencode` 由
`~/.opencode/bin` 原生目录回退探测到——不在当前 shell 的 PATH 上也不误报未安装。
安装通道与官方推荐不一致时，`NOTE` 列会附迁移建议。

## 不负责什么（能力边界）

- **不首次安装缺失的 CLI**：没装的只报 `NOT_INSTALLED`，不代装（唯一例外 `agy`，
  且必须显式 `AGY_INSTALL=1` 授权）。
- **不改 shell profile、PATH、登录态**，不代客户完成任何认证流程。
- **不升级桌面应用**：Cursor 只做版本审计。
- **不判断新版本是否更好**：是否回滚、锁版本归客户决策。
- **不碰秘密**：API key、token、cookie 一律不读取、不记录、不回显。
- **平台范围**：macOS 与 Linux（含 WSL）完整支持；原生 Windows 自 2.3.0 起
  实验性支持（契约测试在 windows-latest 真机回归）；`agy` 官方安装器是 bash
  脚本，原生 Windows 下如实报 MANUAL（请走 WSL）。

## 分流程手册

以下文件按需读取，不随正文常驻：

- **工具通道明细** — [tools-covered.md](references/tools-covered.md)
- **环境变量与配置、输出列语义** — [configuration.md](references/configuration.md)
- **命令变体与回执核对清单** — [workflows.md](references/workflows.md)
- **Gemini consumer migration and Antigravity authentication** — [antigravity-migration.md](references/antigravity-migration.md)
- **Antigravity diagnosis** — [antigravity-diagnosis.md](references/antigravity-diagnosis.md)
