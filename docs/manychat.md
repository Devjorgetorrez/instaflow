# ManyChat: quem comenta a palavra recebe o direct

Todo carrossel termina pedindo um comentário com a palavra do cadastro (`isca_palavra`). O ManyChat é o que responde: quem comenta a palavra recebe, sozinho, uma mensagem no direct com o que foi prometido (`isca_entrega`). Sem ele, cada comentário precisa ser respondido à mão.

O agente não mexe no ManyChat. Ele ensina, passo a passo, com a palavra e a entrega do cadastro já escritas nos textos.

Os nomes dos botões abaixo são os da central de ajuda do ManyChat, que usa o painel em inglês. Se a tela estiver diferente, a central de ajuda (help.manychat.com) tem a versão atual.

## Antes de começar

- **O Instagram precisa ser conta profissional** (Criador ou Empresa). Conta pessoal não conecta. Para trocar, no app do Instagram: Configurações e privacidade → Tipo de conta e ferramentas → Mudar para conta profissional.
- **Liberar as mensagens para ferramentas conectadas.** No app do Instagram: Configurações e atividade → Mensagens e respostas ao story → Controles de mensagens → Ferramentas conectadas → ligar **Permitir acesso às mensagens**. Sem isso a conexão fica dando erro.
- **Custo:** o ManyChat tem plano gratuito, com limite de contatos; os planos pagos liberam mais recursos. Confira os limites atuais na página de preços do ManyChat.

## Passo 1 — Criar a conta e conectar o Instagram

1. Entre em manychat.com e crie a conta.
2. Escolha conectar o **Instagram**. Há duas formas:
   - **Via Instagram**: a mais rápida, não precisa de conta de negócios da Meta.
   - **Via Meta**: a que o ManyChat recomenda, com os recursos mais novos; exige o Instagram ligado a um portfólio empresarial da Meta.
3. Entre com a conta do Instagram do perfil e aceite as permissões.

## Passo 2 — Criar a automação do comentário

1. No menu, abra **Automations** e clique em **+ New Automation**.
2. Escolha o modelo pronto **Auto-DM links from comments**.
3. **Quais posts:** escolha **any post** (qualquer post). Assim vale para todo carrossel que o agente publicar, sem configurar de novo.
4. **Palavra:** marque a opção de comentário com palavra específica e escreva a palavra do cadastro, por exemplo `GRUPO`. Prefira palavra específica a "qualquer comentário": quem recebe direct sem ter pedido costuma deixar de seguir.
5. **Resposta pública (opcional):** até 3 respostas curtas que aparecem embaixo do comentário, por exemplo "Te mandei no direct!". O ManyChat sorteia entre elas.
6. **Mensagem de abertura:** o texto do direct, com um botão. Quem toca no botão libera a conversa, e aí o ManyChat consegue mandar a mensagem seguinte.
7. **Mensagem com o link:** o que a pessoa recebe (`isca_entrega`): o link do grupo, do material, da agenda. Cabem até 3 links.
8. Ligue a automação (**Set Live**) e confira se ela aparece como ativa na lista de Automations.

## Passo 3 — Testar

Peça para alguém que **não** é dono da conta comentar a palavra num post já publicado. Em poucos segundos o direct deve chegar. Comentário feito pela própria conta não dispara.

## O que é bom saber

- A automação responde só ao **primeiro comentário de cada pessoa em cada post**. Se a mesma pessoa comentar a palavra de novo no mesmo post, não recebe outra vez. É regra do Instagram.
- Qualquer comentário que **contenha** a palavra dispara. Por isso a palavra precisa ser específica: "OI" ou "SIM" disparam por engano.
- Não funciona em anúncio criado no Gerenciador de Anúncios, nem em post de remix ou colaboração em que o perfil não é o autor.
- Trocou a palavra no cadastro? Troque também na automação do ManyChat.

## Textos prontos

O agente monta estes três textos com o cadastro e mostra para a pessoa copiar:

```
Resposta pública:  Te mandei no direct! 📩
Abertura do direct: Oi! Que bom que você comentou <isca_palavra>. Toca no botão abaixo que eu te mando agora.
Botão:              Quero receber
Mensagem final:     Aqui está: <isca_entrega>. <link>
```
