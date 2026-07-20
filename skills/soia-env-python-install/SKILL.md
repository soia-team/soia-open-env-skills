---
name: soia-env-python-install
description: 面向小白安装并验证 Python 与 pip：识别系统和架构，优先 Python 官方来源，区分 python/python3/py、PATH、pip 和虚拟环境问题。触发：「安装 Python」「安装 pip」「python 命令不存在」「pip 不能用」。
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.0.0
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-20 18:00:00
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
| pip 不可用 | 区分解释器、PATH、pip 模块和权限问题 | 安全修复方案 |
| 准备脚本或知识库工具 | 创建项目级虚拟环境并验证依赖入口 | 可交给下游技能的 readiness 摘要 |

### 客户如何使用

1. 说目标项目、操作系统和是否有版本要求；不确定时选择官方当前维护版本。
2. Agent 先检查 `python3`、`python`、Windows `py`、pip 和项目配置，不覆盖已有环境。
3. 展示安装源、版本和 PATH 影响；需要管理员权限或系统范围安装时单独确认。
4. 安装后验证解释器、pip 和一个临时虚拟环境；客户不需要手动输入终端命令。

### 依赖与安装

无必需外部 skill。网络问题先调用 `soia-env-network-diagnose`。官方来源、平台差异和维护版本见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 只读检查 OS、架构、`python3 --version`、`python --version`、Windows `py --version`、`python3 -m pip --version`；不把完整用户路径写入回执。
2. 读取项目 `pyproject.toml`、`requirements.txt` 或 `.python-version` 的版本约束；缺少项目文件时不猜测项目依赖。
3. 选择 Python 官方安装器或当前系统的官方包管理器；禁止把第三方“一键脚本”当作默认方案。
4. 安装后优先使用解释器模块形式调用 pip：`python -m pip` 或 `py -m pip`。
5. 在用户指定的项目目录创建 `.venv` 或其他明确虚拟环境；不要把虚拟环境写入仓库提交。
6. 验证解释器、pip、虚拟环境激活/调用和一个无副作用的 import；失败时只报告阻塞类别。

## 权限与回滚

- 默认用户级安装；不自动使用 sudo、管理员权限或替换系统 Python。
- 不执行 `pip install` 到全局环境，不修改项目依赖文件，除非客户明确要求。
- 不删除旧 Python；版本冲突时保留现状并给出可回滚的选择。

## 日志与完成回执

```markdown
完成：Python/pip <已安装/已验证/被阻塞>。

日志摘要：
- started: <OS/架构/目标版本>
- processed: <探测、安装、虚拟环境、验证>
- updated: <Python/pip/venv 状态>
- failed: <原因>

验证：
- <解释器、pip、虚拟环境和无副作用检查>

问题与下一步：
- <版本选择、系统权限、项目依赖或无>
```

## 前向测试

用 fixture 覆盖 Python 已有、仅有 Python 2、pip 缺失、Windows `py` 可用和虚拟环境创建失败；真实验收必须分别验证解释器、pip 和项目虚拟环境。
