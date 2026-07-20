---
name: soia-env-environment-setup
description: 从零规划并验证小白开发环境：诊断网络，按依赖顺序安装 Node.js、Python、Codex、WorkBuddy，并输出可交给 SOIA 其他技能库的环境就绪摘要。触发：「配置开发环境」「从零安装工具」「环境搭建」「帮我准备 Codex/Python/Node/WorkBuddy」。
dependencies:
  hard: [soia-env-network-diagnose]
  optional: [soia-env-node-install, soia-env-python-install, soia-env-codex-install, soia-env-codex-setup-support, soia-env-workbuddy-install]
version: 1.1.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 21:30:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-environment-setup

把“电脑还没准备好”拆成可验证的小步骤。这个编排技能只负责判断顺序、协调专门技能和交付 readiness summary；具体安装细节由对应技能执行。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 从零配置开发环境 | 检查系统、网络、运行时，再按依赖顺序安装 | 每一步计划、权限请求和验证结果 |
| 准备知识库或 PKM 工作 | 先确认 Node/Python、网络和登录状态 | 可交给其他 SOIA 技能库的就绪摘要 |
| 不知道缺什么 | 只读盘点命令、版本和常见阻塞 | 缺什么、为什么缺、下一步怎么补 |

### 客户如何使用

1. 用自然语言说目标，例如“帮我把这台电脑准备好使用 Codex”和系统类型。
2. Agent 先读取当前系统与工具状态，不让客户先猜命令。
3. Agent 生成安装计划；安装、PATH/profile 修改、管理员权限或网络设置变更前展示影响并确认。
4. 客户只在官方图形界面完成登录、验证码、系统安全提示和产品授权；不要求客户操作终端。
5. 每一步独立验证后再进入下一步；失败时停止在当前步骤，不把未完成说成完成。

### 已安装工具的生命周期

- 先盘点版本、安装来源和项目约束，再决定是 `missing`、`ready`、`update_available` 还是 `blocked`。
- `ready` 表示当前可用，不重复安装；`update_available` 只表示发现新版本，是否更新仍要沿用对应专门技能的来源和确认流程。
- 更新前记录旧版本和来源，更新后重新验证版本、帮助命令、登录/签名和项目可用性；失败时保留旧安装，不自动卸载或换源。
- 桌面应用与 CLI、Node/Python 运行时与 pip/npm 包分别管理，不能用一个组件的版本推断另一个组件已更新。

### 依赖与安装

| 依赖 | 类型 | 处理方式 |
|---|---|---|
| `soia-env-network-diagnose` | 前置技能 | 先检查 DNS/HTTPS/下载源；缺少时做最小网络检查 |
| `soia-env-node-install` | 按目标启用 | Codex 或 Node 项目需要时调用 |
| `soia-env-python-install` | 按目标启用 | Python 项目或脚本需要时调用 |
| `soia-env-codex-install` | 按目标启用 | 客户明确要使用 Codex 时调用 |
| `soia-env-codex-setup-support` | 按目标启用 | 同时涉及桌面版、CLI 或 Codex 故障排查时调用 |
| `soia-env-workbuddy-install` | 按目标启用 | 客户明确要使用 WorkBuddy 时调用 |
| `soia-open-skills` | 方法邻居 | 完成环境摘要后再衔接 PKM/云盘技能，不复制其文件 |
| `soia-private-skills` | 私有方法邻居 | 只有已安装且任务需要时才提示，不自动安装 |

各专门技能的官方来源和版本事实见其 `references/`。本技能不读取私有凭据文件。

## 执行流程

1. 识别 OS、版本、架构、shell、当前用户权限和项目目录；缺失信息由 Agent 只读探测。
2. 把目标拆成 `network → runtime → package manager → AI tool → downstream handoff`。
3. 使用 `soia-env-network-diagnose` 的只读流程检查官方站点。出现代理、证书、DNS 或超时问题时，先输出诊断，不自动改网络配置。
4. 按依赖顺序执行：Codex 先准备 Node/npm；同时涉及桌面版、CLI 或 Codex 故障时调用 `soia-env-codex-setup-support`；Python 工作流先准备 Python/venv；WorkBuddy 使用官方桌面安装包。
5. 每一步完成后验证命令、版本、路径和一次无副作用的 `--help`/版本调用。

## 跨库摘要

输出不含秘密的 YAML 或 JSON 摘要，字段固定为：

```yaml
schema_version: 1
os: <macos|windows|linux|unknown>
arch: <architecture>
shell: <shell-or-unknown>
tools:
  node: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  python: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  codex: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  workbuddy: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
network: {status: <ready|degraded|blocked>, checked_sources: <count>}
blockers: []
next_handoff: <none|soia-open-skills|soia-private-skills>
```

只传递状态、版本和阻塞类别，不传递用户名、路径、token、cookie、命令历史或配置内容。

## 权限与回滚

- 默认只读检查；安装由客户明确提出即视为目标授权，但每次新增管理员权限、系统范围安装、PATH/profile 修改仍需单独确认。
- 不使用 `sudo`、管理员终端、注册表、代理、DNS 或证书变更作为“顺手修复”。
- 安装失败时保留已安装状态，记录具体包/版本和回滚方式；不自动卸载、不覆盖现有版本。
- 远程登录和服务授权由客户在官方界面完成，Agent 不代填密码或验证码。

## 日志与完成回执

```markdown
完成：<已完成的环境范围>。

日志摘要：
- started: <OS/架构/目标，不打印秘密>
- processed: <检查和安装步骤数量>
- created/updated: <工具/版本类别>
- skipped/failed: <数量和原因>

验证：
- <网络、命令、版本和无副作用检查>

问题与下一步：
- <阻塞、需客户授权的官方页面或下一步技能>
```

## 前向验收

用 fixture 模拟“Node 缺失、Python 已有、网络阻断”三种状态，确认编排结果只推进可用步骤，并将阻塞写入 `blockers`；真实安装必须另外验证官方二进制版本和客户可用的 GUI 登录状态。
