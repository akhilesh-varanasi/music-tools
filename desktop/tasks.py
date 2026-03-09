from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=repo_root(), check=True)


def desktop_dev(with_vite: bool) -> None:
    if not with_vite:
        run([sys.executable, "-m", "desktop.main", "--dev"])
        return

    vite_proc = subprocess.Popen(["npm", "--prefix", "src/frontend", "run", "dev"], cwd=repo_root())
    try:
        print("\nWaiting for Vite to boot...")
        time.sleep(2)
        run([sys.executable, "-m", "desktop.main", "--dev"])
    finally:
        vite_proc.terminate()
        try:
            vite_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            vite_proc.kill()


def build_ui() -> None:
    run(["npm", "--prefix", "src/frontend", "install"])
    run(["npm", "--prefix", "src/frontend", "run", "build:desktop"])


def package_desktop() -> None:
    run(["pyinstaller", "--noconfirm", "--clean", "desktop/music_guy.spec"])


def run_dist() -> None:
    root = repo_root()
    candidates = []

    if sys.platform == "win32":
        candidates += [
            root / "dist" / "MusicGuy.exe",
            root / "dist" / "MusicGuy" / "MusicGuy.exe",
        ]
    elif sys.platform == "darwin":
        candidates += [
            root / "dist" / "MusicGuy.app" / "Contents" / "MacOS" / "MusicGuy",
            root / "dist" / "MusicGuy",
        ]
    else:
        candidates += [
            root / "dist" / "MusicGuy",
        ]

    for path in candidates:
        if path.exists():
            run([str(path)])
            return

    joined = "\n".join(f"- {p}" for p in candidates)
    raise FileNotFoundError(f"Could not find built desktop executable. Checked:\n{joined}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Desktop workflow helper commands")
    sub = parser.add_subparsers(dest="command", required=True)

    p_dev = sub.add_parser("dev", help="Run desktop app in dev mode")
    p_dev.add_argument(
        "--with-vite",
        action="store_true",
        help="Also launch Vite dev server in the same process",
    )

    sub.add_parser("build-ui", help="Build frontend desktop assets")
    sub.add_parser("package", help="Package desktop app with PyInstaller")
    sub.add_parser("run-dist", help="Run packaged desktop executable")

    args = parser.parse_args()

    if args.command == "dev":
        desktop_dev(with_vite=args.with_vite)
    elif args.command == "build-ui":
        build_ui()
    elif args.command == "package":
        package_desktop()
    elif args.command == "run-dist":
        run_dist()


if __name__ == "__main__":
    main()
