---
name: soia-env-local-model-bench
description: 在 Apple Silicon 上评测本地 LLM：先环境检查与引擎选型（mlx-lm/llama.cpp 等），确认后才下载部署；跑题库判定、吞吐 TTFT 与硬件采样，产出可横比的口径化报告。触发：「评测本地模型」「本地模型跑分」「装个本地模型」「mlx 测速」。
version: 1.2.0
created_at: 2026-08-19 16:00:00
updated_at: 2026-08-20 13:50:00
created_by: claude-fable-5
updated_by: claude-fable-5
---

# soia-env-local-model-bench

本地模型「能跑」和「值得用」之间隔着一整套测量：引擎选没选对、速度质量是什么水平、数字能不能跟别人比。本技能把一次本地 LLM 评测固化成可复现流程：环境检查 → 引擎选型 → 下载部署 → 题库判定 → 吞吐与硬件画像 →（可选）Agent 集成，并按固定契约出报告。首版面向 Apple Silicon macOS。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 不知道这台机器能不能跑本地模型 | 只读探测芯片/内存/磁盘/OS/已装引擎 | 事实清单 + 引擎选型对比与场景推荐 |
| 下载模型又慢又卡死 | aria2c 16 连接方案 + 完整性验证 | 稳定的下载速率与验证结果 |
| 部署起来跑一轮评测 | mlx-lm / llama.cpp 双引擎启动模板 + 题库自动判定 | 每题 PASS/FAIL/待人工 + 速度数字 |
| 想知道并发能到多少 | TTFT 冷/热 + 1/2/4/8 并发聚合吞吐 | 带口径声明的吞吐结果 JSON |
| 跑的时候占多少资源 | 进程 RSS/CPU/GPU 采样与汇总 | 峰值与活跃均值 |
| 接进 pi/dsh/opencode 干活 | Agent 挂本地端点跑沙盒真实任务 | 测试通过与否 + 耗时 + 改动范围 |
| 结果沉淀下来以后对比 | 按报告契约出回执、横比列、口径声明 | 可跨模型、跨社区对比的报告 |

**不做清单**（显式边界）：不做模型训练/微调；不做云端 API 评测；首版不支持非 macOS 平台（脚本在其他平台只报事实不给推荐）；**不自动删除模型文件**（收尾清单只提醒，删除由客户自己执行）。

### 客户如何使用

1. 客户说出目标（评测某个模型 / 想装个本地模型 / 对比两个引擎），不需要先准备命令。
2. Agent **必须先跑第 0 步环境检查**并给出引擎选型表——客户确认引擎与模型后才进入下载安装，不跳步。
3. 下载、装引擎、启停服务都属于改机动作：先展示计划（装什么、放哪、占多少磁盘）再执行。
4. 评测执行中 Agent 边跑边报每题结果；结束按「日志与完成回执」格式收口。
5. 涉及把结论写入客户知识库或发布 Artifact 时，先确认落点再写。

### 依赖与安装

| 依赖 | 类型 | 安装 / 配置 | 缺失时怎么处理 |
|---|---|---|---|
| Python 3.9+ | 强依赖 | 系统自带或 `soia-env-python-install` | 停止并指引安装 |
| PyYAML | 强依赖 | `python3 -m pip install pyyaml` | 题库无法解析，停止并给命令 |
| aria2c | 下载强烈推荐 | `brew install aria2` | 降级 hf 直连，明示慢且可能静默卡死 |
| node | 判定 harness 需要 | `soia-env-node-install` | node_snippet 题记「无法自动判定」，其余照跑 |
| mlx-lm / llama.cpp | 按选型二选一或都装 | venv 内 `pip install mlx-lm` / `brew install llama.cpp` | 走第 0-1 步选型与安装流程 |
| pi / dsh / opencode | 可选（Agent 集成维度） | 各自官方渠道 | 跳过维度三，回执标注 |

配置约定（全部非秘密，均可缺省）：

```text
~/.config/soia-skills/soia-env-local-model-bench/config.yml
SOIA_ENV_LOCAL_MODEL_BENCH_CONFIG_FILE=<custom-config-path>
```

示例见 [config.example.yml](assets/config.example.yml)；优先级：脚本参数 > 环境变量 > config > 内置默认。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-local-model-bench -y
```

### 私密信息与中间数据

- 本技能不需要任何 API key/token；下载走公开仓库，脚本请求本机端点，**不上传评测结果**。私有仓库鉴权走 provider 官方登录流程，不代管、不回显。
- **私有题外置**：取材真实业务代码的题（如 C1/C2）只存在于本机 `~/.config/soia-skills/soia-env-local-model-bench/questions/`，绝不进开源技能仓；对外报告只出现 qid 与判定结果，不出现题面与代码。
- 评测原始数据落在客户工作目录（默认 `~/local-model-bench/`），属客户资产；脚本输出对路径做 home 折叠，不打印用户绝对路径。
- 只读检查（env_check、--list、--mock）不落盘状态；本技能不写审计 state。

### 日志与完成回执

执行中逐题打印 `qid 判定 耗时 tok/s`；每轮结束按 [report-contract.md](references/report-contract.md) 的固定格式收口：完成回执表（含 `更新时间`，RFC 3339 带时区）、skipped 逐条原因、口径声明。对外横比另附横比表列定义。

## 工作流（顺序强制）

### 第 0 步 · 环境检查（必开局，只读）

```bash
python3 scripts/env_check.py --json
```

探测芯片/内存/磁盘/OS + 已装引擎（mlx-lm/llama.cpp/Ollama/vLLM/LM Studio/oMLX）+ 辅助工具（aria2c/node/PyYAML）。拿到事实后对照 [engines.md](references/engines.md) 给出**引擎选型对比表与场景推荐**，并核对内存/磁盘门槛（权重 + KV cache + 系统余量）。**客户确认引擎与模型之前，不下载任何东西。**

### 第 1 步 · 下载（确认后才执行）

按 [download.md](references/download.md)：小文件 hf 直下，权重分片 aria2c 16 连接，完整性验证必做（覆盖所有文件，不只权重）。实测结论：hf 直连单连接约 1.6 MB/s 且会静默卡死；hf-mirror 对大文件只做 308 转发无加速；aria2c 16 连接稳定 7-8 MB/s（2026-08 起 HF 新仓走 Xet 后端整体限速，应对与停滞看门狗规范见 download.md）。下载与评测不并行。

### 第 2 步 · 部署

启动模板、推理深度控制（混合推理模型必须显式降档，否则可能过度思考或零输出）、`model` 字段传完整路径等细节见 [methodology.md](references/methodology.md)。**测完即停服务**。

### 第 3 步 · 题库评测（维度一 + 二）

```bash
python3 scripts/run_bench.py nothink --model <模型完整路径>   # 按矩阵轴换 group 标签重跑
python3 scripts/run_bench.py nothink --list                  # 先看题目与可跑状态
```

题库 = 内置公开题 + 私有题外置合并（见下节）。支持断点续跑（同 group 已有结果的题自动跳过）、`--only` 单题重测。配置矩阵（推理深度 x 温度 x 上下文）见 [methodology.md](references/methodology.md)。

### 第 4 步 · 吞吐专项 + 硬件画像（必测）

```bash
python3 scripts/throughput_bench.py final --model <模型完整路径> --levels 1,2,4,8
python3 scripts/hw_sampler.py final <引擎进程pid> &   # 随测采样
python3 scripts/hw_summary.py final                   # 汇总峰值/活跃均值
```

TTFT 冷/热都要记录；服务器需以 decode 并发 >= 最大级别启动。口径声明已固定写入结果 JSON。

### 第 5 步 · Agent 集成（可选，维度三）

```bash
BENCH_SANDBOX=<沙盒git仓> BENCH_TASK='<任务文本>' BENCH_MODEL=<模型路径> \
  bash scripts/run_agent.sh pi bug
```

沙盒每轮 reset 保证可比；pi/dsh/opencode 的端点接法见 [methodology.md](references/methodology.md)。

### 第 6 步 · 收尾

停服务与采样进程；按 [report-contract.md](references/report-contract.md) 出回执并沉淀落点（知识库档案 + 总览行；Artifact 可选）。旧模型删除只提醒不代删。

## 题库分层（题库文件为唯一真源）

- **公开题内置**：`questions/` 共 15 题——A1/A2/A3/A4（速度，A2/A4 为占位题）、B1/B2/B3（社区经典，保留英文原题保证横向可比）、C3（公开代码修 bug，判定 harness 内置题目文件）、D1/D2/D3a/D3b（中文写作/数学/逻辑陷阱）、E1/E2/E3（Agent 前置）。
- **私有题外置**：本机私有题目录运行时合并加载，**qid 冲突私有覆盖**；目录解析顺序与题目字段规范见 [question-format.md](references/question-format.md)。
- **占位题设计**：A2/A4 依赖本机真实长代码文件，`context_file` 未配置时自动跳过并在回执标注 skipped 与原因，不算失败。
- 改题=改题目文件；文档与知识库只保留概览与意图说明。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| 环境检查 | <已检查/被阻塞> | <引擎+版本> | 不适用 | <正常/降级/异常> | <RFC3339-with-timezone> | <可继续选型/缺口> |
| 题库评测 | <已完成/部分完成> | <模型标识> | 不适用 | <正常/异常> | <RFC3339-with-timezone> | <PASS/FAIL/待人工/skipped 计数> |
| 吞吐专项 | <已完成/跳过> | <模型标识> | 不适用 | <正常/异常> | <RFC3339-with-timezone> | <聚合峰值@并发> |
| Agent 集成 | <已完成/跳过> | <agent 名单> | 不适用 | <正常/异常> | <RFC3339-with-timezone> | <PASS/FAIL 摘要> |

只为实际执行过的阶段输出行；本技能自身无版本概念的行填「不适用」。

## 安全边界

- 引擎与依赖安装走官方渠道（brew / pip / 官网安装包），不执行 pipe-to-shell 的远程脚本；来源不明的转换脚本一律「下载 → 审阅 → 本地执行」三段式。
- 权重只从模型发布方官方仓库获取；下载命令不携带 token。
- 评测脚本只请求用户指定的本机/局域网端点，只读取题库与用户点名的 context 文件；node 判定只执行题目文件内置的 harness。
- 改机动作（装引擎、下载权重、启停服务）逐项确认后执行；只读检查不改任何配置。
- 不采集、不上传任何客户代码；私有题与业务代码永不出现在公开产物里。

## 前向测试

改脚本或题库后必须跑通（无服务器、不改机）：

```bash
python3 -m py_compile scripts/*.py                      # 语法
python3 scripts/run_bench.py nothink --mock --workdir <临时目录>  # 全管线：题库加载→判定→落盘→回执
python3 scripts/run_bench.py nothink --list             # 题目清单与占位题跳过状态
python3 scripts/env_check.py --json                     # 真实只读探测
```

`--mock` 用题目内置 `mock_response` 走真实判定引擎，预期：自动判定题全 PASS（8 题）、B/D 人评题待人工（5 题）、A2/A4 标 skipped、结果写入 `results/nothink.jsonl` 且带 `"mock": true` 标记。私有题目录放一个覆盖同 qid 的文件重跑 `--list`，应看到「覆盖 1 道」。
