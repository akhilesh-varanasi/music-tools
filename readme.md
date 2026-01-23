Music Guy — Dev & Packaging Notes

This repo supports fast local development and desktop packaging using the same codebase.

Prerequisites (build machine)

- Python 3.11
- Node 18+ / 20
- End users do not need Python or Node


Local Development

Frontend (Vue)

```
cd src/frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`


Backend (FastAPI)

```
cd src/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Desktop Dev (pywebview + Vite)

```
cd src/frontend
npm run dev
source .venv-desktop/bin/activate
python desktop/main.py --dev
```

Desktop Build Environment

Use a clean venv for packaging.


macOS / Linux

```
python -m venv .venv-desktop
source .venv-desktop/bin/activate
pip install -U pip
pip install -r src/backend/requirements-desktop.txt
pip install pywebview pyinstaller
```

Windows

```
py -3.11 -m venv .venv-desktop
.\.venv-desktop\Scripts\Activate.ps1
pip install -U pip
pip install -r src\backend\requirements-desktop.txt
pip install pywebview pyinstaller
```

Build Frontend for Desktop

```
npm --prefix src/frontend install
npm --prefix src/frontend run build:desktop
```

Creates src/frontend/dist/


Package Desktop App (folder build)

macOS / Linux
```
source .venv-desktop/bin/activate
pyinstaller --noconfirm --clean desktop/music_guy.spec
./dist/MusicGuy/MusicGuy
```

Windows

```
.\.venv-desktop\Scripts\Activate.ps1
pyinstaller --noconfirm --clean desktop\music_guy.spec
.\dist\MusicGuy\MusicGuy.exe
```

Repackaging Workflow

After code changes:

```
npm --prefix src/frontend run build:desktop
source .venv-desktop/bin/activate
pyinstaller --noconfirm --clean desktop/music_guy.spec
```

Notes

- Desktop uses hash routing and base './' in Vite
- Desktop calls backend services directly (no HTTP)
- requirements-desktop.txt must be pip-only
