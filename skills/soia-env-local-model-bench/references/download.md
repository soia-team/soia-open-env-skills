# 模型权重下载方案（aria2c 多连接）

实测结论来自维护者 2026-08 多次真实下载（国内网络环境，20G-100G 级权重）。
网络环境不同数字会变，但故障模式（单连接慢、静默卡死）是工具行为，普遍适用。

## 为什么不用 hf download 直下

| 方式 | 实测行为 |
|---|---|
| `hf download` 直连 | 单连接约 1.6 MB/s，且会**静默卡死**：进程在、文件不增长，只能盯文件 mtime 才能发现 |
| `hf-mirror.com` | 对大文件只做 308 转发回 HF 源站，**没有加速效果**，还多一跳 |
| `aria2c` 16 连接 | 稳定 7-8 MB/s（同环境约 5 倍），断线自动重连，断点续传 |

## HF Xet 后端限速（2026-08 起）

HF 新仓普遍改走 Xet 存储（下载重定向到 `*.cdn.hf.co/xet-bridge-*`），命中它时上表速度数字不适用：

- 匿名单连接实测 17-140 KB/s 且波动大；aria2c 16 连接聚合也可能只有约 330 KB/s——多连接对 Xet 限速收益有限。
- hf-mirror 对 Xet 仓库同样只做 308 回源，无加速。
- HF 官方提示登录后可解锁更高速率：有账号的用户先 `hf auth login` 是第一杠杆（provider 官方登录流程，凭据由 hf CLI 保管，仍不在下载命令行携带 token）。
- 网络链路变化（如代理节点切换）会让 aria2c 报 `SSL/TLS handshake failure: hostname does not match` 退出；断点无损，原命令重启即续传。

## aria2c 方法

1. 配置类小文件（`config.json`、tokenizer 等）先拿到。**别用带激进 `--max-time` 的 curl**：
   实测 17MB 的 `tokenizer.json` 正值 CDN 慢速期（单连接约 140 KB/s）被 `--max-time 60`
   静默截断到 15%，直到服务加载报 `JSONDecodeError` 才暴露。小文件也用 aria2c 多连接
   （或 hf 直下），且同样进入下方完整性验证。
2. 从 `model.safetensors.index.json`（GGUF 则按分片命名规则）生成分片 URL 列表。
3. 逐个分片下载：

```bash
aria2c --split=16 --max-connection-per-server=16 --min-split-size=50M \
  --continue=true --max-tries=0 --retry-wait=5 \
  -d <模型目录> -o <分片文件名> "<分片URL>"
```

4. **完整性验证（必做，见下节）**：覆盖所有文件，不只权重。

## 完整性验证（必做，覆盖所有文件）

加载时才暴露的截断是最贵的失败。下载完成后逐一核对，**所有文件都查，不只权重分片**：

1. **字节数对账**：对照 HF API `https://huggingface.co/api/models/<repo>/tree/main`
   返回的每个文件 `size` 字段，逐一比对本地文件字节数，必须全等。
2. **权重头部可解析**：safetensors 文件读前 8 字节（小端 uint64 = 头部 JSON 长度），
   按该长度读出 JSON 头并成功解析才算通过——能截住「大小接近但内容坏掉」的分片。
3. 分片数与 `model.safetensors.index.json` 一致；目录内无 `.aria2` 控制文件残留。

少一个分片或截断一个 tokenizer，模型照样加载失败且报错难读。

## 停滞看门狗：禁用 du/文件大小判进度

aria2c 预分配（prealloc）后文件表面大小从一开始就是全尺寸，**用 `du` 或文件大小对比判停滞必然误判**。
真实事故：看门狗每 60 秒比对 `du` 认定「零进度」并重启 aria2c，下载被反复打断近两小时。规范：

- 进度必须解析同名 `.aria2` 控制文件的 bitfield：格式为 2 字节版本 + 4 字节 ext +
  4 字节 infohash 长度 + infohash + 4 字节 piece 长度 + 8 字节总长 + 8 字节已上传长 +
  4 字节 bitfield 长度 + bitfield；数 bitfield 置位 bit x piece 长度即已完成字节。
- 重启阈值给宽：**持续 15 分钟零进度再重启**——慢不等于死，Xet 限速期尤其如此。

## 其他来源

- ModelScope 是备选（Qwen 系官方多有同步），但注意多为 lmstudio-community 打包，
  非 mlx-community 官方量化——引擎格式要对上。
- 下载与评测不要并行：大文件下载抢内存带宽，实测拖慢推理单流 40% 以上。

## 安全边界

- 只从模型发布方官方仓库（HuggingFace / ModelScope 官方组织页）取权重 URL。
- 不执行来源不明的转换脚本；转换需求走引擎官方文档的转换命令。
- 下载命令不携带任何 token；私有仓库鉴权走 provider 官方登录流程，本技能不代管。
