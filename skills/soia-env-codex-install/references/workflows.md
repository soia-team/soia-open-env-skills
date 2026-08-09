# 工作流（标准流程 / 已安装状态与更新）

## 标准流程

1. 先执行 `python3 scripts/inspect_installation.py --json`，查找独立 Codex CLI，并记录版本、安装方式、安装目录、命令路径和配置目录是否真实存在。
2. 将 `ChatGPT.app/Contents/Resources/codex` 视为桌面应用内部组件，不把它当作独立 Codex CLI；即使当前 Agent 进程的 PATH 优先命中它，也要继续查找登录 shell、npm、Homebrew 和官方独立安装路径。
3. 缺少独立 CLI 时，macOS/Linux 优先使用 OpenAI 官方独立安装入口；只有客户明确选择 npm，或机器原来就采用 npm 渠道时，才要求 Node.js/npm 并安装 `@openai/codex`。
4. 已安装 CLI 默认只执行 dry-run 版本审计，只选择 Codex：

   ```bash
   TOOLS=codex DRY_RUN=1 bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
   ```

5. dry-run 发现新版本时先汇报“可更新，未执行”。客户只说“更新”时停下来询问；只有客户明确要求更新到最新，才去掉 `DRY_RUN=1` 执行升级。
6. 不自行复制另一套更新决策。得到最新版授权后，`soia-env-ai-cli-upgrade` 负责调用 `codex update`，由 Codex 根据独立 CLI 的安装上下文选择 npm、Homebrew cask 或官方独立安装器。
7. 更新后再次执行本技能的检查脚本，并使用返回的独立 CLI 绝对路径验证 `--version`、`--help` 和 `login status`。只有同一独立 CLI 更新并验证通过时，处理结果才写“已更新”。
8. 未登录时执行独立 CLI 的 `login` 流程，把浏览器授权交给客户；不要求客户在终端粘贴 API key。
9. 使用固定列表输出结果；依赖检查只在内部使用，正常时不向客户增加 Node.js、npm、ChatGPT 桌面版或其他技能行。

## 已安装状态与更新

先判断独立 Codex CLI 是否已经可用及实际来源；已安装且验证通过时不要重复安装：

```bash
python3 scripts/inspect_installation.py --json
TOOLS=codex DRY_RUN=1 \
  bash ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
```

- ChatGPT.app：是桌面应用，版本和更新渠道与独立 CLI 分开；其内部 `codex` 不进入本技能的 CLI 状态行。
- npm 全局安装：安装目录显示全局 `node_modules/@openai/codex`；升级交给 `soia-env-ai-cli-upgrade`。
- Homebrew cask 或官方独立安装：显示独立 CLI 的真实目录；升级同样交给 `soia-env-ai-cli-upgrade`。
- 已安装且登录状态正常：`当前状态` 始终写“已安装”；更新动作只写入 `处理结果`。
- 未取得客户“更新到最新”的明确指令时，到 dry-run 和版本汇报为止，不执行升级命令。
- 更新后使用检查脚本返回的 `cli_path` 执行 `--version`、`--help` 和 `login status`；不要使用未限定路径的 `codex` 重新引入 App/CLI 混淆。

更新前记录旧版本、安装来源和命令路径。更新失败时保留现有可用版本和错误证据，不自动卸载、降级或清理配置。
