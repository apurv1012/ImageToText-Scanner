"""
Generates icon.ico — a simple, original icon used for both the tray icon and
the packaged .exe. Run this once (python generate_icon.py) whenever you want
to regenerate it; the output is a plain .ico file, no external assets needed.

Design: a blue rounded square with white "viewfinder" corner brackets
(suggesting a screen capture / scan) and two bold horizontal bars in the
center (suggesting extracted text lines). Kept bold and high-contrast so it
still reads clearly at 16x16 in the Windows tray.
"""
from PIL import Image, ImageDraw

CANVAS = 256
BLUE = (37, 99, 235, 255)       # background
WHITE = (255, 255, 255, 255)    # foreground glyph


def draw_icon(paused=False):
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg = (120, 120, 128, 255) if paused else BLUE
    margin = 10
    draw.rounded_rectangle(
        [margin, margin, CANVAS - margin, CANVAS - margin],
        radius=56, fill=bg
    )

    # Viewfinder corner brackets (suggests "capture / scan")
    bracket_len = 56
    bracket_w = 16
    inset = 38
    corners = [
        (inset, inset, 1, 1),                              # top-left
        (CANVAS - inset, inset, -1, 1),                     # top-right
        (inset, CANVAS - inset, 1, -1),                     # bottom-left
        (CANVAS - inset, CANVAS - inset, -1, -1),           # bottom-right
    ]
    half = bracket_w // 2
    for x, y, dx, dy in corners:
        # horizontal arm
        hx0, hx1 = sorted([x, x + dx * bracket_len])
        draw.rounded_rectangle(
            [hx0, y - half, hx1, y + half],
            radius=half, fill=WHITE
        )
        # vertical arm
        vy0, vy1 = sorted([y, y + dy * bracket_len])
        draw.rounded_rectangle(
            [x - half, vy0, x + half, vy1],
            radius=half, fill=WHITE
        )

    # Two bold "text line" bars in the center (suggests extracted text)
    bar_h = 22
    cy = CANVAS // 2
    draw.rounded_rectangle([70, cy - bar_h - 8, 186, cy - 8], radius=bar_h // 2, fill=WHITE)
    draw.rounded_rectangle([70, cy + 8, 152, cy + 8 + bar_h], radius=bar_h // 2, fill=WHITE)

    return img


def main():
    icon = draw_icon(paused=False)
    icon.save("icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    paused_icon = draw_icon(paused=True)
    paused_icon.save("icon_paused.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    print("Wrote icon.ico and icon_paused.ico")


if __name__ == "__main__":
    main()
