# app/services/yt2mp3_service.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import yt_dlp


def download_audio_for_url(url: str, output_dir: Path) -> List[Dict[str, Any]]:
    """
    Download audio as MP3 for a single URL, which may be:
      - a single YouTube video
      - a playlist URL (in which case multiple tracks are downloaded)

    Returns a list of per-track results:
      {
        "url": str,          # original URL that was requested
        "video_id": str|None,
        "title": str|None,
        "output_path": str|None,  # expected MP3 path, if we can infer it
        "success": bool,
        "error": str|None,
      }
    Raises if the URL cannot be processed at all.
    """
    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Template: "<output_dir>/<title>.ext"
    # After FFmpeg postproc, ext should be mp3.
    outtmpl = str(output_dir / "%(title)s.%(ext)s")
    print(f"outtmpl: {outtmpl}")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": False,  # allow playlists to be fully processed
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "cookiesfrombrowser": ("chrome", "Default")
    }

    track_results: List[Dict[str, Any]] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # If it's a playlist, info["entries"] is a list.
    # If it's a single video, info itself is the entry.
    entries = info.get("entries") or [info]

    for entry in entries:
        title = entry.get("title")
        video_id = entry.get("id")

        # We know outtmpl is "%(title)s.%(ext)s" under output_dir,
        # and we forced mp3 as the final codec, so this should match.
        output_path = None
        if title:
            output_path = str(output_dir / f"{title}.mp3")

        track_results.append(
            {
                "url": url,
                "video_id": video_id,
                "title": title,
                "output_path": output_path,
                "success": True,
                "error": None,
            }
        )

    return track_results


def batch_download_audio(urls: List[str], output_dir: Path) -> List[Dict[str, Any]]:
    """
    Download multiple URLs to MP3 in the given output directory.

    Returns a list of per-track result dicts:
      {
        "url": str,
        "video_id": str|None,
        "title": str|None,
        "output_path": str|None,
        "success": bool,
        "error": str|None,
      }

    - For a single video URL, you'll get one result row.
    - For a playlist URL, you'll get one row per video in the playlist.
    - If a URL fails entirely, you get a single failure row for that URL.
    """
    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results: List[Dict[str, Any]] = []

    for raw in urls:
        url = (raw or "").strip()
        if not url:
            continue

        try:
            per_track = download_audio_for_url(url, output_dir)
            all_results.extend(per_track)
        except Exception as e:
            # URL-level failure: record a single failing row
            all_results.append(
                {
                    "url": url,
                    "video_id": None,
                    "title": None,
                    "output_path": None,
                    "success": False,
                    "error": str(e),
                }
            )

    if not all_results:
        raise ValueError("No URLs provided")

    return all_results
