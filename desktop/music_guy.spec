from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

desktop_dir = Path(SPECPATH).resolve()
repo_root = desktop_dir.parent

backend_root = repo_root / "src" / "backend"
frontend_dist = repo_root / "src" / "frontend" / "dist"

hiddenimports = collect_submodules("mutagen") + collect_submodules("yt_dlp")

datas = [
    (str(frontend_dist), "src/frontend/dist"),
]

a = Analysis(
    [str(desktop_dir / "main.py")],
    pathex=[str(repo_root), str(backend_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="MusicGuy",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)
