"""Shared fixtures for UI / security Selenium tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = os.environ.get("QA_ASSISTANT_BASE_URL", "http://localhost:5173")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL.rstrip("/")


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # Stable downloads for CSV assertions if needed later
    download_dir = tempfile.mkdtemp(prefix="qa_assistant_dl_")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(0)  # explicit waits only — anti-flaky
    yield browser
    browser.quit()


@pytest.fixture
def sample_md_file(tmp_path: Path) -> Path:
    path = tmp_path / "requirements.md"
    path.write_text("# Requirement\n\nUser can log in.\n", encoding="utf-8")
    return path


@pytest.fixture
def empty_marker_file(tmp_path: Path) -> Path:
    path = tmp_path / "empty_requirements.md"
    path.write_text("x", encoding="utf-8")
    return path
