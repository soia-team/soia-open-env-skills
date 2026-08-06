# 网络探测源

探测分三组对照进行：先探「基准组」判断本机网络本身是否正常，再探「目标组」官方入口，最后探「镜像组」国内镜像；三组结果对照下方的「判定矩阵」得出结论。以当前日期重新打开页面核对重定向和下载域名；不要把本地镜像写成公共默认值。

## 基准组（国内，判断本机网络是否正常）

至少收录 2 个独立来源，**任一可达即基准通过**（防单个镜像站抽风造成误报）。基准组不可达时优先修本机网络，不要动代理和源配置。

| 来源 | 用途边界 |
|---|---|
| <https://mirrors.cloud.tencent.com/> | 腾讯云镜像站首页 |
| <https://mirrors.aliyun.com/> | 阿里云镜像站首页（可达但响应较慢，默认 5s 超时可能误报，可放宽超时复核） |
| <https://mirrors.tuna.tsinghua.edu.cn/> | 清华 TUNA 镜像站首页 |
| <https://mirrors.ustc.edu.cn/> | 中科大镜像站首页 |

## 目标组（要安装的东西的官方入口）

这些是用于安装前连通性检查的官方入口，不代表每个工具都需要同时可达。

| 用途 | 官方入口 | 用途边界 |
|---|---|---|
| Node.js | <https://nodejs.org/en> | 官网和下载入口 |
| Python | <https://www.python.org/downloads/> | 官网和下载入口 |
| Codex | <https://help.openai.com/en/articles/11096431> | 官方安装说明；实际 npm 请求由 npm registry 完成 |
| npm registry | <https://registry.npmjs.org/> | 仅在 Node/npm 已安装时探测 |
| WorkBuddy | <https://www.workbuddy.cn/> | 官网和桌面客户端下载入口 |

## 镜像组（目标的国内镜像：既是诊断信号也是绕行方案）

与目标组对照：目标组不可达而镜像组可达时，说明仅境外链路受限，可给出换源绕行命令（见下方示例，只给命令不代改）。

| 用途 | 镜像入口 | 用途边界 |
|---|---|---|
| npm registry | <https://registry.npmmirror.com/> | npm registry 镜像；与官方 registry 对照 |
| pypi | <https://pypi.tuna.tsinghua.edu.cn/simple/> | pypi 镜像 |
| pypi 备选 | <https://mirrors.aliyun.com/pypi/simple/> | pypi 镜像备选 |
| Node 安装包 | <https://npmmirror.com/mirrors/node/> | Node 安装包镜像 |

## 判定矩阵

| 基准组 | 目标组 | 镜像组 | 结论 | 下一步 |
|---|---|---|---|---|
| 不可达 | 不可达 | 不可达 | 本机网络或 DNS 故障 | 先修本地网络，不要动代理和源配置 |
| 可达 | 不可达 | 可达 | 仅境外链路受限 | 给出换镜像源命令**和恢复命令**，由用户自己执行 |
| 可达 | 不可达 | 不可达 | 目标与镜像都不可达 | 排查企业代理 / TLS 拦截 |
| 可达 | 可达 | （任意） | 网络正常 | 问题不在网络，转查命令参数、磁盘、权限 |

### npm / pip 换源命令示例

每条成对给出「设置命令 + 恢复命令」；**本技能只给命令不代改**，是否执行、何时恢复由用户自己决定。

npm：

```bash
# 设置（换到 npmmirror）
npm config set registry https://registry.npmmirror.com/
# 恢复（回官方源）
npm config set registry https://registry.npmjs.org/
```

pip：

```bash
# 设置（换到清华 pypi 镜像）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
# 恢复（取消自定义，回官方默认源）
pip config unset global.index-url
```

## 诊断解释

- 官网可达、registry 不可达：不要说成“网络完全正常”，应标记包管理器源阻塞。
- HTTPS 失败且系统时间明显错误：先提示校准时间，不自动改系统时间。
- 只有某个域名失败：复核 DNS、企业代理、地区网络策略和源站状态。
- 需要代理：让客户确认代理来源和权限，再按工具官方配置方式操作；不在诊断阶段记录代理密码。
