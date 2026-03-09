from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_submodules

desktop_dir = Path(SPECPATH).resolve()
repo_root = desktop_dir.parent

backend_root = repo_root / "src" / "backend"
frontend_dist = repo_root / "src" / "frontend" / "dist"

hiddenimports = collect_submodules("mutagen") + collect_submodules("yt_dlp")

datas = [
    (str(frontend_dist), "src/frontend/dist"),
]

binaries = []
if sys.platform == "darwin":
    ff_dir = repo_root / "desktop" / "ffmpeg" / "macos-arm64"
    for bin_name in ("ffmpeg", "ffprobe"):
        bin_path = ff_dir / bin_name
        if bin_path.exists():
            binaries.append((str(bin_path), "."))
elif sys.platform == "win32":
    ff_dirs = [
        repo_root / "desktop" / "ffmpeg" / "windows-x64",
        repo_root / "desktop" / "ffmpeg" / "windows",
    ]
    ff_dir = next((d for d in ff_dirs if d.exists()), None)
    if ff_dir:
        for bin_name in ("ffmpeg.exe", "ffprobe.exe"):
            bin_path = ff_dir / bin_name
            if bin_path.exists():
                binaries.append((str(bin_path), "."))

a = Analysis(
    [str(desktop_dir / "main.py")],
    pathex=[str(repo_root), str(backend_root)],
    binaries=binaries,
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