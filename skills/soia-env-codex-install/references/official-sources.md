# Codex 官方来源（2026-07-20 核对）

- CLI 文档：[Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- 帮助中心入口：[OpenAI Codex CLI – Getting Started](https://help.openai.com/en/articles/11096431)
- 登录说明：[Codex CLI and Sign in with ChatGPT](https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt)
- 官方安装包名：`@openai/codex`
- 官方文档当前给出的 macOS/Linux 独立安装入口：`curl -fsSL https://chatgpt.com/codex/install.sh | sh`
- npm 安装入口：`npm install -g @openai/codex`
- 官方文档给出的登录入口：`codex --login`
- 已安装 CLI 的优先更新入口：`codex update`；独立安装器也可按官方文档重新运行以更新。

## 处理边界

- 当前版本、Node 版本要求、安装方式和登录行为以官方页面与实际 `codex --help` 为准，不把本文件的日期当作永久版本承诺。
- 更新前先识别 `codex` 的来源（自带更新器、独立安装器或 npm），沿用原来源，不把“更新”变成未经确认的换源安装。
- 不把 `OPENAI_API_KEY` 写入仓库、聊天或回执；如客户选择 API key，使用客户自己的安全环境变量并只验证“是否配置”，不打印值。
- 使用 ChatGPT 登录时，客户在官方网页完成授权；Agent 不代点确认、不索要验证码。
