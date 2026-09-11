"""
Captik Font Engine
Extracts Google Font family names from a locally saved copy of
fonts.google.com (Data 6.htm), and provides search over them.
"""

import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FONT_CACHE = DATA_DIR / "font_library.json"
FONT_FILES_DIR = DATA_DIR / "fonts_cache"  # actual .ttf/.woff2 files get cached here


def _find_source_file():
    """
    Locate the saved Google Fonts HTML page.
    Handles both 'Data 6.htm' and 'Data_6.htm' naming, and falls back
    to any .htm file in the data folder.
    """
    candidates = [
        DATA_DIR / "Data 6.htm",
        DATA_DIR / "Data_6.htm",
    ]

    for path in candidates:
        if path.exists():
            return path

    matches = list(DATA_DIR.glob("*.htm"))
    return matches[0] if matches else None


def extract_font_names():
    """Extract font-family names from the saved Google Fonts page."""

    source_file = _find_source_file()

    if not source_file:
        print(f"Source file not found in {DATA_DIR}")
        return []

    html = source_file.read_text(encoding="utf-8", errors="ignore")

    fonts = set()

    # 1. @font-face { font-family: 'Font Name'; }
    pattern_1 = r"font-family\s*:\s*['\"]([^'\"]+)['\"]"
    for font in re.findall(pattern_1, html, re.IGNORECASE):
        font = font.strip()
        if font:
            fonts.add(font)

    # 2. "family":"Font Name"
    pattern_2 = r'["\']family["\']\s*:\s*["\']([^"\']+)["\']'
    for font in re.findall(pattern_2, html, re.IGNORECASE):
        font = font.strip()
        if font:
            fonts.add(font)

    # 3. Google Fonts catalog entries embedded as escaped JSON:
    #    \"Font Name\",\"Font Name\",[\"Designer\", ...]
    pattern_3 = r'\\"([A-Za-z0-9 ]+)\\",\\"\1\\",\['
    for font in re.findall(pattern_3, html):
        font = font.strip()
        if font:
            fonts.add(font)

    # Remove obvious CSS/system fonts
    ignored = {
        "inherit", "initial", "unset",
        "sans-serif", "serif", "monospace", "cursive", "fantasy",
    }
    fonts = {font for font in fonts if font.lower() not in ignored}

    font_list = sorted(fonts, key=str.lower)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "source": source_file.name,
        "total_fonts": len(font_list),
        "fonts": font_list,
    }
    FONT_CACHE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return font_list


def get_fonts():
    """Load cached fonts. Build cache if needed."""

    if FONT_CACHE.exists():
        try:
            data = json.loads(FONT_CACHE.read_text(encoding="utf-8"))
            fonts = data.get("fonts", [])
            if fonts:
                return fonts
        except (json.JSONDecodeError, OSError):
            pass

    return extract_font_names()


def search_fonts(query=""):
    """Fast font name search (used by the live search box in the UI)."""

    fonts = get_fonts()
    query = query.strip().lower()

    if not query:
        return fonts

    return [font for font in fonts if query in font.lower()]


def rebuild_font_library():
    """Delete cache and rebuild it from the source HTML file."""

    if FONT_CACHE.exists():
        FONT_CACHE.unlink()

    return extract_font_names()


if __name__ == "__main__":
    fonts = rebuild_font_library()

    print("=" * 50)
    print("CAPTIK VIP FONT ENGINE")
    print("=" * 50)
    print(f"Total fonts found: {len(fonts)}")

    print("\nFirst 20 fonts:")
    for font in fonts[:20]:
        print("-", font)