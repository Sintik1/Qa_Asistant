"""
Security UI tests: XSS / SQL Injection payloads must not execute.

Frontend has no SQL DB yet — SQLi checks verify input is treated as opaque text.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By

from pages.home_page import HomePage
from pages.settings_page import SettingsPage


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
def test_xss_in_prompt_and_task_not_executed(driver, base_url: str, payload: str):
    page = HomePage(driver, base_url).open_home()
    page.set_task_name(payload).set_prompt(payload)

    assert page.input_value(HomePage.TASK_NAME) == payload
    assert page.input_value(HomePage.PROMPT) == payload
    assert page.js_alert_fired() is False
    # React text binding must not inject a live <script> node
    scripts = driver.find_elements(By.TAG_NAME, "script")
    inline = [s.get_attribute("innerHTML") or "" for s in scripts]
    assert not any("alert('xss')" in html for html in inline)


@pytest.mark.security
@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_token_field_not_executed(driver, base_url: str, payload: str):
    page = (
        SettingsPage(driver, base_url)
        .open_settings()
        .set_token(payload)
        .save()
    )
    assert page.js_alert_fired() is False
    assert "Токен сохранён" in page.driver.page_source or page.token_value() == payload


@pytest.mark.security
@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_sqli_payload_treated_as_text(driver, base_url: str, payload: str):
    page = HomePage(driver, base_url).open_home()
    page.set_task_name(payload).set_prompt(payload)
    assert page.input_value(HomePage.TASK_NAME) == payload
    assert page.input_value(HomePage.PROMPT) == payload
    # No SQL error surface on frontend-only app; payload stays opaque text.
    assert "syntax error" not in page.page_source().lower()
    assert page.js_alert_fired() is False
