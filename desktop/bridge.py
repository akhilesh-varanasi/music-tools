from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import re
import webview


def _add_backend_to_sys_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    backend_root = repo_root / "src" / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


_add_backend_to_sys_path()

class MusicGuyApi:
    @staticmethod
    def _normalize_file_types(
        file_types: Optional[List[Any]],
    ) -> Tuple[str, ...]:
        if not file_types:
            return ()

        normalized: List[str] = []
        for item in file_types:
            if not item or not isinstance(item, (list, tuple)) or len(item) != 2:
                continue

            label, pattern = item[0], item[1]
            if not isinstance(label, str) or not isinstance(pattern, str):
                continue

            label = label.strip()
            pattern = pattern.strip()
            if not label or not pattern:
                continue

            normalized.append(f"{label} ({pattern})")

        return tuple(normalized)

    def pick_files(
        self,
        title: str = "Select files",
        file_types: Optional[List[Any]] = None,
        allow_multiple: bool = True,
    ) -> List[str]:
        filters = self._normalize_file_types(file_types)

        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=allow_multiple,
            file_types=filters,
            # title=title,
        )

        if not result:
            return []
        return [str(p) for p in result]


    def pick_folder(self, title: str = "Select folder") -> Optional[str]:
        result = webview.windows[0].create_file_dialog(webview.FileDialog.FOLDER)
        if not result:
            return None
        return str(result[0])

    def pick_save_file(
        self,
        title: str = "Save as",
        file_types: Optional[List[tuple[str, str]]] = None,
        default_filename: str = "",
    ) -> Optional[str]:
        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=default_filename or None,
            file_types=file_types or (),
        )
        if not result:
            return None
        return str(result)        


    def album_art_replace(
        self,
        song_paths: Sequence[str],
        image_paths: Sequence[str],
    ) -> Dict[str, Any]:
        """
        Calls the same backend logic you use in dev mode, but directly (no HTTP).
        Expected to return a dict matching your UI expectations:
          {
            "results": [...],
            "total_songs": int,
            "total_success": int,
            "total_failed": int
          }
        """
        from app.services.album_art_service import gather_batch_paths, batch_replace_album_art_in_place

        songs, images = gather_batch_paths(song_paths, image_paths)
        results = batch_replace_album_art_in_place(songs, images)
        total = len(results)
        ok = sum(1 for r in results if r["success"])
        failed = total - ok
        return {
            "results": results,
            "total_songs": total,
            "total_success": ok,
            "total_failed": failed,
        }

    def yt2mp3_download(
        self,
        urls: Sequence[str],
        output_dir: str,
    ) -> Dict[str, Any]:
        """
        Calls your yt2mp3 service directly (no HTTP).
        Returns a dict matching your existing API response:
          {
            "results": [...],
            "total_tracks": int,
            "total_success": int,
            "total_failed": int
          }
        """
        from app.services.yt2mp3_service import batch_download_audio

        out_dir = Path(output_dir).expanduser()
        raw_results = batch_download_audio(list(urls), out_dir)

        total = len(raw_results)
        ok = sum(1 for r in raw_results if r.get("success"))
        failed = total - ok

        return {
            "results": raw_results,
            "total_tracks": total,
            "total_success": ok,
            "total_failed": failed,
        }
