# 推理引擎选型对比

环境检查（`env_check.py`）报事实，本页负责判断。实测条目来自维护者在 M4 Max 128GB /
macOS 上的评测（2026-08 核对）；通用条目来自各项目公开资料（2026-08 核对）。
硬件或引擎大版本升级后需复核。

## 对比表

| 引擎 | 形态与格式 | 强项 | 局限 | 安装 |
|---|---|---|---|---|
| **mlx-lm** | Python 包，Apple Silicon 专用（Metal）；MLX 量化格式（mlx-community 打包） | `mlx_lm.server` 原生 OpenAI 兼容端点；`--chat-template-args` 精确控推理深度；prompt cache 让热 TTFT 骤降；`--decode-concurrency` 并发批处理（实测并发聚合可达单流数倍） | 只有 Apple Silicon；模型必须是 MLX 格式；`model` 字段必须传完整路径（别名会触发去 HF 拉仓库） | venv 内 `pip install mlx-lm` |
| **llama.cpp** | C++ 通用引擎；GGUF 格式 | `llama-server` OpenAI 兼容；`-ngl`/`--n-cpu-moe` 分层放置，超大 MoE 可把专家放 CPU（实测 3bit 大模型 98G RSS 可跑，CPU 千percent 级参与）；思考内容在 `reasoning_content` 字段 | 单请求吞吐通常低于 mlx-lm 同档；参数矩阵复杂 | `brew install llama.cpp` 或源码编译 |
| **Ollama** | llama.cpp 封装，模型库一条命令拉取 | 上手最快，适合先试再深测 | 量化版本选择有限；服务参数可调空间小；测速口径与直连 llama-server 有差 | 官网安装包 |
| **LM Studio** | 图形界面（内核含 llama.cpp 与 MLX 双引擎），附 `lms` CLI | 完全不想碰终端的用户；内置下载器 | 打包多为 lmstudio-community 而非 mlx-community 官方量化；自动化评测不便 | 官网安装包 |
| **vLLM** | 服务级引擎（PagedAttention、连续批处理） | 多卡/高并发服务化的事实标准 | 主战场 NVIDIA/Linux；macOS 无 Metal 加速——本技能首版不覆盖 | 不在首版范围 |
| **oMLX** | MLX 生态第三方 runtime（github.com/jundot/omlx，brew 分发）；多模型 LRU 服务器 | OpenAI 兼容；**M 系旧芯片（M4 及更早）跑 MTP 投机解码的可用路线**——mlx-lm 不支持 qwen3_5_mtp 架构，oMLX 已并入 PR 990 补丁（2026-08 实测生效） | per-model 配置只在启动时生效；进程名与 CLI 名不一致，易误判存活（见下方运行要点） | brew |

## 场景推荐（Apple Silicon）

| 场景 | 推荐 | 理由 |
|---|---|---|
| 认真评测、要可控参数与最高单机吞吐 | mlx-lm | 端点、推理深度、并发、prompt cache 全可控，本技能默认引擎 |
| 模型只有 GGUF / 超大 MoE 内存吃紧 | llama.cpp | CPU offload 让 128G 内存跑 100G 级权重成为可能 |
| 快速试用、不折腾 | Ollama 或 LM Studio | 一条命令/纯图形界面，但横比数字前先对口径 |
| M4 及更早芯片跑 MTP 投机解码 | oMLX | mlx-lm 不支持 qwen3_5_mtp 架构，oMLX 可用（运行要点见下节） |
| Linux + NVIDIA 服务化 | vLLM | 本技能首版不覆盖，仅指路 |

## oMLX 运行要点（MTP 投机解码宿主）

- 启动：`omlx serve --model-dir <模型根目录>`——扫描子目录，**model_id = 目录名**。
- per-model 配置在 `~/.omlx/model_settings.json`：

  ```json
  {"version": 1, "models": {"<model_id>": {"mtp_enabled": true, "mtp_num_draft_tokens": 3, "enable_thinking": false}}}
  ```

  **只在服务启动时生效**，改配置必须重启服务。
- **进程名陷阱**：运行时进程名是 `omlx-server`，`pkill -f "omlx serve"` 杀不掉——
  按 PID 杀或 `pkill -f omlx-server`。杀不干净的假重启会直接制造假对照
  （见 methodology.md 配置对照实验一节）。
- **MTP 生效证据（两条都核对，缺任一不得声称在测投机解码）**：
  启动加载日志出现 `Speculative backend selected ... (active)` 行；
  运行日志出现 `MTP[...] accept=.../...(%)` 行（含接受率与每周期 token 数）。

## 环境判定门槛（评测前核对）

- **内存**：权重大小 + KV cache + 系统余量。经验：8bit 27B 级常驻约 27-28G；
  3bit 100G 级权重需接近独占 128G 整机。内存不足优先降量化位宽或换小模型，不硬跑。
- **磁盘**：模型目录按「权重大小 x 想保留的模型数」预留；下载中另需临时空间。
- **推理深度**：混合推理模型默认档位可能严重过度思考（社区实测简单任务 20+ 分钟），
  评测矩阵必须显式控制（见 methodology.md）。

## GPU 显存边界与投机 draft 增量

macOS Metal 默认 wired limit ≈ 物理内存的 75%（128G 整机约 96G 可供 GPU）。
投机解码的 draft 模型是纯 GPU 增量（例：DSpark Q8 draft 约 10.6G），可能把原本
贴边可跑的主模型推过界。症状隐蔽：**加载成功，首个请求才炸**——
`kIOGPUCommandBufferCallbackErrorOutOfMemory` 或 `llama_encode(ctx_dft) rc=-3`。
应对按侵入性从低到高，改完都必须实测：

1. **draft 放 CPU**（llama.cpp `-ngld 0`）：实测可能负优化——draft 前向开销吃掉投机收益
   （例：15.0 tok/s，反低于 17-20 的无投机基线），不默认有效。
2. **主模型多挪层到 CPU**（`--n-cpu-moe` 上调）：能进界，但基线本身会掉。
3. **抬 wired limit**：`sudo sysctl iogpu.wired_limit_mb=<MB>`（需管理员密码，重启后恢复默认）。
   最有效，但必须给系统侧留足内存；属改机动作，先向客户展示计划并确认。

## 思考依赖性三态测试（llama.cpp 的 reasoning-budget）

不同模型对 thinking 的依赖方向相反（实测 Qwen 关掉快 3-5 倍不掉分；Nemotron 关掉判别集反从 8/9 崩到 5/9）。评测新模型时把 thinking 当三态变量测：**全开 / 全关 / 开+预算受控**。llama.cpp 的预算受控用 `--reasoning-budget <N>`（如 2000：允许思考但注入 end-of-thinking 防止思考吃光输出预算——Nemotron 实测三态里它最优）；注意 `--reasoning-budget 0`（立即结束）对部分模型模板不生效，必须按「配置对照实验规范」验证 reasoning_content 实际长度再采信。mlx-lm 无预算参数，只有模板开关（--chat-template-args）。
