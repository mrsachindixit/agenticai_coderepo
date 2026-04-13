from __future__ import annotations

import os
import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

SAMPLE_ROOTS = [
    ROOT / "module01_raw",
    ROOT / "module02_basics",
    ROOT / "module03_langchain",
    ROOT / "module04_production",
    ROOT / "module05_enterprise",
    ROOT / "capstones",
    ROOT / "playground",
    ROOT / "utils",
]

KEY_ENTRYPOINTS = [
    ROOT / "capstones" / "capstone1_sql_agent" / "cap1_app.py",
    ROOT / "capstones" / "capstone2_research_agent" / "run.py",
    ROOT / "capstones" / "capstone3_rag_agent" / "build_index.py",
    ROOT / "capstones" / "capstone3_rag_agent" / "query_agent.py",
    ROOT / "playground" / "app.py",
]

LIVE_SAMPLE_COMMANDS = [
    [sys.executable, "capstones/capstone1_sql_agent/cap1_app.py", "List engineering employees"],
    [sys.executable, "capstones/capstone2_research_agent/run.py", "Survey methods for low-resource NER"],
    [sys.executable, "capstones/capstone3_rag_agent/build_index.py", "--data_dir", "capstones/capstone3_rag_agent/data", "--persist_dir", "capstones/capstone3_rag_agent/chroma_db"],
]


def iter_sample_files() -> list[Path]:
    files: list[Path] = []
    for root in SAMPLE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            files.append(path)
    return sorted(files)


def test_key_entrypoints_exist() -> None:
    missing = [p for p in KEY_ENTRYPOINTS if not p.exists()]
    assert not missing, f"Missing key entrypoints: {[str(m.relative_to(ROOT)) for m in missing]}"


@pytest.mark.parametrize("path", iter_sample_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_python_sample_compiles(path: Path) -> None:
    py_compile.compile(str(path), doraise=True)


def test_readme_python_commands_paths_exist() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    command_lines = [line.strip() for line in readme.splitlines() if line.strip().startswith("python ")]
    referenced = []
    for line in command_lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1].endswith(".py"):
            referenced.append(ROOT / parts[1])
    missing = [p for p in referenced if not p.exists()]
    assert not missing, f"README references missing python paths: {[str(m.relative_to(ROOT)) for m in missing]}"


@pytest.mark.skipif(os.getenv("AGENTICAI_LIVE_SMOKE") != "1", reason="Set AGENTICAI_LIVE_SMOKE=1 for live sample execution")
@pytest.mark.parametrize("cmd", LIVE_SAMPLE_COMMANDS, ids=lambda c: " ".join(c[1:3]))
def test_live_sample_commands(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, (
        f"Command failed: {' '.join(cmd)}\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )
