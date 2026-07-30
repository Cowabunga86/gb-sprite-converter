#!/usr/bin/env python3
"""
gb_sprite_gui.py — interface gráfica moderna para o conversor de sprites Game Boy/GBC.
Construída com CustomTkinter (visual escuro, cantos arredondados).

Executar: python gb_sprite_gui.py
"""

import threading
from pathlib import Path
from tkinter import filedialog, colorchooser

import customtkinter as ctk
from PIL import Image, ImageTk

from gb_sprite_core import (
    GB_GRAY_PALETTE, convert_image, bytes_to_asm,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_GBC_PALETTE = ["#FFFFFF", "#AACCFF", "#335599", "#001133"]


class SpriteConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GB Sprite Converter")
        self.geometry("980x640")
        self.minsize(860, 560)

        self.input_path = None
        self.original_preview_img = None
        self.result_img = None
        self.result_tile_data = None
        self.gbc_palette_hex = list(DEFAULT_GBC_PALETTE)
        self.palette_swatches = []

        self._build_layout()

    # ---------------------------------------------------------------- UI

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_preview_area()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_columnconfigure(0, weight=1)

        row = 0
        ctk.CTkLabel(
            sidebar, text="GB Sprite Converter",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=row, column=0, padx=20, pady=(20, 4), sticky="w")
        row += 1

        ctk.CTkLabel(
            sidebar, text="Converte imagens para sprites\nGame Boy / GBC (2bpp)",
            font=ctk.CTkFont(size=12), text_color="gray70", justify="left"
        ).grid(row=row, column=0, padx=20, pady=(0, 16), sticky="w")
        row += 1

        self.load_btn = ctk.CTkButton(
            sidebar, text="Carregar imagem...", command=self.load_image
        )
        self.load_btn.grid(row=row, column=0, padx=20, pady=(0, 4), sticky="we")
        row += 1

        self.file_label = ctk.CTkLabel(
            sidebar, text="Nenhum arquivo selecionado", font=ctk.CTkFont(size=11),
            text_color="gray60", wraplength=260, justify="left"
        )
        self.file_label.grid(row=row, column=0, padx=20, pady=(0, 16), sticky="w")
        row += 1

        # Tamanho
        ctk.CTkLabel(sidebar, text="Tamanho do sprite (px)", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=row, column=0, padx=20, pady=(4, 4), sticky="w"
        )
        row += 1

        size_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        size_frame.grid(row=row, column=0, padx=20, pady=(0, 12), sticky="we")
        size_frame.grid_columnconfigure((0, 1), weight=1)

        self.width_entry = ctk.CTkEntry(size_frame, placeholder_text="Largura")
        self.width_entry.insert(0, "56")
        self.width_entry.grid(row=0, column=0, padx=(0, 6), sticky="we")

        self.height_entry = ctk.CTkEntry(size_frame, placeholder_text="Altura")
        self.height_entry.insert(0, "56")
        self.height_entry.grid(row=0, column=1, sticky="we")
        row += 1

        ctk.CTkLabel(
            sidebar, text="Precisa ser múltiplo de 8", font=ctk.CTkFont(size=10), text_color="gray50"
        ).grid(row=row, column=0, padx=20, pady=(0, 12), sticky="w")
        row += 1

        # Modo
        ctk.CTkLabel(sidebar, text="Paleta", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=row, column=0, padx=20, pady=(4, 4), sticky="w"
        )
        row += 1

        self.mode_var = ctk.StringVar(value="gb")
        self.mode_menu = ctk.CTkSegmentedButton(
            sidebar, values=["gb (cinza)", "gbc (cores)"],
            command=self._on_mode_change
        )
        self.mode_menu.set("gb (cinza)")
        self.mode_menu.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="we")
        row += 1

        # Paleta customizada (swatches) - só aparece em modo gbc
        self.palette_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.palette_frame.grid(row=row, column=0, padx=20, pady=(0, 12), sticky="we")
        self._build_palette_swatches()
        self.palette_frame.grid_remove()  # começa escondido (modo gb é o padrão)
        row += 1
        self.palette_row = row

        # Dithering
        ctk.CTkLabel(sidebar, text="Dithering", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=row, column=0, padx=20, pady=(4, 4), sticky="w"
        )
        row += 1

        self.dither_var = ctk.StringVar(value="floyd-steinberg")
        self.dither_menu = ctk.CTkOptionMenu(
            sidebar, values=["floyd-steinberg", "ordered", "none"], variable=self.dither_var
        )
        self.dither_menu.grid(row=row, column=0, padx=20, pady=(0, 16), sticky="we")
        row += 1

        # Botão converter
        self.convert_btn = ctk.CTkButton(
            sidebar, text="Converter", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_conversion
        )
        self.convert_btn.grid(row=row, column=0, padx=20, pady=(8, 8), sticky="we")
        row += 1

        self.save_btn = ctk.CTkButton(
            sidebar, text="Salvar arquivos...", height=36,
            fg_color="transparent", border_width=1,
            command=self.save_outputs, state="disabled"
        )
        self.save_btn.grid(row=row, column=0, padx=20, pady=(0, 8), sticky="we")
        row += 1

        self.status_label = ctk.CTkLabel(
            sidebar, text="", font=ctk.CTkFont(size=11), text_color="gray60", wraplength=260
        )
        self.status_label.grid(row=row, column=0, padx=20, pady=(8, 20), sticky="w")

    def _build_palette_swatches(self):
        ctk.CTkLabel(
            self.palette_frame, text="Clique para escolher cada cor",
            font=ctk.CTkFont(size=11), text_color="gray60"
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        self.palette_swatches = []
        for i, hex_color in enumerate(self.gbc_palette_hex):
            btn = ctk.CTkButton(
                self.palette_frame, text="", width=50, height=32,
                fg_color=hex_color, hover_color=hex_color,
                border_width=1, border_color="gray40",
                command=lambda idx=i: self._pick_color(idx)
            )
            btn.grid(row=1, column=i, padx=2)
            self.palette_swatches.append(btn)

    def _pick_color(self, idx):
        color = colorchooser.askcolor(color=self.gbc_palette_hex[idx])
        if color and color[1]:
            self.gbc_palette_hex[idx] = color[1]
            self.palette_swatches[idx].configure(fg_color=color[1], hover_color=color[1])

    def _on_mode_change(self, value):
        if value.startswith("gbc"):
            self.palette_frame.grid()
        else:
            self.palette_frame.grid_remove()

    def _build_preview_area(self):
        preview = ctk.CTkFrame(self)
        preview.grid(row=0, column=1, sticky="nswe", padx=16, pady=16)
        preview.grid_columnconfigure((0, 1), weight=1)
        preview.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(preview, text="Original", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, pady=(12, 4)
        )
        ctk.CTkLabel(preview, text="Convertido (ampliado)", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=1, pady=(12, 4)
        )

        self.original_canvas = ctk.CTkLabel(preview, text="Nenhuma imagem carregada", fg_color="gray17", corner_radius=10)
        self.original_canvas.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nswe")

        self.result_canvas = ctk.CTkLabel(preview, text="Aguardando conversão", fg_color="gray17", corner_radius=10)
        self.result_canvas.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nswe")

    # ------------------------------------------------------------ ações

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Todos os arquivos", "*.*")]
        )
        if not path:
            return

        self.input_path = Path(path)
        self.file_label.configure(text=self.input_path.name)

        img = Image.open(self.input_path).convert("RGB")
        self.original_preview_img = img
        self._show_image(self.original_canvas, img, max_size=380)

        self.result_canvas.configure(image=None, text="Aguardando conversão")
        self.save_btn.configure(state="disabled")
        self.status_label.configure(text="")

    def _show_image(self, label_widget, pil_img, max_size=380):
        img_copy = pil_img.copy()
        img_copy.thumbnail((max_size, max_size), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img_copy)
        label_widget.configure(image=tk_img, text="")
        label_widget.image = tk_img  # evita garbage collection

    def run_conversion(self):
        if not self.input_path:
            self.status_label.configure(text="Carregue uma imagem primeiro.", text_color="orange")
            return

        try:
            w = int(self.width_entry.get())
            h = int(self.height_entry.get())
        except ValueError:
            self.status_label.configure(text="Largura/altura precisam ser números.", text_color="orange")
            return

        w = round(w / 8) * 8
        h = round(h / 8) * 8
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(w))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(h))

        mode = self.mode_menu.get()
        if mode.startswith("gbc"):
            colors = [self._hex_to_rgb(c) for c in self.gbc_palette_hex]
        else:
            colors = GB_GRAY_PALETTE

        dither_mode = self.dither_var.get()

        self.convert_btn.configure(state="disabled", text="Convertendo...")
        self.status_label.configure(text="Processando...", text_color="gray60")

        thread = threading.Thread(
            target=self._convert_worker, args=((w, h), colors, dither_mode), daemon=True
        )
        thread.start()

    def _convert_worker(self, size, colors, dither_mode):
        try:
            final_img, tile_data = convert_image(self.input_path, size, colors, dither_mode)
            self.result_img = final_img
            self.result_tile_data = tile_data
            self.after(0, self._on_conversion_done, size)
        except Exception as e:
            self.after(0, self._on_conversion_error, str(e))

    def _on_conversion_done(self, size):
        preview = self.result_img.resize(
            (size[0] * 6, size[1] * 6), Image.NEAREST
        )
        self._show_image(self.result_canvas, preview, max_size=380)
        n_tiles = (size[0] // 8) * (size[1] // 8)
        self.status_label.configure(
            text=f"Concluído: {size[0]}x{size[1]}px, {n_tiles} tiles 8x8.",
            text_color="light green"
        )
        self.convert_btn.configure(state="normal", text="Converter")
        self.save_btn.configure(state="normal")

    def _on_conversion_error(self, message):
        self.status_label.configure(text=f"Erro: {message}", text_color="red")
        self.convert_btn.configure(state="normal", text="Converter")

    def save_outputs(self):
        if self.result_img is None:
            return
        out_dir = filedialog.askdirectory(title="Escolha a pasta de destino")
        if not out_dir:
            return
        out_dir = Path(out_dir)

        self.result_img.save(out_dir / "out_pixelart.png")
        preview = self.result_img.resize(
            (self.result_img.width * 8, self.result_img.height * 8), Image.NEAREST
        )
        preview.save(out_dir / "out_preview.png")
        (out_dir / "out_tiles.bin").write_bytes(self.result_tile_data)
        (out_dir / "out_tiles.asm").write_text(bytes_to_asm(self.result_tile_data))

        self.status_label.configure(text=f"Arquivos salvos em: {out_dir}", text_color="light green")

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    app = SpriteConverterApp()
    app.mainloop()
