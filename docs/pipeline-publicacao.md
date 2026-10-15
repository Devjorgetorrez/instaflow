# Pipeline de publicação no Instagram

Como um carrossel sai daqui e vai parar no feed sem ninguém arrastar arquivo.

## O gargalo, e por que ele existe

Toda API de publicação exige que a imagem já esteja num servidor público no momento da chamada. Isso não é limitação do Metricool. É de todas:

| Caminho | O que exige | Custo |
|---|---|---|
| Instagram Graph API (Meta) | URL pública + app na Meta + token de longa duração + conta Business | grátis, setup pesado |
| API REST do Metricool | URL pública | plano pago com API |
| Conector Metricool no Claude (o que este agente usa) | URL pública | incluso na conta Metricool |

O conector é o caminho mais curto. Resolvido o hosting, ele publica sem app na Meta.

## Regras do Instagram que quebram o post se ignoradas

1. **Imagem: só JPEG.** PNG, WebP e GIF são rejeitados no feed por API. **Vídeo: MP4/H.264 funciona**, ver "Carrossel com vídeo" abaixo.
2. **Aspect ratio entre 4:5 e 1.91:1.** O canvas 1080x1350 é exatamente 4:5, o limite do retrato.
3. **Todas as imagens do carrossel são cortadas pro formato da primeira.**
4. **Máximo de 10 itens** por carrossel.
5. **Limite de 100 posts por API a cada 24h.** Carrossel conta como 1.
6. **Container expira em 24h** se não for publicado.

## Setup, uma vez só

### 1. Cloudflare R2

1. Cria conta em dash.cloudflare.com (grátis)
2. Menu **R2 Object Storage** → **Create bucket**. Nome sugerido: `instaflow`
3. Dentro do bucket, aba **Settings** → **Public Development URL** → **Enable**. Isso gera uma URL tipo `https://pub-xxxxxxxx.r2.dev`
4. Volta pra tela do R2 → **Manage API Tokens** → **Create API Token**
   - Permissão: **Object Read & Write** (basta para publicar; a regra de limpeza de 30 dias é criada pelo painel, mais abaixo)
   - Escopo: só o bucket criado
5. Copia os valores que ele mostra: Access Key ID, Secret Access Key, e o Account ID (que aparece na URL do painel)

Franquia grátis: 10 GB de armazenamento e 10 milhões de leituras por mês. Um carrossel pesa cerca de 1,2 MB.

### 2. Colar as credenciais no `.env`

O agente cria o arquivo `.env` na raiz do projeto. Abra-o e preencha os valores. **Você cola, não o agente.** O script lê do arquivo e nenhum segredo passa pela conversa nem pelo histórico do shell.

```
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=instaflow
R2_PUBLIC_BASE=https://pub-xxxxxxxx.r2.dev
```

O `.env` já está no `.gitignore`. Nunca envie esse arquivo a ninguém.

### 3. Metricool

Conecte sua conta do Instagram no Metricool e o conector do Metricool no Claude. O ID da marca e o fuso são gravados pelo agente no cadastro.

## O fluxo, depois do setup

```
instaflow            → escolhe os posts de referência e conduz as etapas
instaflow-redator  → escreve o roteiro e a legenda
instaflow-designer    → desenha os slides
scripts/export_jpeg.js → exporta em JPEG 1080x1350
scripts/r2_upload.py → sobe pro R2 e devolve as URLs públicas
conector Metricool   → createScheduledPost com as URLs e a legenda
```

Os dois comandos:

```
node scripts/export_jpeg.js conteudo/<YYYY-MM-DD>-<slug>/v1
```

Exporta os slides em JPEG 1080x1350 dentro de `v1/upload/`. O PNG 2160x2700 da skill de imagem continua sendo o arquivo de arquivo; o JPEG é só para publicação.

```
python scripts/r2_upload.py carrosseis/<slug> <pasta>/upload/*.jpg
```

Imprime uma URL pública por linha, na ordem dos arquivos. Com `--json` devolve `{"urls":[...]}`.

## Como o Metricool trata a mídia

Ele baixa a imagem da URL pública, normaliza e **rehospeda no servidor dele**. Duas consequências:

1. Qualquer URL pública serve.
2. O limite de requisições do `r2.dev` não afeta o post: o bucket só é lido no momento do agendamento. Quem vê o post consome do servidor do Metricool.

## Regra de agendamento

Os horários ficam em `horarios`, no `contexto/cadastro.md`: um por post do dia. A peça vai para o horário dela hoje, se ainda não passou, ou amanhã. Um carrossel por horário.

`publicacao_aprovacao: direto` agenda com `autoPublish: true`. `rascunho` agenda com `draft: true`, e o post fica no Metricool esperando aprovação.

### Trava da legenda

**Nenhum post é agendado sem que a primeira linha do `text` seja o CTA com a palavra da isca** (`isca_palavra` em `contexto/cadastro.md`). Story fica de fora, porque não tem legenda.

O passo é este, sempre nesta ordem:

1. Conferir com `getScheduledPosts` que o horário está livre
2. Pegar a hora atual (no Windows, pelo PowerShell)
3. Agendar no horário do cadastro, conforme `publicacao_aprovacao`
4. Conferir que o `creationDate` devolvido bate com o relógio real
5. Listar de novo e confirmar que existe um só agendamento com aquela mídia

Se o pedido for "agora", agendar de 3 a 5 minutos à frente. O Metricool precisa de folga pra ingerir as imagens antes de disparar.

Atenção: `updateScheduledPost` recria o post e devolve um `id` novo. Depois de atualizar, listar o período e conferir que não sobrou cópia.

### Declaração de conteúdo gerado por IA

Quando qualquer imagem do carrossel for gerada ou alterada de forma significativa por IA, mandar `isAiGenerated: true` dentro de `instagramData`. A flag vale pro carrossel inteiro. Gravação de tela de software real não conta como imagem sintética.

## Custo do Cloudflare e limpeza

| Recurso | Franquia mensal | Preço acima |
|---|---|---|
| Armazenamento | 10 GB-mês | US$ 0,015 por GB-mês |
| Operações Classe A (escrita) | 1 milhão | US$ 4,50 por milhão |
| Operações Classe B (leitura) | 10 milhões | US$ 0,36 por milhão |
| Saída de dados (egress) | ilimitada | sempre grátis |

A dois carrosséis por dia são cerca de 540 escritas e 72 MB por mês. O risco de cobrança é praticamente nulo. Confira os valores atuais no site da Cloudflare.

### Limpeza automática, configurar uma vez

1. **R2** → clica no bucket
2. Aba **Settings**
3. **Object Lifecycle Rules** → **Add rule**
4. Prefixo: `carrosseis/`
5. Ação: apagar objetos **30 dias** após a criação

Depois de publicado, o Metricool já rehospedou tudo, então arquivo velho no bucket não serve pra nada.

## Armadilha do fuso horário (Windows)

O Git Bash pode ignorar a variável `TZ` e devolver UTC. Um horário calculado em cima dele sai defasado em horas.

**No Windows, sempre pegar a hora pelo PowerShell:**

```
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

O `creationDate` que o Metricool devolve vem no fuso configurado. Se ele bater com a hora do PowerShell, o `publicationDate` também está certo.

## Becos sem saída já testados

- **Link do Google Drive não serve de mídia pro Metricool.** Devolve `Failed to normalize media`.
- **Subir arquivo binário codificado por dentro da conversa não é confiável.** O arquivo chega corrompido. Sempre subir por script que lê o arquivo do disco.
