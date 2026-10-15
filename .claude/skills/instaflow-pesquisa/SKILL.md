---
name: instaflow-pesquisa
description: Coleta os posts dos concorrentes listados em contexto/cadastro.md, ranqueia cada post contra a mediana do próprio perfil, baixa as mídias, transcreve reels e carrosséis, analisa hook e rehook e alimenta a fila de modelagem. Não pergunta nada, lê tudo do cadastro. Chamada pelo instaflow; também roda sozinha com /instaflow-pesquisa.
---

# Pesquisa de posts dos concorrentes

Acha os posts que saíram da curva em cada concorrente e deixa cada um pronto para virar carrossel.

**Não faça perguntas.** Concorrentes, modo de coleta, período e métrica estão em `contexto/cadastro.md`. Leia com `python scripts/cadastro.py`.

Caminhos: `SKILL_DIR` = pasta desta skill. `TRABALHO` = `pesquisa-instagram/` na raiz do projeto. Rode os comandos a partir da raiz do projeto.

---

## Etapa 0 — Completar o que já está na fila

Antes de pensar em coletar, deixe prontos os posts que já estão em `TRABALHO/fila.json`. Post de fila sem `tema_central`, `termos_centrais`, `nomes_conferidos`, `criterio` ou, se for de outra língua, `transcricao_pt`, não é usado. Complete esses campos em cada um, direto no `fila.json`, seguindo as Etapas 6 e 7. Para os que estão sem `imagens_locais`, tente baixar a capa:

```bash
python SKILL_DIR/scripts/baixar_midias.py --ranking TRABALHO/fila.json --pasta TRABALHO/midias
```

Link de imagem vencido não é falha: o post segue sem a capa.

Post de fila sem `criterio` (entrou antes de o ranking guardar o motivo): recalcule sobre o `posts.json` da rodada em que ele foi coletado, sem cortes e sem excluir ninguém, e copie os números para a fila:

```bash
python SKILL_DIR/scripts/ranquear.py --entrada TRABALHO/rodadas/<rodada>/posts.json --metrica <metrica> \
  --top 200 --minimo-relativo 0 --minimo-comentarios 0 --saida TRABALHO/rodadas/<rodada>/ranking-completo.json
python SKILL_DIR/scripts/fila.py atualizar --ranking TRABALHO/rodadas/<rodada>/ranking-completo.json
```

Depois disso, post da fila que ficou abaixo de 2 vezes o normal do perfil ou com menos de 5 comentários sai: `fila.py descartar --id <id> --motivo "abaixo do corte"`.

## Etapa 1 — Precisa coletar?

```bash
python SKILL_DIR/scripts/fila.py situacao --a-cada-dias <coleta_a_cada_dias>
```

- `coletar_agora: false` e há pelo menos 1 post em `prontos` → **não colete.** Encerre aqui: fila curta não é motivo para coletar antes da hora.
- `coletou_hoje: true` → **não colete de novo hoje**, em hipótese nenhuma. Coleta paga não se repete no mesmo dia.
- `coletar_agora: true`, ou a fila está sem nenhum post pronto e a última coleta foi em outro dia → crie `TRABALHO/rodadas/AAAA-MM-DD_HHMM/` (abaixo, `RODADA`) e siga.

## Etapa 2 — Coleta

O resultado dos dois modos é o mesmo arquivo `RODADA/posts.json` (schema em `referencias/schema.md`).

### `coleta_modo: apify`
```bash
python SKILL_DIR/scripts/coletar_apify.py \
  --perfis <concorrentes> --dias <periodo_dias> --limite-por-perfil 30 \
  --saida RODADA/posts.json
```
- `--limite-por-perfil`: 30 para até 15 dias; 50 para 30 dias.
- O token vem de `APIFY_TOKEN` no `.env`. Nunca mostre nem grave o token em outro lugar.
- Saída `2` (token inválido), `3` (sem crédito) ou `4` (outro erro): **não troque de modo por conta própria.** A etapa falhou; devolva o erro a quem chamou.

### `coleta_modo: navegador`
Siga `referencias/modo-navegador.md` à risca. Se o Instagram não estiver logado, ou aparecer CAPTCHA ou pedido de verificação, **pare**: a etapa falhou e o motivo é esse. Nunca digite senha, nunca tente contornar verificação.

## Etapa 3 — Ranking

```bash
python SKILL_DIR/scripts/ranquear.py \
  --entrada RODADA/posts.json --metrica <metrica> --dias <periodo_dias> \
  --top <N> --max-por-perfil <M> \
  --minimo-relativo 2.0 --minimo-comentarios 5 \
  --excluir TRABALHO/modelados.json TRABALHO/fila.json \
  --saida RODADA/ranking.json
```

- `N` = posts por dia × `coleta_a_cada_dias`, mais 30% de folga (arredonde para cima).
- `M` = `ceil(N / nº de concorrentes) + 1`.
- Só entra post que rendeu pelo menos **2 vezes** o normal do próprio perfil e teve ao menos 5 comentários. Post comum não serve de referência. Não baixe esses cortes para encher a fila: fila curta é melhor que referência fraca.
- O ranking grava, em cada post, as duas notas separadas e a frase `criterio`, que diz se ele entrou por visualização, por comentários ou pelos dois. O relatório de capas mostra isso.
- O ranking compara cada post com a **mediana do próprio perfil**. Um post grande num perfil gigante não ganha de um post que triplicou a média de um perfil pequeno.
- `--excluir` é a memória: post já modelado ou já na fila não volta.

Repasse os avisos do script no relatório.

## Etapa 4 — Mídias, na hora

Os links de imagem expiram em poucas horas. Baixe antes de qualquer outra coisa. Em reel, o que desce é a capa do vídeo: ela mostra ao designer que criativo fez o post render.

```bash
python SKILL_DIR/scripts/baixar_midias.py --ranking RODADA/ranking.json --pasta RODADA/midias
```

## Etapa 5 — Comentários (métrica `comentarios` ou `ambos`)

- **Apify:** `python SKILL_DIR/scripts/coletar_comentarios_apify.py --ranking RODADA/ranking.json --por-post 15`
- **Navegador:** abra cada post do ranking e leia os ~15 primeiros comentários.

## Etapa 6 — Transcrição

**Reels:**
```bash
python SKILL_DIR/scripts/transcrever.py --ranking RODADA/ranking.json --pasta RODADA/videos
# modo navegador: adicione --cookies-navegador chrome
```

Todo post precisa do campo `idioma` (`pt`, `en`, `es`...). Em reel, a transcrição detecta e grava. Em carrossel e imagem, grave você, pelo texto das artes e da legenda. O idioma é detectado sozinho e gravado em `idioma` nos reels. Post em outra língua entra normalmente: `gancho` e `rehook` ficam literais, na língua original, e a análise é escrita em português.

**Carrosséis e imagens:** leia cada arquivo de `imagens_locais` com a ferramenta Read e grave em `transcricao` o texto das artes, slide a slide, no formato `Slide 1: ... / Slide 2: ...`. Sem imagem local e sem texto legível, o post fica sem transcrição e não entra em uso.

## Etapa 7 — Análise

**Antes da análise, em cada post:**
- **Nomes próprios.** Transcrição automática erra nome de ferramenta, marca e pessoa ("Claw" no lugar de "Claude"). Confira cada nome contra a legenda, a tela do vídeo e uma busca rápida. Corrija na `transcricao` e registre em `analise.nomes_conferidos` uma lista de `{"ouvido": "...", "correto": "..."}` (lista vazia se não havia nome).
- **Tradução.** Post em outra língua (`idioma` diferente de `pt`): grave em `transcricao_pt` a tradução fiel para o idioma do cadastro. `gancho` e `rehook` continuam literais, na língua original.

Para **cada** post do ranking, preencha `analise`:

- `tema_central` — em uma frase, do que o post trata
- `termos_centrais` — de 8 a 15 termos **em português**: o assunto, os conceitos, as ferramentas e as expressões fortes do post. É por eles que o guardião confere se o carrossel manteve o tema

- `gancho` — o hook: a primeira frase falada do reel ou o texto do slide 1, **literal**
- `rehook` — o que segura logo depois: a segunda frase do reel ou o slide 2, **literal**
- `mecanismo_do_gancho` — por que ele para o dedo (número, ameaça, promessa, contraste, pergunta)
- `criativo` — o que a capa do post mostra (abra `imagens_locais[0]` com a ferramenta Read): rosto, tela, objeto, número, texto sobre foto
- `gancho_categoria` — **obrigatório em todo post.** O que o hook faz, em uma palavra: `tela` (mostra ou ensina algo numa tela ou ferramenta), `numero` (se apoia num número, prazo ou preço), `comparacao` (opõe dois lados), `citacao` (parte de notícia, post, avaliação ou fala de alguém), `pessoa` (opinião, alerta ou história dita por alguém) ou `conceito` (gira em torno de uma marca, produto ou ideia)
- `criativo_tipo` — **só em carrossel e imagem.** O tipo da capa do post, classificado como um destes: `simbolo`, `foto`, `recorte`, `objeto`, `numero`, `dividida`, `card`, `print`, ou `texto` quando a capa é só texto
- `criativo_slides` — **só em carrossel.** O layout de cada slide depois da capa, na ordem, um por slide: `padrao` (texto em cima, imagem embaixo), `imagem-topo`, `lado`, `destaque` (frase ou número gigante), `cheia` (imagem cobre o slide) ou `texto` (só texto). Abra cada arquivo de `imagens_locais` para classificar
- `estrutura` — a sequência do conteúdo (ex.: gancho → problema → 3 passos → CTA)
- `pontos_principais` — 3 a 5 ideias centrais
- `cta` — a chamada usada
- `por_que_funcionou` — ligado à métrica
- `comentarios_insight` — o que gerou a conversa
- `dados_a_verificar` — todo número, caso ou promessa que o post afirma. O redator não herda nenhum deles

Grave tudo no próprio `RODADA/ranking.json`.

## Etapa 8 — Fila

```bash
python SKILL_DIR/scripts/fila.py adicionar --ranking RODADA/ranking.json
```

Termine com um relatório de três linhas: quantos posts coletados, quantos entraram na fila, e os avisos.

---

## Regras

- Só dados públicos. Nunca perfil privado, nunca DM.
- Nunca curtir, comentar, seguir ou enviar mensagem.
- O pacote serve para **modelar**, nunca para copiar palavra por palavra.
