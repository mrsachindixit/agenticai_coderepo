"""Tests for Module 4: Security guards and input validation."""

import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from module04_production import module_4_1_security_guards as sg

def test_safe_eval_math_valid():
    """Test that safe_eval_math allows valid arithmetic expressions."""
    result = sg.safe_eval_math("2 * (3 + 4)")
    assert result == 14.0

def test_safe_eval_math_rejects_function_calls():
    """Test that safe_eval_math rejects function calls."""
    try:
        sg.safe_eval_math("__import__('os').system('ls')")
        assert False, "Should raise ValueError"
    except ValueError:
        pass  # Expected

def test_restrict_sql_allows_select():
    """Test that restrict_sql allows SELECT statements."""
    assert sg.restrict_sql("SELECT * FROM employees LIMIT 10") == True

def test_restrict_sql_rejects_drop():
    """Test that restrict_sql rejects DROP statements."""
    assert sg.restrict_sql("DROP TABLE employees") == False

def test_restrict_sql_rejects_delete():
    """Test that restrict_sql rejects DELETE statements."""
    assert sg.restrict_sql("DELETE FROM employees") == False

def test_restrict_sql_rejects_semicolon():
    """Test that restrict_sql rejects multiple statements via semicolon."""
    assert sg.restrict_sql("SELECT * FROM employees; DROP TABLE employees") == False

def test_restrict_sql_case_insensitive():
    """Test that restrict_sql checks case-insensitively."""
    assert sg.restrict_sql("sElEcT * FROM employees") == True
    assert sg.restrict_sql("DrOp TABLE employees") == False
