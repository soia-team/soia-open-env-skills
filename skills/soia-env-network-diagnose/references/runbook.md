# 只读诊断流程与测试细则

先判断问题在哪一侧：报错含超时、证书、DNS、`ECONNRESET` 走网络侧；报错含 `command not found`、版本过低、或客户只问“能不能装”走本机侧。两侧都不确定时先跑本机侧——它更快且不依赖网络。

## 网络侧

1. 记录 OS、架构、时间、网络类型和原始错误；不保存完整命令环境。
2. 按「基准组 → 目标组 → 镜像组」三组对照探测：先探国内基准源判断本机网络是否正常，再探目标官方入口，最后探国内镜像源；源清单见 [providers.md](providers.md)。
3. 逐层分类：`dns_failed`、`tls_failed`、`timeout`、`http_error`、`proxy_required` 或 `reachable`。
4. 基准组至少收录 2 个独立来源，任一可达即基准通过；不因一次探测失败就断言“网络完全不可用”。
5. 将三组结果对照 [providers.md](providers.md) 的判定矩阵得出结论与下一步。

## 本机侧

6. 执行 `python3 scripts/probe_runtimes.py --json`，按 Node/Python/Rust/Go/JVM/包管理器/Shell 分类盘点；只跑白名单内的版本查询命令。
7. 版本参数按工具适配，不得统一改写成 `--version`——差异与实测依据见 [runtimes.md](runtimes.md)。
8. 状态为 `timeout` 时判「待复核」，放宽 `--timeout` 重跑后再下结论；**不得直接当成未安装**。
9. 用运行时结果对照各安装技能声明的渠道依赖与 Node 版本门槛，得出「可安装 / 待复核 / 被阻塞」；被阻塞时写明具体缺口（例如 `node 20.19.0 < 22`），并指向对应安装技能，不代为安装。
10. `host` 段的 OS/架构只作为事实上报，**不判断某个 CLI 是否支持该平台**——支持矩阵在各家官方清单里，由对应安装技能判定，见 [runtimes.md](runtimes.md)。
11. 交付结构化摘要，供环境编排技能或安装技能消费。

## 前向测试

`scripts/probe_endpoints.py` 必须用本地 fixture 覆盖成功、HTTP 错误、超时和非法 scheme；真实运行时只把官方源作为输入并核对终端状态。

`scripts/probe_runtimes.py` 必须覆盖：真机实测输出的版本解析（中文本地化文案、绝对路径输出、`go1.x`、无小数点 Java 版本号）、`absent` 与 `timeout` 分离、stdout 空才回退 stderr、home 折 `~`、三种推导结论（裸机 / Node 过低 / 查询超时）；版本参数表被断言锁住，防回归成统一 `--version`。
