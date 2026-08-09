---
name: soia-env-claude-cli-install
description: 为小白安装、登录与授权更新 Anthropic Claude Code CLI。触发：「安装 Claude CLI」「Claude 命令不存在」「Claude 登录」。
dependencies:
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.0.5
created_at: 2026-07-21 11:20:00
updated_at: 2026-08-09 01:20:00
created_by: gpt-5
updated_by: claude-fable-5
---

# soia-env-claude-cli-install

安装和验证独立的 Anthropic Claude Code CLI（命令 `claude`）。Agent 负责终端操作；客户只需说明目标，并在官方浏览器或系统授权界面完成登录。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Claude Code | 检查系统和已有来源，使用官方用户级渠道安装 | 当前版本、来源、安装目录和验证结果 |
| 检查或更新 | 比较当前版与官方最新版；明确授权后沿原来源更新 | “无需更新”“可更新，未执行”或“已更新” |
| 登录 Claude | 启动 `claude` 官方登录流程 | 浏览器授权步骤，不显示凭据 |
| 命令不可用 | 检查 PATH、重复安装和 `claude doctor` | 阻塞原因与安全修复方案 |

### 客户如何使用

1. 客户直接说“帮我安装 Claude Code CLI”；不要求客户复制终端命令。
2. Agent 先执行只读检查并展示计划。客户的安装请求只授权安装缺失的 CLI，不授权更新已有版本。
3. 只说“更新 Claude”时先显示两个版本并询问是否更新到最新；只有“更新到最新版本”等明确表述才调用更新器。
4. 需要登录时 Agent 启动流程，客户只在官方页面授权；授权码、API key、密码一律不进聊天。
5. 安装、更新和登录后分别验证独立 CLI 的版本、帮助命令、诊断结果和登录状态。

### 首次登录与真实配置验证

配置状态以 `config_status`/`config_file_status` 实测为准，未创建时引导客户在官方
页面完成首次登录，结果只能写「等待首次登录」；完整细则（API key 方式、复验要求）
见 [operations.md](references/operations.md)。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| macOS、Linux 或 Windows | 强依赖 | 只使用官方文档支持的系统和架构 |
| Node.js/npm | npm 渠道依赖 | 官方独立安装不需要；选择 npm 时才调用 `soia-env-node-install` |
| 网络诊断 | 可选前置 | 官方站点失败时调用 `soia-env-network-diagnose`，不自动修改网络 |
| Anthropic 账号 | 登录依赖 | 客户在官方浏览器完成授权，Agent 不读取凭据 |

官方来源、包名、配置和自动更新事实见 [official-sources.md](references/official-sources.md)。

国内网络环境提示：npm 渠道安装超时、下载失败时，可先切换 npmmirror 国内镜像源再重试，完成后按需切回官方源；最新版查询走 npm 官方 registry，受限网络下如实写「未取得」，不猜测：

```bash
npm config set registry https://registry.npmmirror.com   # 切国内镜像
npm config set registry https://registry.npmjs.org       # 切回官方源
```

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读取得独立命令、当前版本、实际路径、安装方式、配置目录以及配置目录/文件是否真实存在。
2. 执行 `python3 scripts/check_latest.py --json`，从 npm 官方发布元数据取得最新版；失败时写“未取得”，不猜测。
3. 已安装且可运行：`当前状态` 始终写“已安装”。没有最新版授权就停止，不重复安装、不更新。
4. 未安装：优先官方独立安装；客户选 npm 时才用 `npm install -g @anthropic-ai/claude-code`。网络脚本先下载到临时目录、审阅内容后执行本地副本，不直接执行网络响应。
5. 更新到最新：官方独立来源用 `claude update`；npm 用 `npm install -g @anthropic-ai/claude-code@latest`；Homebrew 先识别实际 cask 再沿其更新；不得顺便切换来源。
6. 验证同一绝对路径的 `--version`、`--help` 和 `doctor`。登录状态不明时启动官方登录流程；登录由客户在浏览器完成。
7. 重新执行两个检查脚本，以 `scripts/render_status.py` 生成一行客户状态列表。

## 产品自动更新边界

「默认不更新」指 Agent 不调用安装器/更新器；产品自身的自动更新必须在状态说明中
披露，只读检查不改任何配置。改自动更新设置的授权边界见
[operations.md](references/operations.md)。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Claude Code CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Claude Code CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/Homebrew 安装/npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/被阻塞：原因> |

- 用户只问 Claude Code CLI 时，不增加 Node.js、npm、Codex 或其他技能行。
- 无法取得最新版时写“未取得”；`更新时间` 在最终验证后生成；目录用 `~` 相对路径脱敏。
- 已更新后 `当前状态` 仍写“已安装”；多副本只汇报冲突不删除；配置未创建时处理结果写“等待首次登录/配置”。
- 完整逐条细则见 [operations.md](references/operations.md)。

## 安装与更新的中间状态

真正改变机器时生成随机 `run_id`，逐阶段调用 `scripts/record_install_progress.py`
（`checking → planning → [waiting_confirmation] → installing/updating → verifying →
completed/failed/blocked`）并同步展示阶段列表；记录器拒绝未授权更新，只存脱敏
阶段与时间，只读检查不创建记录。参数细则见 [operations.md](references/operations.md)。

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

## 权限与回滚

- 优先用户级安装，不默认 `sudo`；改 profile、切来源、覆盖命令须单独确认。
- 更新前记录旧版本与来源，失败保留原安装不自动回滚破坏；临时产物用后即清。
- 细则见 [operations.md](references/operations.md)。

## 私密信息与中间数据

- 登录凭据由 Claude 官方登录态或系统凭据库管理；不读取或复制 `~/.claude` 中的凭据内容。
- 非秘密配置留在官方配置目录；SOIA 不另建密钥文件。
- 机器变更的脱敏阶段记录存用户 state 目录按规范轮转；只读流程不落盘；仓库、配置、日志、回执一律不存 API key、授权码、cookie、session、账号或私有路径。

## 日志与完成回执

最终回执包含固定十列表格、验证过的命令类别、是否需要浏览器授权，以及失败时可恢复的原版本。正常依赖不展开为额外行。

## 样例：一次真实检查

2026-08-08 在 macOS（arm64）真机执行标准流程第 1、2 步的实际结果（路径经 `~` 脱敏，数据逐字保留）：

`inspect_cli.py --json` 关键字段：

| 字段 | 实际值 |
|---|---|
| current_status | 已安装 |
| current_version | 2.1.226 |
| install_method | Homebrew 安装 |
| install_dir | /opt/homebrew/Caskroom/claude-code@latest/2.1.226 |
| config_status / config_file_status | 已创建 / 已存在 |
| runtime_status | 正常 |

`check_latest.py --json`：latest_version 2.1.226（source: npm）。

最终十列客户状态表（`render_status.py` 实际渲染）：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Claude Code CLI | 已安装 | 2.1.226 | 2.1.226 | 正常 | Homebrew 安装 | /opt/homebrew/Caskroom/claude-code@latest/2.1.226 | ~/.claude | 2026-08-08T16:25:10+08:00 | 已是最新 |

细节一则：同机当天 14:40 还是 2.1.224，16:25 已是 2.1.226——产品自动更新在工作，正是「产品自动更新边界」要求披露的情形。

## 不负责什么（能力边界）

- **不代客户完成登录与授权**：浏览器授权、验证码、API key 创建都由客户在 Anthropic 官方页面完成；不读取、不接收、不回显任何凭据
- **默认不更新已装版本**：「帮我安装」只授权装缺失的；更新需要「更新到最新版本」级别的明确表述
- **不动系统**：不默认 `sudo`，不改 shell profile 与 PATH，不卸载或清理机器上的其他 `claude` 副本（发现多副本只汇报冲突）
- **不负责 Claude 桌面应用与账号计费**：只管 CLI 的安装、检查、更新与登录引导

## 前向测试

用临时 fake `claude` 覆盖未安装、已安装、版本异常和 PATH 多副本；mock npm 最新版响应；验证十列渲染、`~` 路径脱敏、默认不更新，以及没有明确最新版授权时记录器拒绝 `updating`。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-claude-cli-install -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。
