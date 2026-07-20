---
name: soia-env-workbuddy-install
description: 面向小白通过 WorkBuddy 官方站点安装、验证和更新桌面客户端，识别 macOS/Windows 架构与代码签名，避免把 WorkBuddy 误当成 npm 包或 CLI。触发：「安装 WorkBuddy」「更新 WorkBuddy」「安装腾讯龙虾」「WorkBuddy 下载」「WorkBuddy 打不开」。
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.1.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 21:30:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-workbuddy-install

WorkBuddy 是桌面应用，安装路径与 Node/Python 不同。先打开官方站点和下载页，选择对应系统安装包，再由客户完成系统安全提示、登录和服务授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 WorkBuddy | 识别系统/架构并打开官方下载安装入口 | 官方下载链接和安装状态 |
| 更新 WorkBuddy | 识别已安装版本、来源和签名，沿用官方更新路径 | 更新前后版本、签名和启动验证 |
| WorkBuddy 打不开 | 检查安装结果、签名提示、网络和版本 | 可复现的阻塞类别与下一步 |
| 不会登录 | 引导官方界面登录 | 客户自己完成授权，不交出密码 |

### 客户如何使用

1. 说“安装 WorkBuddy”并说明系统；Agent 先确认系统和芯片架构。
2. Agent 只使用官方 `workbuddy.cn` 下载入口，不下载来路不明的 DMG/EXE。
3. 客户在系统安装器中完成打开、拖拽、权限和登录；Agent 不要求客户使用终端。
4. 安装后检查应用是否存在、能否启动、版本信息和代码签名；无法取得版本时标记为“安装完成但未验证”。

### 依赖与安装

无 Node/Python 依赖。官方入口、当前可见平台和安装后验证边界见 [official-sources.md](references/official-sources.md)。网络异常时调用 `soia-env-network-diagnose`。

## 标准流程

1. 只读识别 `macOS/Windows`、CPU 架构、已安装应用版本、签名和当前用户是否能安装应用；Linux 先说明官方桌面支持范围未验证。
2. 打开官方站点的产品下载入口：macOS 区分 ARM64/x64，Windows 选择 x64/兼容 ARM64 版本；不猜测下载 URL。
3. 展示安装动作和系统权限影响，客户确认后再启动安装器。
4. 客户在官方 UI 完成安全提示、登录、验证码和隐私/服务授权；Agent 不代填。
5. 验证应用启动、版本或“关于”页面；若只能确认安装包落地，明确标注剩余验证。

## 已安装状态与更新

先检查已经存在的应用；状态正常时提示“WorkBuddy 已安装，无需重复安装”，不覆盖、不卸载，也不把再次下载当作默认更新方式。

- macOS 记录应用版本、安装位置，并执行 `codesign --verify --deep --strict <WorkBuddy.app>`；可用时再执行 `spctl --assess --type execute <WorkBuddy.app>`。
- Windows 记录“应用和功能”中的版本、发布者和系统安全提示；不关闭 SmartScreen 或杀毒软件。
- 已安装且签名/发布者验证通过：从 WorkBuddy 官方站点或应用内官方更新入口更新，先展示目标版本和影响，再由客户确认。
- 应用存在但签名验证失败、发布者不明或版本无法读取：标记为 `invalid_signature` 或 `installed_unverified`，先处理来源问题，不提示“安装正常”。
- WorkBuddy 没有本技能承诺的 npm/CLI 更新路径；不使用 `npm`、未知下载脚本或第三方镜像更新。

更新前保留旧版本、来源和验证结果。更新失败时保留旧版本和错误证据，不自动卸载、删除用户数据或绕过系统安全策略。

## 权限与回滚

- 不关闭 Gatekeeper、SmartScreen、杀毒软件或系统安全策略。
- 不删除旧版本；新旧版本冲突时先停止并让客户选择。
- 卸载、清理用户数据或撤销授权必须作为单独请求，不能作为安装失败的自动回滚。

## 日志与完成回执

```markdown
完成：WorkBuddy <已安装并验证/已安装待登录/被阻塞>。

日志摘要：
- started: <OS/架构/官方来源>
- processed: <下载入口、安装、启动检查>
- updated: <应用状态>
- failed: <原因>

验证：
- <安装器、应用启动、版本/关于页、登录状态>

问题与下一步：
- <客户需在 UI 完成的动作或无>
```

## 前向测试

用平台 fixture 验证 macOS ARM64、macOS x64、Windows x64 和未知平台的选择逻辑；真实验收必须由客户确认官方安装器和登录页面，不把网页可达当成客户端可用。
