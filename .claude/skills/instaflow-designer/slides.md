# Slides — estrutura e classes

Um carrossel é um arquivo `carrossel.html` com uma `<section class="slide ...">` por slide. São três partes: `capa` (o primeiro), `conteudo` (o miolo) e `cta` (o último).

## O arquivo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="base.css">
  <link rel="stylesheet" href="marca.css">   <!-- sempre depois de base.css -->
</head>
<body>
  <section class="slide capa escura objeto"> ... </section>
  <section class="slide conteudo lado"> ... </section>
  <section class="slide conteudo escuro destaque"> ... </section>
  <section class="slide cta"> ... </section>
</body>
</html>
```

## Identidade — abre toda `<section>`

```html
<div class="identidade">
  <img src="imagens/avatar.jpg" alt="NOME DO PERFIL">
  <div>
    <div class="nome">NOME DO PERFIL</div>
    <div class="arroba">@seuperfil</div>
  </div>
</div>
```

`NOME DO PERFIL` e `@seuperfil` são `perfil_nome` e `perfil_arroba` do cadastro. A imagem é o arquivo do campo `avatar` (foto de rosto ou logo, conforme o `perfil_tipo`).

## Capa

```html
<section class="slide capa escura objeto">
  [identidade]
  <h1 class="titulo">O hook escolhido</h1>
  <p class="apoio">Linha de apoio, se o roteiro tiver</p>
  <div class="visual"> ... </div>
</section>
```

- Tom: `escura` ou `clara`.
- Tipo: `simbolo`, `foto`, `recorte`, `objeto`, `numero`, `dividida`, `card` ou `print`. A posição do bloco `visual` muda com o tipo; veja os exemplos de cada um em [capas-e-imagens.md](capas-e-imagens.md).
- `numero` usa `<div class="numero">7</div>` antes do título.
- `dividida` usa dois `<div class="lado a">` e `<div class="lado b">` dentro do `visual`.
- `card` usa `<div class="cartao">` dentro do `visual`.

## Conteúdo

```html
<section class="slide conteudo lado">
  [identidade]
  <span class="rotulo">Passo 2</span>
  <div class="traco"></div>
  <h2 class="titulo">Título do slide</h2>
  <div class="texto">
    <p>Uma sentença por parágrafo.</p>
    <p>A seguinte em outro.</p>
  </div>
  <div class="visual"> ... </div>
</section>
```

- Fundo: sem classe é claro; `escuro` é escuro. Alterne ao longo do carrossel; se a capa é clara, o slide 2 é escuro.
- Layout: sem classe é o `padrao`; os outros são `imagem-topo`, `lado`, `destaque` e `cheia`. O roteiro diz qual, em `layout:`.
- `destaque` usa `<div class="frase">7 em cada 10</div>` antes do título.
- `rotulo` e `traco` são opcionais; os demais vêm do roteiro.
- Slide com menos de 35 palavras e layout `padrao`: acrescente `compacto`, que centraliza o conjunto na altura.

## CTA

```html
<section class="slide cta">
  [identidade]
  <h2 class="titulo">A pergunta ou promessa final</h2>
  <p class="chamada">O que a pessoa recebe</p>
  <p class="isca">COMENTA PALAVRA</p>
  <div class="visual"> ... </div>
  <p class="registro">Nome · registro · especialidade</p>      <!-- só com regulado: sim -->
  <img class="logo-marca" src="imagens/logo.png" alt="logo">   <!-- só com perfil_tipo: misto -->
</section>
```

Fundo: sem classe é a cor de destaque; `escuro` é o fundo escuro, com a isca na cor de destaque.

## Texto

- O texto é o do roteiro. Você só distribui.
- Cada sentença do campo `texto` vira um `<p>`.
- Sem itálico. Ênfase é `<em>` (sai na cor de destaque) ou `<strong>`.
- Sem travessão longo.
- Menor letra de texto: 36px. A exceção é a linha de fonte do dado (`<p class="fonte-do-dado">`) e o registro profissional.

## marca.css — a identidade do cadastro

```css
@import url("https://fonts.googleapis.com/css2?family=<fonte_titulo>:wght@700;800;900&family=<fonte_texto>:wght@400;600;700&display=swap");
:root {
  --cor-escura:   <cor_fundo_escuro>;
  --cor-clara:    <cor_fundo_claro>;
  --cor-destaque: <cor_destaque>;
  --fonte-titulo: '<fonte_titulo>', system-ui, sans-serif;
  --fonte-texto:  '<fonte_texto>', system-ui, sans-serif;
}
```

Ajuste fino de uma peça (um tamanho, uma posição) vai em `peca.css`, linkado depois de `marca.css`. `base.css` não é editado.
