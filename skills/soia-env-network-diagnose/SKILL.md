---
name: soia-env-network-diagnose
description: 只读诊断小白安装工具时的网络问题：检查 DNS、HTTPS、代理、证书、官方源和超时，区分故障来源，并用固定七列列表汇报网络状态与处理结果。触发：「网络不通」「下载失败」「npm/pip 超时」「证书错误」「安装卡住」。
version: 1.3.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-06 11:39:00
created_by: gpt-5
updated_by: pi deepseek-v4-flash
---

# soia-env-network-diagnose

先用低风险、可复现的探测把“网络有问题”分成具体类别，再决定是否交给安装技能。默认不修改代理、DNS、证书、防火墙或 hosts。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装下载失败 | 探测官方 HTTPS、DNS、证书和延迟 | 可达/不可达、错误类别和下一步 |
| npm/pip 超时 | 区分网络、代理、包源和命令参数 | 不泄露 token 的诊断摘要 |
| 不知道是否能联网 | 执行最小只读检查 | 检查过的源数量和结论 |

### 客户如何使用

1. 用自然语言描述失败的工具、错误提示和系统类型；不要求先运行命令。
2. Agent 先检查当前网络和官方源，不读取浏览器 cookie 或私有代理密码。
3. 诊断完成后，只有客户明确授权才调整代理、DNS 或证书；优先提供官方图形界面路径。
4. 修复后重新探测相同源，不能用“浏览器能打开某个网站”代替包管理器源验证。

### 依赖与安装

无必需外部依赖。脚本使用 Python 标准库，可用以下方式做一次探测：

```bash
python3 scripts/probe_endpoints.py --url https://nodejs.org/en --url https://www.python.org/downloads/ --json
```

不要把包含用户名、密码或 token 的 URL 传给探测器。官方站点清单见 [providers.md](references/providers.md)。

## 只读诊断流程

1. 记录 OS、架构、时间、网络类型和原始错误；不保存完整命令环境。
2. 按「基准组 → 目标组 → 镜像组」三组对照探测：先探国内基准源判断本机网络是否正常，再探目标官方入口，最后探国内镜像源；源清单见 [providers.md](references/providers.md)。
3. 逐层分类：`dns_failed`、`tls_failed`、`timeout`、`http_error`、`proxy_required` 或 `reachable`。
4. 基准组至少收录 2 个独立来源，任一可达即基准通过；不因一次探测失败就断言“网络完全不可用”。
5. 将三组结果对照 [providers.md](references/providers.md) 的判定矩阵得出结论与下一步。
6. 交付结构化摘要，供环境编排技能或安装技能消费。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 网络诊断 | <已检查/被阻塞> | 不适用 | 不适用 | <正常/降级/异常> | <RFC3339-with-timezone> | <可以继续安装/需要处理：错误类别> |

- 网络诊断没有软件版本，两个版本列固定写“不适用”。
- `更新时间` 记录最后一个探测完成并形成结论的时间。
- 用户只问某个工具的网络问题时，`处理结果` 写该目标是否可以继续安装，不增加其他工具状态行。
- 表格后只保留必要的错误类别、受影响官方源和下一步，不输出代理凭据或完整探测流水账。

## 安全边界

- 不执行 `curl | bash`、未知脚本、临时关闭 TLS 校验或绕过系统安全策略。
- 不把代理 URL、Authorization header、cookie、包管理器凭据写入日志。
- 不自动替换 npm/pip 源；如用户明确要求，先显示当前值、目标值和恢复命令。
- 网络探测脚本只返回状态码、错误类别和耗时，不保存响应正文。

## 私密信息与中间数据

- 本技能只读且默认不落盘；探测结果直接输出，经客户要求才保存脱敏报告。
- 代理凭据、Authorization、cookie 和证书私钥只留在 provider/系统凭据库中，不写 SOIA 配置、日志或回执。
- 短期探测文件只能进入每次运行独立的系统临时目录并及时清理；可重建的探测元数据才可进入 cache。
- 不保存响应正文、完整代理 URL、账号标识或客户私有绝对路径。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 网络诊断 | <状态> | 不适用 | 不适用 | <运行状态> | <RFC3339-with-timezone> | <处理结果> |
```

## 输出样例

以下为示例（数值取自一次真实探测：基准组 4 个国内源全部可达，目标组官方入口与镜像组 4 个镜像全部可达）：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 网络诊断 | 已检查 | 不适用 | 不适用 | 正常 | 2026-08-06T11:37:42+08:00 | 可以继续安装：网络正常，问题不在网络 |

判定说明：基准组全部可达，目标组官方入口除 Codex 帮助页对 HEAD 探测返回 403（方法级拒绝，非链路故障）外均可达，镜像组全部可达，对照判定矩阵判定为「网络正常」，下一步应转查命令参数、磁盘、权限，而不是继续排查网络。

## 前向测试

`scripts/probe_endpoints.py` 必须用本地 fixture 覆盖成功、HTTP 错误、超时和非法 scheme；真实运行时只把官方源作为输入并核对终端状态。

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
