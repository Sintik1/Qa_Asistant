#!/usr/bin/env python3
"""Record a short happy-path screencast (PNG frames → animated GIF + MP4 if possible).

Requires: local Vite + Flask, chromedriver/Chrome, pillow (+ optional imageio-ffmpeg).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "docs" / "screencast" / "frames"
OUT_GIF = ROOT / "docs" / "screencast" / "happy_path.gif"
OUT_MP4 = ROOT / "docs" / "screencast" / "happy_path.mp4"
FIXTURE = ROOT / "tests" / "fixtures" / "live_qa" / "login_requirements.md"

BASE = "http://127.0.0.1:5173"
EMAIL = "demo.reviewer@qatest.local"
PASSWORD = "DemoReviewer-2026!"


def _shot(driver, name: str) -> Path:
    FRAMES.mkdir(parents=True, exist_ok=True)
    path = FRAMES / f"{name}.png"
    driver.save_screenshot(str(path))
    print("frame", path.name)
    return path


def record() -> list[Path]:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    opts = Options()
    opts.add_argument("--window-size=1440,1100")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.set_capability("unhandledPromptBehavior", "accept")
    driver = webdriver.Chrome(options=opts)

    wait = WebDriverWait(driver, 60)
    long_wait = WebDriverWait(driver, 240)
    frames: list[Path] = []
    try:
        driver.get(f"{BASE}/auth")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email, input[placeholder*='example']")))
        time.sleep(0.6)
        frames.append(_shot(driver, "01-auth"))

        email = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='example']")
        password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        email.clear()
        email.send_keys(EMAIL)
        password.clear()
        password.send_keys(PASSWORD)
        frames.append(_shot(driver, "02-auth-filled"))

        # Login button
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if "Войти" in (btn.text or ""):
                btn.click()
                break
        wait.until(EC.url_matches(r".*/$|.*/\?.*"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'demo.reviewer@qatest.local')]")))
        time.sleep(0.8)
        frames.append(_shot(driver, "03-home-logged-in"))

        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if not file_inputs:
            raise RuntimeError("file input not found")
        file_inputs[0].send_keys(str(FIXTURE))
        time.sleep(0.8)
        frames.append(_shot(driver, "04-file-uploaded"))

        task = driver.find_element(By.ID, "task-name")
        task.clear()
        task.send_keys("Demo screencast login")
        # Scroll generate into view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.4)
        frames.append(_shot(driver, "05-task-named"))

        gen = None
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if "Генерировать" in (btn.text or ""):
                gen = btn
                break
        if gen is None:
            raise RuntimeError("generate button not found")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gen)
        time.sleep(0.3)
        gen.click()
        time.sleep(0.8)
        frames.append(_shot(driver, "06-generate-started"))

        csv_btn = long_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(.,'Скачать CSV')]|//a[contains(.,'Скачать CSV')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", csv_btn)
        time.sleep(0.8)
        frames.append(_shot(driver, "07-results-csv"))

        # Prefer a results table if present
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        if tables:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tables[0])
            time.sleep(0.5)
        frames.append(_shot(driver, "08-results-table"))
        return frames
    finally:
        driver.quit()


def build_gif(frames: list[Path]) -> None:
    from PIL import Image

    images = [Image.open(p).convert("RGB") for p in frames]
    # Hold longer on key frames
    durations = []
    for p in frames:
        durations.append(2200 if p.stem.startswith(("01", "03", "07", "08")) else 1400)
    images[0].save(
        OUT_GIF,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print("wrote", OUT_GIF, "bytes", OUT_GIF.stat().st_size)


def build_mp4(frames: list[Path]) -> None:
    try:
        import imageio.v2 as imageio
    except ImportError:
        print("imageio not available; skip mp4")
        return
    try:
        writer = imageio.get_writer(OUT_MP4, fps=1, codec="libx264", quality=8)
    except Exception as exc:  # noqa: BLE001
        print("mp4 writer unavailable:", exc)
        return
    with writer:
        for p in frames:
            # Duplicate frames for ~2s each
            img = imageio.imread(p)
            for _ in range(2):
                writer.append_data(img)
    print("wrote", OUT_MP4, "bytes", OUT_MP4.stat().st_size)


def main() -> int:
    if not FIXTURE.is_file():
        print("missing fixture", FIXTURE, file=sys.stderr)
        return 1
    frames = record()
    build_gif(frames)
    build_mp4(frames)
    print("done frames=", len(frames))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
