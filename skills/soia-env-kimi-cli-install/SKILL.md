---
name: soia-env-kimi-cli-install
description: 面向小白检查、安装、登录和按明确授权更新 Moonshot AI Kimi Code CLI；识别官方独立安装与 npm 来源，默认只报告版本和产品自动更新状态。触发：「安装 Kimi CLI」「安装 Kimi Code」「kimi 不存在」「Kimi 登录」「更新 Kimi 到最新」。
dependencies:
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.0.0
created_at: 2026-07-21 00:00:00
updated_at: 2026-07-21 00:00:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-kimi-cli-install

安装和验证 Kimi Code CLI（命令 `kimi`）。Agent 负责终端步骤；客户只在 Kimi 官方页面完成账号登录和授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Kimi Code | 检查已有来源并使用官方稳定渠道安装 | 版本、安装方式、安装和配置目录 |
| 检查或更新 | 从官方 npm 发布元数据比较版本；明确授权后沿原来源更新 | 是否可更新及处理结果 |
| 登录 Kimi | 启动 `kimi login` 或交互界面的 `/login` | 官方浏览器授权步骤 |
| 命令不可用 | 检查 PATH、重复安装和配置目录 | 阻塞原因与安全修复方案 |

### 客户如何使用

1. 客户说“安装 Kimi Code CLI”；不要求客户复制终端命令。
2. Agent 先只读检查并展示计划；安装缺失 CLI 不授权更新已有 CLI。
3. 只说“更新 Kimi”时先显示当前版和最新版；明确“更新到最新版本”才执行更新。
4. 登录由 Agent 启动，客户只在 Moonshot/Kimi 官方页面点击授权；不发送 token、密码或授权码。
5. 完成后验证版本、帮助命令和登录状态，再输出固定十列列表。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| 官方支持的操作系统 | 强依赖 | 不支持时停止并说明 |
| Node.js/npm | npm 渠道依赖 | 官方独立安装不需要；npm 渠道需要官方文档要求的 Node.js，缺失时调用 `soia-env-node-install` |
| 网络诊断 | 可选前置 | 官方安装或登录站点不可达时调用 `soia-env-network-diagnose` |
| Kimi 账号 | 登录依赖 | 客户在官方浏览器授权，Agent 不读取凭据 |

官方来源和运行要求见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读检测 `kimi`、版本、来源、安装目录及 `KIMI_CODE_HOME`/默认配置目录。
2. 执行 `python3 scripts/check_latest.py --json`，从 npm 官方元数据读取 `@moonshot-ai/kimi-code` 最新版。
3. 已安装且正常时写“已安装”；没有明确最新版授权就停止，不调用产品更新命令。
4. 未安装时优先官方独立安装；客户选择 npm 时使用 `npm install -g @moonshot-ai/kimi-code`，并先验证 Node.js 满足官方要求。网络脚本必须先下载到独立临时目录并检查，再执行本地副本；不直接执行网络响应。
5. 明确更新到最新后：独立来源使用 `kimi upgrade` 或当前版本支持的 `kimi update`；npm 来源使用 `npm install -g @moonshot-ai/kimi-code@latest`。不得静默换源。
6. 验证同一绝对路径的 `--version`、`--help` 和登录状态。未登录时启动 `kimi login`，把浏览器交给客户。
7. 复查版本、来源与目录，使用 `scripts/render_status.py` 输出一行客户状态。

## 产品自动更新边界

- Kimi Code CLI 可能后台检查更新；技能默认不主动更新，但要披露产品行为。
- 只读检查不得修改 `KIMI_CODE_NO_AUTO_UPDATE` 或 `tui.toml` 的自动更新设置。
- 客户要求调整自动更新时先展示影响并单独确认；不把配置授权当作本次升级授权。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Kimi Code CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Kimi Code CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/等待登录/被阻塞：原因> |

- 用户只问 Kimi Code CLI 时，不增加 Node.js、npm、其他 AI CLI 或其他技能行。
- `更新时间` 是最终验证时间；目录用 `~` 相对路径，避免用户名。
- 更新后 `当前状态` 仍是“已安装”；多个副本只汇报登录 shell 生效的一份并提示冲突。
- 最新版取得失败写“未取得”，不得猜测。

## 安装与更新的中间状态

真正安装或更新时生成随机 `run_id`，每个实际阶段立即调用 `scripts/record_install_progress.py`，同步展示检查、计划、等待确认、安装/更新、验证和终态。只读检查不创建 state。

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

更新执行和验证阶段必须带客户明确最新版授权标记。阶段事件只保存固定代码和时间，不保存账号、凭据、响应正文、命令全文或私有路径。

## 权限与回滚

- 优先用户级安装，不默认使用 `sudo`。修改 PATH/profile、切换来源或系统范围安装先确认。
- 更新前记录旧版本和来源；失败时保留原安装，不自动卸载、降级或清理配置。
- 临时安装内容在成功、失败或取消后都清理。

## 私密信息与中间数据

- 登录凭据由 Kimi 官方登录态和系统凭据库管理；不读取或打印 `~/.kimi-code` 内的凭据内容。
- 非秘密配置保留在 `KIMI_CODE_HOME` 或默认目录；SOIA 不另建凭据文件。
- 机器变更阶段记录写用户私有 state；版本检查默认无状态。
- 不记录 token、cookie、密码、授权码、账号、响应正文或客户私有绝对路径。

## 日志与完成回执

最终回执包含固定十列表格、版本与帮助验证、自动更新设置是否只读，以及客户是否还需浏览器登录。正常依赖不展开成额外行。

## 前向测试

用临时 fake `kimi` 覆盖缺失、正常、异常和多副本；mock npm 最新版响应；验证十列渲染、`KIMI_CODE_HOME`、路径脱敏、默认不更新和授权门禁。
