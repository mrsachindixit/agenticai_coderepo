from __future__ import annotations

import os
import py_compile
import subprocess
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "module01_raw").exists() and (candidate / "evaluations").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from test file path")


ROOT = _find_repo_root(Path(__file__).resolve())
TARGET = ROOT / "module04_production/4.1_security_guards.py"


def test_target_exists() -> None:
    assert TARGET.exists(), f"Missing target file: {TARGET.relative_to(ROOT)}"


def test_target_compiles() -> None:
    py_compile.compile(str(TARGET), doraise=True)


@pytest.mark.skipif(os.getenv("AGENTICAI_RUN_MODULE_SMOKE") != "1", reason="Set AGENTICAI_RUN_MODULE_SMOKE=1 to enable runtime smoke")
def test_target_runtime_smoke() -> None:
    result = subprocess.run(
        [
            "c:/python314/python.exe",
            str(TARGET),
            "--help",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode in {0, 1, 2}, (
        f"Unexpected return code {result.returncode} for {TARGET.relative_to(ROOT)}\n"
        f"stdout:\n{result.stdout[-2000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )

import re


def safe_eval_math(expr: str) -> float:
    if re.search(r"[A-Za-z_]", expr):
        raise ValueError("unsafe_expression")
    if not re.fullmatch(r"[0-9\s\+\-\*/\(\)\.]+", expr):
        raise ValueError("unsafe_expression")
    return float(eval(expr, {"__builtins__": {}}, {}))


def restrict_sql(query: str) -> bool:
    q = query.strip().lower()
    if ";" in q:
        return False
    if not q.startswith("select"):
        return False
    blocked = ("drop", "delete", "insert", "update", "alter", "truncate")
    return not any(token in q for token in blocked)


def test_safe_eval_math_valid() -> None:
    assert safe_eval_math("2 * (3 + 4)") == 14.0


def test_safe_eval_math_rejects_function_calls() -> None:
    with pytest.raises(ValueError):
        safe_eval_math("__import__('os').system('ls')")


def test_restrict_sql_allows_select() -> None:
    assert restrict_sql("SELECT * FROM employees LIMIT 10") is True


def test_restrict_sql_rejects_dangerous_statements() -> None:
    assert restrict_sql("DROP TABLE employees") is False
    assert restrict_sql("DELETE FROM employees") is False
    assert restrict_sql("SELECT * FROM employees; DROP TABLE employees") is False


def test_restrict_sql_case_insensitive() -> None:
    assert restrict_sql("sElEcT * FROM employees") is True
    assert restrict_sql("DrOp TABLE employees") is False
