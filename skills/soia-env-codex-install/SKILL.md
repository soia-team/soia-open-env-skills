---
name: soia-env-codex-install
description: 面向小白安装并验证 OpenAI Codex CLI：检查 Node.js/npm、从官方文档安装、完成浏览器登录并验证版本与帮助命令。触发：「安装 Codex」「配置 Codex」「Codex 登录」「Codex 命令不存在」。
dependencies:
  hard: [soia-env-node-install]
  optional: [soia-env-network-diagnose]
version: 1.0.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 18:00:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-codex-install

通过官方 npm 包安装 Codex CLI，并把“Node/npm 缺失”“命令不在 PATH”“登录未完成”分开处理。安装和登录可以由 Agent 辅助，但客户只在官方浏览器页面完成授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Codex | 检查 Node/npm、安装官方包、验证命令 | 版本、路径类别和结果 |
| 登录 Codex | 启动官方登录流程 | 可点击的官方授权步骤，不显示密钥 |
| Codex 找不到 | 诊断 PATH、npm 全局目录和 shell | 修复建议或需要确认的变更 |

### 客户如何使用

1. 说“安装 Codex”并说明操作系统；Agent 先检查 Node/npm 和网络。
2. 缺 Node.js 时先调用 `soia-env-node-install`，不要让客户自己猜安装器。
3. 安装前展示包名、来源和可能的 PATH 影响；需要管理员权限时单独确认。
4. Agent 执行安装和无副作用验证；客户在官方登录页面点击授权。

### 依赖与安装

| 依赖 | 类型 | 处理 |
|---|---|---|
| Node.js/npm | 强依赖 | 缺失时先调用 `soia-env-node-install` |
| 网络诊断 | 前置检查 | 失败时先调用 `soia-env-network-diagnose` |
| OpenAI 账号或 API 配置 | 用户授权 | 不读取或索要密钥；由官方登录流程处理 |

官方来源和命令事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 只读检查 `node --version`、`npm --version`、`npm prefix --global` 和 `codex --version`；隐藏用户名、路径和环境变量值。
2. 若 Node/npm 不存在或版本不满足项目要求，停止本技能并交给 Node 安装技能。
3. 通过 npm 安装官方包 `@openai/codex`；不使用未知镜像、全局 shell 脚本或 `curl | bash`。
4. 重新解析 PATH，验证 `codex --version` 与 `codex --help`，记录版本而非完整本地路径。
5. 执行 `codex --login`，把浏览器授权交给客户；不要求客户在终端粘贴 API key。
6. 登录后只做无副作用状态验证；如果登录失败，区分网络、账号权限、组织限制和 PATH 问题。

## 权限与回滚

- npm 全局安装可能写入用户全局目录；优先使用用户级 npm 配置，不默认使用 sudo。
- 不覆盖项目的 `package.json`、锁文件或 Node 版本管理配置。
- 升级前记录旧版本；失败时保留错误证据，不自动卸载或降级。

## 日志与完成回执

```markdown
完成：Codex CLI <已安装/已验证/被阻塞>。

日志摘要：
- started: <Node/npm 检查>
- processed: <安装、PATH、登录检查数量>
- updated: <工具和版本>
- failed: <原因>

验证：
- `node --version`、`npm --version`、`codex --version`、`codex --help`

问题与下一步：
- <浏览器授权、账号权限或无>
```

## 前向测试

用 fake command runner 覆盖 Node 缺失、npm 安装成功、Codex 命令缺失和登录等待四种状态；真实验收必须另行运行版本/帮助检查，不能把 npm 返回 0 当成登录完成。
