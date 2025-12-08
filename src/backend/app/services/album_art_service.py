# app/services/album_art_service.py
from __future__ import annotations

from pathlib import Path
from typing import Set, Tuple, List, Dict, Any
import random

from mutagen.id3 import ID3, APIC, error as ID3Error

ALLOWED_IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def _infer_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix not in ALLOWED_IMAGE_MIME:
        raise ValueError(f"Unsupported image type: {suffix} (use .jpg, .jpeg, or .png)")
    return ALLOWED_IMAGE_MIME[suffix]


def replace_album_art_in_place(mp3_path: Path, image_path: Path) -> None:
    """
    Truly edit the file in place on disk:
    - mp3_path: path to the .mp3 file on disk
    - image_path: path to the cover image (jpg/png) on disk
    """
    if mp3_path.suffix.lower() != ".mp3":
        raise ValueError("Only .mp3 files are supported")

    if not mp3_path.exists():
        raise FileNotFoundError(f"MP3 not found: {mp3_path}")

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type = _infer_mime_type(image_path.name)
    image_bytes = image_path.read_bytes()

    try:
        tags = ID3(mp3_path)
    except ID3Error:
        tags = ID3()
        tags.save(mp3_path)
        tags = ID3(mp3_path)

    tags.delall("APIC")
    tags.add(
        APIC(
            encoding=3,
            mime=mime_type,
            type=3,  # front cover
            desc="Cover",
            data=image_bytes,
        )
    )
    tags.save(mp3_path)


def replace_album_art_bytes(
    mp3_bytes: bytes,
    mp3_filename: str,
    image_bytes: bytes,
    image_filename: str,
) -> Tuple[bytes, str]:
    """
    Web-friendly: work on in-memory bytes using a temp file under the hood.
    Returns (updated_mp3_bytes, output_filename).
    """
    import tempfile

    mime_type = _infer_mime_type(image_filename)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        tmp_mp3.write(mp3_bytes)
        tmp_mp3_path = Path(tmp_mp3.name)

    try:
        try:
            tags = ID3(tmp_mp3_path)
        except ID3Error:
            tags = ID3()
            tags.save(tmp_mp3_path)
            tags = ID3(tmp_mp3_path)

        tags.delall("APIC")
        tags.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc="Cover",
                data=image_bytes,
            )
        )
        tags.save(tmp_mp3_path)

        updated_bytes = tmp_mp3_path.read_bytes()
    finally:
        tmp_mp3_path.unlink(missing_ok=True)

    output_name = mp3_filename
    return updated_bytes, output_name

def _collect_paths_from_any(
    raw_paths: List[str],
    allowed_suffixes: Set[str],
    empty_error_label: str,
    debug_label: str | None = None,
) -> List[Path]:
    """
    For each entry in raw_paths:
      - if it's a file -> include if suffix is allowed
      - if it's a directory -> include all matching files under **/*
    De-dups and ensures paths exist.
    """
    collected: List[Path] = []

    for raw in raw_paths:
        if not raw:
            continue
        p = Path(raw).expanduser()
        if p.is_dir():
            for candidate in p.rglob("*"):
                if candidate.is_file():
                    collected.append(candidate)
        else:
            collected.append(p)

    if debug_label:
        print(f"{debug_label} collected (pre-filter): {collected}")

    unique: Dict[str, Path] = {}
    for p in collected:
        suffix = p.suffix.lower()
        if suffix not in allowed_suffixes:
            continue
        if not p.exists():
            continue
        key = str(p.resolve())
        unique[key] = p

    result = list(unique.values())
    if not result:
        raise ValueError(f"No {empty_error_label} found from provided paths/folders")

    if debug_label:
        print(f"{debug_label} collected (filtered): {result}")

    return result


def _collect_song_paths_from_any(song_paths: List[str]) -> List[Path]:
    """
    For each entry in song_paths:
      - if it's a file -> include if .mp3
      - if it's a directory -> include all **/*.mp3
    """
    return _collect_paths_from_any(
        raw_paths=song_paths,
        allowed_suffixes={".mp3"},
        empty_error_label=".mp3 songs",
        debug_label="songs",
    )


def _collect_image_paths_from_any(image_paths: List[str]) -> List[Path]:
    """
    For each entry in image_paths:
      - if it's a file -> include if supported image type
      - if it's a directory -> include all supported images under **/*
    """
    return _collect_paths_from_any(
        raw_paths=image_paths,
        allowed_suffixes=set(ALLOWED_IMAGE_MIME.keys()),
        empty_error_label="supported image files",
        debug_label="images",
    )


def gather_batch_paths(
    song_paths: List[str],
    image_paths: List[str],
) -> Tuple[List[Path], List[Path]]:
    """
    Resolve and validate songs + images from lists of paths/folders.
    Each entry in song_paths/image_paths may be:
      - a file path, OR
      - a directory path (recursively scanned)
    """
    print(f"song paths: {song_paths}")
    print(f"image paths: {image_paths}")
    songs = _collect_song_paths_from_any(song_paths)
    images = _collect_image_paths_from_any(image_paths)
    return songs, images


def batch_replace_album_art_in_place(
    song_paths: List[Path],
    image_paths: List[Path],
) -> List[Dict[str, Any]]:
    """
    For each song:
      - if one image provided -> use that for all
      - if many images -> randomly pick an image per song
    Returns list of result dicts:
      { song_path, image_used, success, error }
    """
    if not song_paths:
        raise ValueError("No songs provided")

    if not image_paths:
        raise ValueError("No images provided")

    results: List[Dict[str, Any]] = []

    for song in song_paths:
        image = image_paths[0] if len(image_paths) == 1 else random.choice(image_paths)
        try:
            replace_album_art_in_place(song, image)
            results.append(
                {
                    "song_path": str(song),
                    "image_used": str(image),
                    "success": True,
                    "error": None,
                }
            )
        except Exception as e:
            results.append(
                {
                    "song_path": str(song),
                    "image_used": str(image),
                    "success": False,
                    "error": str(e),
                }
            )

    return results