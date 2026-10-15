# Agente de Instagram

Desenvolvido por **Link Flow** · Criado por **Jorge Torrez**

Agente para Claude Code que transforma os melhores posts dos seus concorrentes em carrosséis com a sua identidade. Ele acha os posts que saíram da curva, cria 3 opções de capa para cada um dos 5 melhores, você escolhe, e ele produz e publica ou entrega pronto.

## Os três comandos

| Comando | O que faz |
|---|---|
| `/instaflow novo` | Cadastro. Ele faz as perguntas, grava as respostas e guarda as imagens que você mandar. Você não mexe em pasta |
| `/instaflow` | Rodada. Pesquisa os concorrentes e entrega o relatório com as capas para você escolher |
| `/instaflow escolher 1B 3A` | Produz os carrosséis das capas escolhidas (hook 1 opção B, hook 3 opção A) |

## Como ele trabalha

| Etapa | O que faz | O guardião só deixa passar se |
|---|---|---|
| Cadastro | Pergunta por um roteiro fixo, de 3 em 3. Propõe cores e tom para você aprovar e pesquisa as regras do seu conselho, se houver | Tudo foi respondido e, em profissão regulada, as restrições e o registro estão gravados |
| Pesquisa | Coleta os concorrentes e ranqueia cada post contra a média do próprio perfil | Há posts prontos, com hook e rehook extraídos |
| Capas | Pega os 5 melhores e cria 3 capas diferentes para cada | Há 3 opções por hook, de tipos diferentes, todas com imagem ligada ao assunto |
| Escolha | Você responde com os códigos (ou ele escolhe, se o cadastro disser) | A peça nasceu de uma capa escolhida |
| Copy | Escreve o carrossel para o seu nicho, mantendo hook e rehook | Não há cópia da fonte, dado herdado nem slide sem imagem prevista |
| Design | Monta os slides com suas cores, fontes, avatar e @ | Todo slide tem imagem e texto, a capa é a escolhida, nada cortado |
| Publicação | Agenda no Metricool ou entrega em `entrega/` | Os arquivos estão certos e há um só agendamento |

Cada etapa tem até 3 tentativas. Na terceira falha o agente para aquela peça e explica no chat o que falhou e o que você precisa fazer.

## Instalação

**Antes:** tenha no computador o Claude Code (aplicativo do Claude, aba Code, ou o terminal), o [Node.js](https://nodejs.org) versão LTS e o [Python](https://www.python.org/downloads/) 3.10 ou mais novo. No instalador do Python, marque a caixa **Add Python to PATH** na primeira tela.

1. Baixe este pacote: botão verde **Code** → **Download ZIP**, e descompacte numa pasta sua (por exemplo, Documentos).
2. Dê dois cliques em **`install.bat`** (Windows). No Linux ou macOS, rode `bash install.sh` no terminal, dentro da pasta.
3. O terminal abre e instala tudo sozinho: a biblioteca e o navegador que desenham os slides, as bibliotecas que baixam e transcrevem os vídeos dos concorrentes e o modelo de transcrição (cerca de 500 MB, uma vez só). No fim ele mostra a conferência, com `PRONTO`.
4. Abra a pasta no Claude Code e digite:

```
/instaflow novo
```

Se faltar algo, o próprio agente confere de novo no começo do cadastro e instala o que der.

Só três coisas dependem de você, e o agente avisa quando chegar a hora: **criar a conta** nos serviços que escolher usar, **entrar** nela e **colar a chave** no arquivo `.env`. Chave e senha nunca são pedidas na conversa.

## O cadastro

A primeira pergunta é se o perfil é seu ou do seu negócio; isso define se o topo dos posts leva a sua foto ou o logo. Depois dela são seis mensagens curtas, com no máximo 3 perguntas cada, já escritas para o seu caso. Tenha à mão a foto ou o logo, as fotos que quer ver nos posts (se tiver), os @ dos concorrentes e, se a sua profissão tem conselho, o número de registro. Para mandar uma imagem, arraste o arquivo para a conversa.

Cores, letras e jeito de falar o agente propõe a partir do seu logo, de um post, do seu site ou do seu Instagram, e mostra uma amostra de como os posts vão ficar. Se você não tiver nada disso, ele monta duas opções para o seu ramo e você escolhe. Negócio sem logo ganha uma marca provisória com as iniciais. No fim ele mostra uma **revisão geral** de tudo, e só grava depois que você disser que está certo.

Depois do cadastro:

```
/instaflow
```

Abra o relatório que ele indicar, escolha as capas e responda com os códigos.

## Rodando sozinho

No fim do cadastro o agente pergunta se você quer que ele rode todo dia. Se sim, ele cria a rotina diária; o computador precisa estar ligado no horário. Onde o Claude Code não oferecer agendamento, ele mostra como criar a rotina à mão, com o comando `/instaflow`.

- Com **escolha pelo usuário**, a rotina deixa o relatório de capas pronto e espera. Você responde quando quiser com `/instaflow escolher ...`.
- Com **escolha automática**, a rotina vai até o fim sozinha, seguindo as capas mais bem avaliadas.

A revisão do cadastro diz, em uma linha, até onde o agente vai sem você com as escolhas que fez.

## Nenhuma ferramenta é obrigatória

Apify, Metricool, Cloudflare e ManyChat são sugestões. Para cada uma há um caminho sem ferramenta e sem custo, e se você já usa outra ferramenta para a mesma coisa, pode continuar com ela:

| Para quê | Sugerida | Sem ferramenta | Já usa outra? |
|---|---|---|---|
| Buscar os posts dos concorrentes | Apify | Pelo navegador do Claude, com o seu Instagram logado | Hoje o agente lê pela Apify ou pelo navegador |
| Publicar | Metricool + Cloudflare R2 | Os arquivos ficam prontos em `entrega/` e você posta | Os arquivos de `entrega/` servem para qualquer ferramenta de agendamento |
| Responder quem comenta a palavra | ManyChat | Você responde à mão com o texto pronto | Os textos prontos servem para qualquer automação de direct |

## As escolhas do cadastro que mudam o funcionamento

**Coleta**
- Apify: paga por uso, roda sozinha. Estimativa de US$ 0,80 por coleta com 5 concorrentes.
- Navegador: grátis. Precisa do Instagram logado no navegador do Claude e do computador ligado na hora da rotina.

**Publicação**
- Metricool, direto: publica no horário, sem passar por você. O plano gratuito publica até 20 posts por mês; para 1 post por dia o mês inteiro, é preciso um plano pago.
- Metricool, rascunho: fica no Metricool esperando você aprovar.
- Manual: os slides e a legenda ficam em `entrega/<data>-<tema>/` para você baixar e postar.

Sem as chaves do Cloudflare R2, o agente entrega no modo manual e avisa.

**Resposta aos comentários**
- Todo carrossel pede um comentário com a sua palavra (por exemplo, GRUPO). No fim do cadastro você escolhe como responder no direct: à mão, pelo ManyChat (sugerido, tem plano gratuito; o agente ensina a montar) ou por outra automação que já use. Nos três casos o agente entrega os textos prontos.

**Precisa de ajuda?** Abra [docs/Manual-Agente-Instagram.docx](docs/Manual-Agente-Instagram.docx), copie o manual inteiro e cole numa conversa com o Claude junto com o seu problema e a mensagem de erro. Ele explica tudo o que o agente faz e como resolver os problemas mais comuns.

**Guias passo a passo** (o agente ensina por eles, um passo por vez)
- [Cloudflare R2](docs/pipeline-publicacao.md) · [Metricool](docs/metricool.md) · [ManyChat](docs/manychat.md). A chave da Apify o agente ensina direto na conversa.

## Pastas

| Pasta | O que é |
|---|---|
| `contexto/cadastro.md` | O seu cadastro, escrito pelo agente. Dá para corrigir um valor à mão |
| `assets/perfil/` | Avatar, logo e fotos, gravados pelo agente |
| `conteudo/_selecao/` | Os relatórios de capas |
| `conteudo/` | Cada carrossel produzido, com roteiro, slides e a fonte que serviu de modelo |
| `entrega/` | Posts prontos para postagem manual |
| `pesquisa-instagram/` | A fila de posts a modelar e a memória dos que já foram usados |
| `.claude/skills/` | O agente: `instaflow`, `instaflow-pesquisa`, `instaflow-redator`, `instaflow-designer` |
| `scripts/` | Guardiões, estado da rodada, exportação e upload |
| `install.bat` / `install.sh` | O instalador |

## Profissão regulada

Se a sua atividade tem conselho ou regra de publicidade, o agente pesquisa a norma oficial no cadastro, grava as restrições e passa a aplicá-las em todo texto e em toda imagem. Os guardiões reprovam o que violar. Ele aplica a norma publicada; não substitui a orientação do seu conselho ou de um advogado. Confira o resumo que ele mostrar e refaça o cadastro se a norma mudar.

## O que o agente não faz

- Não produz vídeo nem roteiro de vídeo. Reel de concorrente é só matéria-prima para carrossel.
- Não entrega slide só de texto: todo slide tem imagem e texto.
- Não inventa tema, número ou depoimento.
- Não copia o post de origem nem usa a imagem do concorrente.
