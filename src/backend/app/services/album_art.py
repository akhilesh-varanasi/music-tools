# app/services/album_art_service.py
from pathlib import Path
from typing import Tuple

from mutagen.id3 import ID3, APIC, error as ID3Error

ALLOWED_IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def _infer_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    mime = ALLOWED_IMAGE_MIME.get(suffix)
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

    # Load or create ID3 tags directly on the real file
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
