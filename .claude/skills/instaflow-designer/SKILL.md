---
name: instaflow-designer
description: Desenha carrosséis de Instagram 1080x1350 a partir de um roteiro, com a identidade do cadastro (cores, letras, avatar ou logo, nome e @ em todo slide). Todo slide tem imagem e texto. Também cria as 3 opções de capa de cada hook, antes da escolha. Chamada pelo instaflow.
---

# instaflow-designer

Você transforma texto aprovado em slide. Não escreve nem reescreve texto: o que está no roteiro vai para o slide como está.

Antes de qualquer decisão, releia o cadastro: `python scripts/cadastro.py`.

## Os quatro arquivos

| Arquivo | Para quê |
|---|---|
| [capas-e-imagens.md](capas-e-imagens.md) | **Leia primeiro.** As regras de imagem, o critério que decide o tipo de cada capa e o layout de cada slide, e o modo de 3 capas por hook. Vence os outros arquivos em tudo o que for imagem |
| [slides.md](slides.md) | A estrutura de cada slide em HTML e as classes disponíveis |
| [passo-a-passo.md](passo-a-passo.md) | A ordem de trabalho, do roteiro ao arquivo exportado |
| [css/base.css](css/base.css) | O estilo base. Não edite para mudar a identidade de um perfil |

## Dois modos

- **Modo capas:** para cada hook da seleção, 3 capas de tipos diferentes. O tipo não é escolha livre: segue a referência.
- **Modo carrossel:** a peça inteira. A capa é a opção que o usuário escolheu, copiada sem redesenho.

## O que nunca muda

1. **Todo slide tem imagem e texto.** Nenhum sai só com texto, nem quando a referência é assim.
2. **A imagem mostra o assunto do slide.**
3. **Avatar ou logo, nome e @ no topo de todo slide**, legíveis.
4. **Cores e letras são as do cadastro**, aplicadas em `marca.css`.
5. **O texto do slide é o do roteiro**, palavra por palavra.
6. **Restrições legais do cadastro valem para a imagem** tanto quanto para o texto.
7. **Chamada pelo `instaflow`, você não confirma nada com o usuário.** Quem aprova a peça é o guardião.
8. **Nunca sobrescreva uma versão.** Peça refeita vai para `v2`, `v3`.

## Não é para

- Vídeo ou reel: esta skill só produz carrossel.
- Foto realista de pessoa que não está nas fotos do cadastro: não gere por IA.
