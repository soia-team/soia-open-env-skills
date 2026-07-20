# Python 官方来源（2026-07-20 核对）

- 官网与下载：[Python Downloads](https://www.python.org/downloads/)
- macOS 使用官方安装器和对应架构说明；Windows 使用官方安装器/安装管理器；Linux 结合发行版官方包管理器或 Python 官方源码/发行版说明。
- 当前维护版本、支持周期和平台文件以 Python 官方下载页为准，不在技能正文中固定版本号。

## 选择规则

- 先读取项目的 `pyproject.toml`、`requirements.txt`、`.python-version` 或 CI 配置。
- 验证时优先使用 `python3 -m pip`；Windows 需要时使用 `py -m pip`，避免 `pip` 指向错误解释器。
- 项目依赖安装到用户指定的虚拟环境，不默认写入系统 Python。
- 不使用第三方一键脚本，不关闭 TLS 校验，不自动替换 pip 源。
