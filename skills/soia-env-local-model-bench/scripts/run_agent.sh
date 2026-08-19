#!/bin/bash
# Agent 集成测试执行器：评测 Agent CLI（pi/dsh/opencode）挂本地模型端点后能否完成真实仓库任务。
#
# 用法: run_agent.sh <pi|dsh|opencode> <task-id>
# 任务文本与沙盒都不进技能包，由环境变量提供（不含任何秘密值）：
#   BENCH_SANDBOX          必填  独立 git 沙盒仓路径；每轮先 git reset --hard && git clean -fd
#   BENCH_TASK             必填  交给 Agent 的任务文本（或用 BENCH_TASK_FILE 指向文本文件）
#   BENCH_TASK_FILE        可选  从文件读任务文本，优先于 BENCH_TASK
#   BENCH_WORKDIR          可选  结果目录，默认 ~/local-model-bench
#   BENCH_MODEL            pi/dsh 需要  模型标识（mlx 为模型完整路径）
#   BENCH_PI_PROVIDER      可选  pi 的 provider 名，默认 mlx
#   BENCH_DSH_PATCH        dsh 需要  dsh --patch 的 patch 文件路径
#   BENCH_OPENCODE_MODEL   opencode 需要  provider/model 别名
#   BENCH_TIMEOUT          可选  超时秒数，默认 1500（缺 timeout 命令则不限时并提示）
#
# 判定契约: 沙盒仓必须用 `npm test` 承载验收（node:test 风格输出 ✔/✖）。
#   PASS = 全部测试通过 且 未改任何 tests/ 文件 且 至少有 1 个通过的测试。
# 输出: $BENCH_WORKDIR/results/agent_<agent>_<task>.json 与 outputs/agent/<agent>_<task>.log
set -u

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

[ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] && usage 0
[ $# -lt 2 ] && usage 1

AGENT=$1
TASK_ID=$2
WORKDIR=${BENCH_WORKDIR:-$HOME/local-model-bench}
TIMEOUT_S=${BENCH_TIMEOUT:-1500}
SANDBOX=${BENCH_SANDBOX:-}

[ -z "$SANDBOX" ] && { echo "缺 BENCH_SANDBOX（沙盒 git 仓路径）"; exit 1; }
git -C "$SANDBOX" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || { echo "BENCH_SANDBOX 不是 git 仓：每轮要 reset 保证可比"; exit 1; }

if [ -n "${BENCH_TASK_FILE:-}" ]; then
  TASK=$(cat "$BENCH_TASK_FILE")
else
  TASK=${BENCH_TASK:-}
fi
[ -z "$TASK" ] && { echo "缺任务文本：设 BENCH_TASK 或 BENCH_TASK_FILE"; exit 1; }

TIMEOUT_CMD=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD="timeout $TIMEOUT_S"
else
  echo "警告: 未发现 timeout 命令，本轮不限时（brew install coreutils 可补齐）"
fi

mkdir -p "$WORKDIR/outputs/agent" "$WORKDIR/results"
LOG=$WORKDIR/outputs/agent/${AGENT}_${TASK_ID}.log

cd "$SANDBOX" || exit 1
git reset --hard -q && git clean -fdq

T0=$(date +%s)
case $AGENT in
  pi)
    [ -z "${BENCH_MODEL:-}" ] && { echo "pi 需要 BENCH_MODEL"; exit 1; }
    $TIMEOUT_CMD pi --provider "${BENCH_PI_PROVIDER:-mlx}" --model "$BENCH_MODEL" \
      --no-session -p "$TASK" > "$LOG" 2>&1 ;;
  dsh)
    [ -z "${BENCH_DSH_PATCH:-}" ] && { echo "dsh 需要 BENCH_DSH_PATCH（patch 文件路径）"; exit 1; }
    $TIMEOUT_CMD dsh --profile headless --patch "$BENCH_DSH_PATCH" "$TASK" > "$LOG" 2>&1 ;;
  opencode)
    [ -z "${BENCH_OPENCODE_MODEL:-}" ] && { echo "opencode 需要 BENCH_OPENCODE_MODEL"; exit 1; }
    $TIMEOUT_CMD opencode run -m "$BENCH_OPENCODE_MODEL" "$TASK" > "$LOG" 2>&1 ;;
  *) echo "未知 agent: $AGENT（支持 pi|dsh|opencode）"; usage 1 ;;
esac
EXIT_CODE=$?
T1=$(date +%s)

TEST_OUT=$(npm test 2>&1)
FAILS=$(echo "$TEST_OUT" | grep -cE "^✖ " || true)
PASSES=$(echo "$TEST_OUT" | grep -cE "^✔ " || true)
TOUCHED_TESTS=$(git diff --name-only | grep -c "^tests/" || true)
DIFF_STAT=$(git diff --stat | tail -1)

AGENT_NAME=$AGENT TASK_NAME=$TASK_ID WALL=$((T1-T0)) AGENT_EXIT=$EXIT_CODE \
PASSES=$PASSES FAILS=$FAILS TOUCHED=$TOUCHED_TESTS DIFF_STAT=$DIFF_STAT \
OUT_PATH=$WORKDIR/results/agent_${AGENT}_${TASK_ID}.json \
python3 - << 'PYEOF'
import json, os
from datetime import datetime
env = os.environ
rec = {
    "agent": env["AGENT_NAME"], "task": env["TASK_NAME"],
    "wall_s": int(env["WALL"]), "agent_exit": int(env["AGENT_EXIT"]),
    "tests_pass": int(env["PASSES"]), "tests_fail": int(env["FAILS"]),
    "touched_test_files": int(env["TOUCHED"]),
    "diff_stat": env["DIFF_STAT"].strip(),
    "checked_at": datetime.now().astimezone().replace(microsecond=0).isoformat(),
}
rec["verdict"] = "PASS" if (rec["tests_fail"] == 0 and rec["touched_test_files"] == 0
                            and rec["tests_pass"] > 0) else "FAIL"
json.dump(rec, open(env["OUT_PATH"], "w"), ensure_ascii=False, indent=2)
print(json.dumps(rec, ensure_ascii=False))
PYEOF
