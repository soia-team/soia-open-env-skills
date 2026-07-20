---
name: soia-env-node-install
description: 面向小白安装并验证 Node.js 与 npm：识别系统和架构，优先官方 LTS 来源，诊断 PATH/npm 全局目录，并为 Codex 或 Node 项目准备可复现环境。触发：「安装 Node」「安装 npm」「node 命令不存在」「npm 超时」。
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.0.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 18:00:00
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
| npm 不可用 | 检查 PATH、npm prefix 和权限 | 阻塞原因与安全修复方案 |
| 为 Codex 准备环境 | 先验证 Node/npm，再交给 Codex 技能 | 可继续执行的 readiness 状态 |

### 客户如何使用

1. 说目标项目、操作系统和是否需要特定 Node 大版本；不确定时默认选择官方 LTS。
2. Agent 先检查现有 `node`、`npm` 和项目配置，不自动卸载旧版本。
3. 展示安装来源、版本和 PATH 影响；需要管理员权限时单独确认。
4. 安装后验证 `node --version`、`npm --version` 和一个无副作用的帮助命令。

### 依赖与安装

无必需外部 skill。网络问题先调用 `soia-env-network-diagnose`；Codex 需要 Node/npm 时由 `soia-env-codex-install` 消费本技能的结果。官方来源见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 只读检查 OS、架构、现有版本、PATH 是否含可执行文件和项目的 `.nvmrc`/`package.json` 版本要求；不打印完整环境变量。
2. 选择官方 LTS 安装器或官方认可的版本管理方式；一次只选择一种方法并记录。
3. 安装前确认下载源和权限；禁止未知镜像、修改 TLS 校验或 `curl | bash`。
4. 安装后重新解析 PATH；若需改 shell profile，先显示目标文件和追加内容并确认。
5. 验证 `node --version`、`npm --version`、`npm config get prefix`，并用 `npm --version` 作为最小 npm 健康检查。
6. 输出 `ready|missing|blocked` 和版本，交给上层环境编排或 Codex 技能。

## 权限与回滚

- 默认用户级安装；不主动使用 sudo 或管理员权限。
- 不删除旧 Node，不改项目锁文件，不全局安装业务依赖。
- 版本冲突时保留现状并请求选择；失败时提供官方卸载/修复路径，而不是自动清理。

## 日志与完成回执

```markdown
完成：Node.js/npm <已安装/已验证/被阻塞>。

日志摘要：
- started: <OS/架构/目标版本>
- processed: <探测、安装、PATH、验证>
- updated: <Node/npm 版本>
- failed: <原因>

验证：
- <node、npm、prefix、项目版本匹配>

问题与下一步：
- <需要重新打开应用、确认 PATH、切换版本或无>
```

## 前向测试

用 fixture 覆盖 Node 已有、Node 缺失、PATH 不一致和项目要求冲突；真实验收必须分别执行 Node 和 npm 版本检查。
