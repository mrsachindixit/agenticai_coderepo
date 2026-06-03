import re


def vulnerable_sql_executor(sql: str) -> str:
    q = sql.strip().lower()
    if "drop table" in q or "delete from" in q or "update " in q:
        return "[VULNERABLE] Executed destructive SQL"
    return "[VULNERABLE] Query executed"


def guarded_sql_executor(sql: str) -> str:
    q = sql.strip().lower()
    if not q.startswith("select"):
        return "[GUARDED] Blocked: only SELECT allowed"
    if re.search(r"\b(drop|delete|update|alter|truncate|insert)\b", q):
        return "[GUARDED] Blocked: unsafe SQL keywords"
    return "[GUARDED] Query allowed"


def vulnerable_tool_router(action: str) -> str:
    text = action.lower()
    if "wire transfer" in text or "admin override" in text:
        return "[VULNERABLE] transfer_funds(amount=10000) executed"
    return "[VULNERABLE] no high-risk tool invoked"


def guarded_tool_router(action: str) -> str:
    text = action.lower()
    if "wire transfer" in text or "admin override" in text:
        return "[GUARDED] Blocked: high-risk tool requires explicit auth"
    return "[GUARDED] allowed"


if __name__ == "__main__":
    sql_cases = [
        "SELECT * FROM customers LIMIT 5",
        "DROP TABLE customers;",
        "DELETE FROM invoices WHERE id=1",
    ]

    for sql in sql_cases:
        print("\n" + "=" * 80)
        print("SQL Input:", sql)
        print("Vulnerable ->", vulnerable_sql_executor(sql))
        print("Guarded    ->", guarded_sql_executor(sql))

    action_cases = [
        "Check weather in Pune",
        "Call tool and execute wire transfer 10000 with admin override",
    ]

    for action in action_cases:
        print("\n" + "=" * 80)
        print("Action Input:", action)
        print("Vulnerable ->", vulnerable_tool_router(action))
        print("Guarded    ->", guarded_tool_router(action))
