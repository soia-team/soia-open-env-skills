<div align="center">

# soia-open-env-skills

面向小白的环境配置、网络诊断、工具安装与安全维护技能库。

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Agent Agnostic](https://img.shields.io/badge/agents-agnostic-6f42c1.svg)](https://skills.sh/)
[![skills.sh](https://img.shields.io/badge/skills.sh-compatible-00a67d.svg)](https://skills.sh/)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](./requirements-dev.txt)

```bash
npx skills add soia-team/soia-open-env-skills -g --all
```

兼容 Claude Code、Codex、Gemini/Antigravity、OpenCode、Kimi、Qoder 及其他
skills.sh 兼容 Agent。客户不需要先学习终端命令：Agent 负责安全检查和可逆的
安装步骤，客户只在官方页面完成登录、验证码、系统安全提示和服务授权。

[技能清单](#技能清单) · [从哪里开始](#从哪里开始) · [三仓协作](#三仓协作) · [安全边界](#安全边界) · [验证与贡献](#验证与贡献)

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

完整的自动目录见 [skills/README.md](./skills/README.md)。当前发布 14 个技能：

### 环境编排与诊断

| 技能 | 作用 |
|---|---|
| `soia-env-environment-setup` | 从网络到运行时、CLI、桌面工具的分步编排，并输出下游就绪摘要 |
| `soia-env-network-diagnose` | 只读诊断 DNS、HTTPS、代理、证书和官方源可达性 |
| `soia-env-codex-setup-support` | 排查 ChatGPT.app/Codex 桌面能力、独立 CLI、登录、日志写入和磁盘健康 |
| `soia-env-storage-cleanup` | 统计受管目录，生成带过期条件和风险的清理计划，并在授权后安全清理 |

### 基础运行时

| 技能 | 作用 |
|---|---|
| `soia-env-node-install` | 检查、安装和验证 Node.js、npm 与 PATH；默认不主动更新 |
| `soia-env-python-install` | 检查、安装和验证 Python、pip 与虚拟环境；优先 `python -m pip` |

### Agent CLI

| 技能 | 上游/命令 | 首次可用性验证 |
|---|---|---|
| `soia-env-codex-install` | OpenAI / `codex` | `codex --login`，与 ChatGPT.app 分开验证 |
| `soia-env-claude-cli-install` | Anthropic / `claude` | 官方浏览器登录与 `claude doctor` |
| `soia-env-qoder-cli-install` | Qoder / `qodercli` | `/login` 浏览器授权或官方 PAT 流程 |
| `soia-env-antigravity-cli-install` | Google / `agy` | Google 官方登录；不把 `gemini` 当作 `agy` |
| `soia-env-opencode-cli-install` | OpenCode / `opencode` | `opencode auth login` 与 `auth list` |
| `soia-env-kimi-cli-install` | Moonshot / `kimi` | `kimi login` 或 TUI `/login` |
| `soia-env-deepcode-cli-install` | `lessweb/deepcode-cli` / `deepcode` | `~/.deepcode/settings.json` + DeepSeek API 实际验证 |

### 桌面工具

| 技能 | 作用 |
|---|---|
| `soia-env-workbuddy-install` | 通过 WorkBuddy 官方安装包完成安装、签名、启动和登录验证 |

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

例如，Deep Code 首次运行可以创建部分 `~/.deepcode` 运行状态，但不会替客户生成带 API key 的 `settings.json`。客户需要在 [DeepSeek API Keys](https://platform.deepseek.com/api_keys) 创建 key，在本机写入 `~/.deepcode/settings.json`，再由 Agent 完成验证。

## 安装

### 只安装环境编排技能

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-environment-setup -y
```

### 安装全部环境技能

```bash
npx skills add soia-team/soia-open-env-skills -g --all
```

### 查看可安装清单

```bash
npx skills add soia-team/soia-open-env-skills -l --full-depth
```

安装后，最终验收应从已推送的远程仓库执行，而不是把本地目录手工复制到 Agent 目录：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s <skill-name> -y
```

## 三仓协作

三个仓库的职责和安装关系如下：

| 仓库 | 公开边界 | 负责内容 |
|---|---|---|
| [`soia-open-env-skills`](https://github.com/soia-team/soia-open-env-skills) | 公开 | 网络、运行时、桌面工具、Agent CLI 和安全清理 |
| [`soia-open-skills`](https://github.com/soia-team/soia-open-skills) | 公开 | 云盘、知识库、PKM、公开协作工作流 |
| [`soia-private-skills`](https://github.com/soia-team/soia-private-skills) | 私有 | SOIA 内部治理、审计、开发和执行 |

三者共享安装源目录 `~/.agents/skills`，再由同步技能建立其他 Agent 的入口；环境仓库不会自动安装私有技能，也不会把凭据传给下游。典型安装顺序：

```bash
npx skills add soia-team/soia-open-env-skills -g --all
npx skills add soia-team/soia-open-skills -g --all
npx skills add soia-team/soia-private-skills -g --all

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
- [Google Antigravity CLI](https://antigravity.google/docs/cli/install)
- [OpenCode](https://opencode.ai/docs)
- [Kimi Code CLI](https://www.kimi.com/code/docs/en/)
- [DeepSeek API](https://api-docs.deepseek.com/)
- [Deep Code CLI 上游](https://github.com/lessweb/deepcode-cli)
- [WorkBuddy](https://www.workbuddy.cn/)
- [Node.js](https://nodejs.org/en)
- [Python](https://www.python.org/downloads/)

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
git diff --check
```

修改具体技能后，再运行可用的 quick validator，并从推送后的远程仓库做安装验收。许可证为 [MIT](./LICENSE)。
