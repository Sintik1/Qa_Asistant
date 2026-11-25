"""
Security UI tests: XSS / SQL Injection payloads must not execute.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By

from pages.home_page import HomePage


XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "\"'><img src=x onerror=alert(1)>",
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "1; DROP TABLE users;--",
]


@pytest.mark.security
@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_prompt_and_task_not_executed(logged_in, base_url: str, payload: str):
    page = HomePage(logged_in, base_url).open_home()
    page.set_task_name(payload).set_prompt(payload)

    assert page.input_value(HomePage.TASK_NAME) == payload
    assert page.input_value(HomePage.PROMPT) == payload
    assert page.js_alert_fired() is False
    scripts = logged_in.find_elements(By.TAG_NAME, "script")
    inline = [s.get_attribute("innerHTML") or "" for s in scripts]
    assert not any("alert('xss')" in html for html in inline)


@pytest.mark.security
@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_not_executed_on_settings(logged_in, base_url: str, payload: str):
    from pages.settings_page import SettingsPage

    SettingsPage(logged_in, base_url).open_settings()
    logged_in.execute_script(
        "document.body.setAttribute('data-probe', arguments[0])",
        payload,
    )
    assert logged_in.execute_script("return window.__xss__") is None
    assert SettingsPage(logged_in, base_url).js_alert_fired() is False


@pytest.mark.security
@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_sqli_payload_treated_as_text(logged_in, base_url: str, payload: str):
    page = HomePage(logged_in, base_url).open_home()
    page.set_task_name(payload).set_prompt(payload)
    assert page.input_value(HomePage.TASK_NAME) == payload
    assert page.input_value(HomePage.PROMPT) == payload
    assert "syntax error" not in page.page_source().lower()
    assert page.js_alert_fired() is False
