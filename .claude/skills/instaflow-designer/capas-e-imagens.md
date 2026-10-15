# Capas e imagens

Este arquivo vence qualquer outro desta skill quando o assunto é imagem ou capa.

## Regra 1 — Todo slide tem imagem e texto

Não existe slide só de texto. Vale para capa, miolo e CTA, e é mais dura na capa: **capa sem imagem é reprovada.**

No HTML, a imagem de cada slide fica num bloco com a classe `visual`:

```html
<div class="visual"><img src="imagens/s03.png" alt="..."></div>
<div class="visual"><svg viewBox="0 0 600 400">...</svg></div>
```

O guardião mede: o bloco precisa ter conteúdo de verdade e ocupar pelo menos **12% do slide** (**20% na capa**). O avatar do topo não conta. Ícone decorativo pequeno também não.

## Regra 2 — A imagem tem a ver com o texto

A imagem mostra **o assunto daquele slide**, não um enfeite. Antes de escolher, responda em uma frase: "o que esta imagem mostra, e por que é disso que o slide fala?". Essa frase vai no roteiro, em `imagem.descricao`. Se a resposta for genérica ("um gráfico", "uma pessoa feliz", "formas abstratas"), a imagem está errada.

Use o post de origem como pista: `fonte.json` traz `imagens_locais` (a capa do reel ou os slides do carrossel modelado). Abra com a ferramenta Read para ver **que tipo de criativo** fez aquele post render. Modele a ideia visual; nunca copie a imagem nem a use no slide.

## Regra 3 — De onde vem a imagem, nesta ordem

Releia `contexto/cadastro.md` antes de decidir.

| Ordem | Origem | Quando usar | `origem_imagem` |
|---|---|---|---|
| 1 | **Foto do cadastro** (linhas `foto:`) ou o logo | O slide fala do dono, da equipe, do espaço, do produto ou do atendimento, e existe foto registrada que mostra isso. Leia a descrição de cada foto e escolha a que bate | `foto` |
| 2 | **Print real** | O slide fala de uma tela, ferramenta, resultado de busca, notícia ou página que existe. Capture só o trecho que importa, sem a moldura do navegador | `print` |
| 3 | **Ilustração desenhada** (SVG ou HTML) | Sempre disponível. Tela simplificada, objeto, símbolo, comparação, gráfico com dado real, card de post ou de avaliação. É desenho de uma coisa reconhecível, não forma abstrata | `ilustracao` |
| 4 | **IA** | Só com `OPENROUTER_API_KEY` no `.env`, no máximo 2 por peça, e quando as três anteriores não resolvem | `ia` |

Nunca: imagem do concorrente, banco de imagem genérico, foto de pessoa que não está no cadastro, logo de terceiro como assinatura. Logo de terceiro (Google, ChatGPT e outros em `assets/logos/`) só quando o slide fala daquele produto.

Print com dado de cliente ou de terceiro: esconda nome e foto.

## Regra 4 — Quem aparece no topo

`perfil_tipo` do cadastro decide o bloco de identidade de todo slide:

| `perfil_tipo` | Topo | Fotos |
|---|---|---|
| `pessoa` | foto de rosto + nome da pessoa + @ | a pessoa pode aparecer em capa `foto` ou `recorte` e no CTA |
| `negocio` | logo + nome da marca + @ | fotos do espaço, da equipe e do produto; não invente um rosto para a marca |
| `misto` | foto de rosto + nome da pessoa + @ | como em `pessoa`, e o logo entra discreto no último slide: `<img class="logo-marca" src="imagens/logo.png" alt="logo">` |

A imagem do topo é sempre o arquivo do campo `avatar` (o cadastro já gravou a foto ou o logo no formato certo).

## Regra 5 — Restrições legais

Com `regulado: sim` no cadastro, leia a seção "Restrições legais" antes de escolher qualquer imagem. Ela vale para imagem tanto quanto para texto e vence as outras regras deste arquivo. O que as restrições vetarem (antes e depois, foto de paciente ou cliente identificável, imagem sensacionalista, número de resultado em destaque) não entra, mesmo que o post de origem use. O número de registro aparece uma vez, pequeno e legível, no último slide: `<p class="registro">...</p>`.

## Regra 6 — O tipo de slide não é escolha livre

A regra principal é **modelar o criativo da referência e chegar o mais perto possível dela**. O tipo de capa e o layout de cada slide saem da referência, nesta ordem:

### A referência é carrossel ou imagem → espelhe

A pesquisa já classificou o criativo dela: `criativo_tipo` (o tipo da capa) e `criativo_slides` (o layout de cada slide, um a um).

- **Capa:** a opção **A** é do mesmo tipo da capa da referência (`criativo_tipo`).
- **Miolo:** cada slide seu usa o layout do slide correspondente em `criativo_slides`. Se a referência alterna imagem em cima e imagem ao lado, o seu alterna igual.
- A referência usa foto de pessoa e o cadastro não tem foto: use o tipo mais próximo que não precise de foto (`recorte` → `objeto`; `foto` → `card` ou `print`) e diga isso em `criterio_capa.regra`.
- **A referência é só texto:** o seu slide não é. Mantenha a diagramação do texto e acrescente a imagem do assunto. Nenhum slide sai só com texto, mesmo quando o original é assim.

### A referência é vídeo → use a tabela

Vídeo não tem layout para copiar. O tipo sai do **que o hook faz**, que a pesquisa gravou em `gancho_categoria`:

| `gancho_categoria` | O hook... | Opção A | Alternativas |
|---|---|---|---|
| `tela` | mostra ou ensina algo numa tela, ferramenta ou passo a passo | `print` (se a tela existe e dá para capturar), senão `objeto` | `card`, `dividida` |
| `numero` | se apoia num número, prazo, preço ou estatística | `numero` | `objeto`, `card` |
| `comparacao` | opõe dois lados: antes e depois, certo e errado, você e o concorrente | `dividida` | `card`, `objeto` |
| `citacao` | parte de uma notícia, post, avaliação ou fala de alguém | `card` | `print`, `simbolo` |
| `pessoa` | é opinião, alerta ou história dita por alguém olhando para a câmera | `foto` ou `recorte` (com foto no cadastro), senão `simbolo` | `card`, `objeto` |
| `conceito` | gira em torno de uma marca, produto ou ideia única | `simbolo` | `objeto`, `card` |

- A opção **A** é a da coluna "Opção A". As opções **B** e **C** saem das alternativas da mesma linha.
- No miolo de uma peça que veio de vídeo, o layout de cada slide segue o conteúdo dele: passo com tela → padrão ou `imagem-topo`; dado → `destaque`; comparação → `lado`; momento de impacto com foto → `cheia`.

### Registre o critério

Em cada hook do `selecao.json`:

```json
"criterio_capa": {"origem": "carrossel", "tipo_referencia": "objeto", "regra": "a capa da referência é uma tela com um campo destacado"}
"criterio_capa": {"origem": "video", "gancho_categoria": "numero", "regra": "o hook se apoia em 7 de cada 10"}
```

O guardião confere: a opção A bate com a referência (carrossel) ou com a tabela (vídeo), e as opções B e C estão entre as alternativas.

### Não repetir

- Entre os 5 hooks, nenhum tipo de capa em mais de 3.
- A opção A não repete o tipo da capa dos **2 últimos carrosséis publicados**, a não ser que a referência seja carrossel e exija aquele tipo. Havendo repetição, a opção A passa a ser a primeira alternativa da linha.
- No miolo: com 3 ou mais slides de conteúdo, use pelo menos 2 layouts diferentes e nunca o mesmo 3 vezes seguidas.

## Os layouts de miolo

Cinco layouts, todos com imagem. A classe vai na `<section>`: `class="slide conteudo escuro lado"`. No roteiro, cada slide de conteúdo traz `layout:`.

| `layout` | Como é | Bom para |
|---|---|---|
| `padrao` (sem classe) | Texto em cima, imagem embaixo | Passo com explicação |
| `imagem-topo` | Imagem em cima, texto embaixo | Quando a imagem é a prova |
| `lado` | Texto à esquerda, imagem à direita | Comparação, lista curta |
| `destaque` | Uma frase ou número gigante (`<div class="frase">`) + imagem de apoio | Dado, virada, frase de impacto |
| `cheia` | A imagem cobre o slide, texto ancorado embaixo | Foto forte do cadastro |

## Os tipos de capa

Oito tipos, todos com imagem. A classe do tipo vai na `<section>`: `class="slide capa escura objeto"`.

| Tipo | Como é | Pede |
|---|---|---|
| `simbolo` | Um símbolo grande no centro, título e apoio embaixo, tudo centralizado | Ilustração ou logo do assunto |
| `foto` | A foto cobre o slide inteiro, véu escuro, texto ancorado embaixo | Foto do cadastro |
| `recorte` | Pessoa recortada de um lado, título do outro | Foto do cadastro com fundo removido (`scripts/recortar_fundo.py`) |
| `objeto` | Título em cima, um objeto ou tela simplificada embaixo | Ilustração |
| `numero` | Um número gigante como protagonista, com apoio visual e a fonte do dado | Dado com fonte + ilustração |
| `dividida` | Slide partido em dois: antes e depois, você e o concorrente | Duas ilustrações ou duas fotos |
| `card` | Post, notícia ou avaliação desenhada como card | Ilustração em HTML (`.cartao`) |
| `print` | Tela real recortada, com o título em cima | Print real |

`foto` e `recorte` só existem se o cadastro tiver foto que sirva. Sem foto, não proponha esses tipos.

O layout base de cada tipo está em `css/base.css`. Ajuste tamanho e posição em `vN/peca.css` quando precisar; não edite a base.

A capa alterna tom: se o último carrossel publicado abriu escuro, este abre claro (classes `escura` e `clara`).

## Modo capas — 3 opções por hook

Chamado pelo orquestrador antes de qualquer carrossel ser produzido. Para cada hook da seleção, entregue **3 capas de tipos diferentes**, com o mesmo texto de hook e ideias visuais realmente distintas (não três variações de cor).

Como escolher os 3 tipos de um hook: siga a **Regra 6**. A opção A vem da referência (carrossel) ou da tabela (vídeo); B e C são as alternativas. Não escolha por gosto nem por hábito.
4. Entre os 5 hooks da seleção, varie: nenhum tipo aparece em mais de 3 hooks, e a mesma foto do cadastro entra em no máximo 2 capas. Não comece toda seleção pela foto do dono: ela é uma opção entre outras.
5. Capa com foto do cadastro registra em `foto_arquivo` qual foto foi usada.

Cada opção é uma pasta `conteudo/_selecao/<data>/h<n>/<letra>/` com:

- `carrossel.html` com **uma** `<section class="slide capa <tom> <tipo>">`, o bloco de identidade e o bloco `visual`
- `base.css`, `marca.css` (a identidade do cadastro; modelo em [slides.md](slides.md)), `imagens/avatar.jpg`
- `exportar.js` → `slide-01.png` (2160x2700)

E uma entrada em `selecao.json`:

```json
{"letra": "A", "tipo": "objeto", "origem_imagem": "ilustracao",
 "imagem": "Tela simplificada do perfil da empresa no mapa com o campo de categoria destacado: é o campo de que o hook fala",
 "arquivo": "h1/A/slide-01.png"}
```

## Modo carrossel — depois da escolha

`escolha.json` na pasta da peça diz qual opção venceu. A capa do carrossel **é a opção escolhida**: copie o HTML, o CSS e as imagens daquela pasta para o slide 1, sem redesenhar. O tipo escolhido fica na classe da primeira `<section>`.

Os demais slides seguem as regras 1, 2 e 3, cada um com o seu `imagem:` no roteiro.
