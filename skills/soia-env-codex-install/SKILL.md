---
name: soia-env-codex-install
description: 为新手安装、验证或按授权更新 OpenAI Codex CLI。触发：「安装 Codex CLI」「更新 Codex CLI」「Codex 命令不存在」
dependencies:
  hard: [soia-env-ai-cli-upgrade]
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.6.3
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-09 01:40:00
created_by: gpt-5
updated_by: deepseek-v4-flash
---

# soia-env-codex-install

通过官方支持的安装入口安装 Codex CLI，并把“依赖缺失”“命令不在 PATH”“登录未完成”分开处理。安装和登录可以由 Agent 辅助，但客户只在官方浏览器页面完成授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Codex | 检查依赖、安装官方包、验证命令 | Codex CLI 固定状态列表和安装目录 |
| 检查 Codex 更新 | 识别实际生效的 CLI 来源并比较版本，不自动更新 | 当前版本、最新版本和来源 |
| 更新 Codex 到最新 | 客户明确要求最新版后，沿用原来源更新 | 中间状态、更新结果、安装方式和配置目录 |
| 登录 Codex | 启动官方登录流程 | 可点击的官方授权步骤，不显示密钥 |
| Codex 找不到 | 诊断 PATH、npm 全局目录和 shell | 修复建议或需要确认的变更 |

### 客户如何使用

“安装 Codex”只授权安装缺失的独立 CLI，不授权更新已装版本；“检查更新”或模糊的“更新 Codex”只做版本审计并询问是否更新到最新。只有客户明确说“更新 Codex 到最新”“升级到最新版”或同等指令才调用升级执行；管理员权限、切换来源或修改 PATH 仍需单独确认。

### 首次登录与真实配置验证

`配置文件目录`只显示 `CODEX_HOME` 或默认候选路径，必须同时检查 `config_status`，不能把 `~/.codex` 直接当成已登录；未登录时用独立 CLI 同一绝对路径执行 `codex --login`，客户在官方页面完成授权，登录后复核 `login status`/`--version`/`--help`/`config_status`。细则见 [operations.md](references/operations.md)。

### 依赖与安装

| 依赖 | 类型 | 处理 |
|---|---|---|
| `soia-env-ai-cli-upgrade` | CLI 更新依赖 | 统一执行 Codex 版本审计与原渠道更新 |
| Node.js/npm | npm 渠道依赖 | 仅 npm 安装或更新需要；缺失时调用 `soia-env-node-install` |
| 网络诊断 | 前置检查 | 失败时先调用 `soia-env-network-diagnose` |
| OpenAI 账号或 API 配置 | 用户授权 | 不读取或索要密钥；由官方登录流程处理 |

缺少 CLI 升级技能时，从本环境技能库安装：

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-env@soia
```

只要这一个技能时，可用 npx 路线。注意技能会落进共享真源 `~/.agents/skills`；若同时装了插件，同一技能会出现两份索引且各自漂移，建议二选一：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-codex-install -y
```

官方来源和命令事实见 [official-sources.md](references/official-sources.md)。

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### 私密信息与中间数据

- Codex 登录凭据由官方 `codex login`/浏览器授权流程和系统凭据库管理；SOIA 配置只保存非秘密偏好与路径。
- 安装或更新回执如需追溯，只在用户 state 目录保存脱敏后的来源、版本、结果和时间；只读检查默认不落盘；不记录授权码、token、账号、会话或客户私有绝对路径。
- 版本元数据可放 cache，安装器和解压内容放每次运行独立的系统临时目录并在成功或失败后清理；不读取或复制凭据内容。

### 日志与完成回执

最终回执 = 固定十列客户状态列表 + 已验证的命令类别 + 是否需要浏览器授权 + 失败时可恢复的原版本；`更新时间` 在最终验证后生成，正常依赖不展开为额外行。模板见 [operations.md](references/operations.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_installation.py --json`，查找独立 Codex CLI 并记录版本、安装方式、安装目录、命令路径和配置目录是否真实存在；将 `ChatGPT.app/Contents/Resources/codex` 视为桌面应用内部组件，不把它当作独立 Codex CLI，即使 PATH 优先命中它也要继续查找登录 shell、npm、Homebrew 和官方独立安装路径。
2. 缺少独立 CLI 时 macOS/Linux 优先官方独立安装入口；仅客户明确选 npm 或机器原用 npm 渠道时，才要求 Node.js/npm 并安装 `@openai/codex`。
3. 已安装 CLI 默认只执行 dry-run 版本审计，只选择 Codex：

   ```bash
   TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
   ```

4. dry-run 发现新版本先报“可更新，未执行”；仅客户明确要求更新到最新才去掉 `DRY_RUN=1`，由 `soia-env-ai-cli-upgrade` 调用 `codex update` 并复核 `--version`/`--help`/`login status`。
5. 未登录时执行独立 CLI 的 `login` 流程，把浏览器授权交给客户；用下方固定列表输出结果，正常时不增加 Node.js、npm、ChatGPT 桌面版或其他技能行。

完整九步见 [operations.md](references/operations.md)。

## 客户状态列表（强制）

客户可见回复必须以以下固定十列表格开头，只输出一行 `Codex CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Codex CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <npm 全局安装/Homebrew cask/官方独立安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <无需更新/可更新，未执行/等待确认是否更新到最新/已更新/等待安装/被阻塞：原因> |

- 安装请求只授权安装缺失的 CLI，不授权更新现有 CLI；用户只问 Codex CLI 时，不增加 Node.js、npm、ChatGPT 桌面版或其他技能行。
- 安装目录和配置目录优先显示 `~` 相对路径；`config_status=未创建` 或 `login_status=未登录` 时写“等待首次登录”；其余规则见 [operations.md](references/operations.md)。

## 已安装状态与更新

先判断独立 Codex CLI 是否已经可用及实际来源（npm 全局、Homebrew cask、官方独立安装，或 ChatGPT.app 内部组件——后者不进入 CLI 状态行）；已安装且验证通过时不重复安装，更新统一委托 `soia-env-ai-cli-upgrade`。细则见 [operations.md](references/operations.md)。

## 安装与更新的中间状态

真正执行安装或获得最新版授权的更新时，生成随机 `run_id`，并在每个阶段发生时立即运行 `scripts/record_install_progress.py`（`checking → planning → [waiting_confirmation] → installing/updating → verifying → completed/failed/blocked`）；不得在结束后补写整段历史，只读检查不运行记录器。

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

`--customer-requested-latest` 只能在客户原话明确要求最新版时传入；记录器拒绝缺少该声明的更新执行阶段。命令样例见 [operations.md](references/operations.md)。

## 权限与回滚

- npm 全局安装或 CLI 自更新可能写入用户全局目录；优先用户级配置，不默认使用 sudo。
- 升级前记录旧版本；失败时保留错误证据。

## 不负责什么（能力边界）

- **不代客户完成登录与授权**：浏览器授权、API key 创建都由客户在 OpenAI 官方页面完成；Agent 不读取、不接收、不回显任何凭据。
- **默认不更新已装版本**：“安装 Codex”只授权安装缺失的 CLI；更新需要“更新到最新版本”级别的明确表述。
- **不动系统**：不默认使用 sudo，不覆盖项目的 `package.json`、锁文件或 Node 版本管理配置；失败时不自动卸载、降级或清理配置。
- **不更新桌面应用**：ChatGPT.app 是桌面应用，版本和更新渠道与独立 CLI 分开。

## 前向测试

用 fake command runner 覆盖安装成功、独立 CLI 缺失、只存在 ChatGPT.app 内部二进制、npm 全局安装和存在新版本；验证来源识别与 `scripts/render_status.py` 的固定十列。
