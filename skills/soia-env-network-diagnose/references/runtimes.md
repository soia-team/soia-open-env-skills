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

来源是本仓各安装技能 `SKILL.md` 的「依赖与安装」表，**不是推测**；上游技能改了依赖，要同步 `scripts/probe_runtimes.py` 里的 `AI_CLIS`。

| AI 工具 | 可用渠道 | 是否硬依赖 Node.js | 依据技能 |
|---|---|---|---|
| Claude Code | 官方独立安装 / npm | 否 | `soia-env-claude-cli-install` |
| Codex CLI | 官方独立安装 / Homebrew / npm | 否 | `soia-env-codex-install` |
| Kimi Code CLI | 官方独立安装 / npm | 否 | `soia-env-kimi-cli-install` |
| Qoder CLI | 官方独立安装 / Homebrew / npm | 否 | `soia-env-qoder-cli-install` |
| OpenCode CLI | 官方独立安装 / Homebrew / npm | 否 | `soia-env-opencode-cli-install` |
| Antigravity CLI | 官方独立安装 | 否 | `soia-env-antigravity-cli-install` |
| WorkBuddy | 官方桌面安装包 | 否 | `soia-env-workbuddy-install` |
| Pi | 仅 npm | **是** | `soia-env-pi-cli-install` |
| Deep Code CLI | 仅 npm，且 Node **≥ 22** | **是** | `soia-env-deepcode-cli-install` |

**反直觉但已核对**：九个目标里七个有官方独立安装渠道，一台没有 node/npm/brew 的裸机照样装得上；只有 Pi 与 Deep Code 把 `soia-env-node-install` 标为 `hard` 依赖。所以「装不上 AI CLI」多数时候不是缺 Node，先别急着装环境。

## 推导规则

- 一个渠道的全部依赖都满足 → 该渠道 `ok`；某个 CLI 只要有一个渠道 `ok` → **可安装**。
- 依赖里有 `timeout` 且没有硬缺失 → 该渠道 `uncertain`，CLI 判 **待复核**，提示放宽超时重跑，不判死。
- 依赖缺失或版本低于门槛 → 该渠道 `blocked`，全部渠道都 blocked 才判 **被阻塞**，并写明具体缺口（例如 `node 18.20.0 < 22`）。

## 边界

- 只盘点运行时是否可用，**不判断 AI CLI 本身是否已安装**——那是各安装技能 `inspect_cli.py` 的职责，本技能不重复实现，也不输出它们的安装状态行。
- 不执行安装、升级、换源或改 PATH；缺什么由对应安装技能处理。
- 不回显命令输出正文、绝对路径（home 折成 `~`）、环境变量和账号信息。
- PATH 决定命中哪个副本：同一工具在系统目录与 Homebrew 下版本可能不同（实测 `git` 2.50.1 与 2.54.0、`bash` 3.2.57 与 5.3.15）。报告的是**当前 PATH 下会被用到的那个**，与安装技能的多副本排查不冲突。
