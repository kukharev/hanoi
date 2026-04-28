from PIL import Image, ImageDraw

DISK_COLORS = [
    (255, 107, 107), (255, 160, 122), (255, 217, 61), (107, 203, 119),
    (77, 150, 255), (155, 89, 182), (224, 86, 160), (0, 206, 201),
]
BG_COLOR = (26, 26, 46)
PEG_COLOR = (93, 64, 55)
BASE_COLOR = (62, 39, 35)
TEXT_COLOR = (236, 240, 241)


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(size * 0.05)
    corner_r = max(int(size * 0.08), 2)

    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=corner_r,
        fill=BG_COLOR,
    )

    base_y = int(size * 0.82)
    base_h = int(size * 0.08)
    draw.rectangle(
        [int(size * 0.1), base_y, int(size * 0.9), base_y + base_h],
        fill=BASE_COLOR,
    )

    peg_positions = [0.22, 0.5, 0.78]
    peg_w = max(int(size * 0.04), 2)
    peg_top = int(size * 0.18)

    for px_ratio in peg_positions:
        px = int(size * px_ratio)
        draw.rectangle(
            [px - peg_w // 2, peg_top, px + peg_w // 2, base_y],
            fill=PEG_COLOR,
        )

    disks = [
        (0, 5, 0.7),
        (0, 4, 0.6),
        (0, 3, 0.5),
        (0, 2, 0.38),
        (0, 1, 0.25),
        (1, 6, 0.75),
        (1, 5, 0.6),
        (1, 3, 0.42),
    ]

    disk_h = max(int(size * 0.055), 3)
    spacing = max(int(size * 0.005), 1)
    max_w = int(size * 0.24)
    min_w = int(size * 0.08)

    peg_stacks = {0: [], 1: [], 2: []}
    for peg, disk_size, w_ratio in disks:
        peg_stacks[peg].append((disk_size, w_ratio))

    for peg_idx in peg_stacks:
        px = int(size * peg_positions[peg_idx])
        stack = peg_stacks[peg_idx]
        for slot, (disk_size, w_ratio) in enumerate(stack):
            w = int(min_w + w_ratio * (max_w - min_w))
            color_idx = (disk_size - 1) % len(DISK_COLORS)
            color = DISK_COLORS[color_idx]
            dy = base_y - (slot + 1) * (disk_h + spacing)
            draw.rounded_rectangle(
                [px - w // 2, dy, px + w // 2, dy + disk_h],
                radius=max(int(size * 0.015), 1),
                fill=color,
            )

    if size >= 64:
        try:
            font_size = max(int(size * 0.14), 8)
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except (OSError, IOError):
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except (OSError, IOError):
                    font = ImageFont.load_default()
            text = "H"
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = size // 2 - tw // 2
            ty = int(size * 0.02) + margin
            draw.text((tx, ty), text, fill=TEXT_COLOR, font=font)
        except Exception:
            pass

    return img


sizes = [16, 32, 48, 64, 128, 256]
icons = [draw_icon(s) for s in sizes]

icons[0].save(
    "hanoi.ico",
    format="ICO",
    sizes=[(s, s) for s in sizes],
    append_images=icons[1:],
)

print("hanoi.ico created successfully")
