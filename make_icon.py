"""
Convert avatar.jpg to avatar.ico for the app icon.
Creates multiple sizes (16, 32, 48, 64, 128, 256) for crisp display.
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Missing Pillow library.")
    print("Install it with: python -m pip install Pillow")
    sys.exit(1)


def convert_to_ico(source: Path, output: Path):
    """Convert an image to .ico with multiple sizes."""
    if not source.exists():
        print(f"❌ Source not found: {source}")
        return False

    img = Image.open(source).convert("RGBA")

    # Make it square by cropping to center
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img = img.crop((left, top, left + size, top + size))

    # Save as ICO with multiple sizes
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output, format="ICO", sizes=sizes)
    print(f"✅ Icon created: {output}")
    print(f"   Sizes: {sizes}")
    return True


def main():
    base = Path(__file__).resolve().parent
    assets = base / "data" / "assets"

    # Try multiple source filenames
    source = None
    for name in ("avatar.jpg", "avatar.jpeg", "avatar.png"):
        p = assets / name
        if p.exists():
            source = p
            break

    if not source:
        print("❌ No avatar file found in data/assets/")
        print("   Expected: avatar.jpg, avatar.jpeg, or avatar.png")
        return

    output = assets / "avatar.ico"
    convert_to_ico(source, output)


if __name__ == "__main__":
    main()