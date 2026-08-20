# Configuration（环境变量与私有配置）

脚本用环境变量驱动。需要持久本地配置时放技能专属私有 `config.yml`：

```text
~/.config/soia-skills/soia-env-ai-cli-upgrade/config.yml
SOIA_ENV_AI_CLI_UPGRADE_CONFIG_FILE=<custom-config-path>
```

示例：

```yaml
schema_version: 2
env:
  LOG_DIR: "$HOME/.local/state/soia-env-ai-cli-upgrade/logs"
  TOOLS: "codex,claude,agy"
  NPM_PREFIX: "$HOME/.npm-global"
  CLAUDE_CHANNEL: "preserve"
  AGY_INSTALL: "0"
  AGY_INSTALL_DIR: "$HOME/.local/bin"
```

- 不需要私有配置时可不创建 `config.yml`。
- 配置使用 `schema_version: 2`；脚本优先读新路径，仅在新路径不存在时回退旧位置。
- API key、cookie、session、provider home 只能进私有 `config.yml`、进程环境或
  provider 自己的登录态，不写仓库、vault 正文或日志。
- 第三方 skill 只声明依赖与安装方式，不直接修改第三方 skill 文件。

## 支持的变量

| Variable | Purpose | Default |
|---|---|---|
| `DRY_RUN=1` | 只打印当前版本，不升级 | `0` |
| `TOOLS="codex,claude,agy"` | 限定工具列表 | 消费者安全默认集；`gemini` 须显式 opt-in |
| `NPM_PACKAGES="codex,claude"` | `TOOLS` 的向后兼容别名；`TOOLS` 设置时忽略 | unset |
| `NPM_PREFIX=<path>` | npm 系 CLI 的全局 prefix | `$HOME/.npm-global` |
| `CLAUDE_CHANNEL=preserve\|latest` | 保留已装 Claude Homebrew cask，或显式迁移到 `claude-code@latest` | `preserve` |
| `AGY_INSTALL=1` | 允许从 Google 固定官方 HTTPS 端点安装缺失的 `agy` | `0` |
| `AGY_INSTALL_DIR=<path>` | 原生 `agy` 安装与回退探测目录 | `$HOME/.local/bin` |
| `DSH_TRACK=latest\|next` | dsh 升级轨道；`~/.dsh/profiles` 客户端包在 next 轨道时设 `next` 对齐（防 bootstrap 接口不匹配） | `latest` |
| `DSH_PROFILES_DIR=<path>` | dsh profiles 根目录（一致性检测读客户端版本用） | `$HOME/.dsh/profiles` |
| `LOG_DIR=<path>` | 升级日志目录 | `${TMPDIR:-/tmp}/soia-env-ai-cli-upgrade/logs` |
| `CURSOR_UPGRADE_CMD=<command>` | 可选的 Cursor 更新命令（用户自供代码，须用户明确批准才运行） | unset |

## 日志位置与保留

升级日志定位为**用完即弃**——当次报告看完即无价值，默认落系统临时区
`${TMPDIR:-/tmp}/soia-env-ai-cli-upgrade/logs/`（macOS 的 `$TMPDIR` 约 3 天自动清、
`/tmp` 重启清），同日多次运行由 `LOG_KEEP`（默认 10）轮转防堆积。确需审计追溯
（如排查「哪天升了什么版本导致行为变化」）时设 `LOG_DIR` 改道到持久位置
（如 `~/.local/state/...`）。

## 输出表列语义

| Column | Meaning |
|---|---|
| `TOOL` | 逻辑工具名 |
| `COMMAND` | 实际检查的可执行文件 |
| `OLD` | 升级前版本（dry-run 即当前版本） |
| `NEW` | 升级后版本；dry-run 显示 `N/A` |
| `STATUS` | `INSTALLED` / `UPDATED` / `ALREADY_LATEST` / `NOT_INSTALLED` / `SKIP_DRY_RUN` / `MANUAL` / `FAILED` |
| `NOTE` | 简短原因或下一步动作 |

`agy` 的 `MANUAL` 可能表示安装/更新成功但解析出的二进制目录不在 PATH，或 PATH
解析到了别的二进制；脚本报告解析出的绝对路径，绝不自己改 PATH。
