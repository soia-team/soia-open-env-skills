---
name: soia-env-codex-install
description: 面向小白安装、验证和更新 OpenAI Codex CLI：检查 Node.js/npm、识别安装来源、从官方文档安装或更新、完成浏览器登录并验证版本与帮助命令。触发：「安装 Codex」「更新 Codex」「配置 Codex」「Codex 登录」「Codex 命令不存在」。
dependencies:
  hard: [soia-env-node-install]
  optional: [soia-env-network-diagnose]
version: 1.1.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 21:30:00
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
| 更新 Codex | 识别现有版本和安装来源，沿用原来源更新 | 更新前后版本、验证结果和回滚边界 |
| 登录 Codex | 启动官方登录流程 | 可点击的官方授权步骤，不显示密钥 |
| Codex 找不到 | 诊断 PATH、npm 全局目录和 shell | 修复建议或需要确认的变更 |

### 客户如何使用

1. 说“安装 Codex”并说明操作系统；Agent 先检查 Node/npm 和网络。
2. 缺 Node.js 时先调用 `soia-env-node-install`，不要让客户自己猜安装器。
3. 安装或更新前展示包名、来源、目标版本和可能的 PATH 影响；需要管理员权限时单独确认。
4. Agent 执行安装和无副作用验证；客户在官方登录页面点击授权。

### 依赖与安装

| 依赖 | 类型 | 处理 |
|---|---|---|
| Node.js/npm | 强依赖 | 缺失时先调用 `soia-env-node-install` |
| 网络诊断 | 前置检查 | 失败时先调用 `soia-env-network-diagnose` |
| OpenAI 账号或 API 配置 | 用户授权 | 不读取或索要密钥；由官方登录流程处理 |

官方来源和命令事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 只读检查 `node --version`、`npm --version`、`npm prefix --global`、`codex --version`、`codex update --help` 和 `codex login status`；隐藏用户名、路径和环境变量值。
2. 若 Node/npm 不存在或版本不满足项目要求，停止本技能并交给 Node 安装技能。
3. 缺少 Codex 时，优先按官方 CLI 文档选择官方独立安装器；若当前环境已使用 npm，则安装官方包 `@openai/codex`。不使用未知镜像、未审查的全局 shell 脚本或 `curl | bash`。
4. 重新解析 PATH，验证 `codex --version` 与 `codex --help`，记录版本而非完整本地路径。
5. 执行 `codex --login`，把浏览器授权交给客户；不要求客户在终端粘贴 API key。
6. 登录后只做无副作用状态验证；如果登录失败，区分网络、账号权限、组织限制和 PATH 问题。

## 已安装状态与更新

先判断 Codex 是否已经可用；已安装且验证通过时不要重复安装：

```bash
codex --version
codex update --help
codex login status
command -v codex
npm list -g --depth=0 @openai/codex 2>/dev/null || true
```

- 已安装且登录状态正常：提示“Codex CLI 已安装，无需重复安装”，只在客户要求或检测到新版本时进入更新。
- 支持 `codex update`：在客户确认后执行 `codex update`，这是 CLI 自带的更新路径。
- 由 npm 管理且没有可用的 `codex update`：在客户确认后执行 `npm install -g @openai/codex@latest`。
- 由官方独立安装器管理：按官方 CLI 文档重新运行官方安装入口；不悄悄切换到 npm，也不为了更新删除旧安装。
- 更新后重新执行 `codex --version`、`codex --help` 和 `codex login status`；版本更新不等于登录完成，不强制客户重新登录。

更新前记录旧版本、安装来源和命令路径。更新失败时保留现有可用版本和错误证据，不自动卸载、降级或清理配置。

## 权限与回滚

- npm 全局安装或 CLI 自更新可能写入用户全局目录；优先使用用户级配置，不默认使用 sudo。
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
