#!/usr/bin/env python3
"""soia-env-local-model-bench 共用工具：配置定位、题库合并加载、路径与脱敏。

只用标准库；解析 .yaml 题库/配置时按需导入 PyYAML，缺失时给出可执行的补救提示。
所有对外打印的路径都先做 home 折叠，不输出用户绝对路径。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

SKILL_NAME = "soia-env-local-model-bench"
REPO_NAME = "soia-open-env-skills"
ENV_PREFIX = "SOIA_ENV_LOCAL_MODEL_BENCH"
DEFAULT_PORT = 21000
SKILL_ROOT = Path(__file__).resolve().parent.parent
PACKAGED_QUESTIONS_DIR = SKILL_ROOT / "questions"
QUESTION_SUFFIXES = (".yaml", ".yml", ".json")
CHECK_TYPES = {"speed", "save", "manual", "regex", "node_snippet", "json_expect", "lines_expect"}


def now_rfc3339() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def fold_home(text: str) -> str:
    home = str(Path.home())
    if home and home not in ("/", "\\"):
        return text.replace(home, "~")
    return text


def _config_home() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA")
        return Path(base) if base else Path.home() / "AppData" / "Roaming"
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) if base else Path.home() / ".config"


def skill_config_dirs() -> list[Path]:
    """优先级从高到低：技能名短目录（文档口径）、仓库惯例目录（DATA_STORAGE_SPEC）。"""
    root = _config_home() / "soia-skills"
    return [root / SKILL_NAME, root / REPO_NAME / "skills" / SKILL_NAME]


def load_yaml_or_json(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            f"解析 {fold_home(str(path))} 需要 PyYAML：python3 -m pip install pyyaml；"
            "或改用同名 .json 文件"
        ) from exc
    return yaml.safe_load(text)


def load_config(explicit_file: str | None = None) -> tuple[dict, Path | None]:
    """定位并加载非秘密配置。顺序：--config / 环境变量指定文件 > 配置目录扫描。"""
    candidates: list[Path] = []
    for value in (explicit_file, os.environ.get(f"{ENV_PREFIX}_CONFIG_FILE")):
        if value:
            candidates.append(Path(value).expanduser())
    for directory in skill_config_dirs():
        for name in ("config.yml", "config.yaml", "config.json"):
            candidates.append(directory / name)
    for path in candidates:
        if path.is_file():
            data = load_yaml_or_json(path)
            if data is None:
                data = {}
            if not isinstance(data, dict):
                raise RuntimeError(f"配置 {fold_home(str(path))} 顶层必须是 mapping")
            return data, path
    return {}, None


def private_questions_dir(cli_value: str | None, config: dict | None) -> Path | None:
    """返回第一个存在的私有题目录；全部不存在时返回 None（纯公开题运行）。"""
    candidates: list[Path] = []
    for value in (
        cli_value,
        os.environ.get(f"{ENV_PREFIX}_QUESTIONS_DIR"),
        (config or {}).get("private_questions_dir"),
    ):
        if value:
            candidates.append(Path(str(value)).expanduser())
    candidates.extend(directory / "questions" for directory in skill_config_dirs())
    for path in candidates:
        if path.is_dir():
            return path
    return None


def _validate_question(data: dict, source: Path) -> dict:
    where = fold_home(str(source))
    if not isinstance(data, dict):
        raise RuntimeError(f"题目文件 {where} 顶层必须是 mapping")
    qid = data.get("qid")
    if not isinstance(qid, str) or not qid:
        raise RuntimeError(f"题目文件 {where} 缺少字符串 qid")
    if not isinstance(data.get("prompt"), str) or not data["prompt"].strip():
        raise RuntimeError(f"题目 {qid}（{where}）缺少 prompt")
    check = data.get("check")
    if not isinstance(check, dict) or check.get("type") not in CHECK_TYPES:
        raise RuntimeError(
            f"题目 {qid}（{where}）的 check.type 必须是 {sorted(CHECK_TYPES)} 之一"
        )
    data.setdefault("cat", "未分类")
    data.setdefault("temp", 0.0)
    data.setdefault("max_tokens", 2000)
    return data


def _question_files(directory: Path) -> list[Path]:
    files: list[Path] = []
    for suffix in QUESTION_SUFFIXES:
        files.extend(directory.glob(f"*{suffix}"))
    return sorted(files)


def load_questions(
    packaged_dir: Path | None = None,
    private_dir: Path | None = None,
) -> tuple[dict[str, dict], list[str]]:
    """加载公开题并用私有题覆盖同 qid。返回 (qid->题目, 加载说明)。"""
    notes: list[str] = []
    questions: dict[str, dict] = {}
    packaged = packaged_dir or PACKAGED_QUESTIONS_DIR
    if not packaged.is_dir():
        raise RuntimeError(f"题库目录不存在: {fold_home(str(packaged))}")
    for path in _question_files(packaged):
        data = _validate_question(load_yaml_or_json(path), path)
        data["_source"] = "packaged"
        questions[data["qid"]] = data
    notes.append(f"公开题 {len(questions)} 道（技能包 questions/）")
    if private_dir is not None:
        overridden = 0
        added = 0
        for path in _question_files(private_dir):
            data = _validate_question(load_yaml_or_json(path), path)
            data["_source"] = "private"
            if data["qid"] in questions:
                overridden += 1
            else:
                added += 1
            questions[data["qid"]] = data
        notes.append(
            f"私有题目录 {fold_home(str(private_dir))}：新增 {added} 道，覆盖 {overridden} 道"
        )
    else:
        notes.append("未发现私有题目录（仅公开题运行）")
    return questions, notes


def resolve_workdir(cli_value: str | None, config: dict | None) -> Path:
    value = (
        cli_value
        or os.environ.get(f"{ENV_PREFIX}_HOME")
        or (config or {}).get("workspace")
        or "~/local-model-bench"
    )
    return Path(str(value)).expanduser()


def resolve_model(cli_value: str | None, config: dict | None, *, mock: bool = False) -> str:
    value = cli_value or os.environ.get("BENCH_MODEL") or (config or {}).get("model")
    if value:
        return os.path.expanduser(str(value))
    if mock:
        return "mock-model"
    raise SystemExit(
        "缺少模型标识：用 --model、环境变量 BENCH_MODEL 或 config 的 model 指定"
        "（mlx-lm 服务必须传模型完整路径，传别名会触发去 HF 拉仓库）"
    )


def resolve_base_url(cli_url: str | None, cli_port: int | None, config: dict | None) -> str:
    if cli_url:
        return cli_url.rstrip("/")
    server = (config or {}).get("server") or {}
    if cli_port is None and server.get("base_url"):
        return str(server["base_url"]).rstrip("/")
    port = cli_port or server.get("port") or DEFAULT_PORT
    return f"http://127.0.0.1:{port}/v1"


def context_file_for(question: dict, config: dict | None) -> Path | None:
    """题目 yaml 的 context_file 优先，其次 config 的 context_files.<qid>。都没有返回 None。"""
    value = question.get("context_file")
    if not value:
        value = ((config or {}).get("context_files") or {}).get(question["qid"])
    if not value:
        return None
    return Path(os.path.expandvars(os.path.expanduser(str(value))))
