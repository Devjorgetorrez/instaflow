# Coleta pelo navegador

Quando o cadastro diz `coleta_modo: navegador`, você lê os perfis dos concorrentes pelo navegador do Claude, com o Instagram **já logado pelo dono da conta**. Não há custo, mas depende de a sessão estar aberta e de o computador estar ligado.

## Antes de começar

1. Abra `https://www.instagram.com/`. Se não estiver logado, **pare**: a coleta falhou por esse motivo, e o relatório diz para a pessoa deixar o Instagram logado no navegador do Claude. Não peça login no meio da rodada. **Você nunca digita senha.**
2. Apareceu verificação de segurança, CAPTCHA, "confirme que é você" ou aviso de atividade incomum: **pare tudo**, guarde o que já coletou e diga isso no relatório. Você não tenta contornar.

## Ritmo e limites

- No máximo **10 perfis** e **40 posts abertos** por rodada.
- Espere de **3 a 8 segundos**, variando, entre uma página e outra e entre rolagens.
- Só leitura: não curta, não comente, não siga, não mande mensagem.
- Só perfil público.

## Em cada concorrente

**1. Os reels.** Abra `https://www.instagram.com/PERFIL/reels/`. Cada miniatura mostra o número de visualizações. Role até ter por volta de 24 reels, ou até acabar. Anote o link e as visualizações de cada um, do jeito que aparecem ("15,3 mil", "1,2 mi"): o ranking converte.

**2. Os posts do feed** (só com métrica `comentarios` ou `ambos`). Abra `https://www.instagram.com/PERFIL/` e anote os links dos 12 posts mais recentes que não são reel.

**3. Abra só os candidatos.** Abrir tudo é lento e chama atenção.
- Métrica `views`: os 8 reels com mais visualizações do perfil.
- Métrica `comentarios` ou `ambos`: esses 8, mais os 4 posts de feed mais recentes.

Em cada post aberto, anote:
- o `id` (o código depois de `/p/` ou `/reel/` no link) e o link;
- a data (o atributo `datetime` da data do post);
- o tipo: reel, carrossel ou imagem;
- curtidas e número de comentários;
- a legenda inteira;
- em `imagens`, o endereço da imagem de capa e dos slides visíveis;
- com métrica `comentarios` ou `ambos`, os 15 primeiros comentários (texto, autor, curtidas).

Post mais antigo que o `periodo_dias` do cadastro fica de fora.

## O que gravar

`RODADA/posts.json`, uma lista no formato de [schema.md](schema.md), com `"fonte": "navegador"`. Número pode ficar como texto; o ranking normaliza. O que não estiver visível (curtidas ocultas, por exemplo) vai como `null`.

Para transcrever os reels depois, rode `transcrever.py` com `--cookies-navegador chrome` (ou o navegador em uso), para o download funcionar com a sessão logada.
