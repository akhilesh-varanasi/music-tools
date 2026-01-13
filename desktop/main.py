from __future__ import annotations

import argparse
import sys
from pathlib import Path

import webview

from desktop.bridge import MusicGuyApi


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resource_path(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / rel
    return _repo_root() / rel


def _resolve_frontend_entry(dev: bool) -> str:
    if dev:
        return "http://localhost:5173"

    index_html = _resource_path("src/frontend/dist/index.html")
    if not index_html.exists():
        raise FileNotFoundError(
            f"Frontend build not found: {index_html}\n"
            "Run: (cd src/frontend && npm run build:desktop)"
        )

    return index_html.as_uri()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Load Vite dev server")
    parser.add_argument("--debug", action="store_true", help="Enable webview debug")
    args = parser.parse_args()

    url = _resolve_frontend_entry(args.dev)

    webview.create_window(
        title="Music Guy",
        url=url,
        js_api=MusicGuyApi(),
        width=1100,
        height=800,
    )

    webview.start(debug=args.debug)


if __name__ == "__main__":
    main()
