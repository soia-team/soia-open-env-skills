# 本机运行时清单

网络通不代表装得上。这份清单回答另一半问题：**这台机器现在能装哪些 AI 工具、缺什么、先补什么。**
执行 `python3 scripts/probe_runtimes.py`（加 `--json` 给下游技能消费）。脚本只读，只跑固定白名单里的版本查询命令，不安装、不改配置、不接受任意命令。

## 版本命令按工具适配，不能统一写 `--version`

下表是真机实测结论，不是文档摘抄。统一 `--version` 会在这几处直接判错：

| 工具 | 实测行为 | 脚本的处理 |
|---|---|---|
| `go` | `go --version` 退出码 2（`flag provided but not defined: -version`） | 固定用 `go version` |
| `java` | 版本写进 **stderr**，stdout 为空 | stdout 为空时才回退读 stderr |
| `rustc` | 是指向 `rustup` 的软链，**首次调用可能超过 10s**，二次约 0.08s | 单列 `timeout` 状态，不算作「未安装」 |
| `unzip` | 没有长参数 | 固定用 `-v` |
| `rustup` | stdout 有版本，stderr 另有 `info:` 噪音 | 优先 stdout，避免读到噪音行 |
| `wget` / `bash` | 输出按系统语言本地化（中文） | 用数字版本号正则，不匹配英文关键词 |
| `pip3` | 输出带 `site-packages` 绝对路径 | 只留版本号，路径中的 home 折成 `~` |
| `python` | macOS 上通常不存在，只有 `python3` | 白名单只收 `python3` |

**超时不等于缺失。** 这与网络侧「阿里云镜像站默认 5s 超时会误报」是同一类坑：报 `timeout` 时应放宽 `--timeout` 复核，不能直接判成没装。

## 分类清单

| 类别 | 收录 |
|---|---|
| Node.js 运行时 | `node` `npm` `npx` `pnpm` `yarn` `bun` |
| Python 运行时 | `python3` `pip3` `uv` `pipx` |
| Rust 工具链 | `rustc` `cargo` `rustup` |
| Go 工具链 | `go` |
| JVM 运行时 | `java` |
| 系统与包管理器 | `brew` `git` `curl` `wget` `unzip` `tar` |
| Shell | `bash` `zsh` |

状态取值：`available`（拿到版本）、`absent`（PATH 里没有）、`timeout`（找到但版本查询超时）、`exec_failed`（执行失败）、`version_unreadable`（跑通但解析不出版本）。

## AI CLI 渠道依赖

渠道来源是本仓各安装技能 `SKILL.md` 的「依赖与安装」表，Node 版本门槛来源是各技能
`references/official-sources.md` 的「已核对事实」段——**都不是推测**。上游技能改了依赖或版本，
要同步 `scripts/probe_runtimes.py` 里的 `AI_CLIS` 和对应断言。

| AI 工具 | 可用渠道 | npm 渠道的 Node 门槛 | 是否硬依赖 Node.js | 依据技能 |
|---|---|---|---|---|
| Claude Code | 官方独立安装 / npm | **≥ 22** | 否 | `soia-env-claude-cli-install` |
| Codex CLI | 官方独立安装 / Homebrew / npm | 未核对到具体版本 | 否 | `soia-env-codex-install` |
| Kimi Code CLI | 官方独立安装 / npm | **≥ 22.19** | 否 | `soia-env-kimi-cli-install` |
| Qoder CLI | 官方独立安装 / Homebrew / npm | **≥ 20** | 否 | `soia-env-qoder-cli-install` |
| OpenCode CLI | 官方独立安装 / Homebrew / npm | 未核对到具体版本 | 否 | `soia-env-opencode-cli-install` |
| Antigravity CLI | 官方独立安装 | 不适用 | 否 | `soia-env-antigravity-cli-install` |
| WorkBuddy | 官方桌面安装包 | 不适用 | 否 | `soia-env-workbuddy-install` |
| Pi | 仅 npm | 未核对到具体版本 | **是** | `soia-env-pi-cli-install` |
| Deep Code CLI | 仅 npm | **≥ 22** | **是** | `soia-env-deepcode-cli-install` |

「未核对到具体版本」表示**仓内尚无已核对事实**，不表示「没有版本要求」——Codex 的
`official-sources.md` 明确写了以官方页面与实际 `codex --help` 为准。这类目标不做版本判定，
不要在这里凭印象填一个版本号；补齐要先由对应安装技能核对并写进它的 `official-sources.md`。

**反直觉但已核对**：九个目标里七个有官方独立安装渠道，一台没有 node/npm/brew 的裸机照样装得上；
只有 Pi 与 Deep Code 把 `soia-env-node-install` 标为 `hard` 依赖。所以「装不上 AI CLI」多数时候不是缺 Node，
先别急着装环境。**但反过来也成立**：Node 版本太旧时被挡掉的只是 npm 渠道，官方独立安装照样能用——
实测一台 Node 20.19.0 的机器，Claude Code 与 Kimi Code 的 npm 渠道被挡，整体仍判「可安装」；
只有没有兜底渠道的 Deep Code 真被阻塞。

## OS 与架构

输出里的 `host` 段（`os` / `arch` / `os_version`）只作为**事实上报**，本技能不判断某个 CLI 是否支持该平台。

多个安装技能把「官方支持的操作系统/架构」列为强依赖，但支持矩阵在各家官方清单里
（例如 Antigravity 由自己的 `check_latest.py` 从 Google 平台清单实时拉取），仓内没有静态真源。
在这里维护一张矩阵等于造事实，也必然过期。平台是否受支持由对应安装技能判定，本技能只提供输入。

## 推导规则

- 一个渠道的全部依赖都满足 → 该渠道 `ok`；某个 CLI 只要有一个渠道 `ok` → **可安装**。
- 依赖里有 `timeout` 且没有硬缺失 → 该渠道 `uncertain`，CLI 判 **待复核**，提示放宽超时重跑，不判死。
- 依赖缺失或版本低于门槛 → 该渠道 `blocked`，全部渠道都 blocked 才判 **被阻塞**，并写明具体缺口（例如 `node 18.20.0 < 22`）。

## 边界

- 只盘点运行时是否可用，**不判断 AI CLI 本身是否已安装**——那是各安装技能 `inspect_cli.py` 的职责，本技能不重复实现，也不输出它们的安装状态行。
- 不执行安装、升级、换源或改 PATH；缺什么由对应安装技能处理。
- 不回显命令输出正文、绝对路径（home 折成 `~`）、环境变量和账号信息。
- PATH 决定命中哪个副本：同一工具在系统目录与 Homebrew 下版本可能不同（实测 `git` 2.50.1 与 2.54.0、`bash` 3.2.57 与 5.3.15）。报告的是**当前 PATH 下会被用到的那个**，与安装技能的多副本排查不冲突。

## 真机复跑样例（两种受限环境）

同机把 PATH 收窄到 `/usr/bin:/bin`（模拟没有 node/npm/brew 的裸机）复跑，结论变为：Claude Code、Codex CLI、Kimi Code CLI、Qoder CLI、OpenCode CLI、Antigravity CLI、WorkBuddy 七项仍判「可安装」（走官方独立安装渠道），只有 Pi 与 Deep Code CLI 判「被阻塞 — npm 全局安装：缺 node、缺 npm」。**缺 Node 不等于装不了 AI CLI**，多数目标有官方独立安装渠道，先别急着装环境。

再把 node 换成 20.19.0 复跑，版本门槛按各技能核对过的要求分道：Qoder CLI 的 npm 渠道保留（要求 ≥ 20），Claude Code（≥ 22）与 Kimi Code CLI（≥ 22.19）的 npm 渠道被摘掉但仍可走官方独立安装，只有没有兜底渠道的 Deep Code CLI 判「被阻塞 — node 20.19.0 < 22」。**版本不够挡掉的是渠道，不一定是这个工具。**
