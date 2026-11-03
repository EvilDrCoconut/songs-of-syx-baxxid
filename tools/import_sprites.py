"""
Copies the Baxxid source art in art/ into the mod's asset folder, checked against
the vanilla Argonosh sheets the race is cloned from. Face and infant art in
art/baxxid/ is copied to the race-specific asset paths.

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

FACE_SHEETS = {
    "Baby.png": ("BaxxidBaby.png", (52, 60)),
    "Ears.png": ("BaxxidEars.png", (208, 60)),
    "Eyebrows.png": ("BaxxidEyebrow.png", (208, 60)),
    "Eyes.png": ("BaxxidEyes.png", (208, 60)),
    "Feature.png": ("BaxxidFeature.png", (208, 60)),
    "Hair.png": ("BaxxidHair.png", (208, 60)),
    "Lips.png": ("BaxxidMouth.png", (208, 60)),
    "Make-Up.png": ("BaxxidMakeup.png", (208, 60)),
    "Skull.png": ("BaxxidSkull.png", (208, 60)),
    "SlaveCollar.png": ("BaxxidSlaveCollar.png", (208, 60)),
    "Torso.png": ("BaxxidChest.png", (208, 60)),
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


def custom_sheet(src, folder, name, size):
    source_path = os.path.join(SRC, "baxxid", src)
    if not os.path.exists(source_path):
        print(f"no baxxid/{src} in art/, keeping existing asset")
        return
    with Image.open(source_path) as source:
        if source.size != size:
            raise SystemExit(f"baxxid/{src} is {source.size}, expected {size}")
        im = source.convert("RGBA")
    path = os.path.join(OUT, folder, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    print("wrote", os.path.relpath(path, ROOT), im.size)


if __name__ == "__main__":
    for src, folder in SHEETS.items():
        if os.path.exists(os.path.join(SRC, src)):
            sheet(src, folder)
        else:
            print(f"no {src} in art/, keeping placeholder")
    for src, (name, size) in FACE_SHEETS.items():
        custom_sheet(src, "race/face", name, size)
    custom_sheet("baxxidinfant.png", "race/infant", "Baxxid.png", (176, 22))
