"""Base Page Object with Fluent API helpers."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10.0):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def open(self, path: str = "/") -> "BasePage":
        self.driver.get(f"{self.base_url}{path}")
        return self

    def wait_visible(self, locator: tuple[str, str]) -> WebElement:
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator),
        )

    def wait_clickable(self, locator: tuple[str, str]) -> WebElement:
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator),
        )

    def wait_text(self, locator: tuple[str, str], text: str) -> WebElement:
        return WebDriverWait(self.driver, self.timeout).until(
            EC.text_to_be_present_in_element(locator, text),
        )

    def js_alert_fired(self) -> bool:
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return True
        except Exception:
            return False
