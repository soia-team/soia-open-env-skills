---
name: soia-env-node-install
description: 为新手安装、验证或按授权更新 Node.js 与 npm。触发：「安装 Node.js」「更新 Node.js」「node 命令不存在」
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.4.1
created_at: 2026-07-20 18:00:00
updated_at: 2026-07-27 10:47:17
created_by: gpt-5
updated_by: gpt-5.6-sol
---

# soia-env-node-install

优先使用 Node.js 官方 LTS 安装路径，并把“未安装、装了但 PATH 找不到、npm 源/权限问题、项目版本不匹配”分别诊断。不要在同一台机器上无计划地混用多个版本管理器。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Node.js | 识别系统/架构、选择官方 LTS、安装并验证 | Node/npm 版本和路径状态 |
| 检查 Node.js 更新 | 识别安装来源、比较项目约束与最新 Active LTS，不自动更新 | 当前版本、最新版本和来源 |
| 更新 Node.js 到最新 | 客户明确要求最新版后沿原来源更新 | 中间状态、版本变化和回滚边界 |
| npm 不可用 | 检查 PATH、npm prefix 和权限 | 阻塞原因与安全修复方案 |
| 为 Codex 准备环境 | 先验证 Node/npm，再交给 Codex 技能 | 可继续执行的 readiness 状态 |

### 客户如何使用

其他可识别说法包括「更新 Node 到最新」「安装 npm」「npm 超时」；纯网络故障优先交给 `soia-env-network-diagnose`。

1. 说目标项目、操作系统和是否需要特定 Node 大版本；不确定时默认选择最新官方 Active LTS，不固定写死一个永久版本号。
2. Agent 先检查现有 `node`、`npm` 和项目配置，不自动卸载旧版本。
3. 发现新版本时只汇报；只说“更新 Node”时先询问是否更新到最新，客户明确选择最新版后才执行。
4. 展示安装来源、版本和 PATH 影响；需要管理员权限时单独确认。
5. 安装或明确授权的更新过程中持续显示并记录检查、计划、执行、验证和终态。

### 依赖与安装

无必需外部 skill。网络问题先调用 `soia-env-network-diagnose`；Codex 需要 Node/npm 时由 `soia-env-codex-install` 消费本技能的结果。官方来源见 [official-sources.md](references/official-sources.md)。

## 默认版本策略

- 默认目标是 Node.js 官方最新 Active LTS；生产或长期维护项目不默认选择 Current 版本。
- 先读取 `.nvmrc`、`package.json` 的 `engines`、CI 配置和项目文档；项目约束优先于全局默认值。
- 当前已安装的 Current 版本不等于错误。若项目兼容且客户没有要求切换，不自动降级；回执中明确写出“已安装但不是默认 LTS”。
- 当前版本、LTS 状态和下载入口以 [Node.js Releases](references/official-sources.md) 为准。

## 已安装状态与更新

先判断来源，再更新；不把不同安装方式混在一起：

```bash
node --version
npm --version
command -v node
brew list --versions node 2>/dev/null || true
command -v nvm 2>/dev/null || true
```

- 已安装且满足项目约束：提示“Node.js 已安装，无需重复安装”，继续验证 npm、PATH 和项目版本。
- 已安装但为 Current：提示“已安装，当前不是默认 Active LTS”；是否切换由客户或项目约束决定，不自动降级。
- Homebrew 管理：只有客户明确要求更新到最新 Active LTS 后，才执行 `brew update && brew upgrade node`。
- nvm 管理：只有客户明确要求更新到最新 Active LTS 后，才执行 `nvm install --lts && nvm alias default 'lts/*' && nvm use --lts`；不同时再引入 Homebrew 或官方安装器。
- 官方安装器管理：从 Node.js 官方下载页取得目标 LTS 安装器覆盖更新，安装前记录现有版本和 PATH 状态。

模糊的“更新 Node”只执行版本比较并返回“等待确认是否更新到最新”，不能运行上述命令。明确安装一个缺失的 Node.js 可以安装推荐 Active LTS，不视为更新现有工具。

更新后重新加载 shell，再验证 `node --version`、`npm --version`、`npm config get prefix` 和项目版本约束。失败时保留旧版本，不自动卸载或清理。

## 标准流程

1. 只读检查 OS、架构、现有版本、PATH 是否含可执行文件和项目的 `.nvmrc`/`package.json` 版本要求；不打印完整环境变量。
2. 选择官方 LTS 安装器或官方认可的版本管理方式；一次只选择一种方法并记录。
3. 已安装时默认停在版本报告；只有明确要求最新版才进入更新计划。
4. 安装前确认下载源和权限；禁止未知镜像、修改 TLS 校验或 `curl | bash`。
5. 安装后重新解析 PATH；若需改 shell profile，先显示目标文件和追加内容并确认。
6. 验证 `node --version`、`npm --version`、`npm config get prefix`，并用 `npm --version` 作为最小 npm 健康检查。
7. 输出 `ready|missing|update_available|blocked` 和版本，交给上层环境编排或 Codex 技能。
8. 使用下方固定列表向客户汇报；只显示客户要求的目标工具。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| Node.js | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <RFC3339-with-timezone> | <无需重复安装/可更新，未执行/等待确认是否更新到最新/已更新/等待确认后安装/被阻塞：原因> |

- 用户只问 Node.js 时只输出 `Node.js` 行，不额外输出 npm；用户明确问 npm 时才增加 `npm` 行。
- `更新时间` 记录版本、PATH 和无害运行验证全部完成后的时间。
- 最新版本按项目约束与官方 Active LTS 判断；无法取得时写“未取得”，不猜测。
- 表格后只保留必要的权限确认、PATH 影响或阻塞说明，不展示内部探测流水账。

## 安装与更新的中间状态

真正执行安装或获得最新版授权的更新时，用随机 `run_id` 在阶段实际发生时立即调用 `scripts/record_install_progress.py`：检查前、方案形成后、安装器/更新器调用前、验证前和终态各记录一次；需要额外权限、换源或修改 PATH 时再记录 `waiting_confirmation`。不得结束后补写；时间由记录器生成。只读检查不调用。只有客户原话明确要求最新版时，更新执行阶段才带 `--customer-requested-latest`。

```bash
python3 scripts/record_install_progress.py --run-id <run-id> --action <install|update> --stage checking --status in_progress --result-code checking_started
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage updating --status in_progress --result-code update_started --customer-requested-latest
```

同时持续展示固定阶段表；成功、失败、取消或等待权限时都要追加终态：

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

## 权限与回滚

- 默认用户级安装；不主动使用 sudo 或管理员权限。
- 不删除旧 Node，不改项目锁文件，不全局安装业务依赖。
- 版本冲突时保留现状并请求选择；失败时提供官方卸载/修复路径，而不是自动清理。

## 私密信息与中间数据

- npm 登录凭据使用 npm 官方登录态和系统支持的凭据机制；SOIA 配置只保存非秘密偏好、版本策略和路径。
- 安装或更新阶段使用进度记录器追加脱敏的动作、阶段、结果和时间；只读检查默认不落盘。
- 包元数据可放 cache，安装器和解压内容放每次运行独立的系统临时目录并在成功或失败后清理。
- 不记录 registry token、完整私有 registry URL、用户名或客户私有绝对路径。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| Node.js | <状态> | <当前版本> | <最新版本> | <运行状态> | <RFC3339-with-timezone> | <处理结果> |
```

## 前向测试

用 fixture 覆盖 Node 已有、Node 缺失、PATH 不一致和项目要求冲突；真实验收必须分别执行 Node 和 npm 版本检查。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-node-install -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。
