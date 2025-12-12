from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, parse_qs, urlencode

import yt_dlp
from yt_dlp.utils import DownloadError

MAX_YTDLP_CONCURRENCY = 16


def _build_ydl_opts(outtmpl: str, listing: bool = False) -> Dict[str, Any]:
    """Build yt-dlp options with Chrome Default cookies."""
    opts: Dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "cookiesfrombrowser": ("chrome", "Default"),
    }

    if listing:
        # yt-dlp will return "flat" entries with id/title/url for each item.
        opts["skip_download"] = True
        opts["extract_flat"] = "in_playlist"

        opts.pop("postprocessors", None)

    return opts


def _map_cookies_error(e: DownloadError) -> str:
    msg = str(e)
    if "could not find chrome cookies database" in msg.lower():
        return (
            "Chrome cookies database not found for profile 'Default'. "
            "Please open Chrome on this machine, log into YouTube in the "
            "Default profile, then try again."
        )
    return msg


def _extract_entries_for_url(
    root_index: int,
    url: str,
    output_dir: Path,
) -> Tuple[List[Dict[str, Any]], List[Tuple[int, Dict[str, Any]]]]:
    outtmpl = str(output_dir / "%(title)s.%(ext)s")
    print(f"outtmpl (listing): {outtmpl}")

    opts = _build_ydl_opts(outtmpl, listing=True)
    jobs: List[Dict[str, Any]] = []
    failures: List[Tuple[int, Dict[str, Any]]] = []

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as e:
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
    opts = _build_ydl_opts(outtmpl, listing=False)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(entry_url, download=True)
    except DownloadError as e:
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
    print("into download urls")

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

        print(f"url: {parsed_url}")
        print("done deleting")

        indexed_urls.append((idx, parsed_url))
    print("done indexing")

    if not indexed_urls:
        raise ValueError("No URLs provided")

    failures: List[Tuple[int, Dict[str, Any]]] = []
    results_with_index: List[Tuple[int, Dict[str, Any]]] = []

    print("prior to kicking downloads off")
    with ThreadPoolExecutor(max_workers=MAX_YTDLP_CONCURRENCY) as executor:
        futures = []

        for idx, url in indexed_urls:
            print("prior to extracting url entries")
            jobs, url_failures = _extract_entries_for_url(idx, url, output_dir)
            print("post extracting url entries")
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
