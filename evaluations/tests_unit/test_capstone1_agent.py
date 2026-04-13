import sqlite3
import json
from capstones.capstone1_sql_agent.agent import SQLiteAnalystAgent, safe


def make_test_db(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE employees(
        id INTEGER PRIMARY KEY,
        name TEXT,
        dept TEXT,
        salary INTEGER
    )
    ''')
    employees = [
        (1, 'Alice', 'Engineering', 3000000),
        (2, 'Bob', 'HR', 800000),
        (3, 'Carol', 'Engineering', 2500000),
    ]
    cur.executemany('INSERT INTO employees(id,name,dept,salary) VALUES (?,?,?,?)', employees)
    conn.commit()
    conn.close()


def test_schema(tmp_path):
    db = tmp_path / 'test.db'
    make_test_db(str(db))
    agent = SQLiteAnalystAgent(str(db))
    schema = agent.schema()
    # should include employees table
    assert any('employees' in k.lower() for k in schema.keys())


def test_suggest_sql_parses(monkeypatch, tmp_path):
    db = tmp_path / 'test2.db'
    make_test_db(str(db))
    agent = SQLiteAnalystAgent(str(db))

    def fake_chat(messages, **opts):
        # Return JSON string as model would
        return json.dumps({"sql": "SELECT name, salary FROM employees WHERE dept='Engineering'", "explanation": "Filter engineering"})

    monkeypatch.setattr('capstones.capstone1_sql_agent.agent.chat', fake_chat)
    out = agent.suggest_sql('Show engineering salaries')
    assert 'select' in out['sql'].lower()
    assert 'explanation' in out


def test_execute_and_limit(tmp_path):
    db = tmp_path / 'test3.db'
    make_test_db(str(db))
    agent = SQLiteAnalystAgent(str(db))
    res = agent.execute('SELECT * FROM employees', limit=2)
    assert 'columns' in res
    assert len(res['rows']) <= 2


def test_unsafe_sql_returns_error(tmp_path):
    db = tmp_path / 'test4.db'
    make_test_db(str(db))
    agent = SQLiteAnalystAgent(str(db))
    res = agent.execute('DROP TABLE employees')
    assert res.get('error') == 'unsafe_sql'


def test_handle_end_to_end(monkeypatch, tmp_path):
    db = tmp_path / 'test5.db'
    make_test_db(str(db))
    agent = SQLiteAnalystAgent(str(db))

    def fake_chat(messages, **opts):
        # If messages contain 'Schema:' it's suggest_sql; return JSON
        content = messages[1]['content'] if len(messages) > 1 else ''
        if 'Schema:' in content:
            return json.dumps({"sql": "SELECT name, dept FROM employees WHERE salary>1000000", "explanation": "High earners"})
        # Otherwise treat as summarize and return a plain string
        return 'Found 2 high earners: Alice and Carol.'

    monkeypatch.setattr('capstones.capstone1_sql_agent.agent.chat', fake_chat)
    out = agent.handle('Who are the high earners?')
    assert out['nlq'] == 'Who are the high earners?'
    assert 'SELECT' in out['sql'].upper()
    assert 'result' in out and 'columns' in out['result']
    assert 'summary' in out
