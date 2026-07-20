# Codex 官方来源（2026-07-20 核对）

- 安装说明：[OpenAI Codex CLI – Getting Started](https://help.openai.com/en/articles/11096431)
- 登录说明：[Codex CLI and Sign in with ChatGPT](https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt)
- 官方安装包名：`@openai/codex`
- 官方文档给出的安装入口：`npm install -g @openai/codex`
- 官方文档给出的登录入口：`codex --login`

## 处理边界

- 当前版本、Node 版本要求和登录行为以官方页面与实际 `codex --help` 为准，不把本文件的日期当作永久版本承诺。
- 不把 `OPENAI_API_KEY` 写入仓库、聊天或回执；如客户选择 API key，使用客户自己的安全环境变量并只验证“是否配置”，不打印值。
- 使用 ChatGPT 登录时，客户在官方网页完成授权；Agent 不代点确认、不索要验证码。
