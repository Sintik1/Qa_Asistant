"""Unit tests for AI → test-case parser."""

from core.case_parser import parse_cases_from_ai_text


def test_parse_csv_with_header():
    text = (
        "Name,Status,Step,Expected Result\n"
        "Login,Approved,Open app,Home shown\n"
        "Logout,Approved,Click exit,Login page\n"
    )
    cases = parse_cases_from_ai_text(text)
    assert len(cases) == 2
    assert cases[0].name == "Login"
    assert cases[0].expected_result == "Home shown"


def test_parse_fenced_csv():
    text = """```csv
Name,Status,Step,Expected Result
A,Approved,Do A,Ok
```"""
    cases = parse_cases_from_ai_text(text)
    assert len(cases) == 1
    assert cases[0].name == "A"


def test_parse_empty():
    assert parse_cases_from_ai_text("   ") == []
