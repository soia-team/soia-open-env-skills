---
name: soia-env-python-install
description: 为新手安装、验证或按授权更新 Python 与 pip。触发：「安装 Python」「更新 Python」「python 命令不存在」
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.4.2
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-05 13:30:00
created_by: gpt-5
updated_by: claude-opus-5
---

# soia-env-python-install

先确认系统已有的 Python 解释器和项目版本要求，再选择官方安装器或系统认可的包管理方式。默认使用 `python -m pip` 和项目虚拟环境，避免污染系统 Python。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Python | 识别系统/架构、选择官方稳定版本、安装并验证 | Python/pip 版本和状态 |
| 检查 Python 更新 | 识别解释器来源与项目约束，不自动更新 | 当前版本、最新版本和来源 |
| 更新 Python 到最新 | 客户明确要求最新版后沿原来源更新 | 中间状态、虚拟环境影响和验证结果 |
| pip 不可用 | 区分解释器、PATH、pip 模块和权限问题 | 安全修复方案 |
| 准备脚本或知识库工具 | 创建项目级虚拟环境并验证依赖入口 | 可交给下游技能的 readiness 摘要 |

### 客户如何使用

其他可识别说法包括「更新 Python 到最新」「安装 pip」「pip 不能用」；纯网络超时优先交给 `soia-env-network-diagnose`。

1. 说目标项目、操作系统和是否有版本要求；不确定时选择 Python 官方当前维护的稳定版本。
2. Agent 先检查 `python3`、`python`、Windows `py`、pip 和项目配置，不覆盖已有环境。
3. 发现新版本时只汇报；只说“更新 Python”时先询问是否更新到最新，明确选择最新版后才执行。
4. 展示安装源、版本和 PATH 影响；需要管理员权限或系统范围安装时单独确认。
5. 安装或明确授权的更新过程中持续显示并记录检查、计划、执行、验证和终态。

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
- Homebrew 管理：只有客户明确要求更新到最新兼容版本后，才执行 `brew update && brew upgrade python`，不再叠加官方安装器。
- pyenv 管理：得到最新版授权后沿用 pyenv 安装并选择目标版本，例如 `pyenv install <version>`；不把 pyenv 和 Homebrew/官方安装器混为同一套解释器。
- `pip` 更新是独立动作；只有客户明确要求更新 pip 到最新时，才在选定解释器/虚拟环境中执行 `python -m pip install --upgrade pip`。项目约束只能触发版本报告和确认，不能自动更新 pip，也不能把 pip 更新当作 Python 运行时更新。

模糊的“更新 Python”只执行版本比较并返回“等待确认是否更新到最新”。明确安装一个缺失的 Python 可以安装符合项目约束的推荐稳定版本，不视为更新现有工具。

更新后分别验证解释器版本、`python -m pip --version`、项目虚拟环境和项目版本约束。更新失败时保留旧解释器、虚拟环境与错误证据，不自动删除环境。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| Python | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <RFC3339-with-timezone> | <无需重复安装/可更新，未执行/等待确认是否更新到最新/已更新/等待确认后安装/被阻塞：原因> |

- 用户只问 Python 时只输出 `Python` 行，不额外输出 pip；用户明确问 pip 时才增加 `pip` 行。
- `更新时间` 记录解释器、pip 和无害虚拟环境验证完成后的时间。
- 最新版本必须符合项目约束；无法取得时写“未取得”，不猜测。
- 表格后只保留必要的权限确认、虚拟环境影响或阻塞说明，不展示内部探测流水账。

## 安装与更新的中间状态

真正执行安装或获得最新版授权的更新时，用随机 `run_id` 在阶段实际发生时立即调用 `scripts/record_install_progress.py`：检查前、方案形成后、安装器/更新器调用前、验证前和终态各记录一次；需要管理员权限、换源、修改 PATH 或影响项目虚拟环境时，先展示准确方案并记录 `waiting_confirmation`，得到该项确认后再继续。不得结束后补写；时间由记录器生成。只读检查不调用。只有客户原话明确要求最新版时，更新执行阶段才带 `--customer-requested-latest`。

```bash
python3 scripts/record_install_progress.py --run-id <run-id> --action <install|update> --stage checking --status in_progress --result-code checking_started
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage updating --status in_progress --result-code update_started --customer-requested-latest
```

同时持续展示固定阶段表；成功、失败、取消或等待权限时都要追加终态：

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

## 权限与回滚

- 默认用户级安装；不自动使用 sudo、管理员权限或替换系统 Python。
- 不执行 `pip install` 到全局环境，不修改项目依赖文件，除非客户明确要求。
- 不删除旧 Python；版本冲突时保留现状并给出可回滚的选择。

## 私密信息与中间数据

- 私有包源凭据使用 provider 官方登录态、keyring 或系统凭据库；SOIA 配置只保存非秘密偏好和路径。
- 安装或更新阶段使用进度记录器追加脱敏的动作、阶段、结果和时间；只读检查默认不落盘。
- 包索引元数据可放 cache，wheel、安装器和虚拟环境探测文件放系统临时目录并在成功或失败后清理。
- 不记录 pip token、完整私有 index URL、用户名、虚拟环境内容或客户私有绝对路径。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| Python | <状态> | <当前版本> | <最新版本> | <运行状态> | <RFC3339-with-timezone> | <处理结果> |
```

## 前向测试

用 fixture 覆盖 Python 已有、仅有 Python 2、pip 缺失、Windows `py` 可用和虚拟环境创建失败；真实验收必须分别验证解释器、pip 和项目虚拟环境。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-python-install -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。
