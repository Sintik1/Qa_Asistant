"""Home page Page Object — Fluent API."""

from __future__ import annotations

from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class HomePage(BasePage):
    REQUIREMENTS = (By.ID, "requirements-file")
    TEMPLATES = (By.ID, "templates-file")
    TASK_NAME = (By.ID, "task-name")
    PROMPT = (By.ID, "prompt")
    GENERATE = (
        By.XPATH,
        "//button[@type='submit' and contains(., 'Генерировать тест-кейсы')]",
    )
    ALERT = (By.CSS_SELECTOR, "[role='alert']")
    DOWNLOAD_CSV = (By.XPATH, "//button[contains(., 'Скачать CSV')]")
    NAV_SETTINGS = (By.LINK_TEXT, "Настройки")
    FILE_PREVIEW = (
        By.XPATH,
        "//label[@for='requirements-file']/following-sibling::p[1]",
    )

    def open_home(self) -> "HomePage":
        self.open("/")
        self.wait_visible(self.TASK_NAME)
        return self

    def go_to_settings(self) -> "HomePage":
        self.wait_clickable(self.NAV_SETTINGS).click()
        return self

    def upload_requirements(self, path: Path) -> "HomePage":
        self.wait_visible(self.REQUIREMENTS).send_keys(str(path.resolve()))
        return self

    def set_task_name(self, value: str) -> "HomePage":
        el = self.wait_visible(self.TASK_NAME)
        el.clear()
        el.send_keys(value)
        return self

    def set_prompt(self, value: str) -> "HomePage":
        el = self.wait_visible(self.PROMPT)
        el.clear()
        el.send_keys(value)
        return self

    def generate(self) -> "HomePage":
        self.wait_clickable(self.GENERATE).click()
        return self

    def expect_alert_contains(self, text: str) -> "HomePage":
        self.wait_text(self.ALERT, text)
        return self

    def expect_file_preview_contains(self, text: str) -> "HomePage":
        self.wait_text(self.FILE_PREVIEW, text)
        return self

    def expect_results(self) -> "HomePage":
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.DOWNLOAD_CSV),
        )
        return self

    def page_source(self) -> str:
        return self.driver.page_source

    def input_value(self, locator: tuple[str, str]) -> str:
        return self.wait_visible(locator).get_attribute("value") or ""
