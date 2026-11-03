"""
Copies the Baxxid source art in art/ into the mod's asset folder, checked against
the vanilla Argonosh sheets the race is cloned from.

Usage:  python tools/import_sprites.py [SOURCE_DIR] [GAME_DIR]
Needs:  pip install pillow

Every sheet is optional: until the spriter supplies one, the mod keeps the placeholder
copy of the Argonosh sheet already in assets/sprite. A supplied sheet must be exactly the
same size as the Argonosh sheet it replaces (the game reads frames by fixed position).
"""
import io
import os
import sys
import zipfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "art")
GAME = sys.argv[2] if len(sys.argv) > 2 else "M:/SteamLibrary/steamapps/common/Songs of Syx"
OUT = os.path.join(ROOT, "src/main/resources/mod-files/assets/sprite")

GRID_GREEN = (0, 255, 0, 255)
GRID_BLUE = (0, 0, 132, 255)

# source file (relative to SRC) -> folder under assets/sprite; saved there as Baxxid.png
SHEETS = {
    "Baxxid.png": "race",                 # body
    "skelleton.png": "race/skelleton",    # corpse/skeleton
    "worldcamp.png": "race/worldcamp",    # camp on the world map
    "icon24.png": "icon/24/race",
    "icon32.png": "icon/32/race",
}


def vanilla(path):
    with zipfile.ZipFile(os.path.join(GAME, "base/data.zip")) as z:
        return Image.open(io.BytesIO(z.read("data/assets/" + path))).convert("RGBA")


def sheet(src, folder):
    """Copies one sheet, restoring grid lines that were painted over."""
    im = Image.open(os.path.join(SRC, src)).convert("RGBA")
    ref = vanilla(f"sprite/{folder}/Argonosh.png")
    if im.size != ref.size:
        raise SystemExit(f"{src} is {im.size}, must be {ref.size} like the Argonosh sheet")
    p, r = im.load(), ref.load()
    fixed = 0
    for y in range(im.height):
        for x in range(im.width):
            if r[x, y] == GRID_GREEN and p[x, y] == GRID_BLUE:
                p[x, y] = GRID_GREEN
                fixed += 1
    if fixed:
        print(f"restored {fixed} grid pixels in {src}")
    path = os.path.join(OUT, folder, "Baxxid.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    print("wrote", os.path.relpath(path, ROOT), im.size)


if __name__ == "__main__":
    for src, folder in SHEETS.items():
        if os.path.exists(os.path.join(SRC, src)):
            sheet(src, folder)
        else:
            print(f"no {src} in art/, keeping placeholder")
