# 题库文件格式与私有题外置

**题库文件是唯一真源**：改题=改题目文件，文档只保留概览与意图。
公开题内置技能包 `questions/`；私有题放本机外置目录，运行时合并加载。

## 加载与合并规则

1. 先加载技能包 `questions/*.yaml`（也接受 `.yml` / `.json`）。
2. 再找私有题目录，取第一个存在的：
   `--private-questions` 参数 → 环境变量 `SOIA_ENV_LOCAL_MODEL_BENCH_QUESTIONS_DIR`
   → config 的 `private_questions_dir` → `~/.config/soia-skills/soia-env-local-model-bench/questions/`
   → `~/.config/soia-skills/soia-open-env-skills/skills/soia-env-local-model-bench/questions/`。
3. 私有目录内的题目**同 qid 覆盖公开题，新 qid 直接加入**。回执会写明新增/覆盖数量。
4. 私有题（如取材真实业务代码的 C1/C2）**绝不进开源技能仓**，也不出现在对外分享的报告正文里
   （横比表只出现 qid 与通过与否，不出现题面与代码）。

## 字段说明

```yaml
qid: C1                  # 必填，唯一标识；横比表按 qid 对齐
cat: 真实代码-私有bug      # 分类标签
temp: 0.0                # 温度（判定题一律 0；创意写作类 B1-B3/D1 用 0.7）
max_tokens: 6000
groups: [nothink, low]   # 可选：只在这些 group 跑
only_group: nothink      # 可选：只在这一个 group 跑
context_file: null       # 可选：长 prompt 占位题指向本机代码文件；null 则跳过并标 skipped
max_context_chars: 20000 # 可选：context 截断长度
context_code: |          # 可选：判定时需要拼在模型输出前面的上下文代码（如题面给出的函数）
  function helper() { ... }
prompt: |                # 必填；可含 {context} 占位符（由 context_file 内容替换）
  题面……
mock_response: |         # 可选：--mock 自测管线时使用的固定回答
  ……
check:                   # 必填；type 决定判定方式
  type: node_snippet
  ...
```

## check 类型

| type | 行为 | 专有字段 |
|---|---|---|
| `speed` | 只计时不判对错 | 无 |
| `save` | 抽出代码块存为文件，待人工评审 | `ext`: svg/html |
| `manual` | 待人工评审 | 无 |
| `regex` | 三态：结尾 `tail` 字符内命中任一 `any_patterns` 且全文不命中 `reject` = PASS；只命中 `reject`（或都不中）= FAIL；**两者同时命中 = 转 MANUAL**（矛盾信号，典型：辟谣式输出正确结论时原文引用了错误说法——正则无法裁决真实结论） | `tail`、`any_patterns`、`reject` |
| `node_snippet` | 抽出 js 代码块 + `test` 拼成脚本用 node 执行，stdout 出现 PASS 则过 | `test`（必填）、`prepend_context`（true 时把 `context_code` 拼在模型代码前） |
| `json_expect` | 解析 JSON 后逐条校验 | `exact_keys`、`expects[]`（`path` 支持 `a|b.c` 字段名兼容；规则：`equals`/`in`/`lower_in`/`type`/`min`/`max`/`min_len`/`regex`） |
| `lines_expect` | 去空行后逐行校验 | `min_lines`、`lines[]`（`contains`/`regex`） |

## 私有题模板（业务代码修 bug 类）

放进私有目录即可被加载，例如 `~/.config/soia-skills/soia-env-local-model-bench/questions/C1.yaml`：

```yaml
qid: C1
cat: 真实代码-私有bug
temp: 0.0
max_tokens: 6000
check:
  type: node_snippet
  prepend_context: false     # 模型须输出完整函数时为 false；只输出新增函数时设 true
  test: |
    const cases=[[输入, 期望], ...];
    let ok=true;
    for(const [x,exp] of cases){ if(yourFn(x)!==exp){ok=false;console.error("FAIL "+x);} }
    console.log(ok?"PASS":"FAIL");
prompt: |
  下面是<业务系统>里的工具函数。用户报告 bug：<现象>。
  ```js
  <真实业务代码片段>
  ```
  找出 bug 并修复。只输出修复后的完整函数，一个 js 代码块。
```

新增功能类（C2 风格）把题面上下文放 `context_code`、`prepend_context: true`，
让判定时模型输出可以合法引用题面已给出的函数。

## Markdown 题目格式（知识库友好，2026-08-20 起支持）

私有题常放在 Obsidian 等 Markdown 知识库中维护，`.md` 题目与 `.yaml` 等价且在库内可读可编辑：

- **frontmatter**（YAML）承载标量与配置：`qid`、`cat`、`temp`、`max_tokens`、`check:`（嵌套 mapping，含 `type` 等非大文本字段）。无 frontmatter 或无 `qid` 的 md 文件（如目录说明文档）自动跳过，不报错。
- **正文四个固定 section 承载大文本**（行首 `## ` 精确匹配这四个名字，其余行首 `## `——包括代码块里的——不会被误认为分隔符）：
  - `## prompt`：题面原文（代码围栏保留，判定层自会剥离）
  - `## check.test`：取本节第一个代码块作为判定脚本
  - `## check.prepend_context`：取第一个代码块，判定时拼在模型代码前
  - `## mock_response`：`--mock` 自检用的正确实现（原文，可含围栏）
- section 之外的正文（标题、说明、战绩记录）不进入题面，可自由书写。
- 同一目录同 qid 的 `.yaml` 与 `.md` 并存时后加载者覆盖（按文件名排序 md 在后）；请保持单一真源，删除旧格式。
