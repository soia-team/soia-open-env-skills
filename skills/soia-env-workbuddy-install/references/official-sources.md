# WorkBuddy 官方来源（2026-07-20 核对）

- 官方站点：[workbuddy.cn](https://www.workbuddy.cn/)
- 官方站点当前展示桌面下载入口：Mac ARM64、Mac x64、Windows x64（兼容 ARM64）。
- 产品页还区分 WorkBuddy 与 CodeBuddy IDE；不要把 CodeBuddy IDE 的安装包当成 WorkBuddy。

## 处理边界

- 下载按钮和文件 URL 可能变化；Agent 应从官方站点当前页面进入，不猜测 CDN URL。
- 已安装状态先核对应用版本、发布者/代码签名和启动结果；版本检查默认只读，只有客户明确要求“更新到最新版本”时才沿用官方站点或应用内更新入口，不把 WorkBuddy 当作 npm 包或 CLI。
- macOS 的 `codesign`/`spctl` 验证失败时，不能把“文件存在”当成“安装可用”；先标记签名或来源阻塞。
- WorkBuddy 的登录、验证码、系统安全提示和服务授权由客户在官方 UI 完成。
- Linux 桌面支持范围未在本技能中承诺；如官方页面没有对应下载入口，报告“平台未验证”，不安装第三方移植包。
