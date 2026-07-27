---
name: soia-env-antigravity-cli-install
description: 为新手安装、登录、迁移或按授权更新 Google Antigravity CLI（agy）。触发：「安装 agy」「Gemini CLI 迁移」「agy 登录」
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.0.2
created_at: 2026-07-21 00:00:00
updated_at: 2026-07-27 10:47:17
created_by: gpt-5
updated_by: gpt-5.6-sol
---

# soia-env-antigravity-cli-install

安装和验证 Google Antigravity CLI（命令 `agy`）。`gemini` 是迁移来源，不是本技能用来判定已安装的命令；Agent 操作终端，客户只在 Google 官方界面完成登录。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 agy | 检查系统架构和已有命令，使用 Google 官方安装入口 | 版本、安装目录和可运行验证 |
| 从 Gemini CLI 迁移 | 分别检查 `gemini` 与 `agy`，按官方迁移说明生成计划 | 哪个是旧命令、哪些配置可迁移、哪些需确认 |
| 检查或更新 | 读取 Google 官方平台清单；明确授权后调用 `agy update` | 当前版、最新版和处理结果 |
| 登录或排错 | 启动官方登录并检查 PATH、凭据库和配置目录 | 浏览器步骤或阻塞原因 |

### 客户如何使用

其他可识别说法包括「安装 Antigravity CLI」「更新 agy 到最新」。

1. 客户说“安装 agy”或“把 Gemini CLI 迁移到 Antigravity”；不要求客户操作终端。
2. Agent 先只读检测 OS、架构、`agy`、`gemini` 和已有配置，再展示计划。只检查不会迁移或更新。
3. 安装请求只授权安装缺失的 `agy`；迁移、覆盖配置、修改 PATH 和管理员权限分别确认。
4. 模糊的“更新 agy”只显示版本；只有“更新到最新”才执行 `agy update`。
5. 登录时客户只在 Google 官方页面确认账号和权限，不把验证码、token 或 cookie 发给 Agent。

### 首次登录与真实配置验证

- `~/.gemini/antigravity-cli` 是候选状态/配置目录；技能必须先检查它是否真实存在，不能因为输出了默认路径就判定 agy 已登录。
- 如果目录尚未创建，Agent 启动官方 `agy` 流程；客户在 Google 官方浏览器页面完成登录、账号选择和权限同意。
- 登录后重新检查 agy 的配置/状态目录、`--version`、`--help` 和无副作用启动；只存在 `gemini` 或只有版本命令可运行时，处理结果仍写“等待首次登录/配置”。
- 迁移请求必须把 `gemini` 和 `agy` 的配置分开核对；不得把 Gemini 的目录存在当成 agy 已配置。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| Google 官方支持的 OS/架构 | 强依赖 | 不受支持时停止，不改用非官方二进制 |
| 网络诊断 | 可选前置 | Google 安装与登录域名不可达时调用 `soia-env-network-diagnose` |
| Google 账号 | 登录依赖 | 客户在官方浏览器完成；凭据由系统凭据库管理 |
| Gemini CLI | 迁移来源、非依赖 | 仅迁移请求时检查，不把它算作 `agy` 已安装 |

官方来源和平台路径见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读检测 `agy`、版本、命令路径、安装目录与配置目录的实际存在状态。
2. 执行 `python3 scripts/check_latest.py --json`，从 Google 官方平台清单读取当前 OS/架构的最新版；不支持的平台返回被阻塞。
3. 已安装且正常：写“已安装”，默认不执行更新。只发现 `gemini` 时，`agy` 仍写“未安装”。
4. 未安装：把 `https://antigravity.google/cli/install.sh`（Windows 使用官方对应入口）下载到每次运行独立的系统临时目录，核对 HTTPS 主机、平台选择、写入目录和脚本内容，再执行本地副本；不直接执行网络响应。
5. 明确更新到最新时调用当前 `agy` 绝对路径的 `update`。不手工拼接未知下载地址，不迁移或删除旧 Gemini CLI。
6. 验证同一 `agy` 的 `--version`、`--help` 和无副作用启动；需要登录时启动官方流程并把浏览器交给客户。
7. 重新检查版本、PATH 和配置，使用 `scripts/render_status.py` 输出一行状态。

## Gemini CLI 迁移边界

- 迁移前分别备份和列出非秘密设置；不得读取或复制凭据值。
- `~/.gemini/antigravity-cli` 是 Antigravity CLI 状态/配置位置，`~/.gemini/config/mcp_config.json` 是全局 MCP 配置；覆盖任何现有文件前必须展示差异并确认。
- 迁移成功也不自动卸载 `gemini`；客户明确要求卸载后另行展示删除范围与风险。

## 产品自动更新边界

- Antigravity CLI 具有后台自更新能力；技能默认不主动更新，但要报告该产品行为。
- 只读检查不修改 `AGY_CLI_DISABLE_AUTO_UPDATE`。客户要求改变自动更新策略时单独确认并复核。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Antigravity CLI (agy)`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Antigravity CLI (agy) | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/等待迁移确认/被阻塞：原因> |

- 用户只问 agy 时，不增加 Gemini CLI、Node.js、npm 或其他技能行；旧 Gemini 只在迁移说明中出现。
- `更新时间` 在最终验证后生成；目录用 `~` 或平台泛化路径，避免用户名。
- 更新后 `当前状态` 仍写“已安装”，`处理结果` 才写“已更新”。
- 最新版清单不可达时写“未取得”，不从旧缓存猜测。
- `config_status=未创建` 时，处理结果写“等待首次登录/配置”，并明确由 Agent 启动 `agy`、客户在 Google 官方页面完成授权；不得只显示一个不存在的目录。

## 安装与更新的中间状态

真正安装、更新或修复时生成随机 `run_id`，在每个实际阶段立即调用 `scripts/record_install_progress.py` 并同步展示：

```text
checking → planning → [waiting_confirmation] → installing/updating → verifying → completed/failed/blocked
```

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

只读检查无记录。更新执行阶段必须有客户明确最新版授权；阶段事件只有固定代码和时间，不保存下载响应、账号、路径或凭据。

## 权限与回滚

- 默认安装到用户目录，不使用 `sudo`。PATH/profile 修改、覆盖配置、迁移和系统范围安装先单独确认。
- 更新前记录旧版本和二进制位置；失败时保留旧 `agy` 和旧 `gemini`，不自动卸载或降级。
- 临时安装内容成功、失败或取消后都清理。

## 私密信息与中间数据

- Google 登录凭据留在官方登录态和系统凭据库；不读取、复制或显示其内容。
- 非秘密配置留在官方目录；机器变更阶段记录只写用户私有 state，版本检查默认不落盘。
- 不记录 token、cookie、授权码、账号、响应正文、完整命令或客户私有绝对路径。

## 日志与完成回执

最终回执包含固定十列表格、是否发现旧 Gemini CLI、迁移是否执行、验证项目和客户需要完成的浏览器动作。正常前置项不增加列表行。

## 前向测试

用临时 fake `agy` 覆盖缺失、正常和异常；mock Google 不同平台清单；验证 `gemini` 不会误报 `agy` 已安装、固定十列、路径脱敏和更新授权门禁。
