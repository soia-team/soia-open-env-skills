---
name: soia-env-environment-setup
description: 从零规划并验证面向新手的开发环境，协调所需安装技能。触发：「从零配置开发环境」「准备 AI CLI 环境」「新电脑开发环境搭建」
dependencies:
  hard: [soia-env-network-diagnose]
  optional: [soia-env-node-install, soia-env-python-install, soia-env-codex-install, soia-env-claude-cli-install, soia-env-qoder-cli-install, soia-env-antigravity-cli-install, soia-env-opencode-cli-install, soia-env-kimi-cli-install, soia-env-deepcode-cli-install, soia-env-codex-setup-support, soia-env-workbuddy-install, soia-env-storage-cleanup, soia-env-open-skills-install]
version: 1.6.6
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-09 01:40:00
created_by: gpt-5
updated_by: deepseek-v4-flash
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

用自然语言说目标，例如“帮我把这台电脑准备好使用 Codex”和系统类型；Agent 先读取当前系统与工具状态，生成安装计划，安装、PATH/profile 修改、管理员权限或网络设置变更前展示影响并确认。客户只在官方图形界面完成登录、验证码、系统安全提示和产品授权；每一步独立验证后再进入下一步，失败时停止在当前步骤。只安装单个运行时或 CLI 时交给对应安装技能。

### 已安装工具的生命周期

先盘点版本、来源、配置目录/文件和项目约束，再归入 `missing`、`needs_configuration`、`ready`、`update_available` 或 `blocked`。`ready` 必须同时满足：命令/应用存在、版本验证通过、首次登录或 API 配置完成、无副作用启动/认证验证通过；“已安装”不等于“ready”。默认只检查并汇报当前版本和可用版本，不自动更新；客户只说“更新”时，先展示两个版本并询问是否“更新到最新版本”，没有这句明确选择，不调用更新器。完整状态语义见 [lifecycle.md](references/lifecycle.md)。

### 安装与更新的中间状态

真正开始安装或更新后，必须在对话中持续追加阶段状态：检查、计划/等待确认、安装或更新、验证、完成/失败/被阻塞；不能只给最终表。各专门安装技能使用自己的 `scripts/record_install_progress.py` 写入私有 state；编排技能只汇总子技能的阶段和 `run_id`，不重复保存第二份完整日志。只读盘点不创建中间状态文件。细则见 [lifecycle.md](references/lifecycle.md)。

### 依赖与安装

核心分工：`soia-env-network-diagnose` 是硬前置技能（网络侧先检查 DNS/HTTPS/下载源，本机侧盘点运行时并推导各 AI CLI 可安装性，缺少时做最小检查）；`soia-env-node-install`/`soia-env-python-install` 按目标启用；`soia-env-open-skills-install` 在环境就绪后接管插件市场接入与域插件安装。完整 16 项依赖表见 [dependencies.md](references/dependencies.md)；各专门技能官方来源和版本事实见其 `references/`，本技能不读取私有凭据文件。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-environment-setup -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### 私密信息与中间数据

- provider 登录凭据只使用官方登录态或系统凭据库；配置文件只保存非秘密偏好和路径。
- 只读盘点默认不写文件；改变机器时只在用户 state 目录保存脱敏后的动作、版本、结果和 `checked_at`；只传递状态、版本和阻塞类别，不传递用户名、路径、token、cookie、命令历史或配置内容。
- 可重建元数据放 cache；下载、解压和探测文件放每次运行独立的系统临时目录并在成功或失败后清理；不把仓库目录作为运行时存储，不在日志中打印 token、账号、响应正文或客户私有绝对路径。

### 日志与完成回执

先输出客户明确要求的目标列表（下方固定表），每个目标一行，再提供机器可读 YAML/JSON 摘要；`更新时间` 是该行完成最终验证的时间，不是技能文件的修改时间。

## 执行流程

1. 识别 OS、版本、架构、shell、当前用户权限和项目目录；运行时盘点走 `soia-env-network-diagnose` 的 `scripts/probe_runtimes.py --json`，不要自己临场拼版本命令（各运行时版本参数不一致，该脚本已按工具适配并有测试锁住）。
2. 把目标拆成 `network → runtime → package manager → AI tool → downstream handoff`；网络侧按三组对照探测官方站点，本机侧按类别盘点运行时并给出「可安装 / 待复核 / 被阻塞」；`timeout` 判「待复核」并放宽超时复核，不得当成未安装直接触发安装。
3. 按依赖顺序执行：npm 渠道的 Agent CLI 先满足对应 Node.js 要求（Deep Code 固定要求 Node.js 22+）；Claude Code、Qoder、OpenCode、Kimi Code 有独立安装时不因 Node.js 缺失而阻塞；Antigravity 使用 Google 独立安装；Python 工作流先准备 Python/venv；WorkBuddy 使用官方桌面安装包。
4. 对已安装工具默认只比较版本；没有明确“更新到最新”时不得进入更新执行阶段。安装或授权更新由专门技能边执行边显示阶段并记录私有进度；每步验证命令、版本、路径和一次无副作用的 `--help`/版本调用，需登录或 API key 的 CLI 必须完成首次配置和真实认证验证，否则标为 `needs_configuration`。
5. 客户提出空间清理时调用 `soia-env-storage-cleanup`：本编排只能推进扫描和计划，必须等客户看过风险清单并明确授权后才能删除。

完整流程细则见 [workflow.md](references/workflow.md)。

## 客户状态列表（强制）

先输出客户明确要求的目标，每个目标一行，列名和顺序固定：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| <Node.js/Python/Codex CLI/Claude Code CLI/Qoder CLI/Antigravity CLI/OpenCode CLI/Kimi Code CLI/Deep Code CLI/WorkBuddy/网络诊断/存储清理> | <状态> | <版本/不适用/未取得> | <版本/不适用/未取得> | <正常/降级/异常/未验证> | <RFC3339-with-timezone> | <处理结果> |

- 只列客户要求的目标及其必要前置项，不展开全部已装工具；网络诊断的版本列写“不适用”，无法取得软件最新版本时写“未取得”。机器可读 YAML/JSON 摘要在客户列表之后提供，保持下方固定结构；其余输出规则见 [workflow.md](references/workflow.md)。

## 跨库摘要

客户列表之后输出不含秘密的机器可读 YAML/JSON 摘要：`schema_version: 2`，含 `os`/`arch`/`shell`、`tools` 下各工具 `status`/`version`（`node`、`python`、`codex`、`workbuddy` 保持兼容性字段）、`network`、`blockers`、`next_handoff`；新增 Agent CLI 只在本次被请求或实际检查时加入。固定结构全文见 [workflow.md](references/workflow.md)。

## 不负责什么（能力边界）

- **默认不自动更新**：只检查并汇报当前版本和可用版本；只有“更新到最新版本”“升级到最新版”等同等明确指令才授权更新已有工具。
- **不自动改网络配置**：出现代理、证书、DNS 或超时问题时先输出诊断；不把 `sudo`、管理员终端、注册表、代理、DNS 或证书变更当“顺手修复”。
- **不代客户完成登录授权**：远程登录和服务授权由客户在官方界面完成，Agent 不代填密码或验证码。
- **不自动删除**：空间清理只能推进扫描和计划，必须等客户看过风险清单并明确授权后才能删除。
- **不复制邻居技能文件**：`soia-open-skills` / `soia-private-skills` 只衔接提示，不复制其文件、不自动安装。

## 权限与回滚

- 默认只读检查；安装由客户明确提出即视为目标授权，但每次新增管理员权限、系统范围安装、PATH/profile 修改仍需单独确认；不使用 `sudo`、管理员终端、注册表、代理、DNS 或证书变更作为“顺手修复”。
- 安装失败时保留已安装状态，记录具体包/版本和回滚方式；不自动卸载、不覆盖现有版本；远程登录和服务授权由客户在官方界面完成，Agent 不代填密码或验证码。

## 前向验收

用 fixture 模拟“Node 缺失、Python 已有、网络阻断”三种状态，确认编排结果只推进可用步骤，并将阻塞写入 `blockers`；真实安装必须另外验证官方二进制版本和客户可用的 GUI 登录状态。
