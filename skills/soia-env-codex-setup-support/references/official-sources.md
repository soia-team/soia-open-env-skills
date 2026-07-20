# Codex 官方来源

本文件只记录公开、可复核的入口；下载地址和产品可用范围可能变化，执行时应重新打开官方页面确认。

## CLI

- 当前 CLI 文档：<https://learn.chatgpt.com/docs/codex/cli>
- Codex CLI 安装与升级说明：<https://help.openai.com/en/articles/11096431>
- Codex CLI 使用 ChatGPT 登录：<https://help.openai.com/en/articles/11381614-api-codex-cli-and-sign-in-with-chatgpt>
- 官方 npm 包：<https://www.npmjs.com/package/@openai/codex>

当前文档中的核心命令是：

```bash
npm install -g @openai/codex
codex --login
codex --version
codex --help
codex update
```

当前官方 CLI 文档还给出 macOS/Linux 独立安装入口：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

安装或更新前先识别 CLI 来源（自带更新器、官方独立安装器或 npm），沿用原来源，不把更新静默变成换源安装。执行网页上的安装命令前应先打开官方页面核对内容；不使用未知镜像或未审查脚本。

## 桌面版

- OpenAI Codex app 介绍：<https://openai.com/index/introducing-the-codex-app/>
- ChatGPT 桌面应用迁移说明：<https://help.openai.com/en/articles/20001276-moving-to-the-new-chatgpt-desktop-app>
- Codex 产品页：<https://openai.com/codex/for-work/>

Codex 桌面能力与 ChatGPT 桌面应用是同一官方应用体系，不能要求用户寻找独立的 `Codex.app`。macOS 识别时优先核对 `ChatGPT.app` 的 bundle id `com.openai.codex`、版本和代码签名。桌面版的下载、迁移和系统支持以打开页面时显示的官方信息为准；技能不写死第三方镜像或临时安装包地址。

## 日志写放大问题的上游记录

这些页面用于核对修复版本和原始问题，不替代本机只读测量：

- GitHub issue #28224：<https://github.com/openai/codex/issues/28224>
- Codex 0.142.0 release：<https://github.com/openai/codex/releases/tag/rust-v0.142.0>
- Codex 0.143.0 release：<https://github.com/openai/codex/releases/tag/rust-v0.143.0>
- PR #29432：<https://github.com/openai/codex/pull/29432>
- PR #29457：<https://github.com/openai/codex/pull/29457>
- PR #29599：<https://github.com/openai/codex/pull/29599>

路由规则：版本信息只作为“应该先更新”的依据；是否仍在本机复现，必须由数据库文件/WAL 两次快照、`MAX(id)`/`sqlite_sequence` 速率和热点 target 共同确认。

## 前置运行时与网络

- Node.js 官方下载：<https://nodejs.org/en>
- npm 官方文档：<https://docs.npmjs.com/>
- 网络诊断所需的官方站点清单见上级技能 `soia-env-network-diagnose/references/providers.md`。
