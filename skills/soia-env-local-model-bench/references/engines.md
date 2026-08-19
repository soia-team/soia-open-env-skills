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
| **oMLX** | MLX 生态第三方 runtime（brew 分发） | MLX 模型的替代宿主 | 实测（2026-08）对新架构跟进滞后（如推测解码新版架构未支持），只作备选 | brew |

## 场景推荐（Apple Silicon）

| 场景 | 推荐 | 理由 |
|---|---|---|
| 认真评测、要可控参数与最高单机吞吐 | mlx-lm | 端点、推理深度、并发、prompt cache 全可控，本技能默认引擎 |
| 模型只有 GGUF / 超大 MoE 内存吃紧 | llama.cpp | CPU offload 让 128G 内存跑 100G 级权重成为可能 |
| 快速试用、不折腾 | Ollama 或 LM Studio | 一条命令/纯图形界面，但横比数字前先对口径 |
| Linux + NVIDIA 服务化 | vLLM | 本技能首版不覆盖，仅指路 |

## 环境判定门槛（评测前核对）

- **内存**：权重大小 + KV cache + 系统余量。经验：8bit 27B 级常驻约 27-28G；
  3bit 100G 级权重需接近独占 128G 整机。内存不足优先降量化位宽或换小模型，不硬跑。
- **磁盘**：模型目录按「权重大小 x 想保留的模型数」预留；下载中另需临时空间。
- **推理深度**：混合推理模型默认档位可能严重过度思考（社区实测简单任务 20+ 分钟），
  评测矩阵必须显式控制（见 methodology.md）。
