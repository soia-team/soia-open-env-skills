<div align="center">

# soia-open-env-skills

中文 | [English](README.en.md)

面向小白的环境配置、网络诊断、工具安装与安全维护技能库。

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Agent Agnostic](https://img.shields.io/badge/agents-agnostic-6f42c1.svg)](https://skills.sh/)
[![skills.sh](https://img.shields.io/badge/skills.sh-compatible-00a67d.svg)](https://skills.sh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](./requirements-dev.txt)

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -y
```

兼容 Claude Code、Codex、Gemini/Antigravity、OpenCode、Kimi、Qoder 及其他
skills.sh 兼容 Agent。客户不需要先学习终端命令：Agent 负责安全检查和可逆的
安装步骤，客户只在官方页面完成登录、验证码、系统安全提示和服务授权。

[这是什么](#这是什么) · [从哪里开始](#从哪里开始) · [技能清单](#技能清单) · [高频技能速览](#高频技能速览) · [安装](#安装) · [触发词映射](#触发词映射) · [仓库结构](#仓库结构) · [三仓协作](#三仓协作) · [安全边界](#权限与安全边界) · [致谢](#致谢) · [验证与贡献](#验证与贡献)

</div>

---

## 这是什么

`soia-open-env-skills` 是 SOIA 的公开环境技能真源，负责把一台“还不能稳定工作”的电脑准备成可交给其他技能使用的环境：

```text
网络可达性
    ↓
Node.js / Python / npm / pip 等基础运行时
    ↓
桌面应用与 Agent CLI 安装
    ↓
首次登录、API 配置与真实可用性验证
    ↓
脱敏 readiness summary
    ↓
soia-open-skills / soia-private-skills
```

本仓库只负责环境就绪，不负责知识库内容、云盘工作流或 SOIA 内部治理。

### 适合什么场景

- “帮我从零配置这台 Mac/Windows/Linux 电脑。”
- “安装 Codex、Claude Code、OpenCode、Kimi 或 Deep Code CLI。”
- “检查为什么网络、npm、pip 或官方安装器失败。”
- “检查工具是否真的登录并可用，而不是只看命令是否存在。”
- “统计 SOIA 受管目录空间，并在确认风险后清理缓存。”

### 不负责什么

- 不把 `ChatGPT.app` 当成独立 Codex CLI，也不混淆桌面版和 CLI 的版本、登录与更新。
- 不把“命令存在”或“默认配置路径”当成“已经登录、已经配置、可以调用模型”。
- 不保存 API key、密码、cookie、token 或客户私有配置。
- 不自动升级已有工具；只有客户明确要求“更新到最新版本”才执行更新。
- 不复制 `soia-open-skills` 或 `soia-private-skills` 的技能。

## 从哪里开始

### 推荐入口

| 目标 | 先调用 | 完成标准 |
|---|---|---|
| 从零搭建环境 | `soia-env-environment-setup` | 网络、运行时、目标工具和首次配置逐项验收 |
| 先判断网络 | `soia-env-network-diagnose` | DNS、HTTPS、代理、证书和下载源有证据 |
| 安装 Codex | `soia-env-codex-install` | 独立 CLI 与 ChatGPT.app 分开，登录状态单独验证 |
| 安装 Deep Code | `soia-env-deepcode-cli-install` | DeepSeek API key 在本机配置，并完成真实请求验证 |
| 安装其他 Agent CLI | 对应 `soia-env-*-cli-install` | 命令、来源、版本、配置/凭据和首次登录分别确认 |
| 检查磁盘空间 | `soia-env-storage-cleanup` | 先扫描和生成计划，客户二次授权后才删除 |

### 一个客户请求如何被处理

1. 识别系统、架构、shell、包管理器、已有版本和实际安装来源。
2. 只读检查网络和依赖，展示安装或配置计划。
3. 客户授权后安装缺失工具；安装已有工具不等于授权更新。
4. 对需要登录的工具启动官方流程；客户在官方页面完成授权。
5. 检查配置目录/文件是否真实存在，并做一次无副作用启动或认证验证。
6. 用固定列表汇报当前状态、版本、安装方式、目录、更新时间和处理结果。

## 技能清单

完整的自动目录见 [skills/README.md](./skills/README.md)。当前发布 14 个技能，按下方四组归类。

> **状态图例**：✅ 装完不需要额外凭据或客户端登录即可直接用 · 🟡 还需客户申请 API key 或完成独立客户端登录才能用起来
> **依赖列**：来自每个技能 `SKILL.md` frontmatter 里的 `dependencies`；标注“跨仓”的依赖不在本仓库内，见 [三仓协作](#三仓协作)。

### 环境编排与诊断

核心价值：在动手装任何工具之前，先把“电脑到底缺什么、网络通不通”弄清楚——这是后面所有安装步骤不白跑的前提。

| 技能 | 说明 | 状态 | 依赖 |
|---|---|:---:|---|
| [`soia-env-environment-setup`](./skills/soia-env-environment-setup/) | 从网络到运行时、CLI、桌面工具的分步编排，并输出下游就绪摘要 | ✅ | 硬依赖 `soia-env-network-diagnose`；可选按目标启用其余全部 12 个环境技能 |
| [`soia-env-network-diagnose`](./skills/soia-env-network-diagnose/) | 只读诊断 DNS、HTTPS、代理、证书和官方源可达性 | ✅ | 无 |
| [`soia-env-codex-setup-support`](./skills/soia-env-codex-setup-support/) | 排查 ChatGPT.app/Codex 桌面能力、独立 CLI、登录、日志写入和磁盘健康 | ✅ | 可选：`soia-env-network-diagnose`、`soia-env-node-install`、`soia-env-codex-install` |
| [`soia-env-storage-cleanup`](./skills/soia-env-storage-cleanup/) | 统计受管目录，生成带过期条件和风险的清理计划，并在授权后安全清理 | ✅ | 无技能依赖（需 Python 3.10+） |

### 基础运行时

核心价值：Agent CLI 和大多数开发工具最终都要落在 Node.js 或 Python 上——这两个技能是几乎所有后续安装的地基。

| 技能 | 说明 | 状态 | 依赖 |
|---|---|:---:|---|
| [`soia-env-node-install`](./skills/soia-env-node-install/) | 检查、安装和验证 Node.js、npm 与 PATH；默认不主动更新 | ✅ | 可选：`soia-env-network-diagnose` |
| [`soia-env-python-install`](./skills/soia-env-python-install/) | 检查、安装和验证 Python、pip 与虚拟环境；优先 `python -m pip` | ✅ | 可选：`soia-env-network-diagnose` |

### Agent CLI

核心价值：每个编码 Agent 的 CLI 都有自己的安装渠道、登录方式和“命令存在≠能用”的坑；这组技能把这些坑一个一个填平，而不是让客户自己踩。

| 技能 | 说明 | 状态 | 依赖 | 首次可用性验证 |
|---|---|:---:|---|---|
| [`soia-env-codex-install`](./skills/soia-env-codex-install/) | 安装、验证和按明确授权更新 OpenAI Codex CLI，识别实际生效的安装来源 | ✅ | 硬依赖 `soia-dev-ai-cli-upgrade`（**跨仓**，来自 `soia-open-skills`）；可选：`soia-env-node-install`、`soia-env-network-diagnose` | `codex --login`，与 ChatGPT.app 分开验证 |
| [`soia-env-claude-cli-install`](./skills/soia-env-claude-cli-install/) | 检查、安装、登录和按明确授权更新 Anthropic Claude Code CLI | ✅ | 可选：`soia-env-node-install`、`soia-env-network-diagnose` | 官方浏览器登录与 `claude doctor` |
| [`soia-env-qoder-cli-install`](./skills/soia-env-qoder-cli-install/) | 检查、安装、登录和按明确授权更新 Qoder CLI | ✅ | 可选：`soia-env-node-install`、`soia-env-network-diagnose` | `/login` 浏览器授权或官方 PAT 流程 |
| [`soia-env-antigravity-cli-install`](./skills/soia-env-antigravity-cli-install/) | 检查、安装、登录、迁移和按明确授权更新 Google Antigravity CLI（`agy`），区分 `agy` 与旧 Gemini CLI | ✅ | 可选：`soia-env-network-diagnose` | Google 官方登录；不把 `gemini` 当作 `agy` |
| [`soia-env-opencode-cli-install`](./skills/soia-env-opencode-cli-install/) | 检查、安装、登录、配置和按明确授权更新开源 OpenCode CLI | ✅ | 可选：`soia-env-node-install`、`soia-env-network-diagnose` | `opencode auth login` 与 `auth list` |
| [`soia-env-kimi-cli-install`](./skills/soia-env-kimi-cli-install/) | 检查、安装、登录和按明确授权更新 Moonshot AI Kimi Code CLI | ✅ | 可选：`soia-env-node-install`、`soia-env-network-diagnose` | `kimi login` 或 TUI `/login` |
| [`soia-env-deepcode-cli-install`](./skills/soia-env-deepcode-cli-install/) | 检查、安装、配置和按明确授权更新面向 DeepSeek 优化的开源 Deep Code Agent CLI（`lessweb/deepcode-cli`） | 🟡 需客户在 DeepSeek 官方平台申请 API key | 硬依赖 `soia-env-node-install`（Node.js 22+）；可选：`soia-env-network-diagnose` | `~/.deepcode/settings.json` + DeepSeek API 实际验证 |

### 桌面工具

核心价值：不是所有客户工具都是 CLI；这组技能把同样的“来源核实 + 首次登录验证”标准套用到桌面客户端上。

| 技能 | 说明 | 状态 | 依赖 |
|---|---|:---:|---|
| [`soia-env-workbuddy-install`](./skills/soia-env-workbuddy-install/) | 通过 WorkBuddy 官方安装包完成安装、签名、启动和登录验证 | 🟡 需在桌面客户端内完成登录 | 可选：`soia-env-network-diagnose` |

## 首次配置不是安装完成

这是本仓库统一遵守的状态边界：

```text
命令存在
  ≠ 已安装来源正确
  ≠ 已创建配置
  ≠ 已完成登录/API key
  ≠ 真实请求成功
```

每个 CLI 技能都会分别检查：

- `config_status`：配置或状态目录是否真实存在；
- `config_file_status`：已知配置文件是否真实存在；
- `credential_status`：有独立凭据文件的工具是否发现凭据；
- 首次启动、浏览器授权或无副作用模型调用是否成功。

例如，Deep Code 首次运行可以创建部分 `~/.deepcode` 运行状态，但不会替客户生成带 API key 的 `settings.json`。客户需要在 [DeepSeek API Keys](https://platform.deepseek.com/api_keys) 创建 key，在本机写入 `~/.deepcode/settings.json`，再由 Agent 完成验证。这正是上面技能清单里 `soia-env-deepcode-cli-install` 被标记为 🟡 而不是 ✅ 的原因。

## 高频技能速览

从 14 个技能里挑 5 个最能代表不同工作方式的技能，各给一个最小示例和典型输出，降低第一次使用的上手门槛。

### soia-env-environment-setup

从零编排环境的入口，只负责判断顺序和汇总下游技能的结果，不重复实现具体安装逻辑。

```text
帮我把这台电脑准备好使用 Codex
从零配置开发环境
```

**典型输出**：先给出固定列（技能/当前状态/当前版本/最新版本/运行状态/更新时间/处理结果）的客户状态列表，逐个目标一行；表格之后附一份不含秘密的 YAML 摘要（`schema_version`、`os`、`arch`、`tools`、`network`、`blockers`、`next_handoff`），供 `soia-open-skills` 等下游技能消费。

### soia-env-network-diagnose

只读诊断，任何安装类技能卡住时的第一站；不修改代理、DNS、证书或防火墙。

```bash
python3 scripts/probe_endpoints.py --url https://nodejs.org/en --url https://www.python.org/downloads/ --json
```

**典型输出**：固定七列状态表，`处理结果` 明确写“可以继续安装”或“需要处理：<错误类别>”；错误类别限定在 `dns_failed`/`tls_failed`/`timeout`/`http_error`/`proxy_required`/`reachable` 之内，不做“网络整体不可用”这种一次探测就下的断言。

### soia-env-codex-install

区分“ChatGPT.app 桌面版”和“独立 Codex CLI”，是本仓库里状态边界体现得最完整的一个技能。

```bash
python3 scripts/inspect_installation.py --json
TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-dev-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
```

**典型输出**：十列状态表（技能/当前状态/当前版本/最新版本/运行状态/安装方式/安装目录/配置文件目录/更新时间/处理结果），只输出 `Codex CLI` 一行；未登录时 `处理结果` 写“等待首次登录”并给出 `codex --login`，不会因为 `~/.codex` 目录存在就当作已登录。

### soia-env-deepcode-cli-install

演示“需要客户去外部平台申请 API key”这类 🟡 状态的技能。

```bash
python3 scripts/inspect_cli.py --json
npm install -g @vegamo/deepcode-cli
```

**典型输出**：同样的十列状态表；`config_file_status` 未创建时 `处理结果` 固定写“等待首次配置”，并附上 [DeepSeek API Keys](https://platform.deepseek.com/api_keys) 入口和本机 `~/.deepcode/settings.json` 路径——不会因为命令能跑起来就报“正常”。

### soia-env-storage-cleanup

演示删除类操作的强制授权流程：扫描、计划、删除是三个独立阶段，任何一步都不能替客户跳过。

```bash
python3 scripts/storage_cleanup.py scan --json
python3 scripts/storage_cleanup.py plan --json
# 客户看到风险提醒并回复"确认按计划 <plan_id> 删除"之后：
python3 scripts/storage_cleanup.py clean --plan <plan-path> --confirmed-plan-id <plan-id> --execute --json
python3 scripts/storage_cleanup.py verify --receipt <receipt-path> --json
```

**典型输出**：先给四类受管数据（配置/审计状态/缓存/临时文件）的大小、可清理大小和候选文件数，再附带 `plan_id` 和不可撤销风险提醒；只有客户针对该 `plan_id` 明确确认后才真正删除，删除后必须跑 `verify` 复核实际释放空间，命令返回 0 不能代替复核。

## 安装

### 只安装环境编排技能

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-environment-setup -y
```

### 安装全部环境技能

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -y
```

### 查看可安装清单

```bash
npx skills add soia-team/soia-open-env-skills -l --full-depth
```

安装后，最终验收应从已推送的远程仓库执行，而不是把本地目录手工复制到 Agent 目录：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s <skill-name> -y
```

## 触发词映射

装完之后直接用自然语言说话即可，Agent 按下表触发对应技能（每个技能的完整触发词列表见其 `SKILL.md` frontmatter 的 `description`）：

| 你说 | 触发技能 |
|---|---|
| `配置开发环境` / `从零安装工具` / `环境搭建` | `soia-env-environment-setup` |
| `网络不通` / `下载失败` / `npm/pip 超时` / `证书错误` | `soia-env-network-diagnose` |
| `Codex 打不开` / `Codex 变慢` / `检查磁盘健康` | `soia-env-codex-setup-support` |
| `检查 SOIA 占用` / `清理临时文件` / `释放磁盘空间` | `soia-env-storage-cleanup` |
| `安装 Node` / `node 命令不存在` / `npm 超时` | `soia-env-node-install` |
| `安装 Python` / `python 命令不存在` / `pip 不能用` | `soia-env-python-install` |
| `安装 Codex` / `更新 Codex 到最新` / `Codex 登录` | `soia-env-codex-install` |
| `安装 Claude CLI` / `Claude 命令不存在` / `Claude 登录` | `soia-env-claude-cli-install` |
| `安装 Qoder CLI` / `qodercli 不存在` / `Qoder 登录` | `soia-env-qoder-cli-install` |
| `安装 agy` / `Gemini CLI 迁移` / `agy 登录` | `soia-env-antigravity-cli-install` |
| `安装 OpenCode` / `opencode 不存在` / `OpenCode 登录` | `soia-env-opencode-cli-install` |
| `安装 Kimi CLI` / `kimi 不存在` / `Kimi 登录` | `soia-env-kimi-cli-install` |
| `安装 DeepCode` / `deepcode 不存在` / `配置 DeepSeek Agent` | `soia-env-deepcode-cli-install` |
| `安装 WorkBuddy` / `安装腾讯龙虾` / `WorkBuddy 打不开` | `soia-env-workbuddy-install` |

## 仓库结构

本仓库只使用一个技能前缀域 `soia-env-`（环境域），因此不单独设命名规范章节；跨域命名约定见 [SKILL_SPEC.md](./SKILL_SPEC.md)。

```text
soia-open-env-skills/
├── AGENTS.md
├── README.md · README.en.md
├── LICENSE · CONTRIBUTING.md · SECURITY.md
├── SKILL_SPEC.md                    ← skill 结构与前言规范
├── DATA_STORAGE_SPEC.md             ← 凭据/状态/缓存/临时文件边界
├── requirements-dev.txt
├── scripts/
│   ├── audit_skills.py              ← 公开技能审计（命名、frontmatter、密钥、链接）
│   ├── audit_skill_output.py        ← 校验 readiness summary 的机器可读格式
│   ├── generate_skill_catalog.py    ← 从 SKILL.md 生成 skills/README.md
│   └── check_readme_coverage.py     ← 校验本文件是否提到全部技能名
├── templates/skill-template/        ← 新 skill 起手模板
├── tests/                           ← unittest 用例，覆盖脚本与状态表格式
└── skills/                          ← npx skills 扫描此目录
    ├── README.md                          ← 自动生成的技能总目录，勿手改
    ├── soia-env-environment-setup/        ├── soia-env-network-diagnose/
    ├── soia-env-codex-setup-support/      ├── soia-env-storage-cleanup/
    ├── soia-env-node-install/             ├── soia-env-python-install/
    ├── soia-env-codex-install/            ├── soia-env-claude-cli-install/
    ├── soia-env-qoder-cli-install/        ├── soia-env-antigravity-cli-install/
    ├── soia-env-opencode-cli-install/     ├── soia-env-kimi-cli-install/
    ├── soia-env-deepcode-cli-install/
    └── soia-env-workbuddy-install/
```

每个技能目录一个 `SKILL.md`（frontmatter 含 `name`/`description`/`version`/依赖/作者与时间戳）+ 自己的 `references/` 和 `scripts/`；`soia-env-environment-setup` 是纯编排技能，没有自己的 `scripts/`。

## 三仓协作

三个仓库的职责和安装关系如下：

| 仓库 | 公开边界 | 负责内容 |
|---|---|---|
| [`soia-open-env-skills`](https://github.com/soia-team/soia-open-env-skills) | 公开 | 网络、运行时、桌面工具、Agent CLI 和安全清理 |
| [`soia-open-skills`](https://github.com/soia-team/soia-open-skills) | 公开 | 云盘、知识库、PKM、公开协作工作流 |
| [`soia-private-skills`](https://github.com/soia-team/soia-private-skills) | 私有 | SOIA 内部治理、审计、开发和执行 |

### 跨仓硬依赖

本仓库的技能大多互相独立，但有一个真实的跨仓硬依赖，必须如实标注，不能含糊带过：

| 本仓库技能 | 硬依赖 | 依赖位置 | 用途 |
|---|---|---|---|
| `soia-env-codex-install` | `soia-dev-ai-cli-upgrade` | **`soia-open-skills`（跨仓，公开）** | 统一执行 Codex 版本审计与原渠道更新；本仓库不重复实现一套升级逻辑 |
| `soia-env-environment-setup` | `soia-env-network-diagnose` | 本仓库内 | 编排开始前先确认网络可达性 |
| `soia-env-deepcode-cli-install` | `soia-env-node-install` | 本仓库内 | Deep Code CLI 要求 Node.js 22+ |

跨仓依赖不会被自动安装。`soia-env-codex-install` 发现本机缺少 `soia-dev-ai-cli-upgrade` 时，会提示从配套公开仓库单独安装：

```bash
npx skills add soia-team/soia-open-skills -g -a '*' -s soia-dev-ai-cli-upgrade -y
```

三者共享安装源目录 `~/.agents/skills`，再由同步技能建立其他 Agent 的入口；环境仓库不会自动安装私有技能，也不会把凭据传给下游。典型安装顺序：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -y
npx skills add soia-team/soia-open-skills -g -a '*' -y
npx skills add soia-team/soia-private-skills -g -a '*' -y

# 如需同步到 SOIA 运行时，由公开仓库中的同步技能执行
npx skills add soia-team/soia-open-skills -g -a '*' -s soia-dev-sync-skills -y
python3 ~/.agents/skills/soia-dev-sync-skills/scripts/sync_soia_skills.py \
  --source-dir ~/.agents/skills \
  --targets soia
```

环境技能完成后只交付脱敏摘要，例如 `os`、`arch`、工具版本、状态和阻塞类别；下游技能必须根据摘要判断是否继续。

## 权限与安全边界

- 只读检查默认不写文件；安装、登录启动、PATH/profile 修改、管理员权限和网络设置变更前先展示计划。
- 版本发现默认只汇报；“更新”含义不明确时先报告当前/最新版本，只有明确要求“更新到最新版本”才执行。
- 官方脚本先下载到每次运行独立的临时目录并核对来源，不直接执行未经检查的网络响应。
- 客户不需要操作终端；客户负责官方浏览器登录、验证码、系统安全提示和服务授权。
- API key、密码、cookie、token 和 session 只能留在供应商登录态、OS keychain 或客户认可的本机安全位置。
- 状态回执不保存命令全文、凭据、响应正文、账号或客户私有绝对路径。
- 删除不可逆：清理技能必须先扫描，再展示不可变计划、候选、保留/清理条件和风险，客户必须对具体 `plan_id` 再次明确授权。

详细规则见 [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md)。

## 状态、记录与存储

所有客户可见安装回执都使用固定列表：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| `<目标技能>` | `<已安装/未安装/被阻塞>` | `<版本>` | `<版本/未取得>` | `<正常/异常/未验证>` | `<来源>` | `<目录>` | `<目录/未取得>` | `<RFC3339-with-timezone>` | `<结果>` |

真正改变机器时，技能还会实时记录检查、计划/确认、安装或更新、验证和终态；只读版本检查不创建进度 state。配置、审计 state、cache、临时数据和清理条件遵循 [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md)。

## 官方来源

技能优先使用供应商官方入口；具体版本事实和替代来源写在各技能的 `references/official-sources.md`：

- [OpenAI Codex CLI](https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Qoder CLI](https://docs.qoder.com/en/cli/quick-start)
- [Google Antigravity CLI](https://codelabs.developers.google.com/antigravity-cli-hands-on)
- [OpenCode](https://opencode.ai/docs)
- [Kimi Code CLI](https://www.kimi.com/code/docs/kimi-code-cli/guides/getting-started)
- [DeepSeek API](https://api-docs.deepseek.com/)
- [Deep Code CLI 上游](https://github.com/lessweb/deepcode-cli)
- [WorkBuddy](https://www.workbuddy.cn/)
- [Node.js](https://nodejs.org/en)
- [Python](https://www.python.org/downloads/)

## 致谢

- 本仓库的跨仓依赖：`soia-env-codex-install` 等技能的实际版本审计/更新动作硬依赖 [`soia-open-skills`](https://github.com/soia-team/soia-open-skills) 仓库里的 `soia-dev-ai-cli-upgrade`（详见 [三仓协作](#三仓协作) 里的跨仓硬依赖表），不在本仓库单独重复实现。
- 各 Agent CLI/桌面工具的安装与登录流程均以官方文档为准，具体链接见上方 [官方来源](#官方来源)；本仓库不镜像、不改写供应商自己的安装逻辑。

## 验证与贡献

维护者请先阅读：

- [AGENTS.md](./AGENTS.md)：仓库边界、权限和发布流程；
- [SKILL_SPEC.md](./SKILL_SPEC.md)：技能结构和前言规范；
- [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md)：私密信息、中间数据和清理规范；
- [CONTRIBUTING.md](./CONTRIBUTING.md)：贡献、审计和 PR 流程。

提交前运行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py
python3 scripts/check_readme_coverage.py
git diff --check
```

修改具体技能后，再运行可用的 quick validator，并从推送后的远程仓库做安装验收。许可证为 [MIT](./LICENSE)。

## 维护者

**soia-team** · [GitHub](https://github.com/soia-team)
