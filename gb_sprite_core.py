"""
gb_sprite_core.py
Lógica de conversão de imagens para o formato de sprite Game Boy / GBC.
Usado tanto pela CLI (gb_sprite_converter.py) quanto pela GUI (gb_sprite_gui.py).
"""

import numpy as np
from PIL import Image

GB_GRAY_PALETTE = [
    (255, 255, 255),
    (170, 170, 170),
    (85, 85, 85),
    (0, 0, 0),
]

GB_GREEN_PALETTE = [
    (155, 188, 15),
    (139, 172, 15),
    (48, 98, 48),
    (15, 56, 15),
]


def hex_to_rgb(hexstr):
    hexstr = hexstr.strip().lstrip("#")
    return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))


def build_palette_image(colors):
    pal_img = Image.new("P", (1, 1))
    flat = []
    for c in colors:
        flat.extend(c)
    while len(flat) < 768:
        flat.extend(colors[-1])
    pal_img.putpalette(flat[:768])
    return pal_img


def downscale(img, target_size):
    img = img.convert("RGB")
    return img.resize(target_size, Image.LANCZOS)


def ordered_dither(img, colors):
    bayer = np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5],
    ]) / 16.0 - 0.5

    arr = np.asarray(img).astype(np.float32)
    h, w, _ = arr.shape
    threshold_map = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w]
    threshold_map = threshold_map[:, :, None] * 32

    noisy = np.clip(arr + threshold_map, 0, 255).astype(np.uint8)
    noisy_img = Image.fromarray(noisy, "RGB")

    pal_img = build_palette_image(colors)
    return noisy_img.quantize(palette=pal_img, dither=Image.Dither.NONE)


def quantize_to_palette(img, colors, dither_mode):
    if dither_mode == "ordered":
        quantized = ordered_dither(img, colors)
    else:
        pal_img = build_palette_image(colors)
        dither = Image.Dither.FLOYDSTEINBERG if dither_mode == "floyd-steinberg" else Image.Dither.NONE
        quantized = img.quantize(palette=pal_img, dither=dither)
    return quantized.convert("RGB")


def rgb_to_index(pixel, colors):
    distances = [sum((int(a) - int(b)) ** 2 for a, b in zip(pixel, c)) for c in colors]
    return distances.index(min(distances))


def image_to_2bpp(img, colors):
    w, h = img.size
    if w % 8 != 0 or h % 8 != 0:
        raise ValueError(f"Dimensões ({w}x{h}) precisam ser múltiplos de 8.")

    pixels = np.asarray(img)
    output = bytearray()
    tiles_x, tiles_y = w // 8, h // 8

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            for row in range(8):
                y = ty * 8 + row
                lo_byte = hi_byte = 0
                for col in range(8):
                    x = tx * 8 + col
                    idx = rgb_to_index(tuple(pixels[y, x]), colors)
                    bit_pos = 7 - col
                    lo_byte |= (idx & 0b01) << bit_pos
                    hi_byte |= ((idx & 0b10) >> 1) << bit_pos
                output.append(lo_byte)
                output.append(hi_byte)
    return bytes(output)


def bytes_to_asm(data, label="SpriteTiles"):
    lines = [f"{label}::"]
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_values = ", ".join(f"${b:02X}" for b in chunk)
        lines.append(f"    DB {hex_values}")
    return "\n".join(lines)


def convert_image(input_path, size, colors, dither_mode):
    """Pipeline completo: retorna (imagem_final_PIL, dados_2bpp_bytes)."""
    original = Image.open(input_path)
    small = downscale(original, size)
    final_img = quantize_to_palette(small, colors, dither_mode)
    tile_data = image_to_2bpp(final_img, colors)
    return final_img, tile_data
