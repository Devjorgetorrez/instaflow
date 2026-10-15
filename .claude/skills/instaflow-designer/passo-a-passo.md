# Passo a passo

Rode os comandos a partir da raiz do projeto. `SKILL` = `.claude/skills/instaflow-designer`.

## Modo carrossel

`PECA` = `conteudo/<slug>` (o slug do roteiro já começa pela data; não repita a data).

### 1. Ler

- `python scripts/cadastro.py` (identidade, `perfil_tipo`, fotos, restrições legais).
- `PECA/roteiro.md`, `PECA/escolha.json` e `PECA/fonte.json`.
- Confira o roteiro antes de desenhar: a primeira parte é `capa`, a última é `cta`, todo slide tem `imagem:` com `tipo` e `descricao`, todo slide de conteúdo tem `layout:`. Faltou algo: a peça volta para o redator; você não completa.

### 2. Preparar a pasta

Crie `PECA/v1/` (ou a próxima versão livre) com `imagens/`. Copie:

- `SKILL/css/base.css` → `vN/base.css`
- `SKILL/modelos/exportar.js` → `vN/exportar.js`
- o arquivo do campo `avatar` do cadastro → `vN/imagens/avatar.jpg`

Grave `vN/marca.css` com as três cores e as duas letras do cadastro (modelo em [slides.md](slides.md)).

### 3. A capa

Copie de `pasta_capa` (em `escolha.json`) a `<section>` da capa, o `peca.css` dela, se existir, e as imagens que ela usa. **Sem redesenho:** a capa do carrossel é a opção que foi escolhida.

### 4. As imagens dos outros slides

Para cada slide, o roteiro diz o `tipo` e a `descricao`. A ordem de preferência e os limites estão em [capas-e-imagens.md](capas-e-imagens.md).

- `foto`: copie a foto do cadastro para `vN/imagens/`. Para tirar o fundo de uma pessoa: `python scripts/recortar_fundo.py <entrada> <saida.png>`.
- `print`: capture só o trecho que importa, sem a moldura do navegador. PNG com menos de 10 KB é captura que falhou.
  ```bash
  npx playwright screenshot --viewport-size=1440,2000 "<url>" "vN/imagens/sNN.png"
  ```
  Print com dado de cliente ou de terceiro: esconda nome e foto.
- `ilustracao`: desenhe em SVG ou HTML, direto no slide. É o desenho de uma coisa reconhecível (uma tela, um objeto, uma comparação, um gráfico com dado real), nas cores do cadastro. Forma abstrata não serve.
- `ia`: só com `OPENROUTER_API_KEY` no `.env`, no máximo 2 por peça, e quando os três anteriores não resolvem.
  ```bash
  python scripts/generate.py --prompt "<em inglês: o objeto, o enquadramento, as cores do cadastro, sem texto e sem pessoas>" --output "vN/imagens/sNN.png" --aspect-ratio 4:5
  ```
  Confira o resultado: sem texto embutido, sem rosto, nas cores do cadastro. Duas tentativas ruins: troque por ilustração. Peça com imagem de IA é publicada com o aviso de conteúdo gerado por IA.

### 5. Montar o `carrossel.html`

Siga [slides.md](slides.md): uma `<section>` por slide, a identidade abrindo cada uma, o bloco `visual` em todas, o layout que o roteiro pediu, claro e escuro alternando. Perfil `misto`: o logo no último slide. `regulado: sim`: o registro no último slide.

### 6. Exportar e conferir

```bash
node PECA/vN/exportar.js
node scripts/checar_slides.js PECA/vN
```

O primeiro grava `slide-NN.png` (2160x2700). O segundo aponta texto para fora, imagem quebrada, slide sem imagem ou com imagem pequena demais. Corrija em `peca.css` ou no HTML e exporte de novo. Abra os PNGs e olhe: o que o guardião vai conferir, você confere antes.

## Modo capas

Para cada hook da seleção `conteudo/_selecao/<ID>/`, três pastas `h<n>/A`, `h<n>/B` e `h<n>/C`. Em cada uma:

1. `base.css`, `marca.css`, `exportar.js` e `imagens/avatar.jpg`, como no passo 2.
2. `carrossel.html` com **uma** `<section class="slide capa <tom> <tipo>">`: identidade, o hook como título e o bloco `visual`.
3. `node <pasta>/exportar.js` e `node scripts/checar_slides.js <pasta>`.

O tipo de cada opção sai da Regra 6 de [capas-e-imagens.md](capas-e-imagens.md), não de preferência.

## Uso avulso

Fora da rotina, com o usuário presente e sem o `instaflow`: mostre o resultado e pergunte se aprova antes de dar por terminado, e confirme antes de gerar imagem por IA. Dentro da rotina, nenhuma das duas perguntas é feita.
