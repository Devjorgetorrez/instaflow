# Identidade visual — como definir, com ou sem logo

A identidade são cinco coisas: cor de fundo escura, cor de fundo clara, cor de destaque, letra de título e letra de texto. Você nunca pergunta por elas uma a uma. Você **deduz, mostra uma amostra e a pessoa aprova**.

## A escada: use o primeiro degrau que existir

| Degrau | De onde sai | Como |
|---|---|---|
| 1 | **Logo** enviado | `python scripts/salvar_imagem.py cores "<arquivo do logo>"` lista as cores dominantes |
| 2 | **Post ou site** que a pessoa indicou | Imagem: o mesmo comando. Site: abra e leia as cores e as letras da página |
| 3 | **O próprio Instagram dela** | Abra `instagram.com/<@>`: a foto de perfil e os últimos posts. Se der para salvar uma imagem, rode o comando de cores nela. Não conseguiu abrir: siga para o degrau 4, sem insistir |
| 4 | **Tabela por ramo**, abaixo | Ache o ramo pelo que ela respondeu sobre o negócio |

Do degrau 1 ao 3, monte assim:
- **Fundo escuro:** a cor mais escura da marca. Se a marca não tem cor escura, use um quase-preto puxado para o tom dela.
- **Fundo claro:** branco, ou o tom claro da marca.
- **Destaque:** a cor mais viva da marca, a que chama o olho. Tem de contrastar com os dois fundos.
- **Letras:** as do Google Fonts mais parecidas com as do material. Na dúvida, use o par do ramo, da tabela.

## Sem logo: a definição precisa ser mais firme, não mais solta

Quem não tem logo não tem referência para conferir a proposta de cabeça. Por isso:

1. **Sempre gere a amostra** (abaixo) e mostre a imagem. Nunca descreva cores só em palavras para quem não tem logo.
2. **Degrau 4 (nada de material): mostre as duas opções do ramo, A e B, lado a lado, e pergunte qual combina mais.** É a única pergunta extra do cadastro, e só existe neste caso.
3. Depois da escolha, o cadastro guarda as cinco definições. A partir daí todo carrossel sai igual: é essa repetição que cria a identidade de quem não tem logo.

**Perfil do negócio sem logo:** o topo dos slides precisa de uma imagem. Gere uma marca de texto com as iniciais, nas cores definidas:

```bash
python scripts/salvar_imagem.py marca-texto "<nome da marca>" "<cor de destaque>" "<cor de fundo escuro>"
```

O fundo da marca é a cor de destaque e a letra é a cor escura: assim ela aparece tanto no slide escuro quanto no claro.

Grave o caminho devolvido em `avatar` e `tem_logo` = `nao`. Diga à pessoa que é uma marca provisória e que basta mandar o logo quando tiver.

## A amostra

```bash
node scripts/amostra_identidade.js A "<fundo escuro>" "<fundo claro>" "<destaque>" "<letra de título>" "<letra de texto>"
node scripts/amostra_identidade.js B "<...>"      # só quando houver duas opções
```

Cada chamada grava `contexto/amostras/opcao-<letra>.png`: um slide escuro e um claro, com o nome, o @ e a imagem do topo do rascunho. Mostre a imagem à pessoa (ferramenta de enviar arquivo, ou abrindo o arquivo). Se o Node.js não estiver instalado, descreva as cores por nome e diga que a amostra visual sai na primeira rodada.

## Tabela por ramo (degrau 4)

Cada ramo tem duas opções. A é a mais sóbria; B, a mais viva.

| Ramo | Opção | Fundo escuro | Fundo claro | Destaque | Título | Texto |
|---|---|---|---|---|---|---|
| Saúde (médico, dentista, fisio, clínica) | A | `#0F2A3D` | `#FFFFFF` | `#1FA39A` | Manrope | Inter |
| | B | `#12333A` | `#F4FAF8` | `#2BB673` | Poppins | Inter |
| Psicologia e bem-estar | A | `#2B2A3A` | `#FAF7F2` | `#C98B6B` | Fraunces | Inter |
| | B | `#1F3A36` | `#F6F3EC` | `#7FB7A4` | Manrope | Inter |
| Jurídico e contábil | A | `#0B2C56` | `#FFFFFF` | `#AE8E53` | Playfair Display | Inter |
| | B | `#1B1F2A` | `#F5F3EE` | `#B5463C` | Manrope | Inter |
| Finanças, seguros e imóveis | A | `#0D2B24` | `#FFFFFF` | `#C9A227` | Manrope | Inter |
| | B | `#101828` | `#F4F6FA` | `#2E6BE6` | Inter Tight | Inter |
| Beleza e estética | A | `#2A1F24` | `#FBF6F4` | `#C97B84` | Playfair Display | Inter |
| | B | `#1E1B2E` | `#FAF7FC` | `#B57EDC` | Poppins | Inter |
| Alimentação (restaurante, confeitaria) | A | `#2A1810` | `#FFF8EE` | `#E0672B` | Poppins | Inter |
| | B | `#16281C` | `#F7F4EA` | `#D9A441` | Fraunces | Inter |
| Construção, reforma e serviços de casa | A | `#1C1F22` | `#FFFFFF` | `#F2A20C` | Inter Tight | Inter |
| | B | `#14273A` | `#F3F5F7` | `#E5532D` | Manrope | Inter |
| Tecnologia, marketing e serviços para empresa | A | `#0F1222` | `#FFFFFF` | `#5B6CFF` | Inter Tight | Inter |
| | B | `#111111` | `#F5F5F2` | `#F25C05` | Manrope | Inter |
| Educação, cursos e mentoria | A | `#16213A` | `#FFFFFF` | `#F2B705` | Poppins | Inter |
| | B | `#1D2B24` | `#F6F4EC` | `#E4572E` | Manrope | Inter |
| Esporte, academia e nutrição | A | `#101418` | `#FFFFFF` | `#B6E11E` | Inter Tight | Inter |
| | B | `#1A2238` | `#F4F6F8` | `#FF6B35` | Poppins | Inter |
| Pet, veterinária | A | `#17313B` | `#FFFDF7` | `#F2A541` | Poppins | Inter |
| | B | `#2A2433` | `#F8F5FA` | `#4BB4A6` | Manrope | Inter |
| Não se encaixa em nenhum | A | `#141414` | `#FFFFFF` | `#2E6BE6` | Inter Tight | Inter |
| | B | `#1E1A16` | `#F7F3EC` | `#D9622B` | Manrope | Inter |

Profissão com conselho: prefira a opção A. Sobriedade costuma ser exigência da norma de publicidade.

## O que a pessoa vê na revisão geral

> **Identidade visual** (tirada do seu logo | do seu Instagram | montada para o seu ramo)
> Fundo escuro: azul-marinho. Fundo claro: branco. Destaque: dourado.
> Título em letra firme e sem enfeite; texto em letra simples.
> [a amostra]

Os códigos das cores ficam no cadastro; na conversa, use o nome da cor.
