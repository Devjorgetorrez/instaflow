---
name: instaflow
description: Orquestrador de carrosséis de Instagram. "/instaflow novo" faz o cadastro do perfil por um roteiro fixo de perguntas. "/instaflow" roda a rodada - busca os melhores posts dos concorrentes, cria 3 opções de capa para os 5 melhores hooks e apresenta o relatório de escolha. "/instaflow escolher 1B 3A" produz os carrosséis escolhidos e publica ou entrega. Cada etapa passa por um guardião; na terceira falha, para e avisa. Triggers - "/instaflow", "/instaflow novo", "/instaflow escolher", "roda a rotina", "carrosséis de hoje".
---

# instaflow — orquestrador

O produto final é sempre **carrossel**. Reel de concorrente é só matéria-prima. Rode todos os comandos a partir da raiz do projeto.

## Qual modo é este

| Chamada | Modo |
|---|---|
| `/instaflow novo` | **Cadastro.** Vá para "Modo cadastro" |
| `/instaflow escolher <códigos>` ou o usuário respondeu com códigos como `1B 3A` | **Produção.** Vá para "Modo produção" |
| `/instaflow` sem nada | **Rodada.** Vá para "Modo rodada" |

## As regras que valem em todos os modos

1. **O cadastro é a fonte da verdade, e você relê sempre.** Toda etapa começa com `python scripts/cadastro.py`. Nunca use de memória o que leu numa etapa anterior, e nunca decida algo que o cadastro responde.
2. **Fora do cadastro, você não pergunta nada.** As perguntas existem só no `/instaflow novo`, e são as do roteiro fixo. Na rodada e na produção, o que você precisa está no cadastro ou na fonte.
3. **Nenhuma etapa avança sem o guardião aprovar.** Cada guardião tem duas partes: o script (`scripts/guardiao.py`), que confere regra, e o revisor independente, que confere critério. As duas precisam aprovar.
4. **Três tentativas, depois para.** Antes de cada tentativa rode `python scripts/estado.py tentar <etapa> [--peca SLUG]`:
   - saída `0` → execute a etapa
   - saída `4` → já concluída nesta rodada: **pule** (é assim que a rotina não faz duas vezes)
   - saída `3` → limite estourado: **pare o que depende dela** e vá para o Relatório

   **Esse limite está no código, não só aqui.** O `guardiao.py` se recusa a conferir sem uma tentativa aberta, aceita no máximo 5 conferências por tentativa e, depois da terceira tentativa, responde `LIMITE` e não confere mais. Resposta `SEM_TENTATIVA`, `TENTATIVA_ENCERRADA` ou `LIMITE` (saída 3) não é reprovação a consertar: é a ordem para abrir a próxima tentativa ou parar. Com `LIMITE`, vá ao Relatório.

   Depois do guardião: `estado.py ok ...` se aprovou; `estado.py falha ... --motivo "<o que o guardião apontou>"` se reprovou, e tente de novo corrigindo exatamente o que foi apontado.
5. **A ordem das etapas é fixa:** cadastro → pesquisa → capas → escolha → copy → design → publicação. Nenhum carrossel é escrito ou desenhado antes da escolha da capa. Os guardiões de copy e de design reprovam peça sem `escolha.json`.
6. **Todo slide tem imagem e texto**, e a imagem tem a ver com o assunto do slide. Capa sem imagem é reprovada.
7. **Restrições legais vencem tudo.** Se o cadastro tem `regulado: sim`, a seção "Restrições legais" vale acima do tom de voz, do hook do concorrente e de qualquer regra desta skill, no texto **e na imagem**. Toda chamada ao redator e ao designer leva essa seção inteira. O número de registro aparece uma vez, discreto, no último slide e na legenda; nunca como argumento de venda.
8. **Quem aparece.** `perfil_tipo` do cadastro decide o topo dos slides e o uso das fotos: `pessoa` e `misto` mostram a foto e o nome da pessoa; `negocio` mostra o logo e o nome da marca. Em `misto`, o logo entra discreto no último slide.
9. **Modelar, não reinventar.** O carrossel mantém o **tema central** do post de referência e usa **palavras parecidas** com as dele. Não é copiar, e também não é mudar de assunto. Os guardiões medem as duas pontas: no máximo 20% de trechos repetidos palavra por palavra, e no mínimo 60% dos termos centrais da referência presentes. Se o tema da referência não serve ao público do cadastro, o post é descartado; ele não é torcido até virar outro assunto.
10. **Idioma.** Tudo sai no `idioma` do cadastro (português, se ninguém pediu diferente), mesmo quando a referência está em outra língua.
11. **A URL do post de referência acompanha a peça até o fim:** está no relatório de capas, no `publicacao.json`, no `referencia.txt` da entrega e no relatório final.

Uma peça bloqueada não derruba as outras.

---

# Modo cadastro — `/instaflow novo`

Siga [cadastro-perguntas.md](cadastro-perguntas.md) do começo ao fim: a pergunta de abertura sozinha (o perfil é da pessoa, do negócio ou dos dois) e mais seis mensagens na redação daquele tipo, nunca mais de 3 perguntas por mensagem, a **revisão geral** e a instalação. As respostas vão para um rascunho; cores e letras você define por [identidade-visual.md](identidade-visual.md) e mostra numa amostra; o tom de voz você deduz e mostra na revisão; havendo conselho ou regra de publicidade, você pesquisa a norma oficial. **O cadastro só é gravado depois que a pessoa aprova a revisão geral.** Depois de gravar, você confere e instala o que o agente precisa e, se ela quiser, cria a rotina diária. Você anota cada resposta no **rascunho** na hora e grava os arquivos que a pessoa mandar (avatar, logo, fotos), também em rascunho. Ela não mexe em pasta, e o cadastro e as imagens em uso só mudam quando ela aprova a revisão.

```bash
python scripts/guardiao.py cadastro --rascunho     # antes da revisão geral
python scripts/cadastro.py confirmar               # só depois do "pode gravar"
python scripts/instalar.py checar                  # depois de gravar
```

O guardião só aprova com **tudo** respondido. Cada `FALHA` é uma pergunta a refazer; refaça só ela. Aqui não vale o limite de 3 tentativas: o cadastro termina quando a pessoa aprova a revisão ou interrompe.

**"Concluir a instalação"** (a pessoa voltou depois de criar uma conta, colar uma chave ou ligar um conector, e o cadastro já está gravado): não refaça pergunta nenhuma. Rode `python scripts/instalar.py checar` e siga a seção "Instalação" do roteiro a partir do que ainda falta, depois a rotina, se foi pedida e ainda não foi criada.

Não comece pesquisa nem rodada dentro do modo cadastro. Encerre dizendo que `/instaflow` roda a primeira rodada.

---

# Modo rodada — `/instaflow`

## Etapa 0 — Cadastro (sempre, no modo rodada e no modo produção)

```bash
python scripts/guardiao.py cadastro
```

Rode toda vez, mesmo que já tenha rodado hoje: esta etapa não usa o `estado.py`.

- `REPROVADO` → **não tente de novo e não faça as perguntas aqui.** Vá ao Relatório, liste cada `FALHA` e diga para rodar `/instaflow novo`.
- `APROVADO` → guarde `MODO_PUBLICACAO`, `AUTOMACAO` e os `AVISO` para o relatório.

Com o cadastro aprovado, confira a máquina: `python scripts/instalar.py checar`. Linha `FALTA` de biblioteca → rode `python scripts/instalar.py instalar` uma vez e siga. Linha `VOCE` não trava a rodada: leve ao relatório o que falta e o que deixa de funcionar (sem as chaves do R2 ou sem o conector, a entrega sai no modo manual). A única que trava é a falta do Node.js: sem ele não há slide; pare e avise.

## Existe seleção aberta?

```bash
python scripts/selecao.py situacao
```

- `em_montagem` → uma rodada anterior parou no meio das capas. **Continue nela**, com o mesmo `ID`, a partir da Etapa 2: não crie outra e não apresente essas capas antes de o guardião aprovar.
- `aguardando_escolha` e `escolha_capa: usuario`, com `dias_esperando` até 3 → **não gere outra.** Vá ao Relatório lembrando onde está o relatório de capas e como responder.
- `aguardando_escolha` há mais de 3 dias → os posts envelheceram: `python scripts/selecao.py descartar`, diga isso no relatório e siga para a Etapa 1.
- `aguardando_escolha` e `escolha_capa: automatica` → vá para "Escolha automática".
- `escolhido` → vá para "Modo produção".
- `produzido` com a `data` de hoje e `escolha_capa: automatica` → a rodada de hoje já foi feita. Vá ao Relatório dizendo isso; não produza um segundo lote no mesmo dia.
- `produzido`, `descartada` ou `sem_selecao` → siga para a Etapa 1.

Se o usuário pedir capas novas no lugar das que estão esperando ("refaz as capas", "não gostei de nenhuma"): `python scripts/selecao.py descartar` e siga para a Etapa 1.

## Etapa 1 — Pesquisa

```bash
python scripts/estado.py tentar pesquisa
```

Invoque a skill **`instaflow-pesquisa`**. Ela decide sozinha se precisa coletar ou se a fila já cobre.

**Guardião:**
```bash
python scripts/guardiao.py pesquisa --n 1
```
(`--n 1` é o mínimo para seguir. O ideal são 5 posts prontos; com menos, a seleção sai menor e o relatório avisa.)
Revisor independente, critérios:
Revise só os posts que podem entrar na seleção: os que `fila.py proximos --n 5 --max-por-perfil 2` devolve, mais 2 de reserva. Post que não vai ser usado não precisa de revisão.
- o `gancho` e o `rehook` de cada post pronto são trechos literais da transcrição, não resumo
- `dados_a_verificar` lista todo número, caso e promessa da transcrição
- quando o post tem `imagens_locais`, `criativo` descreve o que a capa dele mostra
- `gancho_categoria` descreve de verdade o que o hook faz; em carrossel, `criativo_tipo` e `criativo_slides` batem com as imagens baixadas
- `tema_central` diz em uma frase do que o post trata, e os `termos_centrais` são os conceitos e as palavras fortes dele, em português
- todo nome de ferramenta, marca ou pessoa da transcrição foi conferido em `nomes_conferidos` (transcrição automática erra nome próprio)
- post em outra língua tem `transcricao_pt` fiel ao original

Post que ainda bloqueia na terceira tentativa é descartado, e a etapa passa com os demais. Com zero posts prontos, vá ao Relatório. Não invente tema.

## Etapa 2 — Capas

Dê um nome à seleção (`ID`): a data de hoje, `AAAA-MM-DD`. Se já existe uma seleção **encerrada** com esse nome, use `AAAA-MM-DD-2`, depois `-3`: uma seleção nunca sobrescreve outra. Se a seleção existente está `em_montagem`, o `ID` é o dela.

```bash
python scripts/estado.py tentar capas --peca <ID>
python .claude/skills/instaflow-pesquisa/scripts/fila.py proximos --n 5 --max-por-perfil 2
```

São os **5 melhores posts** da fila (menos, se a fila tiver menos), com no máximo 2 do mesmo concorrente enquanto houver post pronto de outro. Use exatamente os que o comando devolver. Para cada um:

1. **Adapte o hook.** Reproduza o mecanismo e o ritmo do `gancho` da fonte, trocando só o que é do nicho do concorrente pelo nicho, público e produto do cadastro. Com `regulado: sim`, o hook respeita as restrições: se o gancho da fonte depende de algo vetado (promessa de resultado, antes e depois, comparação), reconstrua o mecanismo sem o elemento vetado; se não sobrar hook, descarte o post (`fila.py descartar`) e pegue o próximo da fila. O hook sai no `idioma` do cadastro, em fala natural, não tradução literal. Faça o mesmo com o `rehook`.
   **O assunto não muda.** O hook e o rehook falam do mesmo tema da referência (`tema_central`) e trazem pelo menos 2 dos `termos_centrais` dela. Se esse tema não interessa ao `publico` do cadastro, não force: descarte o post (`fila.py descartar --id ... --motivo "tema fora do público"`) e peça os próximos de novo.
2. **Crie 3 capas** para esse hook: invoque a skill **`instaflow-designer`** no **modo capas**. **O tipo de cada capa não é escolha livre:** segue a Regra 6 de `capas-e-imagens.md`. Referência em carrossel ou imagem → a opção A espelha a capa dela. Referência em vídeo → a opção A sai da tabela, pela `gancho_categoria`. B e C são as alternativas da mesma linha. Todas com imagem ligada ao assunto; nenhuma só de texto, mesmo que a referência seja.

Grave `conteudo/_selecao/<ID>/selecao.json` (o campo `data` leva o `ID`, igual ao nome da pasta):

```json
{
  "data": "<ID>",
  "status": "em_montagem",
  "hooks": [
    {
      "n": 1,
      "fonte_id": "<id do post>", "perfil": "<perfil de origem>", "url": "<url>", "motivo": "<motivo do ranking>",
      "hook_original": "<gancho literal da fonte>",
      "hook": "<hook adaptado, o texto da capa>",
      "rehook": "<rehook adaptado>",
      "tema": "<em uma frase, do que o carrossel vai tratar: o mesmo assunto da referência>",
      "mantido": "<o que ficou igual à referência: tema, promessa, estrutura, palavras>",
      "mudou": "<o que foi adaptado ao cadastro, e por quê>",
      "criterio_capa": {"origem": "carrossel | video", "tipo_referencia": "<criativo_tipo, se carrossel>", "gancho_categoria": "<se vídeo>", "regra": "<por que a opção A é desse tipo>"},
      "opcoes": [
        {"letra": "A", "tipo": "objeto", "origem_imagem": "ilustracao", "imagem": "<o que aparece e por que tem a ver com o hook>", "arquivo": "h1/A/slide-01.png"},
        {"letra": "B", "tipo": "numero", "origem_imagem": "ilustracao", "imagem": "...", "arquivo": "h1/B/slide-01.png"},
        {"letra": "C", "tipo": "foto",   "origem_imagem": "foto", "foto_arquivo": "assets/perfil/fotos/02.jpg", "imagem": "...", "arquivo": "h1/C/slide-01.png"}
      ]
    }
  ],
  "escolhas": []
}
```

Varie de verdade: nenhum tipo de capa em mais de 3 dos 5 hooks, e a mesma foto do cadastro em no máximo 2 capas.

Depois monte o relatório. O script puxa da fila, para cada hook, o post de referência: a URL, a capa, a data, o formato, os números com a média do perfil ao lado, **por que ele foi escolhido** (visualização, comentários ou os dois), o texto original e a tradução.
```bash
python scripts/selecao.py relatorio
```

**Guardião:**
```bash
python scripts/guardiao.py capas
```
Revisor independente: abra **cada** capa com a ferramenta Read e confira, opção por opção:
- a imagem mostra o assunto do hook (dá para dizer em uma frase o que ela mostra e por que é disso que o hook fala). Imagem genérica reprova
- o hook adaptado preserva o mecanismo do `hook_original` e fala com o `publico` do cadastro
- **o assunto é o mesmo da referência:** leia o `tema_central` da fonte e o `tema` do hook; se não são o mesmo assunto, reprova
- `mantido` e `mudou` descrevem com verdade o que aconteceu
- as 3 opções do mesmo hook são ideias visuais diferentes, não a mesma com outra cor
- a opção A é a mais próxima do criativo da referência: abra a capa original (`origem.capa`, quando existir) e compare
- avatar, nome e @ legíveis; título legível em miniatura; cores do cadastro
- nada do campo `proibido`; nenhum número sem fonte
- com `regulado: sim`: nenhuma restrição legal violada, no texto nem na imagem (leia as restrições uma a uma contra cada capa)

Guardião e revisor aprovaram: libere a seleção. Só agora ela pode ser mostrada ou escolhida.
```bash
python scripts/selecao.py liberar
```

O revisor também devolve, para cada hook, **a melhor das 3 opções** e a ordem dos hooks do mais forte ao mais fraco. Guarde isso: é a recomendação do relatório e a base da escolha automática.

## Depois das capas

**`escolha_capa: usuario`** → a rodada termina aqui. Vá ao Relatório no formato "Escolha".

**`escolha_capa: automatica`** → "Escolha automática".

### Escolha automática

Escolha os `posts_por_dia` hooks mais fortes segundo o revisor, cada um com a opção que ele apontou como melhor:
```bash
python scripts/selecao.py escolher <códigos>
```
e siga direto para o Modo produção.

---

# Modo produção — `/instaflow escolher <códigos>`

Comece pela **Etapa 0 — Cadastro**, como no modo rodada.

Se a chamada trouxe códigos, grave a escolha:
```bash
python scripts/selecao.py escolher 1B 3A
```
Erro do script (código inexistente, duas opções do mesmo hook) → explique em uma linha e pare; essa é a única resposta que você pede de novo.

Veja o que falta produzir:
```bash
python scripts/selecao.py pendentes
```
Ele lista só as escolhas ainda não publicadas. Para **cada uma**, na ordem:

- `peca_existente` preenchido → a peça foi começada antes (ontem, ou numa sessão que caiu). **Retome nessa pasta**, com o mesmo `SLUG`; o `estado.py` pula as etapas já concluídas. Não crie outra pasta.
- `peca_existente` vazio → defina `SLUG` = `<AAAA-MM-DD>-<3 a 5 palavras do tema>` e `PECA` = `conteudo/<SLUG>`. O `SLUG` já leva a data: onde outra skill pedir "data + slug", use o `SLUG` como está, sem repetir a data.

Na peça nova, grave:
- `PECA/fonte.json`: o post de origem inteiro, tirado de `pesquisa-instagram/fila.json`
- `PECA/escolha.json`: `{"data": "<ID da seleção>", "n": <n, como número>, "letra": "<letra>", "tipo": "<tipo>", "fonte_id": "<id>", "hook": "<hook da seleção, sem mudar>", "rehook": "<rehook da seleção, sem mudar>", "pasta_capa": "conteudo/_selecao/<ID>/h<n>/<letra>"}`

### Etapa 3 — Escolha

```bash
python scripts/estado.py tentar escolha --peca <SLUG>
python scripts/guardiao.py escolha --peca <PECA>
```
Reprovou → a peça não existe na seleção. Não produza.

### Etapa 4 — Copy

```bash
python scripts/estado.py tentar copy --peca <SLUG>
```

Invoque a skill **`instaflow-redator`** entregando `PECA/fonte.json`, `PECA/escolha.json` e o cadastro. As regras de escrita e o formato dos arquivos estão nela; o que ela precisa respeitar daqui é:

```
SEM PERGUNTAS. Não pare, não peça briefing, não proponha outro ângulo.

HOOK E REHOOK: os de escolha.json. Slide 1 = `hook`; slide 2 abre com o `rehook`. Sem reescrever.

MIOLO: mesmo tema central, mesma estrutura de argumento e mesma ordem de ideias da fonte.
Pelo menos 60% dos `termos_centrais` aparecem; no máximo 20% do miolo coincide palavra
por palavra com a fonte. Nunca outro assunto.

IDIOMA: o `idioma` do cadastro. Fonte em outra língua: trabalhe sobre `transcricao_pt`.

DADOS: nenhum número, caso, cliente ou promessa da fonte é herdado. Cada item de
`dados_a_verificar` é confirmado em fonte pública (URL em `pesquisa:`) ou sai do texto.
Resultado de cliente só entra se estiver no cadastro.

LAYOUT: cada slide de conteúdo traz `layout:` (padrao, imagem-topo, lado, destaque ou cheia).
Fonte em carrossel: o layout de cada slide é o do slide correspondente em `criativo_slides`.
Fonte em vídeo: o layout segue o conteúdo do slide. Com 3 ou mais slides de conteúdo, pelo
menos 2 layouts diferentes, e nunca o mesmo 3 vezes seguidas.

IMAGEM: todo slide tem `imagem:` com `tipo` (foto, print, ilustracao ou ia) e `descricao`
(o que a imagem mostra e por que é disso que o slide fala). No slide 1, a `descricao`
começa pelo tipo de capa escolhido. Sem ideia de imagem para um slide, o slide não entra.

CTA: último slide e primeira linha da legenda pedem para comentar a `isca_palavra`,
prometendo a `isca_entrega`. Nada do CTA do concorrente.

PROIBIDO: o que estiver em `proibido` no cadastro; citar o perfil de origem; travessão longo.

RESTRIÇÕES LEGAIS (com `regulado: sim`): a seção "Restrições legais" do cadastro é
inviolável. O último slide traz a linha `registro:` e a legenda traz o registro uma vez,
no fim, antes das hashtags.

TAMANHO: de 4 a `slides_max` slides. Slide 1 = parte capa; último = parte cta.

ENTREGA, em arquivos, no formato definido na skill:
- PECA/roteiro.md
- PECA/legenda.txt  (texto puro; primeira linha = pedido da isca; 5 a 7 hashtags no fim)
```

**Guardião:**
```bash
python scripts/guardiao.py copy --peca <PECA>
```
Revisor independente, critérios:
- o slide 1 é o hook escolhido e o slide 2 é o rehook escolhido
- o carrossel trata do mesmo tema da referência, na mesma ordem de ideias; ponto da referência que sumiu ou ponto novo que não estava nela precisa de motivo (dado sem fonte, restrição legal, item proibido)
- o texto fala com o `publico` do cadastro, no `tom_de_voz` do cadastro, sobre o `nicho` do cadastro
- nenhum número, caso ou promessa aparece sem estar no cadastro ou numa URL de `pesquisa:`
- a `descricao` da imagem de cada slide é específica e tem a ver com o texto daquele slide
- nada do campo `proibido`; nenhum dos sinais de `sinais-de-ia.md`, da skill de texto
- com `regulado: sim`: cada restrição legal conferida contra o texto e contra a `descricao` das imagens; o registro aparece só no último slide e no fim da legenda

### Etapa 5 — Design

```bash
python scripts/estado.py tentar design --peca <SLUG>
```

Invoque a skill **`instaflow-designer`** no **modo carrossel**, com `PECA/roteiro.md`. A capa é a opção escolhida, copiada de `pasta_capa`, sem redesenho. Os outros slides ganham a imagem descrita no roteiro. Onde o workflow dela pede confirmação, a resposta é sim.

**Guardião:**
```bash
python scripts/guardiao.py design --peca <PECA>
```
Revisor independente: abra **cada** `slide-NN.png` com a ferramenta Read e confira:
- o slide 1 é a capa escolhida
- em todo slide há imagem **e** texto, e a imagem mostra o que o roteiro descreveu
- o layout de cada slide é o do roteiro, e o conjunto se parece com a referência (quando ela é carrossel, compare slide a slide com as imagens originais)
- avatar, nome e @ legíveis no topo de todos os slides
- contraste suficiente, nada cortado, nada sobreposto, cores do cadastro
- o texto de cada slide é exatamente o do roteiro
- o topo segue o `perfil_tipo` (foto e nome da pessoa, ou logo e nome da marca)
- com `regulado: sim`: nenhuma imagem vetada (antes e depois, paciente ou cliente identificável, o que as restrições listarem) e o registro legível no último slide

### Etapa 6 — Publicação

```bash
python scripts/estado.py tentar publicacao --peca <SLUG>
node scripts/export_jpeg.js <PECA>/vN
```

O horário da peça é o próximo horário livre de `horarios`, no `fuso` do cadastro: hoje se ainda não passou, senão amanhã. Havendo mais peças que horários no dia, as seguintes vão para os dias seguintes. No Windows, pegue a hora atual pelo PowerShell (`Get-Date -Format "yyyy-MM-dd HH:mm:ss"`), nunca pelo Git Bash.

**`MODO_PUBLICACAO manual`**
1. Copie `vN/upload/slide-*.jpg` e `legenda.txt` para `entrega/<SLUG>/`.
2. Grave `entrega/<SLUG>/referencia.txt` com a URL do post de referência, o perfil, os números dele e por que foi escolhido.
3. Grave `PECA/publicacao.json`: `{"modo": "manual", "pasta": "entrega/<SLUG>", "horario": "<data e hora sugeridas>", "fonte_url": "<url do post de referência>"}`.

**`MODO_PUBLICACAO metricool`**
0. **Nova tentativa?** Se `PECA/publicacao.json` já tem `metricool_id`, o post **já foi agendado**: não agende de novo. Confira e corrija só o que o guardião apontou (com `updateScheduledPost`, se for o caso).
1. Suba as imagens: `python scripts/r2_upload.py carrosseis/<SLUG> <PECA>/vN/upload/slide-*.jpg --json`
2. Confira com `getScheduledPosts` que o horário não está ocupado.
3. `createScheduledPost` com o `metricool_blog_id` do cadastro, `providers: [{"network":"instagram"}]`, `instagramData: {"type":"POST"}` (acrescente `isAiGenerated: true` se alguma imagem foi gerada por IA), as URLs em `media` na ordem dos slides, o conteúdo de `legenda.txt` em `text`, e:
   - `publicacao_aprovacao: direto` → `autoPublish: true`, `draft: false`
   - `publicacao_aprovacao: rascunho` → `autoPublish: false`, `draft: true`
4. **Logo depois do `createScheduledPost`, antes de qualquer conferência,** grave `PECA/publicacao.json`: `{"modo": "metricool", "urls": [...], "metricool_id": ..., "horario": "...", "aprovacao": "direto|rascunho", "fonte_url": "<url do post de referência>"}`.
5. Conector do Metricool indisponível nesta sessão: a etapa falhou por esse motivo. **Na terceira tentativa**, em vez de agendar, entregue a peça em `entrega/<SLUG>/` como no modo manual e grave o `publicacao.json` com `"modo": "manual"` e `"motivo_fallback": "<por que o Metricool falhou>"`. O guardião aceita esse plano B e o relatório diz o que aconteceu.

Detalhes e armadilhas em `docs/pipeline-publicacao.md`.

**Guardião:**
```bash
python scripts/guardiao.py publicacao --peca <PECA>
```
No modo metricool, confira também com `getScheduledPosts` que existe **um só** agendamento com essa mídia, no horário certo, e que a primeira linha do texto é o CTA da isca.

**Aprovada a publicação**, tire a fonte da fila, grave na memória e marque a escolha como feita:
```bash
python .claude/skills/instaflow-pesquisa/scripts/fila.py marcar --id <fonte_id> --slug <SLUG>
python scripts/selecao.py feita <código> --slug <SLUG>
```

Peça bloqueada em copy ou design: `fila.py descartar --id <fonte_id> --motivo "..."`.

### Fechar a seleção

Quando `selecao.py pendentes` não listar mais nada (tudo publicado ou bloqueado e descartado):
```bash
python scripts/selecao.py produzido
```
Os hooks que não foram escolhidos voltam à fila uma vez. Hook mostrado em duas seleções sem ser escolhido sai de cena sozinho, para o relatório não repetir os mesmos posts.

---

## Como chamar o revisor

Quem produziu não aprova. Para a parte de critério de cada guardião, abra um **subagente novo** (ferramenta Agent) e entregue só: os arquivos a conferir, o cadastro e a lista de critérios da etapa. Não conte como você fez nem o que acha do resultado.

**O revisor separa o que bloqueia do que é ajuste.** Peça a resposta neste formato, um item por linha, cada um apontando o trecho, o post ou a capa exata:

```
BLOQUEIA <item>: <motivo>     -> quebra uma regra: assunto trocado, afirmação que a referência não faz,
                                 imagem que não mostra o assunto, restrição legal, dado sem fonte,
                                 identidade ausente, duas opções com a mesma ideia
AJUSTE   <item>: <sugestão>   -> poderia ficar melhor, mas nenhuma regra foi quebrada
APROVADO                      -> quando não há nenhum BLOQUEIA
```

- Só `BLOQUEIA` reprova. `AJUSTE` não reprova e não gera nova tentativa: aplique os que forem rápidos e siga.
- Motivo vago ("pode melhorar", "não está ideal") não é `BLOQUEIA`.
- **Uma revisão por tentativa.** Não chame o revisor duas vezes na mesma tentativa.

**Na nova tentativa, conserte e reveja só o que bloqueou.** Não refaça o que foi aprovado e não mande tudo de novo para o revisor: entregue a ele apenas os itens que bloquearam, com a pergunta "isto foi resolvido?". O que ele já aprovou continua aprovado.

**Um item ruim não derruba os outros.** Se depois da segunda tentativa um item continua bloqueando, na terceira ele sai e o resto segue:

- **Pesquisa:** o post que continua com problema é descartado (`fila.py descartar --id <id> --motivo "<o que o revisor apontou>"`). A etapa passa com os posts que estão bons.
- **Capas:** o hook que continua com problema sai da seleção. Tire-o de `hooks`, registre em `"retirados": [{"fonte_id": "...", "motivo": "..."}]` no `selecao.json`, refaça o relatório e libere a seleção com os hooks aprovados (mínimo 1). O post volta para a fila.
- **Copy, design e publicação:** a peça com problema fica bloqueada; as outras peças seguem.

Só bloqueie a etapa inteira quando não sobrar nada aprovado.

Se a ferramenta Agent não estiver disponível, releia você mesmo os arquivos do zero, critério por critério, e registre no relatório que a revisão não foi independente.

**Diga ao usuário onde você está.** A cada etapa e a cada nova tentativa, escreva uma linha: a etapa, o número da tentativa ("capas, tentativa 2 de 3") e o que está sendo corrigido. Rodada longa em silêncio parece travada.

## Relatório

Termine **sempre** com o relatório no chat, mesmo quando tudo falhou. É por aqui que o usuário é avisado.

**Formato "Escolha"** (fim do modo rodada, com `escolha_capa: usuario`):

O `selecao.py relatorio` gera um **cartão em imagem por hook** (`conteudo/_selecao/<ID>/cartao-hook-N.jpg`). Cada cartão já traz tudo junto: o post original que serviu de modelo, os números dele, por que entrou, a URL e as 3 capas lado a lado com os códigos. **É isso que você mostra.** Não separe a explicação das imagens e não descreva as capas em texto.

Para cada hook, na ordem, envie o cartão (ferramenta de enviar arquivo ou imagem) e, logo abaixo, só duas linhas:

```
<N>. <hook>
Post modelado: <url do post de referência>  ·  Recomendo <código>: <motivo do revisor em poucas palavras>
```

Depois do último cartão:

```
Para produzir, responda com os códigos. Exemplo: /instaflow escolher 1B 3A
Você publica <posts_por_dia> por dia; pode escolher de 1 a <N>. (seleção <ID>)
Página com tudo: conteudo/_selecao/<ID>/relatorio.html
```

Nada além disso: sem tabela, sem lista das opções, sem repetir o que o cartão mostra. Se a sessão não permitir enviar imagem, diga onde estão os cartões e mande as duas linhas de cada hook.

**Formato "Produção"**:

```
RODADA <data>: <X> de <N escolhidos> carrosséis prontos

PEÇA 1: <título> (opção <código>)
  Post de referência: <url>
  <perfil> · <por que foi escolhido, com os números>
  Situação: agendado para <horário> (rascunho | direto)  |  pronto em entrega/<SLUG>/ para postar às <horário>
  Tentativas: copy 1 · design 2 · publicação 1

BLOQUEADO: <etapa> da <peça ou rodada>
  O que falhou nas 3 tentativas: <motivos, um por linha>
  O que você precisa fazer: <ação concreta>

AVISOS
  <avisos do cadastro, da coleta e da fila>

FILA: <prontos> posts prontos · próxima coleta em <data>
```

Se algo ficou bloqueado, comece o relatório pela linha `ATENÇÃO: a rodada não fechou.`

## O que você nunca faz

- Perguntar fora do `/instaflow novo`, fazer no cadastro pergunta que não está no roteiro fixo, ou mandar mais de 3 perguntas numa mensagem.
- Publicar algo que viole a regulamentação da profissão do cadastro.
- Agir sem reler o cadastro.
- Escrever ou desenhar um carrossel antes da escolha da capa.
- Entregar slide sem imagem, ou com imagem que não tem a ver com o texto.
- Inventar tema, número, caso ou depoimento.
- Trocar o assunto do post de referência, ou entregar uma peça sem a URL dele.
- Produzir vídeo ou roteiro de vídeo.
- Digitar senha ou token, ou contornar CAPTCHA e verificação do Instagram.
- Mandar o usuário salvar, mover ou renomear arquivo.
- Tentar uma etapa pela quarta vez.
