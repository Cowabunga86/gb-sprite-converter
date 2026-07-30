# gb-sprite-converter

Ferramenta de conversão de sprites para o formato Game Boy / Game Boy Color,
com interface gráfica moderna (CustomTkinter) e build automático do `.exe`
via GitHub Actions.

Inclui dois executáveis:
- **GB_Sprite_Converter.exe** — interface gráfica (arraste, ajuste, clique em Converter)
- **gb_sprite_converter_cli.exe** — linha de comando, útil para automatizar/batch

## Como gerar o .exe (sem instalar nada no seu PC)

### 1. Criar o repositório no GitHub
1. Acesse https://github.com/new
2. Dê um nome (ex: `gb-sprite-converter`)
3. Deixe como **Public** ou **Private**, tanto faz
4. **Não** marque "Add a README" (já temos um) — clique em **Create repository**

### 2. Subir estes arquivos
Na página do repositório recém-criado, clique em **"uploading an existing file"**
(link que aparece na tela inicial do repo vazio) e arraste estes 4 itens,
mantendo a estrutura de pastas:

```
gb_sprite_core.py
gb_sprite_converter.py
gb_sprite_gui.py
README.md
.github/workflows/build.yml
```

> Importante: a pasta `.github/workflows/build.yml` precisa manter esse
> caminho exato. Se o GitHub "achatar" a estrutura ao arrastar, crie a pasta
> manualmente pela opção "Create new file" e digite o caminho completo
> `.github/workflows/build.yml` no campo de nome do arquivo — o GitHub cria
> as pastas automaticamente.

Clique em **Commit changes** para confirmar o upload.

### 3. Acompanhar o build
1. Vá na aba **Actions** do repositório (menu superior)
2. Você verá o workflow "Build Windows EXE" rodando automaticamente
   (leva ~1-2 minutos)
3. Quando o ícone ficar verde (✓), clique no workflow concluído

### 4. Baixar o .exe
Na página do workflow concluído, role até **Artifacts** (embaixo) e clique em
`gb_sprite_converter-windows` para baixar um `.zip` contendo os dois executáveis.

### 5. Usar

**Interface gráfica** (recomendado): extraia o `.zip` e dê duplo-clique em
`GB_Sprite_Converter.exe`. Carregue uma imagem, ajuste tamanho/paleta/dithering,
veja o preview lado a lado e salve os arquivos finais.

**Linha de comando**: abra o `cmd` ou PowerShell na pasta extraída e rode:

```
gb_sprite_converter_cli.exe sua_imagem.png --size 56 56 --mode gb
```

## Rodar de novo no futuro
Qualquer novo push na branch `main` (ex: se você editar o script depois)
dispara um novo build automaticamente. Também dá pra forçar manualmente
pela aba Actions → "Build Windows EXE" → "Run workflow".
