# Codex 官方来源（2026-07-20 核对）

- CLI 文档：[Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- 帮助中心入口：[OpenAI Codex CLI – Getting Started](https://help.openai.com/en/articles/11096431)
- 登录说明：[Codex CLI and Sign in with ChatGPT](https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt)
- 官方安装包名：`@openai/codex`
- 官方文档当前给出的 macOS/Linux 独立安装入口：`curl -fsSL https://chatgpt.com/codex/install.sh | sh`
- npm 安装入口：`npm install -g @openai/codex`
- Homebrew cask 安装入口：`brew install --cask codex`
- 官方文档给出的登录入口：`codex --login`
- API key 管理入口（仅客户选择 API key 方式时）：[OpenAI API Keys](https://platform.openai.com/api-keys)
- OpenAI 源码中的 `codex update` 会根据独立 CLI 的安装上下文选择更新动作：npm 使用 `npm install -g @openai/codex`，Homebrew 使用 `brew upgrade --cask codex`，官方独立安装使用官方安装器。
- SOIA 的已安装 CLI 审计和升级统一委托 `soia-dev-ai-cli-upgrade`，不在安装技能里复制更新器。

## 处理边界

- 当前版本、Node 版本要求、安装方式和登录行为以官方页面与实际 `codex --help` 为准，不把本文件的日期当作永久版本承诺。
- 更新前先识别独立 CLI 的来源（官方独立安装器、Homebrew cask 或 npm）。版本检查默认只读；只有客户明确要求“更新到最新版本”时才沿用原来源执行，不把模糊的“更新”变成升级或换源安装。
- `ChatGPT.app/Contents/Resources/codex` 是桌面应用内部组件，OpenAI 源码把 app-bundled binary 归类为 `Other`，不是独立 CLI 安装渠道。ChatGPT.app 与独立 CLI 的版本、安装目录和更新结果必须分开。
- 同机存在多个 `codex` 时，桌面 Agent 进程的 PATH 可能优先出现 ChatGPT.app 内部路径；CLI 检查必须继续查找登录 shell和已知独立安装目录。
- 不把 `OPENAI_API_KEY` 写入仓库、聊天或回执；如客户选择 API key，使用客户自己的安全环境变量并只验证“是否配置”，不打印值。
- 使用 ChatGPT 登录时，客户在官方网页完成授权；Agent 不代点确认、不索要验证码。
