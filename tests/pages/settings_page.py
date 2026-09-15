"""Settings page Page Object — Fluent API."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage


class SettingsPage(BasePage):
    TOKEN = (By.ID, "api-token")
    SAVE = (
        By.XPATH,
        "//button[@type='submit' and contains(., 'Сохранить токен')]",
    )
    STATUS = (By.CSS_SELECTOR, "[role='status']")
    ALERT = (By.CSS_SELECTOR, "[role='alert']")
    NAV_HOME = (By.LINK_TEXT, "Написание тест-кейсов")

    def open_settings(self) -> "SettingsPage":
        self.open("/settings")
        self.wait_visible(self.TOKEN)
        return self

    def set_token(self, value: str) -> "SettingsPage":
        el = self.wait_visible(self.TOKEN)
        el.clear()
        el.send_keys(value)
        return self

    def save(self) -> "SettingsPage":
        self.wait_clickable(self.SAVE).click()
        return self

    def expect_saved(self) -> "SettingsPage":
        self.wait_text(self.STATUS, "Токен сохранён")
        return self

    def expect_missing_token_error(self) -> "SettingsPage":
        self.wait_text(self.ALERT, "Введите API-токен")
        return self

    def go_home(self) -> "SettingsPage":
        self.wait_clickable(self.NAV_HOME).click()
        return self

    def token_value(self) -> str:
        return self.wait_visible(self.TOKEN).get_attribute("value") or ""
