---
name: soia-env-python-install
description: 面向小白安装、验证和更新 Python 与 pip：识别系统和架构，优先 Python 官方来源，区分解释器、PATH、pip 和虚拟环境问题，并用固定六列列表汇报目标工具状态。触发：「安装 Python」「更新 Python」「安装 pip」「python 命令不存在」「pip 不能用」。
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.2.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 22:30:00
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-python-install

先确认系统已有的 Python 解释器和项目版本要求，再选择官方安装器或系统认可的包管理方式。默认使用 `python -m pip` 和项目虚拟环境，避免污染系统 Python。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Python | 识别系统/架构、选择官方稳定版本、安装并验证 | Python/pip 版本和状态 |
| 更新 Python | 识别解释器来源与项目约束，沿用原来源更新 | 更新前后版本、虚拟环境影响和验证结果 |
| pip 不可用 | 区分解释器、PATH、pip 模块和权限问题 | 安全修复方案 |
| 准备脚本或知识库工具 | 创建项目级虚拟环境并验证依赖入口 | 可交给下游技能的 readiness 摘要 |

### 客户如何使用

1. 说目标项目、操作系统和是否有版本要求；不确定时选择 Python 官方当前维护的稳定版本。
2. Agent 先检查 `python3`、`python`、Windows `py`、pip 和项目配置，不覆盖已有环境。
3. 展示安装源、版本和 PATH 影响；需要管理员权限或系统范围安装时单独确认。
4. 安装后验证解释器、pip 和一个临时虚拟环境；客户不需要手动输入终端命令。

### 依赖与安装

无必需外部 skill。网络问题先调用 `soia-env-network-diagnose`。官方来源、平台差异和维护版本见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 只读检查 OS、架构、`python3 --version`、`python --version`、Windows `py --version`、`python3 -m pip --version`，并记录解释器来源；不把完整用户路径写入回执。
2. 读取项目 `pyproject.toml`、`requirements.txt` 或 `.python-version` 的版本约束；缺少项目文件时不猜测项目依赖。
3. 选择 Python 官方安装器或当前系统的官方包管理器；禁止把第三方“一键脚本”当作默认方案。
4. 安装后优先使用解释器模块形式调用 pip：`python -m pip` 或 `py -m pip`。
5. 在用户指定的项目目录创建 `.venv` 或其他明确虚拟环境；不要把虚拟环境写入仓库提交。
6. 验证解释器、pip、虚拟环境激活/调用和一个无副作用的 import；失败时只报告阻塞类别。

## 已安装状态与更新

先确定当前解释器和来源；如果已安装且满足项目约束，提示“Python 已安装，无需重复安装”，不覆盖系统 Python，也不因为 pip 旧就重装运行时。

- 先检查 `python3 --version`、`python3 -m pip --version`、`command -v python3`，以及 Homebrew、`pyenv`、官方安装器或 Windows `py` 的来源迹象。
- 官方安装器管理：从 Python 官方下载页取得目标维护版本安装器，更新前记录现有解释器和项目约束。
- Homebrew 管理：客户确认后执行 `brew update && brew upgrade python`，不再叠加官方安装器。
- pyenv 管理：沿用 pyenv 安装并选择目标版本，例如 `pyenv install <version>`；不把 pyenv 和 Homebrew/官方安装器混为同一套解释器。
- `pip` 更新是独立动作；只在客户或项目需要时，在选定解释器/虚拟环境中执行 `python -m pip install --upgrade pip`，不把它当作 Python 运行时更新。

更新后分别验证解释器版本、`python -m pip --version`、项目虚拟环境和项目版本约束。更新失败时保留旧解释器、虚拟环境与错误证据，不自动删除环境。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |
|---|---|---|---|---|---|
| Python | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <无需重复安装/可更新/等待确认后安装/被阻塞：原因> |

- 用户只问 Python 时只输出 `Python` 行，不额外输出 pip；用户明确问 pip 时才增加 `pip` 行。
- 最新版本必须符合项目约束；无法取得时写“未取得”，不猜测。
- 表格后只保留必要的权限确认、虚拟环境影响或阻塞说明，不展示内部探测流水账。

## 权限与回滚

- 默认用户级安装；不自动使用 sudo、管理员权限或替换系统 Python。
- 不执行 `pip install` 到全局环境，不修改项目依赖文件，除非客户明确要求。
- 不删除旧 Python；版本冲突时保留现状并给出可回滚的选择。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |
|---|---|---|---|---|---|
| Python | <状态> | <当前版本> | <最新版本> | <运行状态> | <处理结果> |
```

## 前向测试

用 fixture 覆盖 Python 已有、仅有 Python 2、pip 缺失、Windows `py` 可用和虚拟环境创建失败；真实验收必须分别验证解释器、pip 和项目虚拟环境。
