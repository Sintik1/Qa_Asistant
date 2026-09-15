"""
UI E2E + user scenarios for QA Assistant (Page Object + Fluent API).

Prerequisites:
  - App running: `cd qa-assistant && npm run dev` (or docker on :8080)
  - BASE_URL via QA_ASSISTANT_BASE_URL (default http://localhost:5173)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pages.home_page import HomePage
from pages.settings_page import SettingsPage


@pytest.mark.ui
class TestUserScenarios:
    def test_settings_save_token_then_home_generate_success(
        self,
        driver,
        base_url: str,
        sample_md_file: Path,
    ):
        (
            SettingsPage(driver, base_url)
            .open_settings()
            .set_token("test-token-e2e")
            .save()
            .expect_saved()
            .go_home()
        )
        (
            HomePage(driver, base_url)
            .upload_requirements(sample_md_file)
            .expect_file_preview_contains("requirements.md")
            .set_task_name("CRM-E2E")
            .generate()
            .expect_results()
        )

    def test_generate_without_token_shows_tz_error(
        self,
        driver,
        base_url: str,
        sample_md_file: Path,
    ):
        # Origin must be loaded before localStorage is accessible; clear after open.
        home = HomePage(driver, base_url).open_home()
        driver.execute_script("window.localStorage.clear()")
        (
            home.upload_requirements(sample_md_file)
            .generate()
            .expect_alert_contains("Не настроен API-токен")
        )

    def test_invalid_format_rejected(
        self,
        driver,
        base_url: str,
        tmp_path: Path,
    ):
        bad = tmp_path / "notes.txt"
        bad.write_text("nope", encoding="utf-8")
        (
            HomePage(driver, base_url)
            .open_home()
            .upload_requirements(bad)
            .expect_alert_contains("Поддерживаются только PDF, DOCX, DOC и Markdown")
        )

    def test_empty_marker_file_shows_no_requirements(
        self,
        driver,
        base_url: str,
        empty_marker_file: Path,
    ):
        (
            SettingsPage(driver, base_url)
            .open_settings()
            .set_token("tok")
            .save()
            .go_home()
        )
        (
            HomePage(driver, base_url)
            .upload_requirements(empty_marker_file)
            .generate()
            .expect_alert_contains("не обнаружено требований")
        )


@pytest.mark.ui
@pytest.mark.parametrize(
    "marker,fragment",
    [
        ("fail_api.md", "Не удалось подключиться"),
        ("corrupt_doc.md", "Не удалось извлечь текст"),
    ],
)
def test_negative_generation_markers(
    driver,
    base_url: str,
    tmp_path: Path,
    marker: str,
    fragment: str,
):
    path = tmp_path / marker
    path.write_text("payload", encoding="utf-8")
    (
        SettingsPage(driver, base_url)
        .open_settings()
        .set_token("tok")
        .save()
        .go_home()
    )
    (
        HomePage(driver, base_url)
        .upload_requirements(path)
        .generate()
        .expect_alert_contains(fragment)
    )
