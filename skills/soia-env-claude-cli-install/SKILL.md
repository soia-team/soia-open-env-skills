---
name: soia-env-claude-cli-install
description: 为小白安装、登录与授权更新 Anthropic Claude Code CLI。触发：「安装 Claude CLI」「Claude 命令不存在」「Claude 登录」。
dependencies:
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.0.3
created_at: 2026-07-21 11:20:00
updated_at: 2026-08-05 13:30:00
created_by: gpt-5
updated_by: claude-opus-5
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
4. 需要登录时 Agent 启动流程，客户只在 Anthropic 官方页面点击授权；不得让客户把授权码、API key 或密码发到聊天中。
5. 安装、更新和登录后分别验证独立 CLI 的版本、帮助命令、诊断结果和登录状态。

### 首次登录与真实配置验证

- `配置文件目录`只显示候选目录；技能必须同时读取 `config_status` 和 `config_file_status`，不能把默认路径当成“已配置”。
- 如果 `~/.claude` 或 `settings.json` 尚未创建，Agent 在客户选定的项目中启动 `claude`，由 Claude Code 展示官方登录选项；客户只在 Anthropic 官方页面或 Claude 官方应用完成授权。
- 如果客户选择 Anthropic API 方式，客户自行在 Anthropic Console 创建并保管 API key；Agent 只检查“存在/可认证”的结果，不接收、不回显密钥。
- 登录完成后重新运行 `claude doctor` 和技能检查脚本；没有完成浏览器授权时，处理结果必须写“等待首次登录”，不能写“运行正常”。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| macOS、Linux 或 Windows | 强依赖 | 只使用官方文档支持的系统和架构 |
| Node.js/npm | npm 渠道依赖 | 官方独立安装不需要；选择 npm 时才调用 `soia-env-node-install` |
| 网络诊断 | 可选前置 | 官方站点失败时调用 `soia-env-network-diagnose`，不自动修改网络 |
| Anthropic 账号 | 登录依赖 | 客户在官方浏览器完成授权，Agent 不读取凭据 |

官方来源、包名、配置和自动更新事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读取得独立命令、当前版本、实际路径、安装方式、配置目录以及配置目录/文件是否真实存在。
2. 执行 `python3 scripts/check_latest.py --json`，从 npm 官方发布元数据取得最新版；失败时写“未取得”，不猜测。
3. 已安装且可运行：`当前状态` 始终写“已安装”。没有最新版授权就停止，不重复安装、不更新。
4. 未安装：优先官方独立安装；客户选择 npm 时才使用 `npm install -g @anthropic-ai/claude-code`。安装网络脚本时先下载到系统临时目录、检查来源和内容，再执行本地副本；不直接执行网络响应。
5. 更新到最新：官方独立来源使用 `claude update`；npm 来源使用 `npm install -g @anthropic-ai/claude-code@latest`；Homebrew 来源先识别实际 cask，再沿该 cask 更新。不得顺便切换来源。
6. 验证同一绝对路径的 `--version`、`--help` 和 `doctor`。登录状态不明时启动官方登录流程；登录由客户在浏览器完成。
7. 重新执行两个检查脚本，以 `scripts/render_status.py` 生成一行客户状态列表。

## 产品自动更新边界

- 本技能“默认不更新”是指 Agent 不调用安装器或更新器。Claude Code 产品自身可能启用自动更新，必须在状态说明中披露。
- 只读检查不得修改 `autoUpdates`、`DISABLE_AUTOUPDATER` 或任何配置。
- 客户明确要求关闭或开启产品自动更新时，先展示影响，再按官方设置修改并复核；该配置授权不等于本次更新授权。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Claude Code CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Claude Code CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/Homebrew 安装/npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/被阻塞：原因> |

- 用户只问 Claude Code CLI 时，不增加 Node.js、npm、Codex、Claude 桌面产品或其他技能行。
- `更新时间` 必须在最终验证后生成；安装目录和配置目录优先显示 `~` 相对路径，避免暴露用户名。
- 已更新后 `当前状态` 仍写“已安装”，更新结果只放在 `处理结果`。
- 发现多个 `claude` 时汇报当前登录 shell 实际生效的副本，并提示冲突；不删除其他副本。
- 无法取得最新版时写“未取得”；不得用缓存、记忆或其他产品版本代替。
- `config_status=未创建` 或 `config_file_status=未创建` 时，处理结果写“等待首次登录/配置”，并给出启动命令和官方授权方式；不得只打印一个不存在的路径。

## 安装与更新的中间状态

真正改变机器时，为本次运行生成随机 `run_id`，在每个实际阶段立即调用 `scripts/record_install_progress.py`，并同步展示阶段列表。只读检查不创建记录。

```text
checking → planning → [waiting_confirmation] → installing/updating → verifying → completed/failed/blocked
```

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

- 安装使用 `--action install`；更新使用 `--action update`。
- 只有客户明确要求最新版时，更新阶段才能传 `--customer-requested-latest`；记录器会拒绝未授权更新。
- 记录只保存固定 `result_code`、阶段和时间，不保存命令全文、账号、token、响应正文或客户私有绝对路径。

## 权限与回滚

- 优先用户级安装，不默认使用 `sudo`。需要管理员权限、修改 shell profile、切换来源或覆盖现有命令时先展示计划并取得单独确认。
- 更新前记录旧版本和来源；失败时保留原安装，不自动卸载、降级、清理配置或关闭自动更新。
- 网络脚本和安装包只存于每次运行独立的系统临时目录，成功、失败或取消都清理。

## 私密信息与中间数据

- 登录凭据由 Claude 官方登录态或系统凭据库管理；不读取或复制 `~/.claude` 中的凭据内容。
- 非秘密配置留在官方配置目录；SOIA 不另建密钥文件。
- 机器变更的脱敏阶段记录保存在用户 state 目录，默认按仓库存储规范轮转；只读流程默认不落盘。
- 不在仓库、普通配置、日志或回执中保存 API key、授权码、cookie、session、账号或私有路径。

## 日志与完成回执

最终回执包含固定十列表格、验证过的命令类别、是否需要浏览器授权，以及失败时可恢复的原版本。正常依赖不展开为额外行。

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
