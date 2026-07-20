---
name: soia-env-node-install
description: 面向小白安装、验证和更新 Node.js 与 npm：识别系统和架构，默认选择官方 Active LTS，诊断 PATH/npm 全局目录，并用固定六列列表汇报目标工具状态。触发：「安装 Node」「更新 Node」「安装 npm」「node 命令不存在」「npm 超时」。
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.2.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 22:30:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-node-install

优先使用 Node.js 官方 LTS 安装路径，并把“未安装、装了但 PATH 找不到、npm 源/权限问题、项目版本不匹配”分别诊断。不要在同一台机器上无计划地混用多个版本管理器。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Node.js | 识别系统/架构、选择官方 LTS、安装并验证 | Node/npm 版本和路径状态 |
| 更新 Node.js | 识别安装来源、比较项目约束与最新 Active LTS | 更新计划、版本变化和回滚边界 |
| npm 不可用 | 检查 PATH、npm prefix 和权限 | 阻塞原因与安全修复方案 |
| 为 Codex 准备环境 | 先验证 Node/npm，再交给 Codex 技能 | 可继续执行的 readiness 状态 |

### 客户如何使用

1. 说目标项目、操作系统和是否需要特定 Node 大版本；不确定时默认选择最新官方 Active LTS，不固定写死一个永久版本号。
2. Agent 先检查现有 `node`、`npm` 和项目配置，不自动卸载旧版本。
3. 展示安装来源、版本和 PATH 影响；需要管理员权限时单独确认。
4. 安装后验证 `node --version`、`npm --version` 和一个无副作用的帮助命令。

### 依赖与安装

无必需外部 skill。网络问题先调用 `soia-env-network-diagnose`；Codex 需要 Node/npm 时由 `soia-env-codex-install` 消费本技能的结果。官方来源见 [official-sources.md](references/official-sources.md)。

## 默认版本策略

- 默认目标是 Node.js 官方最新 Active LTS；生产或长期维护项目不默认选择 Current 版本。
- 先读取 `.nvmrc`、`package.json` 的 `engines`、CI 配置和项目文档；项目约束优先于全局默认值。
- 当前已安装的 Current 版本不等于错误。若项目兼容且客户没有要求切换，不自动降级；回执中明确写出“已安装但不是默认 LTS”。
- 当前版本、LTS 状态和下载入口以 [Node.js Releases](references/official-sources.md) 为准。

## 已安装状态与更新

先判断来源，再更新；不把不同安装方式混在一起：

```bash
node --version
npm --version
command -v node
brew list --versions node 2>/dev/null || true
command -v nvm 2>/dev/null || true
```

- 已安装且满足项目约束：提示“Node.js 已安装，无需重复安装”，继续验证 npm、PATH 和项目版本。
- 已安装但为 Current：提示“已安装，当前不是默认 Active LTS”；是否切换由客户或项目约束决定，不自动降级。
- Homebrew 管理：客户确认后执行 `brew update && brew upgrade node`。
- nvm 管理：客户确认后执行 `nvm install --lts && nvm alias default 'lts/*' && nvm use --lts`；不同时再引入 Homebrew 或官方安装器。
- 官方安装器管理：从 Node.js 官方下载页取得目标 LTS 安装器覆盖更新，安装前记录现有版本和 PATH 状态。

更新后重新加载 shell，再验证 `node --version`、`npm --version`、`npm config get prefix` 和项目版本约束。失败时保留旧版本，不自动卸载或清理。

## 标准流程

1. 只读检查 OS、架构、现有版本、PATH 是否含可执行文件和项目的 `.nvmrc`/`package.json` 版本要求；不打印完整环境变量。
2. 选择官方 LTS 安装器或官方认可的版本管理方式；一次只选择一种方法并记录。
3. 安装前确认下载源和权限；禁止未知镜像、修改 TLS 校验或 `curl | bash`。
4. 安装后重新解析 PATH；若需改 shell profile，先显示目标文件和追加内容并确认。
5. 验证 `node --version`、`npm --version`、`npm config get prefix`，并用 `npm --version` 作为最小 npm 健康检查。
6. 输出 `ready|missing|update_available|blocked` 和版本，交给上层环境编排或 Codex 技能。
7. 使用下方固定列表向客户汇报；只显示客户要求的目标工具。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |
|---|---|---|---|---|---|
| Node.js | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <无需重复安装/可更新/等待确认后安装/被阻塞：原因> |

- 用户只问 Node.js 时只输出 `Node.js` 行，不额外输出 npm；用户明确问 npm 时才增加 `npm` 行。
- 最新版本按项目约束与官方 Active LTS 判断；无法取得时写“未取得”，不猜测。
- 表格后只保留必要的权限确认、PATH 影响或阻塞说明，不展示内部探测流水账。

## 权限与回滚

- 默认用户级安装；不主动使用 sudo 或管理员权限。
- 不删除旧 Node，不改项目锁文件，不全局安装业务依赖。
- 版本冲突时保留现状并请求选择；失败时提供官方卸载/修复路径，而不是自动清理。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |
|---|---|---|---|---|---|
| Node.js | <状态> | <当前版本> | <最新版本> | <运行状态> | <处理结果> |
```

## 前向测试

用 fixture 覆盖 Node 已有、Node 缺失、PATH 不一致和项目要求冲突；真实验收必须分别执行 Node 和 npm 版本检查。
