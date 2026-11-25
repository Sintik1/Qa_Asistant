"""Auth page Page Object — Fluent API."""

from __future__ import annotations

import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class AuthPage(BasePage):
    EMAIL = (By.ID, "auth-email")
    PASSWORD = (By.ID, "auth-password")
    SUBMIT = (By.XPATH, "//button[@type='submit' and contains(., 'Войти')]")
    HOME_NAV = (By.LINK_TEXT, "Написание тест-кейсов")
    TASK_NAME = (By.ID, "task-name")

    def open_auth(self) -> "AuthPage":
        self.open("/auth")
        self.wait_visible(self.EMAIL)
        return self

    def login(self, email: str, password: str) -> "AuthPage":
        last_err: Exception | None = None
        for _ in range(3):
            self.fill(self.EMAIL, email)
            self.fill(self.PASSWORD, password)
            self.wait_clickable(self.SUBMIT).click()
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.visibility_of_element_located(self.TASK_NAME),
                        EC.visibility_of_element_located(self.HOME_NAV),
                    )
                )
                return self
            except Exception as exc:  # noqa: BLE001 — retry login on Auth/network flake
                last_err = exc
        if last_err:
            raise last_err
        return self

    def ensure_logged_in(self) -> "AuthPage":
        email = os.environ.get("E2E_EMAIL", "demo.reviewer@qatest.local")
        password = os.environ.get("E2E_PASSWORD", "DemoReviewer-2026!")
        self.open("/")
        WebDriverWait(self.driver, 25).until(
            EC.any_of(
                EC.visibility_of_element_located(self.EMAIL),
                EC.visibility_of_element_located(self.TASK_NAME),
                EC.visibility_of_element_located(self.HOME_NAV),
            )
        )
        if self._on_auth() and not self.driver.find_elements(*self.TASK_NAME):
            self.login(email, password)
        WebDriverWait(self.driver, 25).until(
            EC.visibility_of_element_located(self.TASK_NAME),
        )
        return self

    def _on_auth(self) -> bool:
        try:
            return bool(self.driver.find_elements(*self.EMAIL))
        except Exception:
            return False
