# Metricool: do zero até o agente agendar

O Metricool é onde o agente agenda o carrossel. Ele precisa de três coisas: a conta no Metricool, o Instagram conectado dentro dela, e o Metricool conectado ao Claude. As imagens ficam no Cloudflare R2 (passo a passo em [pipeline-publicacao.md](pipeline-publicacao.md)).

O agente não cria conta e não digita senha. Ele ensina um passo por vez e, no fim, testa a conexão sozinho.

**É opcional.** Sem o Metricool, o agente entrega os slides e a legenda prontos na pasta `entrega/`, e você posta como preferir: pelo celular, pelo Meta Business Suite (gratuito, da própria Meta) ou pela ferramenta de agendamento que já usa. Nesse caminho também não precisa do Cloudflare.

Fontes: central de ajuda do Metricool (help.metricool.com), artigos "How to connect Instagram to Metricool" e "How to connect Metricool's MCP with Claude". Se a tela estiver diferente, a versão atual está lá.

## Antes de começar

- **O Instagram precisa ser conta profissional** (Criador ou Empresa). Conta pessoal não conecta. Para trocar, no app do Instagram: Configurações e privacidade → Tipo de conta e ferramentas → Mudar para conta profissional.
- **Plano gratuito:** 1 marca e até **20 posts publicados por mês**, sem cartão de crédito. O limite volta a zero no dia 1º. Com 1 carrossel por dia, o gratuito acaba perto do dia 20; a partir daí o post fica agendado e não sai. Para postar todo dia o mês inteiro, é preciso um plano pago.

## Passo 1 — Criar a conta

1. Entre em metricool.com e crie a conta grátis.
2. A conta já nasce com uma **marca** (o espaço de um perfil). Dê a ela o nome do perfil.

## Passo 2 — Conectar o Instagram no Metricool

1. No Metricool, clique na foto do perfil (canto de cima, à direita) → **Connections** (Conexões). Escolha a marca na lista.
2. Clique em **Instagram**. Há duas formas de conectar:
   - **Pelo Facebook** (recomendada pelo Metricool, mais estável): o Instagram precisa estar ligado a uma Página do Facebook. Para ligar, no Instagram: Editar perfil → Página → escolher a Página. A ligação precisa aparecer nos dois lados.
   - **Pelo login do Instagram**: não precisa de Página, agenda e publica normalmente, mas mostra menos métricas.
3. Entre com a conta, escolha o perfil e **aceite todas as permissões**. Permissão desmarcada é a causa mais comum de falha.
4. Se um dia precisar reconectar, use a mesma forma da primeira vez. A conexão da Meta expira a cada 60 dias e às vezes pede para reconectar.

## Passo 3 — Conectar o Metricool ao Claude

**No aplicativo do Claude ou em claude.ai** (vale para os dois de uma vez):

1. Abra **Settings** (Configurações) → **Connectors** (Conectores) → **Add** (Adicionar) → **Browse connectors** (Procurar conectores) e pesquise **Metricool**.
2. Clique no **+** ao lado do Metricool.
3. Confira as permissões e clique em **Grant access** (Conceder acesso).
4. Confira que o Metricool aparece como **Conectado**.

Não precisa de chave: o login é feito pela tela do próprio Metricool. Conta gratuita do Claude usa só um conector por vez.

**No Claude Code pelo terminal** (só se não usa o aplicativo): exige plano Pro ou Max. Rode `claude mcp add --transport http metricool https://ai.metricool.com/mcp`, abra o `claude`, digite `/mcp`, escolha Metricool → **Authenticate** e autorize no navegador.

## Passo 4 — O agente confere

O agente pede ao conector a lista de marcas. Achou: grava o ID da marca no cadastro e diz o nome da marca encontrada. Não achou: o conector não está ligado nesta conversa. Abra uma conversa nova na pasta e escreva **concluir a instalação**.

Se o conector demorar ou não responder, o agente não fica tentando: ele pergunta o ID da marca, que é o número depois de `blogId=` no endereço da página do Metricool, e segue.
