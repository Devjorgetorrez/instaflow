# Roteiro fixo do cadastro (`/instaflow novo`)

Sete mensagens (a primeira com uma pergunta só), uma revisão geral e a instalação. Sempre nesta ordem, sempre com estas perguntas. **Nunca mais de 3 perguntas por mensagem.** Não pule, não reordene, não invente pergunta.

## Como conduzir

1. Antes da primeira pergunta, deixe a máquina pronta. **Avise antes, em uma linha,** que vai instalar o que o agente precisa e que isso leva alguns minutos na primeira vez; depois rode `python scripts/instalar.py instalar`. Ele instala o que dá para instalar sozinho (inclusive o que você precisa para gravar as imagens do cadastro). **Ao terminar, mostre o resultado** em lista curta, em português simples: o que foi instalado e para que serve cada coisa (desenhar os slides, baixar os vídeos dos concorrentes, transcrever os vídeos), e o que ficou para depois.
   - O comando `python` não existe nesta máquina: pare e peça para a pessoa instalar o Python em python.org (versão 3.10 ou mais nova, marcando a caixa "Add Python to PATH" na primeira tela) e abrir o Claude Code de novo. Sem ele nada roda.
   - Faltou o Node.js (linha `VOCE`): peça para instalar em nodejs.org, versão LTS, e abrir o Claude Code de novo. Sem ele não há como desenhar os slides nem a amostra da identidade visual.
   - Algum item terminou com `FALHOU`: rode o `instalar` mais uma vez; se repetir, diga qual item falhou e o que deixa de funcionar sem ele.
   Depois rode `python scripts/cadastro.py novo`. Ele abre um **rascunho** em branco e grava os padrões que não são perguntados: português, até 10 slides, fuso de Brasília, busca a cada 7 dias olhando os últimos 15, e post bom medido por visualização e comentário juntos. O cadastro em uso não muda até a revisão ser aprovada.
2. Envie **uma mensagem por vez**, com as perguntas numeradas como abaixo. Espere a resposta completa. Depois de enviar, não execute mais nada até ela chegar.
3. Ao receber a resposta, anote no rascunho na hora: `python scripts/cadastro.py gravar <campo> "<valor>"`. Faltou algo ou ficou ambíguo: repita **só aquela** pergunta.
4. Fale a língua do cliente. Nunca diga "hexadecimal", "Google Fonts", "token", "campo" ou nome de arquivo. Pergunte pelo resultado, não pela técnica.
   **Serviço de fora nunca é vago.** Quando a pergunta envolve um serviço externo (Apify, Metricool, Cloudflare), diga sempre: o **nome**, **o que ele faz** em uma linha, **quanto custa** com os números abaixo, e **o que a pessoa vai precisar fazer**. "Um serviço pago" sem nome não é resposta que alguém consiga escolher.
   **Toda ferramenta de fora é opcional.** Nenhuma é obrigatória para o agente funcionar. Sempre que oferecer uma (Apify, Metricool, Cloudflare, ManyChat), mostre junto o caminho **sem ferramenta** (custo zero) e diga que, se a pessoa já usa **outra ferramenta** para aquilo, ela pode continuar com a dela: você entrega o material num formato que serve para qualquer uma. Nunca apresente uma ferramenta como requisito.
5. **O que você consegue deduzir, não pergunte: proponha na revisão.** Cores, letras e tom de voz saem do material e do negócio da pessoa, e ela aprova tudo de uma vez no fim.
6. **Imagens:** peça para arrastar o arquivo para a conversa ou colar o caminho. Você grava com `scripts/salvar_imagem.py`, que precisa do caminho do arquivo no computador; se a imagem chegou colada, sem caminho, peça o caminho ou o arquivo arrastado. Nunca mande salvar, mover ou renomear arquivo. `RECUSADA`: diga o motivo em uma linha e peça outra. Durante o cadastro as imagens ficam numa pasta de rascunho; o avatar, o logo e as fotos em uso só são trocados no `confirmar`.
7. Senha e chave de acesso: nunca peça na conversa e nunca digite você. Diga em que linha do arquivo `.env` a pessoa cola.
8. **Nada vira cadastro sem a revisão geral aprovada.** A ordem do fim é: guardião do rascunho → revisão geral → "está correto?" → `confirmar` → instalação → rotina.

---

## Mensagem 1 — Quem aparece (uma pergunta, sozinha)

> Antes de tudo: esse Instagram é **seu**, como pessoa, é **do seu negócio**, ou os dois?
>
> (1) Meu: minha foto e meu nome nos posts.
> (2) Do negócio: o logo e o nome da marca.
> (3) Os dois: minha foto no topo e o logo discreto no post.

Grave `perfil_tipo`: `pessoa`, `negocio` ou `misto`. Espere a resposta antes de qualquer outra pergunta.

**Daqui em diante, tudo sai na forma daquele tipo.** Use só a redação da coluna que vale, nunca as duas ("sua foto ou o logo"), e não volte a perguntar o que essa resposta já decidiu: quem respondeu "do negócio" não é perguntado por foto de rosto nem por nome de pessoa; quem respondeu "meu" não é perguntado por logo como imagem do topo.

| | `pessoa` | `negocio` | `misto` |
|---|---|---|---|
| Topo de todo slide | foto de rosto + nome dela | logo + nome da marca | foto de rosto + nome dela |
| Logo | opcional, só para tirar as cores | é a imagem do topo | entra discreto no último slide |
| Fotos para os posts | dela, em ação | do espaço, equipe, produto | as duas coisas |

## Mensagem 2 — Perfil (3 perguntas, na redação do tipo)

| # | `pessoa` | `negocio` | `misto` | Campo |
|---|---|---|---|---|
| 1 | Qual é o seu @? | Qual é o @ da marca? | Qual é o @? | `perfil_arroba` |
| 2 | Como seu nome deve aparecer nos posts? | Qual é o nome da marca, como deve aparecer nos posts? | Como seu nome deve aparecer nos posts? | `perfil_nome` |
| 3 | Me mande uma foto sua de rosto. É ela que vai no topo de todos os posts. | Me mande o logo. É ele que vai no topo de todos os posts. Se a marca ainda não tem logo, é só dizer. | Me mande uma foto sua de rosto. É ela que vai no topo de todos os posts. | `avatar` |

- Foto de rosto: `python scripts/salvar_imagem.py avatar "<origem>"` → grave em `avatar` o caminho devolvido.
- Logo no topo (`negocio`): `python scripts/salvar_imagem.py marca "<origem>"` devolve dois caminhos. Grave o `logo.png` em `logo`, o `avatar.jpg` em `avatar` e `tem_logo` = `sim`.
- `negocio` sem logo: grave `tem_logo` = `nao`. O topo vai usar uma marca de texto com as iniciais, gerada depois que as cores estiverem definidas (ver [identidade-visual.md](identidade-visual.md)).

## Mensagem 3 — Marca e fotos (até 2 perguntas, na redação do tipo)

| # | `pessoa` | `negocio` | `misto` | Campo |
|---|---|---|---|---|
| 1 | Tem algum post ou site com as cores que você usa? Mande, que eu tiro a sua identidade dali. Se não tiver, eu monto e te mostro. | **Com logo: não pergunte, as cores saem do logo.** Sem logo: Tem algum post ou site com as cores da marca? Mande, que eu tiro a identidade dali. Se não tiver, eu monto e te mostro. | Me mande o logo do negócio. Se não tiver, mande um post ou site com as cores que você usa; ou eu monto e te mostro. | `logo`, `tem_logo` |
| 2 | Tem fotos suas que eu posso usar nos posts? Trabalhando, atendendo, falando. Mande quantas quiser e diga em uma frase o que é cada uma. Se não tiver, é só dizer. | Tem fotos do negócio que eu posso usar nos posts? Do espaço, da equipe, do produto, do atendimento. Mande quantas quiser e diga em uma frase o que é cada uma. Se não tiver, é só dizer. | Tem fotos que eu posso usar nos posts? Suas e do negócio. Mande quantas quiser e diga em uma frase o que é cada uma. Se não tiver, é só dizer. | `tem_fotos` e uma linha `foto:` por arquivo |

- Logo em `misto` (ou em `pessoa`, se ela mandar): `python scripts/salvar_imagem.py logo "<origem>"`, grave em `logo` e `tem_logo` = `sim`. Sem logo: `tem_logo` = `nao`.
- Cada foto: `python scripts/salvar_imagem.py foto "<origem>"`, depois `python scripts/cadastro.py foto "<caminho devolvido>" "<o que é>"`. Sem descrição não entra: pergunte o que é. Grave `tem_fotos` = `sim` ou `nao`.

**Identidade visual (você define, a pessoa aprova a amostra).** Siga [identidade-visual.md](identidade-visual.md): use o primeiro degrau que existir (logo → post ou site → o próprio Instagram dela → tabela por ramo), anote no rascunho as três cores e as duas letras, e gere a amostra.
- Com logo ou material: a amostra entra na revisão geral, sem pergunta.
- **Sem logo e sem material:** depois da Mensagem 4 (você precisa saber o ramo), gere as duas opções da tabela, mostre as duas amostras e pergunte só: "Qual combina mais com você, A ou B?". É a única pergunta extra do cadastro.
- `negocio` sem logo: com as cores definidas, gere a marca de texto e grave em `avatar`.

## Mensagem 4 — Negócio (3 perguntas)

| # | Pergunta | Campo |
|---|---|---|
| 1 | O que você faz, e para quem? Qual é o problema dessa pessoa? | `nicho` e `publico` |
| 2 | O que você vende e que resultado a pessoa leva? | `produto` |
| 3 | Sua atividade tem conselho, órgão ou regra que limita o que você pode divulgar? Por exemplo: médico, dentista, advogado, psicólogo, contador, nutricionista, corretor, ou setor como saúde, finanças, bebida e apostas. Se tiver, qual? | `regulado` (`sim` ou `nao`) e `orgao` |

**Tom de voz (você deduz, sem perguntar):** leia [tom-de-voz.md](tom-de-voz.md), escolha o perfil pelo que a pessoa respondeu e anote em `tom_de_voz` o nome do perfil e a descrição. Ela aprova na revisão.

### Só se houver conselho ou regra — não pule

1. Grave `regulado` = `sim` e `orgao`.
2. Pesquise na internet a norma **vigente** de publicidade daquele órgão, na fonte oficial. Vale para qualquer profissão ou setor: os exemplos da pergunta não são lista fechada.
3. Grave `restricao_norma` (nome e número), `restricao_fonte` (o link oficial) e `restricao_consultada_em` (a data de hoje, AAAA-MM-DD).
4. Grave cada regra, escrita para quem vai criar post de Instagram:
   - `python scripts/cadastro.py restricao OBRIGATORIO "<o que toda peça precisa trazer>"`
   - `python scripts/cadastro.py restricao PROIBIDO "<o que não pode, no texto ou na imagem>"`
   - `python scripts/cadastro.py restricao PERMITIDO "<o que pode, para não travar o conteúdo à toa>"`

   Cubra texto **e imagem**: promessa de resultado, comparação, preço e oferta, depoimento, antes e depois, foto de paciente ou cliente, autopromoção, sensacionalismo, identificação obrigatória.
5. Grave as expressões que o guardião vai procurar: `python scripts/cadastro.py termo "<expressão>"` (ex.: "resultado garantido", "o melhor", "antes e depois").
6. Mostre o resumo em linguagem simples (obrigatório, não pode, pode) e de onde veio. Então pergunte, numa mensagem só:

| # | Pergunta | Campo |
|---|---|---|
| 1 | Qual é o seu número de registro, do jeito que deve aparecer? (ex.: CRM-SP 123456, OAB/SP 123.456) | `registro_profissional` |
| 2 | Qual é a sua área ou especialidade, do jeito que você pode anunciar? | `especialidade` |

O número de registro é **bloqueante**: sem ele o guardião reprova.

**Não achou a norma oficial:** diga com franqueza, peça as regras que a pessoa conhece, grave do mesmo jeito e grave `restricao_fonte` = `informado pelo usuario`. O guardião avisa disso em toda rodada.

**Sem conselho:** `regulado` = `nao`.

## Mensagem 5 — Posts (3 perguntas)

| # | Pergunta | Campo |
|---|---|---|
| 1 | Qual palavra a pessoa comenta no post para receber algo de você, e o que ela recebe? | `isca_palavra` (uma palavra só) e `isca_entrega` |
| 2 | Quantos carrosséis por dia, e em que horário cada um sai? | `posts_por_dia` e `horarios` |
| 3 | Tem algo que você nunca quer ver nos seus posts? Um assunto, uma palavra, um tipo de promessa, o nome de alguém. Se não, é só dizer. | `proibido` ("nada" se não houver) |

Não pergunte número de slides, idioma nem fuso. Só mude o padrão se a pessoa pedir.

**Ao gravar a palavra, explique em até 3 linhas, junto com a próxima mensagem** (não é pergunta, não espere resposta): quem comenta a palavra precisa receber o que foi prometido no direct. Dá para responder à mão, sem ferramenta nenhuma, ou deixar sozinho com uma automação: você sugere o **ManyChat** (tem plano gratuito), mas serve qualquer outra que a pessoa já use. No fim do cadastro ela escolhe e você ensina. A palavra precisa ser específica: palavra comum ("OI", "SIM") dispara por engano.

## Mensagem 6 — Concorrentes (3 perguntas)

| # | Pergunta | Campo |
|---|---|---|
| 1 | Quais perfis eu devo acompanhar para achar os posts que mais renderam? Mande os @. | `concorrentes` |
| 2 | Como eu busco os posts deles? (texto completo das duas opções logo abaixo) | `coleta_modo` (`apify` ou `navegador`) |
| 3 | A cada rodada eu separo os 5 melhores posts e crio 3 opções de capa para cada um. Quem escolhe quais viram carrossel? (1) Você: eu mostro e **espero a sua resposta para continuar**; nada é publicado antes. (2) Eu: sigo as melhores e vou até o fim sem parar. | `escolha_capa` (`usuario` ou `automatica`) |

**Pergunta 2, dita assim, com os nomes e os números:**

> Como eu busco os posts deles?
>
> **(1) Pela Apify.** É um serviço que lê perfis públicos do Instagram e me entrega os posts com visualizações, curtidas e comentários. Eu busco sozinho, sem você fazer nada.
> - Custo: você paga pelo uso, em dólar. Cada busca com 5 perfis sai por cerca de US$ 0,80.
> - A conta é gratuita e vem com US$ 5 de crédito por mês. Buscando uma vez por semana, são umas 4 buscas, perto de US$ 3,20: cabe no crédito grátis. Com mais perfis ou buscas mais frequentes, passa disso.
> - O que você faz: cria a conta em apify.com e cola a chave dela num arquivo aqui do projeto. Eu te mostro onde.
>
> **(2) Pelo seu navegador.** Eu abro o Instagram no navegador do Claude e leio os perfis um a um.
> - Custo: nada.
> - O que precisa: o seu Instagram logado nesse navegador e o computador ligado na hora da busca.
> - Limite: é mais lento, e se o Instagram pedir verificação eu paro e te aviso.
>
> A Apify é opcional: pelo navegador funciona sem conta e sem custo.

Os valores são estimativa: o preço é da Apify e pode mudar. Diga isso se a pessoa perguntar, e não prometa valor fechado.

Mais de 5 perfis: diga o custo proporcional (cerca de US$ 0,16 por perfil a cada busca na Apify) e que a busca demora mais, e siga com a lista que a pessoa confirmar.

## Mensagem 7 — Publicação e rotina (até 3 perguntas)

| # | Pergunta | Campo |
|---|---|---|
| 1 | Quando o carrossel fica pronto, como ele vai para o Instagram? (texto completo das duas opções logo abaixo) | `publicacao_modo` (`metricool` ou `manual`) |
| 2 | Só se for Metricool: publico direto no horário, ou deixo como rascunho para você aprovar? | `publicacao_aprovacao` (`direto` ou `rascunho`) |
| 3 | Quer que eu rode sozinho todo dia? Eu crio a rotina; o computador precisa estar ligado no horário. | `rotina` (ver "Rotina", abaixo) |

**Pergunta 1, dita assim, com os nomes:**

> Quando o carrossel fica pronto, como ele vai para o Instagram?
>
> **(1) Eu agendo pelo Metricool.** É uma ferramenta de agendamento de redes sociais; eu marco o post no horário que você definiu.
> - O que precisa: uma conta no Metricool com o seu Instagram conectado (o plano gratuito publica até 20 posts por mês, então com 1 post por dia ele acaba perto do dia 20; para postar o mês inteiro é preciso um plano pago) e a conexão do Metricool ligada aqui no Claude.
> - Precisa também de uma conta gratuita na Cloudflare, onde as imagens ficam guardadas por até 30 dias para o Metricool conseguir ler. No nosso volume não gera cobrança. Eu te guio na criação.
>
> **(2) Eu te entrego os arquivos.** Os slides e a legenda ficam numa pasta aqui do projeto, prontos para postar como você preferir: pelo celular, pelo Meta Business Suite (gratuito, da própria Meta) ou pela ferramenta de agendamento que você já usa.
> - Custo: nada. Não precisa de conta em lugar nenhum.
>
> O Metricool é opcional. Já usa outra ferramenta de agendamento? Escolha a (2): os arquivos servem para qualquer uma.

- Entrega de arquivos: não faça a pergunta 2; grave `publicacao_aprovacao` = `rascunho`.
- Metricool: descubra o ID da marca pelo conector e grave em `metricool_blog_id`; o nome da marca aparece na revisão geral, para a pessoa conferir.
  - **Uma chamada só.** O conector às vezes demora ou não responde. Se a chamada falhar, for recusada, for interrompida ou a pessoa disser que está demorando, **não chame de novo no cadastro**: pergunte o ID da marca (no Metricool, é o número que aparece no endereço da página depois de `blogId=`) e siga. O conector volta a ser testado na instalação e na publicação; se ele não responder lá, a peça sai no modo manual, sem travar.
  - Sem conector nesta sessão, o ID entra como a 3ª pergunta desta mensagem, no lugar da rotina, e a rotina vai numa mensagem só dela.
- Pergunta 3 = não: grave `rotina` = `nao`. = sim: grave `rotina` = `pedida`; ela vira `criada` (ou `manual`) no passo "Rotina".

---

## Revisão geral — antes de gravar o cadastro

1. Rode `python scripts/guardiao.py cadastro --rascunho`. Cada `FALHA` é uma pergunta a refazer; refaça só ela. Não mostre a revisão com `FALHA` pendente.
2. Mostre a revisão em linguagem simples, numa tabela curta, com **tudo** o que vai ser gravado, inclusive o que você deduziu e os padrões:

| Bloco | O que mostrar |
|---|---|
| Quem aparece | pessoa, negócio ou os dois; @; nome; a imagem do topo |
| Marca | **a amostra da identidade** (a imagem), as cores por nome e o estilo das letras, dizendo de onde você tirou; logo ou marca de texto provisória; quantas fotos e o que são |
| Negócio | o que faz, para quem, o que vende |
| Jeito de falar | o perfil de tom com uma frase de exemplo no ramo dela |
| Regras | o que nunca aparece; se houver conselho: o órgão, a norma, o registro e o resumo do que não pode |
| Posts | a palavra e o que a pessoa recebe; quantos por dia e horários; até 10 slides; em português |
| Concorrentes | os perfis e como você busca |
| Automação | quem escolhe a capa, como publica, rotina |
| **Até onde eu vou sozinho** | a frase da linha `AUTOMACAO` que o guardião imprimiu, dita em português simples |

3. Pergunte: **"Está tudo certo? Posso gravar?"**
   - Corrigiu algo: `gravar` no rascunho, guardião de novo, mostre só o item corrigido e pergunte de novo.
   - Confirmou: `python scripts/cadastro.py confirmar`. Ele roda o guardião de novo e só grava se aprovar. Só agora o cadastro e as imagens novas passam a valer.

## Instalação — depois de gravar

```bash
python scripts/instalar.py checar
```

- Linhas `FALTA`: rode `python scripts/instalar.py instalar` e cheque de novo. Você instala; a pessoa não digita comando.
- Linhas `VOCE`: é o que só ela resolve (criar conta, entrar, colar chave). Leia a linha, diga o passo em português simples, um de cada vez, e cheque de novo quando ela avisar. Se ela quiser, acompanhe pelo navegador com ela já logada, dizendo onde clicar; **criar a conta, digitar senha e colar chave são sempre dela**.
- **Apify** (só se a coleta escolhida foi Apify), sem a chave: guie um passo por vez — criar a conta grátis em apify.com, abrir Settings → API & Integrations, copiar a chave, abrir o arquivo `.env` desta pasta e colar depois de `APIFY_TOKEN=`, salvar. Cheque de novo: a linha só vira `OK` quando a chave é aceita pelo Apify.
- **Cloudflare R2** (só se a publicação é pelo Metricool), sem as chaves: leia `docs/pipeline-publicacao.md`, parte "Setup, uma vez só", e guie **um passo por mensagem**, esperando o "feito" de cada um: criar a conta, criar o bucket, ligar a URL pública, criar a chave de acesso, colar os cinco valores no `.env`. Diga o nome exato de cada linha do `.env` e de onde vem cada valor. Cheque de novo ao final.
- **Metricool** (só se a publicação é pelo Metricool): **teste você mesmo**, pedindo ao conector a lista de marcas (uma chamada só). Funcionou: grave o ID da marca em `metricool_blog_id`, se ainda não está gravado, e diga o nome da marca encontrada. Não há ferramenta do Metricool nesta sessão, ou a marca não aparece: leia `docs/metricool.md` e ensine **um passo por mensagem**, esperando o "feito" de cada um — conta profissional no Instagram, criar a conta no Metricool, conectar o Instagram dentro dele (Connections), conectar o Metricool ao Claude (Settings → Connectors → Browse connectors → Metricool → Grant access). Pule os passos que a pessoa disser que já fez. Lembre o limite do plano gratuito (20 posts publicados por mês). Quando ela avisar que conectou, teste de novo. Se a ferramenta ainda não aparecer nesta conversa, peça para abrir uma conversa nova nesta pasta e escrever **concluir a instalação**: o cadastro já está gravado, e você retoma direto daqui, sem refazer pergunta.
- **Resposta aos comentários** (sempre, para todo cadastro): pergunte, numa mensagem só, como a pessoa quer responder quem comenta a palavra — (1) **ManyChat**, sugerido, com plano gratuito: você ensina a montar; (2) **outra ferramenta** que ela já usa: diga qual; (3) **à mão**, sem ferramenta. Em todos os casos entregue os textos prontos de `docs/manychat.md` ("Textos prontos"), preenchidos com `isca_palavra` e `isca_entrega`. No (2), diga que a configuração é a mesma ideia em qualquer ferramenta (palavra no comentário → direct com a entrega) e não invente tela de ferramenta que você não conhece. No (3), diga que o texto final é o que ela cola no direct de quem comentar. Só no (1) siga o passo a passo abaixo.
- **ManyChat** (só se ela escolheu o ManyChat): você não mexe no ManyChat, você ensina. Leia `docs/manychat.md` e ensine **um passo por mensagem**, esperando o "feito" de cada um: conta profissional e "Permitir acesso às mensagens" no Instagram, criar a conta e conectar o Instagram, criar a automação, testar. No passo da automação, entregue os textos prontos já preenchidos com a palavra (`isca_palavra`) e a entrega (`isca_entrega`) do cadastro, para ela só copiar, e diga para escolher **qualquer post**, assim vale para todo carrossel sem configurar de novo. Se ela já usa ManyChat, pule para a automação; se disser que faz depois, diga que o guia está em `docs/manychat.md` e siga.
- Cloudflare R2 com `FALTA` na regra de limpeza: rode `python scripts/r2_limpeza.py configurar`. Se a chave não tiver permissão, guie a criação pelo painel (bucket → Settings → Object Lifecycle Rules → apagar depois de 30 dias, prefixo `carrosseis/`).
- Só encerre a instalação com `PRONTO`, ou dizendo com clareza o que ficou pendente e o que deixa de funcionar por causa disso.

## Rotina — só se a resposta foi sim

1. Horário da rotina: 2 horas antes do primeiro horário de `horarios`.
2. Se houver ferramenta de agendamento nesta sessão (rotinas ou tarefas agendadas do Claude Code), crie uma rotina **diária**, nesta pasta, com o comando `/instaflow`. Confira listando as rotinas.
3. Criou e conferiu: `python scripts/cadastro.py corrigir rotina criada` e `python scripts/cadastro.py corrigir rotina_horario HH:MM`.
4. Não há ferramenta, ou a criação falhou: **não diga que agendou.** `python scripts/cadastro.py corrigir rotina manual` e mostre o passo a passo para a pessoa criar (rotina diária, esta pasta, comando `/instaflow`, o horário calculado).

## Encerramento

Diga em três linhas: o cadastro foi gravado; o que está instalado e o que ficou pendente; até onde você vai sozinho com as escolhas dela. Termine dizendo que `/instaflow` roda a primeira rodada.
