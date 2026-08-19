# Tools Covered（工具通道与默认升级方式）

| Tool | Command | Default upgrade method |
|---|---|---|
| Codex | `codex` | `codex update`（内部自检 native/brew-cask/npm）；安装走官方安装脚本（chatgpt.com/codex 下载审阅后本地执行）、`brew install --cask codex` 或 `npm install -g @openai/codex`；**⚑ npm 通道**：NOTE 列附官方安装器迁移建议 |
| Claude Code | `claude` | 自动检测：native → `claude update`；Homebrew 默认保留已装 cask，授权 `CLAUDE_CHANNEL=latest` 后安全迁移 `claude-code` → `claude-code@latest`（先预取后回滚保护）；npm（legacy）→ `npm install -g @anthropic-ai/claude-code`；Desktop 托管 → 跳过（MANUAL） |
| Antigravity CLI（消费者 Google 账号） | `agy` | Gemini CLI 消费者登录通道的官方后继；native `agy update`；缺失安装需 `AGY_INSTALL=1` 显式授权 |
| Gemini CLI（非消费者通道） | `gemini` | 自动检测：brew formula（`brew install gemini-cli`）→ `brew upgrade <formula>`；npm → `npm install -g @google/gemini-cli`；native → `gemini update`；须 `TOOLS=gemini` 显式 opt-in |
| Qwen Code | `qwen` | 自动检测：brew formula → `brew upgrade`；npm → `npm install -g @qwen-code/qwen-code`；native → `qwen update`；**⚑ npm 通道**：NOTE 列附官方安装器建议 |
| MiniMax CLI | `mmx` | `mmx update`（内部封装 npm）；npm-only：`npm install -g mmx-cli` |
| Kimi Code | `kimi` | 自动检测：Homebrew formula（含相对 `bin` 软链）→ `brew upgrade`；npm → `npm install -g @moonshot-ai/kimi-code`；native → `kimi upgrade`；Homebrew 失败如实报告，不当作已最新 |
| OpenCode | `opencode` | 自动检测：brew formula → `brew upgrade`；npm → `npm install -g opencode-ai`；native → MANUAL（从 opencode.ai/install 下载官方安装器，审阅后本地执行刷新）；**⚑ npm 通道**：NOTE 列附官方安装器建议 |
| Qoder CLI | `qodercli` | `qodercli update` |
| DeepCode Agent CLI | `deepcode` | npm → `npm install -g deepcode`（`@vegamo/deepcode-cli` 已装时更新该包名） |
| DeepSeek Harness | `dsh` | npm → `npm install -g @deepseek-ai/dsh`（官方 scoped 包；裸名 `dsh` 是被占用的无关老包，勿用） |
| Pi (pi-coding-agent) | `pi` | `pi update --self`（npm 包 `@earendil-works/pi-coding-agent`） |
| Cursor | `cursor` | 仅版本审计，除非用户自设 `CURSOR_UPGRADE_CMD` |

## 为什么 agy 与 gemini 两行并存

`agy` 是 Gemini CLI 消费者 Google 登录通道的替代品。`gemini` 行仅用于审计明确受支持的
Standard/Enterprise、API Key 与 Vertex AI 安装形态，已不在默认批次内。

## `~/.opencode/bin` 回退探测

v2.2.0 起对 opencode 增加原生安装目录回退探测：旧 shell 会话 PATH 缺失该目录时
不再误报未安装（2026-08-08 真机实跑发现并修复）。
