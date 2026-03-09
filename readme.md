# Music Guy — Unified Dev + Desktop Packaging Guide

This repo contains:
- **Frontend**: Vue + Vite (`src/frontend`)
- **Backend**: FastAPI services (`src/backend`)
- **Desktop shell**: pywebview launcher/bridge (`desktop`)

The desktop app and web flow share the same service logic. In desktop mode, the UI calls Python directly through `window.pywebview.api` (no HTTP server required).

---

## Prerequisites

Build machine requirements:
- Python **3.11**
- Node **18+** (Node 20 recommended)

End users do **not** need Python/Node.

---

## 1) Desktop environment setup (one time)

Use a dedicated virtual environment for desktop dev/packaging.

### macOS / Linux
```bash
python -m venv .venv-desktop
source .venv-desktop/bin/activate
python -m pip install -U pip
pip install -r src/backend/requirements-desktop.txt
pip install pywebview pyinstaller
```

### Windows (PowerShell)
```powershell
py -3.11 -m venv .venv-desktop
.\.venv-desktop\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r src\backend\requirements-desktop.txt
pip install pywebview pyinstaller
```

---

## 2) Local development flows

### A) Browser/Web dev flow (HTTP)

Run frontend and backend separately:

```bash
npm --prefix src/frontend install
npm --prefix src/frontend run dev
```

```bash
cd src/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend runs at `http://localhost:5173` and proxies `/api` to backend.

### B) Desktop dev flow (recommended parity with packaged app)

#### Option 1: two terminals
Terminal 1:
```bash
npm --prefix src/frontend run dev
```

Terminal 2:
```bash
source .venv-desktop/bin/activate   # macOS/Linux
python -m desktop.main --dev
```

#### Option 2: one command (from repo root)
```bash
python -m desktop.tasks dev --with-vite
```

> You can also run `make desktop-dev-all` if `make` is available.

#### Important note about the old error
If you run `python desktop/main.py --dev`, imports can fail (`ModuleNotFoundError: No module named 'desktop'`) depending on path context. Prefer:

```bash
python -m desktop.main --dev
```

---

## 3) Packaging desktop app with PyInstaller

From repo root:

```bash
npm --prefix src/frontend install
npm --prefix src/frontend run build:desktop
pyinstaller --noconfirm --clean desktop/music_guy.spec
```

Equivalent helper commands:

```bash
python -m desktop.tasks build-ui
python -m desktop.tasks package
```

or with `make`:

```bash
make desktop-build-ui
make desktop-package
```

### Run packaged output

```bash
python -m desktop.tasks run-dist
```

---

## 4) Canonical root-level commands

If you use `Makefile`:

- `make desktop-dev` → run desktop app in `--dev` mode (expects Vite already running)
- `make desktop-dev-all` → run Vite + desktop together
- `make desktop-build-ui` → build frontend `dist` for desktop
- `make desktop-package` → build PyInstaller package
- `make desktop-run-dist` → run built app from `dist`

Python equivalents:

```bash
python -m desktop.tasks dev
python -m desktop.tasks dev --with-vite
python -m desktop.tasks build-ui
python -m desktop.tasks package
python -m desktop.tasks run-dist
```

---

## 5) Shipping for Windows + macOS (and Linux)

For reliable releases, build on each target OS natively.

### Key rule
You generally **cannot** produce a proper Windows `.exe` from macOS with PyInstaller in one step. Build on Windows for Windows artifacts, macOS for macOS artifacts.

### Recommended approach
- Use CI matrix builds per OS.
- This repo includes `.github/workflows/release-desktop.yml`.
- On tag push (`v*`) or manual dispatch, it builds artifacts for:
  - `windows-latest`
  - `macos-latest`
  - `ubuntu-latest`

Download artifacts from the workflow run and distribute per platform.

---

## Notes

- Desktop Vite build uses `base: './'` for file-based loading in packaged app.
- Desktop mode uses direct Python bridge calls (`window.pywebview.api`) instead of HTTP.
- Keep `src/backend/requirements-desktop.txt` pip-installable only.
