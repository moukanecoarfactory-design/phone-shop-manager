"""
Create a circular avatar .ico for Desktop shortcut.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import sys


def make_circular_icon(source: Path, output: Path, size: int = 512):
    """Convert an image to a circular icon with transparent background."""
    if not source.exists():
        print(f"❌ Not found: {source}")
        return False

    img = Image.open(source).convert("RGBA")

    # Make it square by cropping to center
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize to target
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Create transparent result
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)

    # Add a blue border ring
    border = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    ring_width = int(size * 0.04)  # 4% of size
    border_draw.ellipse(
        (0, 0, size - 1, size - 1),
        outline=(14, 165, 233, 255),  # #0ea5e9 blue
        width=ring_width
    )

    # Combine
    final = Image.alpha_composite(result, border)

    # Save as .ico with multiple sizes
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    final.save(output, format="ICO", sizes=sizes)

    # Also save PNG version for reference
    png_output = output.with_suffix(".png")
    final.save(png_output, format="PNG")

    print(f"✅ Circular icon created: {output}")
    print(f"✅ PNG preview: {png_output}")
    return True


def main():
    base = Path(__file__).parent
    assets = base / "data" / "assets"

    # Try multiple source filenames
    source = None
    for name in ("avatar.jpg", "avatar.jpeg", "avatar.png"):
        p = assets / name
        if p.exists():
            source = p
            break

    if not source:
        print("❌ No avatar found in data/assets/")
        return

    output = assets / "avatar_circular.ico"
    make_circular_icon(source, output)


if __name__ == "__main__":
    main()