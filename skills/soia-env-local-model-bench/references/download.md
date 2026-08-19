# 模型权重下载方案（aria2c 多连接）

实测结论来自维护者 2026-08 多次真实下载（国内网络环境，20G-100G 级权重）。
网络环境不同数字会变，但故障模式（单连接慢、静默卡死）是工具行为，普遍适用。

## 为什么不用 hf download 直下

| 方式 | 实测行为 |
|---|---|
| `hf download` 直连 | 单连接约 1.6 MB/s，且会**静默卡死**：进程在、文件不增长，只能盯文件 mtime 才能发现 |
| `hf-mirror.com` | 对大文件只做 308 转发回 HF 源站，**没有加速效果**，还多一跳 |
| `aria2c` 16 连接 | 稳定 7-8 MB/s（同环境约 5 倍），断线自动重连，断点续传 |

## aria2c 方法

1. 配置类小文件（`config.json`、tokenizer 等）先用 `hf download` 拿到——小文件单连接无所谓。
2. 从 `model.safetensors.index.json`（GGUF 则按分片命名规则）生成分片 URL 列表。
3. 逐个分片下载：

```bash
aria2c --split=16 --max-connection-per-server=16 --min-split-size=50M \
  --continue=true --max-tries=0 --retry-wait=5 \
  -d <模型目录> -o <分片文件名> "<分片URL>"
```

4. **完整性验证（必做）**：分片数与 index.json 一致；无 `.aria2` 控制文件残留；
   总大小符合预期。少一个分片模型照样加载失败且报错难读。

## 其他来源

- ModelScope 是备选（Qwen 系官方多有同步），但注意多为 lmstudio-community 打包，
  非 mlx-community 官方量化——引擎格式要对上。
- 下载与评测不要并行：大文件下载抢内存带宽，实测拖慢推理单流 40% 以上。

## 安全边界

- 只从模型发布方官方仓库（HuggingFace / ModelScope 官方组织页）取权重 URL。
- 不执行来源不明的转换脚本；转换需求走引擎官方文档的转换命令。
- 下载命令不携带任何 token；私有仓库鉴权走 provider 官方登录流程，本技能不代管。
