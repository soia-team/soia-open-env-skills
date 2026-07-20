---
name: soia-env-codex-setup-support
description: 面向小白安装和验证 Codex 桌面版与 CLI，并按磁盘、网络、Node/npm、登录、权限和工作区顺序排查问题。触发：「安装 Codex 桌面版」「安装 Codex CLI」「Codex 打不开」「Codex 卡住」「Codex 磁盘问题」。
dependencies:
  optional: [soia-env-network-diagnose, soia-env-node-install, soia-env-codex-install]
version: 1.0.0
created_at: 2026-07-20 18:30:00
updated_at: 2026-07-20 20:30:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-codex-setup-support

这是 Codex 环境问题的用户入口：先判断客户要用 ChatGPT 桌面应用中的 Codex 能力、CLI，还是两者都要，再用可复现的只读检查定位问题。安装、登录和管理员权限操作分开确认；客户只需要在官方图形界面完成登录、验证码和系统授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Codex 桌面版 | 引导打开 OpenAI 官方 ChatGPT 桌面应用入口，确认系统和架构 | 官方来源、安装状态和启动验证 |
| 安装 Codex CLI | 检查 Node/npm，调用 CLI 安装技能或使用官方 npm 包 | `codex` 版本、帮助命令和登录状态 |
| Codex 打不开或卡住 | 按磁盘、网络、运行时、登录、权限、工作区顺序排查 | 当前阻塞、证据和下一步 |
| 检查 Mac 磁盘是否影响 Codex | 先确认设备，再读取 SMART 健康、寿命、写入量和温度 | 安全摘要；不自动修复、抹盘或长测 |

### 客户如何使用

1. 直接说“安装 Codex 桌面版”“安装 Codex CLI”或“排查 Codex 为什么打不开”，并说明操作系统。
2. Agent 先做只读检查，展示将使用的官方来源、命令和可能的权限请求。
3. 客户只在官方网页或桌面应用中点击登录、授权和系统安全提示；不要求客户在终端输入确认字母、密码、验证码或 API key。
4. 每个故障分支单独给出“已确认 / 未确认 / 下一步”，没有证据时不把“磁盘有问题”当成结论。

### 依赖与安装

| 依赖 | 类型 | 处理方式 |
|---|---|---|
| macOS/Windows/Linux | 系统前置 | 先读取版本和架构，再选择官方桌面入口或 CLI 流程 |
| Node.js/npm | CLI 强依赖 | 缺失时调用 `soia-env-node-install`，不默认使用 sudo |
| 网络诊断 | 排障依赖 | 下载、登录或 npm 失败时调用 `soia-env-network-diagnose` |
| `smartmontools` | macOS 磁盘分支可选依赖 | 已有 Homebrew 时安装；只在客户确认后执行 |
| OpenAI 账号 | 用户授权 | 客户在官方页面完成授权；技能不读取或索要密钥 |

## 桌面版与 CLI 的边界

- Codex 桌面能力现在由 OpenAI 官方 ChatGPT 桌面应用承载；不能再用“是否存在独立 `Codex.app`”作为判断依据。macOS 上优先检查 `ChatGPT.app` 的 bundle id `com.openai.codex`、版本和代码签名。
- 技能只提供官方 ChatGPT 桌面应用入口，不猜测或传播第三方 DMG、破解包和未知下载地址。
- CLI 使用官方 npm 包 `@openai/codex`。安装后验证 `codex --version`、`codex --help`，需要登录时启动 `codex --login`，授权在浏览器中完成。
- `soia-env-codex-install` 保留为 CLI 的专门安装技能；本技能是桌面版 + CLI + 故障排查的编排入口，必要时调用它，不重复发明另一套登录流程。
- 桌面版和 CLI 的登录状态、工作区权限与网络可用性可能不同，不能因为其中一个能用就推断另一个正常。

官方链接和当前命令见 [official-sources.md](references/official-sources.md)。

## 标准排查流程

按下面顺序推进，前一步没有证据时不跳到后一步：

1. **系统与资源**：读取 macOS/Windows/Linux 版本、架构、可用磁盘空间和当前用户权限；不打印完整用户名、路径或环境变量。
2. **网络**：检查官方 OpenAI、npm、Node.js 和 Python 站点的 DNS/HTTPS 可达性；网络技能只读诊断，不自动改代理、DNS、证书或防火墙。
3. **Mac 磁盘（本技能的第一故障分支）**：如果安装失败、应用异常退出、机器明显变慢或磁盘空间异常，优先做 SMART 读取和空间检查。
4. **Node/npm/CLI**：检查 `node --version`、`npm --version`、全局 npm 前缀和 `codex --version`；缺 Node 时交给 `soia-env-node-install`，缺 CLI 时交给 `soia-env-codex-install`。
5. **桌面应用**：macOS 先用 `scripts/check_codex_desktop.py` 检查 `ChatGPT.app` 的 bundle id、版本和签名，再由客户在官方 UI 启动验证；Windows 按官方 ChatGPT 桌面入口核对安装和架构。不把独立 `Codex.app` 缺失当成 Codex 桌面版缺失。
6. **登录与权限**：区分浏览器授权未完成、账号/组织权限、网络阻断和本地权限；不索要或回显 token、cookie、API key。
7. **工作区**：最后检查项目目录、写权限、Git 状态和项目依赖；不要把工作区报错误判为 Codex 安装失败。

## Mac 磁盘健康与寿命检查

此分支只读取磁盘信息。它不能证明所有 SSD 都支持 SMART，也不能替代 Apple 磁盘工具或硬件诊断。

### 客户可复制的命令

先安装 `smartmontools`（已有 Homebrew 时）：

```bash
brew install smartmontools
```

用户要求的一键查看健康与寿命命令如下，保留原样供 Agent 或有经验的维护人员使用：

```bash
sudo smartctl -a /dev/disk0 | grep -E "SMART|Percentage Used|Available Spare|Data Units Written|Temperature"
```

但 `/dev/disk0` 不一定是实际物理设备。运行前先只读确认设备，例如 `diskutil list` 或 `smartctl --scan-open`，再将正确设备传给 `smartctl -a`。`sudo` 只用于读取受保护的 SMART 信息，密码必须只在 macOS 系统提示中输入，不能发送到对话中。

### 结果判读

- `SMART overall-health ... PASSED` 是一个健康信号，但不是“整块磁盘绝对正常”的证明。
- `Percentage Used` 越高表示标称寿命消耗越多；接近或超过 100% 应优先备份并安排更换评估。
- `Available Spare` 过低是预警；数值异常或持续下降时，应先备份重要数据。
- `Data Units Written` 是累计写入量，不等于剩余寿命；它用于判断是否存在长期高写入压力。
- 温度异常升高可能导致降速或不稳定，应结合环境、散热和系统日志判断。
- 如果输出提示不支持 SMART、没有这些字段、需要不同设备参数或权限不足，只能报告“未取得有效 SMART 证据”，不能直接判定磁盘损坏。

禁止自动执行 `smartctl -t long`、擦除、修复、分区、格式化或任何可能增加风险的命令。需要进一步处理时，优先使用 macOS“磁盘工具”、`diskutil info`、备份和 Apple Diagnostics。

技能附带的 `scripts/check_macos_disk.py` 只解析已经取得的筛选结果，不执行 `sudo`，也不读取序列号等无关信息：

```bash
sudo smartctl -a /dev/disk0 | grep -E "SMART|Percentage Used|Available Spare|Data Units Written|Temperature" | python3 scripts/check_macos_disk.py --stdin --json
```

## ChatGPT 桌面应用只读识别

不要把 `codex app` 当作安装状态检查命令：当 CLI 没识别到桌面应用时，它可能直接下载约数百 MB 的安装器。先执行不启动、不下载的识别脚本：

```bash
python3 scripts/check_codex_desktop.py --json
```

脚本优先检查 `/Applications/ChatGPT.app` 和用户应用目录中的 `ChatGPT.app`，确认 bundle id 为 `com.openai.codex`、读取版本，并验证代码签名。结果含义：

- `ready`：ChatGPT 桌面应用被识别为 Codex 宿主，签名验证通过；仍需由客户确认能否打开和登录。
- `missing`：没有找到 ChatGPT 桌面应用；只展示官方入口，不自动下载。
- `invalid_signature`：应用存在但签名验证失败；不要提示“安装正常”，也不要绕过系统安全策略。
- `unexpected_bundle`：应用存在但不是 Codex 使用的官方 ChatGPT bundle；停止并让客户确认来源。

## 权限、隐私与回滚

- 默认只读；安装 Homebrew 包、桌面应用或 npm 全局包前说明来源、写入范围和回滚方式。
- 不默认使用 `sudo`。只有读取受保护 SMART 信息确有必要时才单独请求管理员确认。
- 不自动修改 PATH、shell profile、代理、DNS、证书、系统安全设置或工作区文件。
- 安装失败时保留错误证据，不自动卸载、降级、删除缓存或清理应用数据。
- 日志只保留工具名、版本、错误类别、退出码和下一步，不保留 token、cookie、API key、密码、完整本地路径或浏览器授权内容。

## 日志与完成回执

```markdown
完成：Codex <桌面版/CLI/排查> <已完成/部分完成/被阻塞>。

日志摘要：
- started: <系统、架构、目标>
- processed: <磁盘、网络、Node/npm、应用、登录、工作区检查数量>
- updated: <工具或应用类别；没有则写 none>
- failed: <错误类别；没有则写 none>

验证：
- desktop: <已启动/未安装/未验证>
- cli: <版本、帮助命令或未安装>
- disk: <SMART 摘要/unsupported/未检查>

问题与下一步：
- <需要客户打开的官方页面、确认的权限或下一项技能>
```

## 前向测试

用 fixture 覆盖 SMART 健康通过、寿命预警、温度预警和不支持/字段缺失四种状态；用 fake command runner 覆盖桌面应用未安装、CLI 缺 Node、登录等待和工作区权限错误。真实验收必须从官方来源安装并分别验证桌面版和 CLI，不能把 npm 返回 0 当成登录完成。
