

import ast
import time
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

# -----------------------------
# 1) Safe evaluation (math only)
# -----------------------------

def safe_eval_math(expr: str):
    """Evaluate a math-only expression using AST allow-listing."""
    tree = ast.parse(expr, mode="eval")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Load,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )
    if not all(isinstance(n, allowed) for n in ast.walk(tree)):
        raise ValueError("Unsafe expression")
    return eval(compile(tree, "<ast>", "eval"))


# -----------------------------
# 2) SQL guardrail (read-only)
# -----------------------------

FORBIDDEN_SQL_TOKENS = [
    ";",
    "--",
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "attach",
    "pragma",
]

def restrict_sql(sql: str) -> bool:
    """Allow only simple SELECT queries; block common injection tokens."""
    s = sql.lower().strip()
    if not s.startswith("select"):
        return False
    return not any(tok in s for tok in FORBIDDEN_SQL_TOKENS)


# -----------------------------
# 3) Tool argument validation
# -----------------------------

class WeatherArgs(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)
    units: Optional[str] = Field(default="celsius", pattern=r"^(celsius|fahrenheit)$")

def validate_tool_args(payload: dict) -> WeatherArgs:
    """Validate tool arguments using Pydantic schemas."""
    return WeatherArgs(**payload)


# -----------------------------
# 4) Simple rate limiter
# -----------------------------

class RateLimiter:
    """Allow up to N calls per window_seconds."""

    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = []

    def allow(self) -> bool:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.window_seconds]
        if len(self.calls) >= self.max_calls:
            return False
        self.calls.append(now)
        return True


if __name__ == "__main__":
    print("Safe math:", safe_eval_math("2 * (3 + 4)"))
    print("SQL allowed:", restrict_sql("SELECT * FROM employees LIMIT 10"))
    print("SQL blocked:", restrict_sql("DROP TABLE employees"))

    try:
        args = validate_tool_args({"city": "Berlin", "units": "celsius"})
        print("Validated args:", args.model_dump())
    except ValidationError as e:
        print("Validation error:", e)

    limiter = RateLimiter(max_calls=2, window_seconds=5)
    print("Rate limit 1:", limiter.allow())
    print("Rate limit 2:", limiter.allow())
    print("Rate limit 3:", limiter.allow())
