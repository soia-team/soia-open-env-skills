---
name: soia-env-codex-install
description: 为新手安装、验证或按授权更新 OpenAI Codex CLI。触发：「安装 Codex CLI」「更新 Codex CLI」「Codex 命令不存在」
dependencies:
  hard: [soia-env-ai-cli-upgrade]
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.6.1
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-27 10:47:17
created_by: gpt-5
updated_by: gpt-5.6-sol
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

其他可识别说法包括「更新 Codex 到最新」「配置 Codex」「Codex 登录」；桌面版打不开、性能或磁盘问题交给 `soia-env-codex-setup-support`。

1. 说“安装 Codex”并说明操作系统；Agent 先检查系统、网络和已有 CLI 来源。
2. 官方独立安装不要求 Node.js；只有选择或沿用 npm 渠道时，缺 Node.js/npm 才调用 `soia-env-node-install`。
3. “安装 Codex”只授权安装缺失的独立 CLI，不授权更新已经存在的 CLI；“检查更新”或模糊的“更新 Codex”只做版本审计并询问是否更新到最新。
4. 只有客户明确说“更新 Codex 到最新”“升级到最新版”或同等指令，才调用升级执行；管理员权限、切换来源或修改 PATH 仍需单独确认。
5. 安装/更新过程中 Agent 持续展示阶段状态并写入私有进度记录；客户只在官方登录页面点击授权。

### 首次登录与真实配置验证

- `配置文件目录`只显示 `CODEX_HOME` 或默认候选路径；技能必须同时检查 `config_status`，不能把 `~/.codex` 直接当成已登录。
- 如果独立 CLI 未登录，Agent 使用同一绝对路径执行 `codex --login`；客户点击官方页面的 “Sign in with ChatGPT” 完成授权，不需要客户申请或粘贴 API key。该流程会在本地保存凭据。
- 如果客户明确选择传统 API key 方式，客户在 [OpenAI API Keys](https://platform.openai.com/api-keys) 创建并通过客户自己的安全环境注入；Agent 不读取、不接收、不回显密钥。
- 登录后再次运行 `login status`、`--version`、`--help`，并复查 `config_status`；没有完成授权时处理结果写“等待首次登录”，不能只写“已安装”。ChatGPT.app 的登录状态仍与 CLI 分开。

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
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-ai-cli-upgrade -y
```

官方来源和命令事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 先执行 `python3 scripts/inspect_installation.py --json`，查找独立 Codex CLI，并记录版本、安装方式、安装目录、命令路径和配置目录是否真实存在。
2. 将 `ChatGPT.app/Contents/Resources/codex` 视为桌面应用内部组件，不把它当作独立 Codex CLI；即使当前 Agent 进程的 PATH 优先命中它，也要继续查找登录 shell、npm、Homebrew 和官方独立安装路径。
3. 缺少独立 CLI 时，macOS/Linux 优先使用 OpenAI 官方独立安装入口；只有客户明确选择 npm，或机器原来就采用 npm 渠道时，才要求 Node.js/npm 并安装 `@openai/codex`。
4. 已安装 CLI 默认只执行 dry-run 版本审计，只选择 Codex：

   ```bash
   TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
   ```

5. dry-run 发现新版本时先汇报“可更新，未执行”。客户只说“更新”时停下来询问；只有客户明确要求更新到最新，才去掉 `DRY_RUN=1` 执行升级。
6. 不自行复制另一套更新决策。得到最新版授权后，`soia-env-ai-cli-upgrade` 负责调用 `codex update`，由 Codex 根据独立 CLI 的安装上下文选择 npm、Homebrew cask 或官方独立安装器。
7. 更新后再次执行本技能的检查脚本，并使用返回的独立 CLI 绝对路径验证 `--version`、`--help` 和 `login status`。只有同一独立 CLI 更新并验证通过时，处理结果才写“已更新”。
8. 未登录时执行独立 CLI 的 `login` 流程，把浏览器授权交给客户；不要求客户在终端粘贴 API key。
9. 使用下方固定列表输出结果；依赖检查只在内部使用，正常时不向客户增加 Node.js、npm、ChatGPT 桌面版或其他技能行。

## 客户状态列表（强制）

客户可见回复必须以以下 Markdown 表格开头，列名和顺序固定，只输出一行 `Codex CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Codex CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <npm 全局安装/Homebrew cask/官方独立安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <无需更新/可更新，未执行/等待确认是否更新到最新/已更新/等待安装/被阻塞：原因> |

输出规则：

- 用户只问 Codex CLI 时，不增加 Node.js、npm、ChatGPT 桌面版或其他技能行。
- `更新时间` 记录独立 CLI 的来源、版本和无害运行验证完成后的时间。
- Node.js/npm 检查正常时不展示；仅当它们阻塞 Codex CLI 安装时，把原因压缩写入 `处理结果`。
- `soia-env-ai-cli-upgrade` 返回 `ALREADY_LATEST` 且验证通过：`处理结果` 写“已是最新”。
- `soia-env-ai-cli-upgrade` 返回 `UPDATED` 且复核成功：`处理结果` 写“已更新”。
- dry-run 发现新版本但没有最新版授权：`处理结果` 写“可更新，未执行”；模糊更新请求写“等待确认是否更新到最新”。
- 安装请求只授权安装缺失的 CLI，不授权更新现有 CLI；管理员权限、切换来源、修改 PATH 或更新桌面应用需要客户操作时，明确显示下一步。
- 未安装：`运行状态` 写“未验证”，`处理结果` 写“等待安装”或具体阻塞原因；仅发现 ChatGPT.app 内部二进制仍属于独立 CLI 未安装。
- 无法取得最新版本时写“未取得”，不要用旧缓存、记忆或猜测填充。
- 安装目录和配置目录优先显示 `~` 相对路径，避免暴露用户名；配置文件目录使用 `CODEX_HOME`，未设置时为 `~/.codex`。
- 多个独立 Codex CLI 同时存在时，优先汇报登录 shell 实际解析到的独立副本；桌面 Agent 进程额外注入的 ChatGPT.app 内部路径不能覆盖该判断。
- `config_status=未创建` 或 `login_status=未登录` 时，处理结果写“等待首次登录”，并给出 `codex --login`；不得只显示 `~/.codex` 这个默认路径。
- 表格后仅在需要浏览器授权、管理员确认或错误说明时追加简短下一步；不要回显内部依赖检查流水账。

为保证格式稳定，优先使用 `scripts/render_status.py` 生成表格。

## 已安装状态与更新

先判断独立 Codex CLI 是否已经可用及实际来源；已安装且验证通过时不要重复安装：

```bash
python3 scripts/inspect_installation.py --json
TOOLS=codex DRY_RUN=1 \
  bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
```

- ChatGPT.app：是桌面应用，版本和更新渠道与独立 CLI 分开；其内部 `codex` 不进入本技能的 CLI 状态行。
- npm 全局安装：安装目录显示全局 `node_modules/@openai/codex`；升级交给 `soia-env-ai-cli-upgrade`。
- Homebrew cask 或官方独立安装：显示独立 CLI 的真实目录；升级同样交给 `soia-env-ai-cli-upgrade`。
- 已安装且登录状态正常：`当前状态` 始终写“已安装”；更新动作只写入 `处理结果`。
- 未取得客户“更新到最新”的明确指令时，到 dry-run 和版本汇报为止，不执行升级命令。
- 更新后使用检查脚本返回的 `cli_path` 执行 `--version`、`--help` 和 `login status`；不要使用未限定路径的 `codex` 重新引入 App/CLI 混淆。

更新前记录旧版本、安装来源和命令路径。更新失败时保留现有可用版本和错误证据，不自动卸载、降级或清理配置。

## 安装与更新的中间状态

真正执行安装或获得最新版授权的更新时，生成一个随机 `run_id`，并在每个阶段发生时立即运行 `scripts/record_install_progress.py`：执行检查前记录 `checking`，形成方案后记录 `planning`，需要额外权限或换源时记录 `waiting_confirmation`，调用安装器/更新器前记录 `installing`/`updating`，随后记录 `verifying` 和终态。不得在结束后补写整段历史；时间由记录器生成。只读检查不运行记录器。

```bash
python3 scripts/record_install_progress.py --run-id <run-id> --action <install|update> --stage checking --status in_progress --result-code checking_started
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage updating --status in_progress --result-code update_started --customer-requested-latest
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage verifying --status in_progress --result-code verification_started --customer-requested-latest
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage completed --status completed --result-code operation_completed --customer-requested-latest
```

同时在对话中持续更新，不得只在结束时输出：

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

任何失败或取消都立即追加 `failed` 或 `blocked` 终态。`--customer-requested-latest` 只能在客户原话明确要求最新版时传入；记录器拒绝缺少该声明的更新执行阶段。记录中不保存完整命令、token、账号、私有绝对路径或带查询参数的 URL，也不向客户输出记录文件的绝对路径。

## 权限与回滚

- npm 全局安装或 CLI 自更新可能写入用户全局目录；优先使用用户级配置，不默认使用 sudo。
- 不覆盖项目的 `package.json`、锁文件或 Node 版本管理配置。
- 升级前记录旧版本；失败时保留错误证据，不自动卸载或降级。

## 私密信息与中间数据

- Codex 登录凭据由官方 `codex login`/浏览器授权流程和系统凭据库管理；SOIA 配置只保存非秘密偏好与路径。
- 安装或更新回执如需追溯，只在用户 state 目录保存脱敏后的来源、版本、结果和时间；只读检查默认不落盘。
- 版本元数据可放 cache，安装器和解压内容放每次运行独立的系统临时目录并在成功或失败后清理。
- 不读取或复制凭据内容，不记录授权码、token、账号、会话或客户私有绝对路径。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Codex CLI | <状态> | <当前版本> | <最新版本> | <运行状态> | <安装方式> | <安装目录> | <配置文件目录> | <RFC3339-with-timezone> | <处理结果> |
```

## 前向测试

用 fake command runner 覆盖安装成功、独立 CLI 缺失、只存在 ChatGPT.app 内部二进制、npm 全局安装和存在新版本；验证来源识别与 `scripts/render_status.py` 的固定十列。升级行为由 `soia-env-ai-cli-upgrade` 自己的测试覆盖；本技能只验证委托、独立 CLI 复核和客户状态映射。

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。
