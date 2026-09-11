"""
Captik Google Font Downloader
------------------------------
Data 6.htm only gives us font NAMES (e.g. "Poppins"). To actually draw
text on a video frame (PIL / ffmpeg / ASS subtitles), we need the real
.ttf/.woff2 file for that font. This module fetches it from Google's
public Fonts CSS API and caches it locally in data/fonts_cache/.

Usage (from your video-rendering code, once it exists):

    from .google_font_downloader import get_font_file

    font_path = get_font_file(project.selected_font or project.template.font_family)
    if font_path:
        # pass font_path into PIL.ImageFont.truetype(font_path, size)
        # or reference it in your ffmpeg/ASS style definition
        ...
"""

import re
import urllib.request
from pathlib import Path
from typing import Optional

from .font_engine import FONT_FILES_DIR

CSS_API = "https://fonts.googleapis.com/css2?family={family}:wght@400;700&display=swap"

# Modern browsers get served .woff2 (not usable by PIL for drawing text).
# An old browser User-Agent makes Google's API return plain .ttf instead,
# which PIL / ffmpeg / ASS can use directly.
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.34 (KHTML, like Gecko)"
}


def _safe_filename(family: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", family).strip("_").lower()


def get_font_file(family: str) -> Optional[Path]:
    """
    Returns a local Path to a font file for `family`, downloading it
    from Google Fonts on first use and caching it after that.
    Returns None if the font could not be found/downloaded.
    """

    if not family:
        return None

    FONT_FILES_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_filename(family)
    cached = list(FONT_FILES_DIR.glob(f"{safe_name}.*"))
    if cached:
        return cached[0]

    url = CSS_API.format(family=family.replace(" ", "+"))

    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            css_text = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[fonts] could not fetch CSS for '{family}': {e}")
        return None

    match = re.search(r"src:\s*url\(([^)]+)\)", css_text)
    if not match:
        print(f"[fonts] no font file URL found for '{family}' (name may be wrong)")
        return None

    font_url = match.group(1).strip("'\"")
    ext = ".ttf" if font_url.endswith(".ttf") else ".woff2"
    dest = FONT_FILES_DIR / f"{safe_name}{ext}"

    try:
        urllib.request.urlretrieve(font_url, dest)
    except Exception as e:
        print(f"[fonts] could not download font file for '{family}': {e}")
        return None

    return dest
