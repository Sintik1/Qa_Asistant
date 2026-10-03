# Screencast — happy path (для проверяющего)

Короткая демонстрация: демо-вход → upload `.md` → generate → таблица кейсов.

| Файл | Формат |
|------|--------|
| [`happy_path.mp4`](happy_path.mp4) | видео (~0.7 MB) |
| [`happy_path.gif`](happy_path.gif) | анимация (~0.9 MB) |
| [`frames/`](frames/) | отдельные PNG-кадры |

**Демо-учётка** (как в корневом README):

- Email: `demo.reviewer@qatest.local`
- Password: `DemoReviewer-2026!`

Переснять локально (Vite `:5173` + Flask + AI):

```bash
source .venv/bin/activate
pip install 'selenium>=4.18' pillow imageio imageio-ffmpeg
PYTHONPATH=. python scripts/record_happy_path_screencast.py
```
