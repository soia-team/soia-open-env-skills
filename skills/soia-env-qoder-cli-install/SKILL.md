---
name: soia-env-qoder-cli-install
description: 面向小白检查、安装、登录和按明确授权更新 Qoder CLI；识别官方独立安装、Homebrew 与 npm 来源，默认只报告版本和自动更新设置。触发：「安装 Qoder CLI」「qodercli 不存在」「Qoder 登录」「检查 Qoder 更新」「更新 Qoder 到最新」。
dependencies:
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.0.1
created_at: 2026-07-21 00:00:00
updated_at: 2026-07-21 14:40:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-qoder-cli-install

安装和验证独立的 Qoder CLI（命令 `qodercli`）。Agent 执行终端步骤，客户只在 Qoder 官方页面完成登录和授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Qoder CLI | 检查系统和现有来源，安装官方稳定版 | 版本、安装来源、目录和验证结果 |
| 检查或更新 | 只读比较版本；明确要求最新版后沿原来源更新 | 是否可更新及真实处理结果 |
| 登录 Qoder | 启动 `qodercli login` 或官方交互登录 | 官方浏览器授权步骤 |
| 命令不可用 | 检查 PATH、重复安装和配置状态 | 阻塞原因与安全修复方案 |

### 客户如何使用

1. 客户直接说“安装 Qoder CLI”；不要求客户输入终端命令。
2. Agent 先只读检查并展示安装计划。安装缺失工具不等于更新已有工具。
3. “更新 Qoder”先汇报当前和最新版本；只有明确说“更新到最新版本”才执行更新。
4. 登录时 Agent 启动官方流程，客户只在官方浏览器点击授权；不在聊天或终端粘贴密钥。
5. 完成后验证版本、帮助命令和一次无副作用启动，再输出固定十列列表。

### 首次登录与真实配置验证

- `配置文件目录`只显示候选目录；技能必须同时检查 `config_status` 和 `config_file_status`，目录或 `~/.qoder/settings.json` 不存在时明确报告“未初始化”。
- 首次使用时由 Agent 启动 `qodercli`，在交互界面执行 `/login`；客户选择浏览器登录并在 Qoder 官方页面完成授权，不需要客户操作终端。
- 如果客户明确选择 Personal Access Token，申请入口是 [Qoder Integrations](https://qoder.com/account/integrations)；客户只在官方登录流程中输入，Agent 不接收或打印 token。
- 登录后重新检查 `~/.qoder/settings.json`、运行 `qodercli --version` 和无副作用启动；没有完成登录时处理结果写“等待首次登录”，不能只写“已安装”。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| 官方支持的操作系统 | 强依赖 | 不支持的平台停止安装并说明原因 |
| Node.js/npm | npm 渠道依赖 | 官方独立安装不需要；选择 npm 时才调用 `soia-env-node-install` |
| 网络诊断 | 可选前置 | 官方站点不可达时调用 `soia-env-network-diagnose` |
| Qoder 账号 | 登录依赖 | 客户在官方页面完成授权，Agent 不读取凭据 |

官方事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，检测 `qodercli`、版本、来源、安装目录和 `~/.qoder` 配置目录/文件的实际存在状态。
2. 执行 `python3 scripts/check_latest.py --json`，从 npm 官方元数据读取 `@qoder-ai/qodercli` 最新版。
3. 已安装且正常时写“已安装”；未取得最新版授权时只汇报，不重复安装或调用更新器。
4. 未安装时优先官方独立安装；客户选择 npm 时使用 `npm install -g @qoder-ai/qodercli`。官方网络脚本先下载到独立临时目录、核对来源和内容，再执行本地副本；不直接执行网络响应。
5. 明确更新到最新后：独立来源使用 `qodercli update`；npm 来源使用 `npm install -g @qoder-ai/qodercli@latest`；Homebrew 沿实际已安装 cask 更新。不得静默换源。
6. 验证同一绝对路径的 `--version`、`--help` 和无副作用启动。需要登录时启动 `qodercli login`，把浏览器交给客户。
7. 复查版本与目录，使用 `scripts/render_status.py` 输出客户列表。

## 产品自动更新边界

- Qoder CLI 自身可能默认启用自动升级；Agent 必须披露该状态，但本技能不会因版本检查而触发更新。
- 只读检查不得修改 `~/.qoder/settings.json` 的 `general.enableAutoUpdate`。
- 客户要求调整自动更新时，先展示影响、备份非秘密设置并复核；这与“本次更新到最新”是两个独立授权。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Qoder CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Qoder CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/Homebrew 安装/npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/被阻塞：原因> |

- 用户只问 Qoder CLI 时，不增加 Node.js、npm、其他 AI CLI 或其他技能行。
- `更新时间` 在最终验证后生成；目录用 `~` 相对路径，避免暴露用户名。
- 更新完成后 `当前状态` 仍是“已安装”，`处理结果` 写“已更新”。
- 多个命令副本只汇报登录 shell 当前生效的一份并提示冲突，不自动删除。
- 最新版取得失败时写“未取得”，不得猜测。
- `config_status=未创建` 或 `config_file_status=未创建` 时，处理结果写“等待首次登录/配置”，同时给出 `qodercli`、`/login` 和官方入口；不得把候选路径当成现成配置。

## 安装与更新的中间状态

真正安装或更新时生成随机 `run_id`，每个实际阶段立即调用 `scripts/record_install_progress.py` 并同步展示：

```text
checking → planning → [waiting_confirmation] → installing/updating → verifying → completed/failed/blocked
```

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

只读检查不落盘。更新的 `updating`、`verifying` 和 `completed` 必须带客户明确最新版授权标记；阶段记录只保存固定代码和时间，不保存账号、命令全文、响应正文或私有路径。

## 权限与回滚

- 优先用户级安装，不默认使用管理员权限。修改 PATH、shell profile、切换来源或覆盖命令时先单独确认。
- 更新前记录旧版本和来源；失败时保留原安装，不自动卸载、降级或清理配置。
- 临时安装文件使用系统临时目录，成功、失败和取消都清理。

## 私密信息与中间数据

- 登录凭据由 Qoder 官方登录态或系统凭据库保存；不读取、复制或打印凭据内容。
- 非秘密配置留在 `~/.qoder`；SOIA 不另建凭据文件。
- 只有机器变更写入脱敏进度 state；版本检查默认无状态。
- 不记录 token、cookie、session、授权码、账号、响应正文或客户私有绝对路径。

## 日志与完成回执

最终回执包含固定十列表格、验证项、自动更新设置是否仅被读取，以及客户是否还需在浏览器授权。正常依赖不展开为额外行。

## 前向测试

用临时 fake `qodercli` 覆盖缺失、正常、版本异常和多副本；mock npm 最新版响应；验证固定列表、路径脱敏、默认不更新和更新授权门禁。
