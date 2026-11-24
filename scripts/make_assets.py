"""Derive the build and README assets from the AETHERVEXA brand artwork in assets/.

The brand originals in assets/ are never modified. This script writes:

  aethervexa/resources/app-icon.ico        window and taskbar icon (copied from AETHERVEXA_App_Icon.ico)
  aethervexa/resources/app-icon-256.png    in-app logo
  assets/generated/portable.ico            icon for the portable builds (from Portable_EXE_Thumbnail.png)
  assets/generated/splash-public.png       portable-build splash screens
  assets/generated/splash-personal.png
  assets/generated/wizard-small-{100,150,200}.bmp   Setup wizard header icon at 100-200 % scaling
  assets/generated/social-preview.png      1280x640 GitHub social preview

Run:  .venv\\Scripts\\python.exe scripts\\make_assets.py
"""

import os
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ASSETS, "generated")
RESOURCES = os.path.join(ROOT, "aethervexa", "resources")
sys.path.insert(0, ROOT)

from aethervexa import APP_TAGLINE  # noqa: E402

SOURCES = {
    "icon": "AETHERVEXA_App_Icon.ico",
    "portable": "Portable_EXE_Thumbnail.png",
    "logo": "AETHERVEXA_Master_Logo1.png",
    "background": "Installer_Background.png",
    "welcome": "Installer_Welcome_Banner.bmp",
    "uninstall": "Uninstaller_Banner.bmp",
}
ICON_SIZES = [(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)]


def src(key: str) -> str:
    path = os.path.join(ASSETS, SOURCES[key])
    if not os.path.isfile(path):
        raise SystemExit(f"Missing brand artwork: {path}")
    return path


def ui_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    for name in (("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")):
        path = os.path.join(windir, "Fonts", name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def largest_icon_frame() -> Image.Image:
    icon = Image.open(src("icon"))
    icon.size = max(icon.info.get("sizes", {(256, 256)}))
    return icon.convert("RGBA")


def rounded(image: Image.Image, radius_ratio: float) -> Image.Image:
    """Make the corners outside a rounded rectangle transparent (for artwork drawn on a dark square)."""
    image = image.convert("RGBA")
    mask = Image.new("L", image.size, 0)
    radius = int(min(image.size) * radius_ratio)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius, fill=255)
    image.putalpha(mask)
    return image


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS)


def screen_paste(base: Image.Image, art: Image.Image, position: tuple[int, int]) -> Image.Image:
    """Blend artwork drawn on black onto a background with a screen blend, so its dark backing disappears."""
    base = base.convert("RGB")
    region = (position[0], position[1], position[0] + art.width, position[1] + art.height)
    base.paste(ImageChops.screen(base.crop(region), art.convert("RGB")), region[:2])
    return base


def make_app_icon() -> None:
    os.makedirs(RESOURCES, exist_ok=True)
    shutil.copyfile(src("icon"), os.path.join(RESOURCES, "app-icon.ico"))
    largest_icon_frame().resize((256, 256), Image.Resampling.LANCZOS).save(os.path.join(RESOURCES, "app-icon-256.png"))


def make_portable_icon() -> None:
    art = rounded(Image.open(src("portable")), 0.16).resize((256, 256), Image.Resampling.LANCZOS)
    art.save(os.path.join(OUT, "portable.ico"), sizes=ICON_SIZES)


def make_splashes() -> None:
    logo = Image.open(src("logo")).convert("RGB")
    for edition, label in (("public", "Public Edition"), ("personal", "Personal Edition")):
        splash = cover(Image.open(src("background")), (600, 320))
        overlay = Image.new("RGBA", splash.size, (5, 6, 20, 120))
        splash = Image.alpha_composite(splash.convert("RGBA"), overlay)
        splash = screen_paste(splash, logo.resize((540, 180), Image.Resampling.LANCZOS), (30, 40))
        draw = ImageDraw.Draw(splash)
        draw.text((300, 232), f"{APP_TAGLINE} · {label}", font=ui_font(17), fill=(199, 210, 254), anchor="mm")
        draw.rectangle((0, 0, 599, 319), outline=(90, 80, 200))
        splash.convert("RGB").save(os.path.join(OUT, f"splash-{edition}.png"))


def make_wizard_small() -> None:
    icon = largest_icon_frame()
    for name, scale in (("100", 1.0), ("150", 1.5), ("200", 2.0)):
        size = (round(55 * scale), round(58 * scale))
        tile = Image.new("RGB", size, (255, 255, 255))
        side = min(size) - round(4 * scale)
        art = icon.resize((side, side), Image.Resampling.LANCZOS)
        tile.paste(art, ((size[0] - side) // 2, (size[1] - side) // 2), art)
        tile.save(os.path.join(OUT, f"wizard-small-{name}.bmp"))


def make_social_preview() -> None:
    canvas = cover(Image.open(src("background")), (1280, 640)).convert("RGBA")
    canvas = Image.alpha_composite(canvas, Image.new("RGBA", canvas.size, (5, 6, 20, 90)))
    logo = Image.open(src("logo")).convert("RGB").resize((1020, 340), Image.Resampling.LANCZOS)
    canvas = screen_paste(canvas, logo, (130, 90))
    draw = ImageDraw.Draw(canvas)
    draw.text((640, 470), "AI watermark & provenance analysis for Windows", font=ui_font(38, True),
              fill=(241, 245, 249), anchor="mm")
    draw.text((640, 530), "C2PA Content Credentials · Google SynthID · AI-image detectors · invisible-text forensics",
              font=ui_font(24), fill=(165, 180, 252), anchor="mm")
    canvas.convert("RGB").save(os.path.join(OUT, "social-preview.png"))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for key in ("welcome", "uninstall"):
        src(key)  # fail early if the installer artwork is missing
    make_app_icon()
    make_portable_icon()
    make_splashes()
    make_wizard_small()
    make_social_preview()
    print(f"Assets derived from the brand artwork into {OUT} and {RESOURCES}")


if __name__ == "__main__":
    main()
