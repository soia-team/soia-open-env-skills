# SQLite 日志写放大诊断

本文件只在用户提到 `logs_2.sqlite`、TRACE、WAL、SSD 写入或 Codex 长时间运行变慢时加载。

## 目录

- [判断模型](#判断模型)
- [只读采样](#只读采样)
- [分级判定](#分级判定)
- [解决方案](#解决方案)

## 判断模型

同时回答四个问题：

| 问题 | 指标 | 不能推出的结论 |
|---|---|---|
| 文件是否变大 | 主库、`-wal`、`-shm` 两次大小 | 文件稳定不等于没有插入/清理 |
| 写入是否持续 | `MAX(id)`、`sqlite_sequence.seq` 时间差 | ID 速率不是物理 SSD 写入量 |
| 谁在写、写什么 | 持有进程、`level`、`target`、时间窗口 | 看到 TRACE 行不等于复现原始事故 |
| SSD 是否受损 | SMART 寿命、错误、温度、累计写入 | 数据库估算字节不能替代 SSD `Data Units Written` |

原始事故的强证据组合是：短时间 `MAX(id)` 高速推进、保留行数近似不变、TRACE/SSE/桥接目标占主导，并伴随 WAL 或系统写入增长。

## 只读采样

### 1. 定位文件和持有进程

使用当前用户的 `CODEX_HOME`；未设置时才使用默认目录。不要写死维护者路径：

```bash
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
DB_PATH="$CODEX_HOME_DIR/logs_2.sqlite"

for p in "$DB_PATH" "$DB_PATH-wal" "$DB_PATH-shm"; do
  if [ -e "$p" ] || [ -L "$p" ]; then
    printf '%s ' "$p"
    wc -c < "$p"
    if [ -L "$p" ]; then readlink "$p"; fi
  fi
done
lsof -nP "$DB_PATH" "$DB_PATH-wal" "$DB_PATH-shm" 2>/dev/null || true
```

Windows 使用 `Get-Item` 查看三个文件，用任务管理器或 Process Explorer 确认 `Codex`、`ChatGPT` 或 `codex` 进程。

### 2. 只读读取 SQLite

必须使用 `-readonly` 和 `mode=ro`，避免诊断命令创建或修改数据库：

```bash
sqlite3 -readonly "file:${DB_PATH}?mode=ro" <<'SQL'
.headers on
.mode column
PRAGMA integrity_check;
SELECT COUNT(*) AS retained_rows,
       MIN(id) AS min_id,
       MAX(id) AS max_id,
       SUM(COALESCE(estimated_bytes, 0)) AS estimated_payload_bytes
  FROM logs;
SELECT seq AS sqlite_sequence_max_id
  FROM sqlite_sequence WHERE name = 'logs';
SELECT level, COUNT(*) AS rows,
       SUM(COALESCE(estimated_bytes, 0)) AS estimated_payload_bytes
  FROM logs GROUP BY level ORDER BY rows DESC;
SELECT target, level, COUNT(*) AS rows,
       SUM(COALESCE(estimated_bytes, 0)) AS estimated_payload_bytes
  FROM logs
  WHERE ts >= CAST(strftime('%s','now','-10 minutes') AS INTEGER)
  GROUP BY target, level ORDER BY rows DESC LIMIT 20;
SQL
```

若 schema 不同，先只读执行 `.schema` 和 `PRAGMA table_info(<table>)`，再调整查询。若不存在 `sqlite_sequence`，将其记为“不可用”，不要创建它。

禁止在本分支执行：`VACUUM`、`wal_checkpoint`、`ANALYZE`、`CREATE TRIGGER`、`DELETE`、`UPDATE`、`PRAGMA journal_mode=...` 或任何清理命令。

### 3. 两次采样

至少间隔 30–60 秒，记录以下字段：

```bash
date '+%Y-%m-%d %H:%M:%S%z'
for p in "$DB_PATH" "$DB_PATH-wal" "$DB_PATH-shm"; do
  if [ -e "$p" ]; then printf '%s ' "$p"; wc -c < "$p"; fi
done
sqlite3 -readonly "file:${DB_PATH}?mode=ro" \
  "SELECT COUNT(*), MIN(id), MAX(id) FROM logs;"
sqlite3 -readonly "file:${DB_PATH}?mode=ro" \
  "SELECT level, target, COUNT(*) FROM logs WHERE ts >= CAST(strftime('%s','now','-1 minute') AS INTEGER) GROUP BY level, target ORDER BY COUNT(*) DESC LIMIT 10;"
```

报告 `delta_bytes / seconds`、`delta_max_id / seconds`、保留行数变化、WAL 变化和热点 target。没有进程级物理 I/O 证据时，明确写“无法把 SSD 写入归因到 Codex”。

## 分级判定

| 等级 | 证据 | 结论 | 下一步 |
|---|---|---|---|
| L0 | 文件/WAL 稳定，ID 变化小，无热点 | 未见异常 | 转查其他类别 |
| L1 | ID 持续增加，但文件/WAL 有界 | 有残余日志活动，未证明 SSD 高风险 | 更新/重启后复测 |
| L2 | ID 高速推进，TRACE/SSE/桥接目标占主导，WAL/文件同步增长 | 高写入风险 | 保存证据，确认无任务后退出、更新、复测 |
| L3 | 持续快速增长并伴随空间下降、资源失控或 SMART 预警 | 紧急风险 | 先备份；确认后隔离日志库，另行处理硬件 |

这些是排障启发式，不是 SSD 厂商寿命标准。保留行数稳定不等于没有写入；数据库字节数也不等于 SSD 主机写入量。

## 解决方案

| 顺序 | 方案 | 是否修改状态 | 使用条件 |
|---|---|---|---|
| 1 | 建议更新桌面版/CLI，完全退出后重启并复测 | 只有客户明确要求最新版才执行 | 版本旧或出现 L1/L2 |
| 2 | 确认并关闭重复进程 | 是，需确认 | 没有正在执行的任务 |
| 3 | 备份后隔离 `logs_2.sqlite`、`-wal`、`-shm` | 是，需确认 | L2/L3 且无持有者 |
| 4 | `VACUUM` | 是，高风险 | 仅备份后回收空闲页；不能修复持续写入 |
| 5 | 触发器、改 WAL、RAM 盘 | 是，高风险 | 仅高级维护人员明确选择；不作为默认方案 |

隔离前必须展示目标、备份目录、回滚方式和日志历史影响。诊断请求到此结束，不执行任何状态变更。
