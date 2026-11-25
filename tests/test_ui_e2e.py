"""
UI E2E + user scenarios for QA Assistant (Page Object + Fluent API).

Prerequisites:
  - App running: `cd qa-assistant && npm run dev` (or docker on :8080)
  - Flask API on VITE_API_BASE_URL (typically :5001)
  - BASE_URL via QA_ASSISTANT_BASE_URL (default http://localhost:5173)
  - E2E_EMAIL / E2E_PASSWORD (defaults: demo.reviewer@qatest.local)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pages.auth_page import AuthPage
from pages.home_page import HomePage
from pages.settings_page import SettingsPage


@pytest.mark.ui
def test_unauthenticated_root_shows_auth(driver, base_url: str):
    AuthPage(driver, base_url).open("/")
    AuthPage(driver, base_url).wait_visible(AuthPage.EMAIL)


@pytest.mark.ui
class TestUserScenarios:
    def test_settings_page_shows_token_flag_controls(
        self,
        logged_in,
        base_url: str,
    ):
        page = SettingsPage(logged_in, base_url).open_settings()
        assert page.wait_clickable(SettingsPage.MARK_CONFIGURED).is_displayed()
        assert "Настройки" in logged_in.page_source
        page.go_home()

    def test_home_generate_success(
        self,
        logged_in,
        base_url: str,
        sample_md_file: Path,
    ):
        (
            HomePage(logged_in, base_url)
            .open_home()
            .upload_requirements(sample_md_file)
            .expect_file_preview_contains("requirements.md")
            .set_task_name("CRM-E2E")
            .generate()
            .expect_results()
        )

    def test_generate_without_file_keeps_button_disabled(
        self,
        logged_in,
        base_url: str,
    ):
        home = HomePage(logged_in, base_url).open_home()
        btn = home.wait_visible(HomePage.GENERATE)
        assert btn.get_attribute("disabled") is not None

    def test_invalid_format_rejected(
        self,
        logged_in,
        base_url: str,
        tmp_path: Path,
    ):
        bad = tmp_path / "notes.txt"
        bad.write_text("nope", encoding="utf-8")
        (
            HomePage(logged_in, base_url)
            .open_home()
            .upload_requirements(bad)
            .expect_alert_contains("Поддерживаются только PDF, DOCX, DOC и Markdown")
        )

    def test_empty_file_shows_empty_error(
        self,
        logged_in,
        base_url: str,
        tmp_path: Path,
    ):
        empty = tmp_path / "empty.md"
        empty.write_bytes(b"")
        (
            HomePage(logged_in, base_url)
            .open_home()
            .upload_requirements(empty)
            .expect_alert_contains("Файл не содержит текста")
        )


@pytest.mark.ui
def test_nav_chat_page(logged_in, base_url: str):
    from selenium.webdriver.common.by import By

    HomePage(logged_in, base_url).open_home()
    logged_in.find_element(By.LINK_TEXT, "Чат по проекту").click()
    HomePage(logged_in, base_url).wait_visible((By.ID, "chat-question"))
