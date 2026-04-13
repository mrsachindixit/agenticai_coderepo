import argparse
import compileall
import importlib
import os
import platform
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "requirements.txt",
    ROOT / "setup_steps.md",
    ROOT / "README.md",
    ROOT / "capstones" / "capstone1_sql_agent" / "cap1_app.py",
    ROOT / "capstones" / "capstone2_research_agent" / "run.py",
    ROOT / "capstones" / "capstone3_rag_agent" / "build_index.py",
    ROOT / "capstones" / "capstone3_rag_agent" / "query_agent.py",
    ROOT / "playground" / "app.py",
    ROOT / "evaluations" / "tests_unit",
]

REQUIRED_IMPORTS = [
    "requests",
    "pydantic",
    "langchain",
    "langchain_community",
    "langchain_ollama",
    "langgraph",
    "streamlit",
    "fastapi",
    "uvicorn",
    "numpy",
    "PIL",
    "sklearn",
    "chromadb",
    "pypdf",
    "tqdm",
    "typing_extensions",
    "pytest",
    "dotenv",
    "openai",
    "faiss",
]

SAMPLE_COMMANDS = [
    [sys.executable, "-m", "pytest", "-q", "evaluations/tests_samples"],
]


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def check_python(min_major: int = 3, min_minor: int = 9) -> bool:
    v = sys.version_info
    if (v.major, v.minor) < (min_major, min_minor):
        fail(f"Python {min_major}.{min_minor}+ required, found {v.major}.{v.minor}")
        return False
    ok(f"Python version {v.major}.{v.minor}.{v.micro}")
    return True


def check_files() -> bool:
    good = True
    for path in REQUIRED_FILES:
        if path.exists():
            ok(f"Exists: {path.relative_to(ROOT)}")
        else:
            fail(f"Missing: {path.relative_to(ROOT)}")
            good = False
    return good


def check_imports(verbose: bool = False) -> bool:
    good = True
    missing = []
    for mod in REQUIRED_IMPORTS:
        try:
            importlib.import_module(mod)
            if verbose:
                ok(f"Import: {mod}")
        except Exception as ex:
            fail(f"Import failed: {mod} ({ex})")
            good = False
            missing.append(mod)
    if good:
        ok("All required imports succeeded")
    else:
        info("Install dependencies with: pip install -r requirements.txt")
        info(f"Missing imports ({len(missing)}): {', '.join(missing)}")
    return good


def check_python_sources_compile() -> bool:
    info("Compiling Python sources (syntax sanity)")
    ok_compile = compileall.compile_dir(str(ROOT), maxlevels=10, quiet=1)
    if ok_compile:
        ok("Python source compile sanity passed")
        return True
    fail("Python source compile sanity failed")
    return False


def run_pytest_collect() -> bool:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "evaluations/tests_unit",
        "evaluations/tests_rag",
        "evaluations/tests_agents",
    ]
    info("Running pytest collection smoke check")
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode == 0:
        ok("Pytest collection passed")
        return True
    fail("Pytest collection failed")
    print(result.stdout)
    print(result.stderr)
    return False


def check_ollama(base: str) -> bool:
    url = base.rstrip("/") + "/api/tags"
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=5) as resp:
            if 200 <= resp.status < 300:
                ok(f"Ollama reachable at {url}")
                return True
            fail(f"Ollama returned status {resp.status} at {url}")
            return False
    except (URLError, HTTPError, TimeoutError) as ex:
        fail(f"Ollama check failed at {url} ({ex})")
        return False


def run_sample_commands(timeout_seconds: int = 60, live: bool = False) -> bool:
    mode = "live" if live else "deterministic"
    info(f"Running sample command suite ({mode}, timeout={timeout_seconds}s each)")
    all_good = True
    env = os.environ.copy()
    if live:
        env["AGENTICAI_LIVE_SMOKE"] = "1"
    for cmd in SAMPLE_COMMANDS:
        display = " ".join(cmd)
        info(f"Sample: {display}")
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
        if result.returncode == 0:
            ok(f"Sample passed: {display}")
        else:
            fail(f"Sample failed: {display} (exit={result.returncode})")
            if result.stdout:
                print(result.stdout[-2000:])
            if result.stderr:
                print(result.stderr[-2000:])
            all_good = False
    return all_good


def list_sample_commands() -> None:
    info("Sample commands configured in smoke suite:")
    for cmd in SAMPLE_COMMANDS:
        print("  - " + " ".join(cmd))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reusable smoke test for agenticai_repo")
    parser.add_argument("--with-pytest", action="store_true", help="Run pytest --collect-only checks")
    parser.add_argument("--with-ollama", action="store_true", help="Check Ollama endpoint reachability")
    parser.add_argument("--with-samples", action="store_true", help="Run sample command sanity suite")
    parser.add_argument("--with-live-samples", action="store_true", help="Run sample suite with AGENTICAI_LIVE_SMOKE=1")
    parser.add_argument("--samples-timeout", type=int, default=60, help="Timeout seconds per sample command")
    parser.add_argument("--list-samples", action="store_true", help="List sample commands and exit")
    parser.add_argument("--ollama-base", default=os.getenv("OLLAMA_BASE", "http://localhost:11434"), help="Ollama base URL")
    parser.add_argument("--verbose", action="store_true", help="Verbose import output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_samples:
        list_sample_commands()
        return 0

    info(f"Platform: {platform.system()} {platform.release()}")
    info(f"Repo root: {ROOT}")

    checks = [
        check_python(),
        check_files(),
        check_python_sources_compile(),
        check_imports(verbose=args.verbose),
    ]

    if args.with_ollama:
        checks.append(check_ollama(args.ollama_base))

    if args.with_pytest:
        checks.append(run_pytest_collect())

    if args.with_samples:
        checks.append(run_sample_commands(timeout_seconds=args.samples_timeout, live=False))

    if args.with_live_samples:
        checks.append(run_sample_commands(timeout_seconds=args.samples_timeout, live=True))

    all_good = all(checks)
    if all_good:
        ok("Smoke test passed")
        return 0
    fail("Smoke test failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
