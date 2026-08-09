---
name: soia-env-network-diagnose
description: 只读诊断安装 AI 工具前的环境问题：网络侧检查 DNS、HTTPS、代理、证书、官方源和超时；本机侧按 Node/Python/Rust/Go/包管理器/Shell 分类盘点运行时，推导当前机器能装哪些 AI CLI，并用固定七列列表汇报。触发：「网络不通」「下载失败」「npm/pip 超时」「证书错误」「安装卡住」「装之前先检查环境」「这台机器能装什么」「有没有装 node」。
version: 1.4.3
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-09 01:40:00
created_by: gpt-5
updated_by: deepseek-v4-flash
---

# soia-env-network-diagnose

装不上 AI 工具通常卡在两处：**外面连不上**，或者**本机缺运行时**。本技能用低风险、可复现的只读探测把两处分开定位，再决定交给哪个安装技能。默认不修改代理、DNS、证书、防火墙、hosts，也不安装任何运行时。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装下载失败 | 探测官方 HTTPS、DNS、证书和延迟 | 可达/不可达、错误类别和下一步 |
| npm/pip 超时 | 区分网络、代理、包源和命令参数 | 不泄露 token 的诊断摘要 |
| 不知道是否能联网 | 执行最小只读检查 | 检查过的源数量和结论 |
| 装之前先体检 | 按类别盘点本机运行时 | Node/Python/Rust/Go/包管理器/Shell 的可用性与版本 |
| 这台机器能装什么 AI CLI | 用运行时结果对照各安装技能的渠道依赖 | 可安装 / 待复核 / 被阻塞，以及具体缺口 |

### 客户如何使用

1. 用自然语言描述失败的工具、错误提示和系统类型；不要求先运行命令。
2. Agent 先检查当前网络和官方源，不读取浏览器 cookie 或私有代理密码。
3. 诊断完成后，只有客户明确授权才调整代理、DNS 或证书，优先提供官方图形界面路径；修复后重新探测相同源。

### 依赖与安装

无必需外部依赖。网络侧运行 `python3 scripts/probe_endpoints.py --url <官方入口> --json`，本机侧运行 `python3 scripts/probe_runtimes.py --json`，两个脚本都只用 Python 标准库；不要把包含用户名、密码或 token 的 URL 传给探测器。官方站点清单见 [providers.md](references/providers.md)，运行时清单与渠道依赖见 [runtimes.md](references/runtimes.md)。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-network-diagnose -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### 私密信息与中间数据

- 本技能只读且默认不落盘；探测结果直接输出，经客户要求才保存脱敏报告。
- 代理凭据、Authorization、cookie 和证书私钥只留在 provider/系统凭据库中，不写 SOIA 配置、日志或回执。
- 短期探测文件只能进入每次运行独立的系统临时目录并及时清理；可重建的探测元数据才可进入 cache。

### 日志与完成回执

回执以「客户状态列表（强制）」的固定七列表格开头，只保留错误类别、受影响源、缺口与下一步，不输出代理凭据或完整流水账。

## 只读诊断流程

先判断问题在哪一侧：报错含超时、证书、DNS、`ECONNRESET` 走网络侧；报错含 `command not found`、版本过低、或客户只问“能不能装”走本机侧。两侧都不确定时先跑本机侧。

### 网络侧

按「基准组 → 目标组 → 镜像组」三组对照探测：先探国内基准源判断本机网络是否正常（至少收录 2 个独立来源，任一可达即基准通过），再探目标官方入口，最后探国内镜像源；逐层分类 `dns_failed`、`tls_failed`、`timeout`、`http_error`、`proxy_required` 或 `reachable`，三组结果对照 [providers.md](references/providers.md) 的判定矩阵得出结论与下一步。

### 本机侧

执行 `python3 scripts/probe_runtimes.py --json`，按类别盘点并对照各安装技能的渠道依赖与 Node 版本门槛，得出「可安装 / 待复核 / 被阻塞」，被阻塞时写明具体缺口并指向对应安装技能。`timeout` 判「待复核」，放宽 `--timeout` 重跑后再下结论，不得直接当成未安装；`host` 段的 OS/架构只作为事实上报，不判断某个 CLI 是否支持该平台（支持矩阵在各家官方清单里，由对应安装技能判定）。版本参数按工具适配，不得统一改写成 `--version`，实测差异见 [runtimes.md](references/runtimes.md)。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 网络诊断 | <已检查/被阻塞> | 不适用 | 不适用 | <正常/降级/异常> | <RFC3339-with-timezone> | <可以继续安装/需要处理：错误类别> |
| 运行时盘点 | <已检查/被阻塞> | 不适用 | 不适用 | <正常/降级/异常> | <RFC3339-with-timezone> | <可安装：目标/被阻塞：具体缺口> |

- 本技能无软件版本，版本列固定「不适用」；只为实际执行过的检查输出行，`更新时间` 记该行最后一次形成结论的时间。

## 不负责什么

- 不修改代理、DNS、证书、hosts 或包管理器源配置——判定矩阵给出的换源命令只是建议，执行与恢复都由用户自己决定。
- 不安装、升级或切换任何运行时——盘点只回答「缺什么」，装的动作交给 `soia-env-node-install`、`soia-env-python-install` 等对应安装技能；也不判断 AI CLI 本身是否已安装，那是各安装技能 `inspect_cli.py` 的职责。
- 不诊断 AI 模型服务的运行时可达性——DeepSeek、智谱等 API 连通性属于另一场景，不在「安装前的环境问题」边界内。

## 安全边界

- 不执行 pipe-to-shell 形式的远程安装命令与未知脚本；涉及安装建议时一律采用「下载 → 审阅 → 本地执行」三段式表述，不临时关闭 TLS 校验或绕过系统安全策略。
- 不自动替换 npm/pip 源；如用户明确要求，先显示当前值、目标值和恢复命令。探测脚本只返回状态码、错误类别和耗时，不保存响应正文；运行时探测只执行脚本内固定白名单里的版本查询命令，命令名与参数都不接受外部传入，不用 shell 拼接，不执行任意命令；只保留版本号，丢弃命令输出正文，路径中的 home 折成 `~`。

## 输出样例

数值取自两次真实探测（网络侧 2026-08-06T11:37，本机侧 2026-08-07T11:46，同一台 macOS 26 / arm64）：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 网络诊断 | 已检查 | 不适用 | 不适用 | 正常 | 2026-08-06T11:37:42+08:00 | 可以继续安装：网络正常，问题不在网络 |
| 运行时盘点 | 已检查 | 不适用 | 不适用 | 正常 | 2026-08-07T11:46:22+08:00 | 可安装：9 个 AI CLI 全部可装 |

网络侧判定：基准组全部可达，目标组官方入口除 Codex 帮助页对 HEAD 探测返回 403（方法级拒绝，非链路故障）外均可达，镜像组全部可达，对照判定矩阵判定为「网络正常」，下一步应转查命令参数、磁盘、权限，而不是继续排查网络。

本机侧盘点（darwin 26.5.2 / arm64，23 项并发探测，耗时 0.25s）：

| 类别 | 可用 | 缺失 |
|---|---|---|
| Node.js 运行时 | node 26.5.0、npm 11.17.0、npx 11.17.0、pnpm 11.9.0、bun 1.3.11 | yarn |
| Python 运行时 | python3 3.14.6、pip3 26.1.2、uv 0.11.2 | pipx |
| Rust 工具链 | rustc 1.92.0、cargo 1.92.0、rustup 1.28.2 | — |
| Go 工具链 | go 1.26.4 | — |
| JVM 运行时 | java 24 | — |
| 系统与包管理器 | brew 6.0.15、git 2.54.0、curl 8.7.1、wget 1.25.0、unzip 6.00、tar 3.5.3 | — |
| Shell | bash 5.3.15、zsh 5.9 | — |

另有两组受限环境复跑样例（裸机 PATH、node 20.19.0），核心结论：**缺 Node 不等于装不了 AI CLI**、**版本不够挡掉的是渠道不一定是工具**——全文见 [runtimes.md](references/runtimes.md) 的「真机复跑样例」节。

## 前向测试

`scripts/probe_endpoints.py` 必须用本地 fixture 覆盖成功、HTTP 错误、超时和非法 scheme；`scripts/probe_runtimes.py` 必须覆盖真机实测输出的版本解析（中文本地化文案、绝对路径输出、`go1.x`、无小数点 Java 版本号）、`absent` 与 `timeout` 分离、stdout 空才回退 stderr、home 折 `~`、三种推导结论；版本参数表被断言锁住，防回归成统一 `--version`。
