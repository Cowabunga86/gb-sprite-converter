# gb-sprite-converter

Converte imagens para o formato de sprite Game Boy / Game Boy Color (2bpp),
com interface gráfica moderna e build automático de executáveis Windows via GitHub Actions.

## Download

1. Vá na aba **Actions** deste repositório
2. Clique no workflow **Build Windows EXE** mais recente (deve ter um ✓ verde)
3. Role até **Artifacts** e baixe `gb_sprite_converter-windows`
4. Extraia o `.zip` — você terá dois executáveis prontos para usar

> O build roda automaticamente a cada push. Se ainda estiver em andamento, aguarde ~2 minutos.

## Executáveis

- **GB_Sprite_Converter.exe** — interface gráfica (carregue uma imagem, ajuste tamanho, paleta e dithering, veja o preview e salve)
- **gb_sprite_converter_cli.exe** — linha de comando, útil para automatizar conversões em lote

## Uso — Interface Gráfica

Dê duplo-clique em `GB_Sprite_Converter.exe`. A interface permite:

- Carregar qualquer imagem (PNG, JPG, BMP...)
- Definir o tamanho de saída em pixels (ex: 16x16, 32x32, 56x56)
- Escolher a paleta: GB cinza clássico ou GB verde original
- Escolher o modo de dithering: nenhum, ordered ou Floyd-Steinberg
- Ver o preview antes de salvar
- Exportar `.png` (imagem final) e `.asm` (dados de tile em formato RGBDS)

## Uso — Linha de Comando

```
gb_sprite_converter_cli.exe <imagem> [opções]
```

Exemplos:

```
gb_sprite_converter_cli.exe sprite.png --size 16 16 --mode gb
gb_sprite_converter_cli.exe arte.png --size 56 56 --mode gbc --dither floyd-steinberg
```

Opções:

| Opção | Descrição | Padrão |
|---|---|---|
| `--size W H` | Tamanho de saída em pixels | `16 16` |
| `--mode` | Paleta: `gb` (cinza) ou `gbc` (verde) | `gb` |
| `--dither` | Dithering: `none`, `ordered` ou `floyd-steinberg` | `none` |
| `--out` | Caminho de saída (sem extensão) | nome da imagem |

## Disparar um novo build manualmente

Vá em **Actions** → **Build Windows EXE** → **Run workflow** → **Run workflow**.
Útil se quiser regenerar o executável sem fazer nenhuma alteração no código.

## Tecnologias

- Python 3.11
- [Pillow](https://python-pillow.org/) — manipulação de imagens
- [NumPy](https://numpy.org/) — dithering ordenado
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — interface gráfica
- [PyInstaller](https://pyinstaller.org/) — geração dos `.exe`
- GitHub Actions — build automático na nuvem
