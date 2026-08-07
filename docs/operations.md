# SOIA Open Env Skills · 操作细则

本文件收纳原先挤在 README 里的操作细节。README 只做导航与入口，
这些内容按需查阅——它们更新频率低，但真要用时需要完整。

[← 返回 README](../README.md)

---

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

从 15 个技能里挑 5 个最能代表不同工作方式的技能，各给一个最小示例和典型输出，降低第一次使用的上手门槛。

### soia-env-environment-setup

从零编排环境的入口，只负责判断顺序和汇总下游技能的结果，不重复实现具体安装逻辑。

```text
帮我把这台电脑准备好使用 Codex
从零配置开发环境
```

**典型输出**：先给出固定列（技能/当前状态/当前版本/最新版本/运行状态/更新时间/处理结果）的客户状态列表，逐个目标一行；表格之后附一份不含秘密的 YAML 摘要（`schema_version`、`os`、`arch`、`tools`、`network`、`blockers`、`next_handoff`），供 `soia-open-skills` 等下游技能消费。

### soia-env-network-diagnose

只读诊断，任何安装类技能卡住时的第一站；不修改代理、DNS、证书或防火墙，也不安装任何运行时。分两侧：网络侧判断外面连不连得上，本机侧判断缺不缺运行时。

```bash
# 网络侧
python3 scripts/probe_endpoints.py --url https://nodejs.org/en --url https://www.python.org/downloads/ --json
# 本机侧：分类盘点运行时并推导可安装的 AI CLI
python3 scripts/probe_runtimes.py --json
```

**典型输出**：固定七列状态表，`处理结果` 明确写“可以继续安装”或“需要处理：<错误类别>”；错误类别限定在 `dns_failed`/`tls_failed`/`timeout`/`http_error`/`proxy_required`/`reachable` 之内，不做“网络整体不可用”这种一次探测就下的断言。

### soia-env-codex-install

区分“ChatGPT.app 桌面版”和“独立 Codex CLI”，是本仓库里状态边界体现得最完整的一个技能。

```bash
python3 scripts/inspect_installation.py --json
TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
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

### 技能硬依赖

本仓库的技能大多互相独立；AI CLI 批量升级技能收编后，现有 hard 依赖均位于本仓库内：

| 本仓库技能 | 硬依赖 | 依赖位置 | 用途 |
|---|---|---|---|
| `soia-env-codex-install` | `soia-env-ai-cli-upgrade` | 本仓库内 | 统一执行 Codex 版本审计与原渠道更新；单工具安装技能不重复实现升级逻辑 |
| `soia-env-environment-setup` | `soia-env-network-diagnose` | 本仓库内 | 编排开始前先确认网络可达性 |
| `soia-env-deepcode-cli-install` | `soia-env-node-install` | 本仓库内 | Deep Code CLI 要求 Node.js 22+ |

`soia-env-codex-install` 发现本机缺少 `soia-env-ai-cli-upgrade` 时，会提示从本仓库单独安装：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-ai-cli-upgrade -y
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

