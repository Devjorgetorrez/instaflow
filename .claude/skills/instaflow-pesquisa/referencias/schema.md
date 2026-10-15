# Schemas

## posts.json (saída da coleta — igual nos dois modos)

Lista de objetos:

```json
{
  "id": "AbCdEfGh123",
  "url": "https://www.instagram.com/reel/AbCdEfGh123/",
  "perfil": "concorrente1",
  "tipo": "reel",                 // reel | carrossel | imagem
  "data": "2026-10-01T14:00:00Z", // ISO 8601 (UTC)
  "legenda": "texto da legenda",
  "views": 241820,                // null se não houver (imagens/carrosséis)
  "curtidas": 11481,              // null se ocultas
  "comentarios": 92,
  "duracao": 45.2,                // segundos, só vídeos
  "video_url": "https://...mp4",  // link direto (Apify); expira em horas
  "imagens": ["https://...jpg"],     // links expiram em horas
  "imagens_locais": ["pesquisa-instagram/rodadas/.../midias/ID/01.jpg"],  // preenchido por baixar_midias.py
  "comentarios_amostra": [
    {"texto": "...", "autor": "fulano", "curtidas": 4}
  ],
  "fonte": "apify"                // apify | navegador
}
```

Números podem vir como texto no modo navegador (`"15,3 mil"`, `"1,2 mi"`, `"12.5K"`); o `ranquear.py` converte.

## ranking.json (saída do ranking)

```json
{
  "gerado_em": "...",
  "metrica": "ambos",
  "dias": 15,
  "top": 10,
  "avisos": ["..."],
  "posts": [
    {
      "posicao": 1,
      "score": 0.93,
      "alcance_relativo": 6.0,        // vezes a mediana do proprio perfil
      "motivo": "241 mil views · 6,0x a mediana do perfil · 0,04% comentários/alcance",
      "taxa_comentarios": 0.0004,
      "...todos os campos de posts.json...": "",
      "transcricao": null,
      "analise": null
    }
  ]
}
```

## fila.json (entrada do orquestrador)

Lista com os posts do ranking que ainda não foram modelados. Cada post traz os campos de `posts.json`, os do ranking e os da análise:

```json
{
  "id": "AbCdEfGh123",
  "url": "https://www.instagram.com/reel/AbCdEfGh123/",
  "perfil": "concorrente1", "tipo": "reel", "data": "2026-10-01T14:00:00Z",
  "views": 241820, "curtidas": 11481, "comentarios": 92,
  "idioma": "en",
  "transcricao": "texto original, com os nomes próprios já corrigidos",
  "transcricao_pt": "tradução fiel (só quando o idioma não é pt)",
  "imagens_locais": ["pesquisa-instagram/rodadas/.../midias/AbCdEfGh123/01.jpg"],

  "score": 0.93,
  "alcance": 241820, "alcance_relativo": 6.0, "comentarios_relativo": 2.4, "taxa_comentarios": 0.0004,
  "mediana_perfil_alcance": 40300, "mediana_perfil_comentarios": 38,
  "nota_alcance": 0.97, "nota_comentarios": 0.71,
  "criterio": "Entrou pelos dois: 6,0 vezes o alcance normal desse perfil e 2,4 vezes os comentarios normais desse perfil.",
  "motivo": "241,8 mil views · 6,0x a mediana do perfil · 92 comentarios",
  "apresentacoes": 0,

  "analise": {
    "gancho": "primeira frase ou slide 1, literal, na língua original",
    "rehook": "segunda frase ou slide 2, literal",
    "mecanismo_do_gancho": "número, ameaça, promessa, contraste ou pergunta",
    "criativo": "o que a capa do post mostra",
    "gancho_categoria": "tela | numero | comparacao | citacao | pessoa | conceito",
    "criativo_tipo": "só carrossel e imagem: simbolo | foto | recorte | objeto | numero | dividida | card | print | texto",
    "criativo_slides": ["só carrossel: padrao | imagem-topo | lado | destaque | cheia | texto, um por slide depois da capa"],
    "tema_central": "em uma frase, do que o post trata",
    "termos_centrais": ["8 a 15 termos em português"],
    "nomes_conferidos": [{"ouvido": "Claw", "correto": "Claude"}],
    "estrutura": "gancho → problema → 3 passos → CTA",
    "pontos_principais": ["...", "..."],
    "cta": "...",
    "por_que_funcionou": "...",
    "comentarios_insight": "...",
    "dados_a_verificar": ["todo número, caso ou promessa que o post afirma"]
  }
}
```

Um post está **pronto** para modelar quando tem `url`, `idioma`, `transcricao`, `transcricao_pt` (se não for pt), e na análise `gancho`, `rehook`, `gancho_categoria`, `tema_central`, 6 ou mais `termos_centrais` e a lista `nomes_conferidos`.

`modelados.json` guarda id, url, perfil, data, slug e situação de cada post já usado ou descartado.
