# 官方网络探测源

这些是用于安装前连通性检查的官方入口，不代表每个工具都需要同时可达。以当前日期重新打开页面核对重定向和下载域名；不要把本地镜像写成公共默认值。

| 用途 | 官方入口 | 用途边界 |
|---|---|---|
| Node.js | <https://nodejs.org/en> | 官网和下载入口 |
| Python | <https://www.python.org/downloads/> | 官网和下载入口 |
| Codex | <https://help.openai.com/en/articles/11096431> | 官方安装说明；实际 npm 请求由 npm registry 完成 |
| npm registry | <https://registry.npmjs.org/> | 仅在 Node/npm 已安装时探测 |
| WorkBuddy | <https://www.workbuddy.cn/> | 官网和桌面客户端下载入口 |

## 诊断解释

- 官网可达、registry 不可达：不要说成“网络完全正常”，应标记包管理器源阻塞。
- HTTPS 失败且系统时间明显错误：先提示校准时间，不自动改系统时间。
- 只有某个域名失败：复核 DNS、企业代理、地区网络策略和源站状态。
- 需要代理：让客户确认代理来源和权限，再按工具官方配置方式操作；不在诊断阶段记录代理密码。
