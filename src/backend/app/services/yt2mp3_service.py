from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import sys

import yt_dlp
from yt_dlp.utils import DownloadError

MAX_YTDLP_CONCURRENCY = 16


def _is_cookie_db_missing_error(message: str) -> bool:
    lower = (message or "").lower()
    return (
        "could not find chrome cookies database" in lower
        or "could not find edge cookies database" in lower
    )


@lru_cache(maxsize=1)
def _cookie_browser_candidates() -> Tuple[Tuple[str, Optional[str]], ...]:
    candidates: List[Tuple[str, Optional[str]]] = [("chrome", "Default")]

    # On Windows, users are often signed into YouTube under "Profile X"
    # instead of the hardcoded "Default" profile.
    if sys.platform == "win32":
        candidates.append(("chrome", None))

        local_app_data = os.environ.get("LOCALAPPDATA", "")
        user_data_dir = Path(local_app_data) / "Google" / "Chrome" / "User Data"
        if user_data_dir.exists():
            profile_names: List[str] = []
            for child in user_data_dir.iterdir():
                if not child.is_dir():
                    continue
                name = child.name
                if name == "Default" or name.startswith("Profile "):
                    profile_names.append(name)

            profile_names.sort(key=lambda n: (0 if n == "Default" else 1, n))
            for name in profile_names:
                candidates.append(("chrome", name))

    deduped: List[Tuple[str, Optional[str]]] = []
    seen: set[Tuple[str, Optional[str]]] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)

    return tuple(deduped)

def _resolve_ffmpeg_location() -> Optional[str]:
    exe_dir = Path(sys.executable).resolve().parent

    # onedir bundle: ffmpeg sits next to the executable
    if sys.platform == "win32":
        if (exe_dir / "ffmpeg.exe").exists():
            return str(exe_dir)
    else:
        if (exe_dir / "ffmpeg").exists():
            return str(exe_dir)

    # onefile bundle fallback
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(meipass)
        if sys.platform == "win32":
            if (base / "ffmpeg.exe").exists():
                return str(base)
        else:
            if (base / "ffmpeg").exists():
                return str(base)

    return None

def _build_ydl_opts(
    outtmpl: str,
    listing: bool = False,
    cookies_from_browser: Optional[Tuple[str, Optional[str]]] = None,
) -> Dict[str, Any]:
    """Build yt-dlp options with browser cookies."""
    if cookies_from_browser is None:
        cookies_from_browser = ("chrome", "Default")

    opts: Dict[str, Any] = {
        # Prefer direct HTTPS audio formats first; keep generic fallbacks after.
        # This helps avoid fragile HLS-only paths when challenge solving is degraded.
        "format": "bestaudio[protocol!=m3u8][protocol!=m3u8_native]/bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
        "no_warnings": False,
        "cookiesfrombrowser": cookies_from_browser,
        # YouTube extraction increasingly requires JS challenge solving.
        # yt-dlp expects a dict format for js_runtimes.
        "js_runtimes": {"node": {}, "deno": {}},
        # Allow yt-dlp to fetch the current external challenge solver bundle.
        "remote_components": ["ejs:github"],
        "retries": 5,
        "fragment_retries": 5,
        "concurrent_fragment_downloads": 1,
        "skip_unavailable_fragments": False,
    }

    if listing:
        # yt-dlp will return "flat" entries with id/title/url for each item.
        opts["skip_download"] = True
        opts["extract_flat"] = "in_playlist"

        opts.pop("postprocessors", None)
    
    ffmpeg_loc = _resolve_ffmpeg_location()
    if ffmpeg_loc:
        opts["ffmpeg_location"] = ffmpeg_loc

    return opts


def _map_cookies_error(e: DownloadError) -> str:
    msg = str(e)
    lower = msg.lower()

    if _is_cookie_db_missing_error(msg):
        return (
            "Chrome cookies database was not found in any detected Chrome profile. "
            "Please open Chrome for this Windows user, confirm YouTube is signed in, "
            "close Chrome, and try again."
        )

    if "no supported javascript runtime could be found" in lower:
        return (
            "yt-dlp could not find a supported JavaScript runtime for YouTube "
            "challenge solving. Install Node.js and ensure `node` is available "
            "in PATH for the Python process running this app, then retry."
        )

    if "signature solving failed" in lower or "n challenge solving failed" in lower:
        return (
            "YouTube challenge/signature solving failed, which can cause broken "
            "or missing media URLs. Ensure Node.js is installed, keep yt-dlp "
            "updated, and allow the EJS remote component (ejs:github)."
        )

    if "requested format is not available" in lower or "only images are available" in lower:
        return (
            "No playable audio format was exposed by YouTube for this request. "
            "This is commonly a challenge-solver issue. Ensure Node.js is in PATH, "
            "update yt-dlp, and allow remote component `ejs:github`."
        )

    if "downloaded file is empty" in lower:
        return (
            "The remote stream returned no media fragments. This is usually a "
            "YouTube challenge/runtime issue. Ensure Node.js is installed and "
            "yt-dlp is up to date in this environment."
        )

    return msg


def _extract_entries_for_url(
    root_index: int,
    url: str,
    output_dir: Path,
) -> Tuple[List[Dict[str, Any]], List[Tuple[int, Dict[str, Any]]]]:
    outtmpl = str(output_dir / "%(title)s.%(ext)s")

    jobs: List[Dict[str, Any]] = []
    failures: List[Tuple[int, Dict[str, Any]]] = []
    last_cookie_error: Optional[DownloadError] = None

    info: Optional[Dict[str, Any]] = None
    for cookies_candidate in _cookie_browser_candidates():
        opts = _build_ydl_opts(
            outtmpl,
            listing=True,
            cookies_from_browser=cookies_candidate,
        )
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            break
        except DownloadError as e:
            if _is_cookie_db_missing_error(str(e)):
                last_cookie_error = e
                continue

            err = _map_cookies_error(e)
            failures.append(
                (
                    root_index,
                    {
                        "url": url,
                        "video_id": None,
                        "title": None,
                        "output_path": None,
                        "success": False,
                        "error": err,
                    },
                )
            )
            return jobs, failures

    if info is None:
        err = _map_cookies_error(last_cookie_error or DownloadError("Unknown download error"))
        failures.append(
            (
                root_index,
                {
                    "url": url,
                    "video_id": None,
                    "title": None,
                    "output_path": None,
                    "success": False,
                    "error": err,
                },
            )
        )
        return jobs, failures

    entries = info.get("entries") or [info]

    for entry in entries:
        entry_url = entry.get("webpage_url") or entry.get("url") or url
        jobs.append(
            {
                "root_index": root_index,
                "root_url": url,
                "entry_url": entry_url,
                "video_id": entry.get("id"),
                "title_hint": entry.get("title"),
            }
        )

    return jobs, failures


def _download_single_track(
    job: Dict[str, Any],
    output_dir: Path,
) -> Tuple[int, Dict[str, Any]]:
    root_index = job["root_index"]
    root_url = job["root_url"]
    entry_url = job["entry_url"]
    video_id_hint = job.get("video_id")
    title_hint = job.get("title_hint")

    outtmpl = str(output_dir / "%(title)s.%(ext)s")
    info: Optional[Dict[str, Any]] = None
    last_cookie_error: Optional[DownloadError] = None

    for cookies_candidate in _cookie_browser_candidates():
        opts = _build_ydl_opts(
            outtmpl,
            listing=False,
            cookies_from_browser=cookies_candidate,
        )
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(entry_url, download=True)
            break
        except DownloadError as e:
            if _is_cookie_db_missing_error(str(e)):
                last_cookie_error = e
                continue

            err = _map_cookies_error(e)
            return root_index, {
                "url": root_url,
                "video_id": video_id_hint,
                "title": title_hint,
                "output_path": None,
                "success": False,
                "error": err,
            }
        except Exception as e:
            return root_index, {
                "url": root_url,
                "video_id": video_id_hint,
                "title": title_hint,
                "output_path": None,
                "success": False,
                "error": str(e),
            }

    if info is None:
        err = _map_cookies_error(last_cookie_error or DownloadError("Unknown download error"))
        return root_index, {
            "url": root_url,
            "video_id": video_id_hint,
            "title": title_hint,
            "output_path": None,
            "success": False,
            "error": err,
        }

    title = info.get("title") or title_hint or "(untitled)"
    output_path = str(output_dir / f"{title}.mp3")

    return root_index, {
        "url": root_url,
        "video_id": info.get("id") or video_id_hint,
        "title": title,
        "output_path": output_path,
        "success": True,
        "error": None,
    }


def _download_for_urls(urls: List[str], output_dir: Path) -> List[Dict[str, Any]]:
    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    indexed_urls: List[Tuple[int, str]] = []
    for idx, raw in enumerate(urls):
        url = (raw or "").strip()
        if not url:
            continue

        url_tuple = urlparse(url)
        query_dict = parse_qs(url_tuple.query, keep_blank_values=True)
        query_dict.pop("start_radio", None)
        new_query = urlencode(query_dict, doseq=True)
        parsed_url = url_tuple._replace(query=new_query).geturl()

        indexed_urls.append((idx, parsed_url))

    if not indexed_urls:
        raise ValueError("No URLs provided")

    failures: List[Tuple[int, Dict[str, Any]]] = []
    results_with_index: List[Tuple[int, Dict[str, Any]]] = []

    with ThreadPoolExecutor(max_workers=MAX_YTDLP_CONCURRENCY) as executor:
        futures = []

        for idx, url in indexed_urls:
            jobs, url_failures = _extract_entries_for_url(idx, url, output_dir)
            failures.extend(url_failures)

            for job in jobs:
                fut = executor.submit(_download_single_track, job, output_dir)
                futures.append(fut)

        for fut in futures:
            root_index, result = fut.result()
            results_with_index.append((root_index, result))

    results_with_index.extend(failures)
    results_with_index.sort(key=lambda pair: pair[0])

    return [res for _, res in results_with_index]


def batch_download_audio(urls: List[str], output_dir: Path) -> List[Dict[str, Any]]:
    return _download_for_urls(urls, output_dir)
