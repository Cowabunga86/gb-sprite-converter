#!/usr/bin/env python3
"""
gb_sprite_converter.py — versão linha de comando
Uso: python gb_sprite_converter.py entrada.png --size 56 56 --mode gb
"""

import argparse
import sys
from pathlib import Path
from PIL import Image

from gb_sprite_core import (
    GB_GRAY_PALETTE, hex_to_rgb, convert_image, bytes_to_asm,
)


def parse_args():
    p = argparse.ArgumentParser(description="Converte uma imagem para sprite estilo Game Boy/GBC")
    p.add_argument("input", type=str)
    p.add_argument("--size", type=int, nargs=2, default=[56, 56], metavar=("LARGURA", "ALTURA"))
    p.add_argument("--mode", choices=["gb", "gbc"], default="gb")
    p.add_argument("--custom-palette", type=str, default=None,
                   help="4 cores em hex separadas por vírgula, ex: FFFFFF,AACCFF,335599,001133")
    p.add_argument("--dither", choices=["floyd-steinberg", "ordered", "none"], default="floyd-steinberg")
    p.add_argument("--upscale-preview", type=int, default=8)
    return p.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erro: arquivo não encontrado: {input_path}")
        sys.exit(1)

    size = tuple(args.size)
    if size[0] % 8 != 0 or size[1] % 8 != 0:
        size = (round(size[0] / 8) * 8, round(size[1] / 8) * 8)
        print(f"Aviso: ajustado para múltiplo de 8 -> {size}")

    if args.mode == "gbc" and args.custom_palette:
        hex_colors = args.custom_palette.split(",")
        if len(hex_colors) != 4:
            print("Erro: --custom-palette precisa ter exatamente 4 cores.")
            sys.exit(1)
        colors = [hex_to_rgb(h) for h in hex_colors]
    else:
        colors = GB_GRAY_PALETTE

    print(f"Carregando {input_path} ...")
    print(f"Convertendo para {size[0]}x{size[1]} px, modo {args.mode}, dither {args.dither} ...")
    final_img, tile_data = convert_image(input_path, size, colors, args.dither)

    out_dir = input_path.parent
    final_img.save(out_dir / "out_pixelart.png")
    preview = final_img.resize(
        (size[0] * args.upscale_preview, size[1] * args.upscale_preview), Image.NEAREST
    )
    preview.save(out_dir / "out_preview.png")
    (out_dir / "out_tiles.bin").write_bytes(tile_data)
    (out_dir / "out_tiles.asm").write_text(bytes_to_asm(tile_data))

    print("\nConcluído! Arquivos gerados em:", out_dir)
    print(f"Total de tiles 8x8: {(size[0] // 8) * (size[1] // 8)}")


if __name__ == "__main__":
    main()
