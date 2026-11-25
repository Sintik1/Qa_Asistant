"""Settings page Page Object — Fluent API (server token flag, no secret in UI)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class SettingsPage(BasePage):
    MARK_CONFIGURED = (
        By.XPATH,
        "//button[@type='submit' and contains(., 'Отметить токен настроенным')]",
    )
    CLEAR_FLAG = (By.XPATH, "//button[contains(., 'Сбросить флаг')]")
    STATUS = (By.CSS_SELECTOR, "[role='status']")
    ALERT = (By.CSS_SELECTOR, "[role='alert']")
    NAV_HOME = (By.LINK_TEXT, "Написание тест-кейсов")

    def open_settings(self) -> "SettingsPage":
        self.open("/settings")
        self.wait_clickable(self.MARK_CONFIGURED)
        return self

    def mark_token_configured(self) -> "SettingsPage":
        self.wait_clickable(self.MARK_CONFIGURED).click()
        return self

    def expect_saved(self) -> "SettingsPage":
        WebDriverWait(self.driver, 15).until(
            lambda d: "Флаг has_api_token" in d.page_source
            or "отмечен как настроенный" in d.page_source
            or bool(d.find_elements(*self.ALERT))
        )
        return self

    def go_home(self) -> "SettingsPage":
        self.wait_clickable(self.NAV_HOME).click()
        return self
