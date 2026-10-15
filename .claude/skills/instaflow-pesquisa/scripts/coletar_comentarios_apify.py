"""Busca os comentários dos posts do ranking via Apify (apify/instagram-comment-scraper)
e grava em comentarios_amostra de cada post, atualizando o próprio ranking.json."""
import argparse

from coletar_apify import chamar_actor
from comum import carregar, ler_token, salvar, shortcode

ACTOR = "apify~instagram-comment-scraper"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config")
    p.add_argument("--ranking", required=True)
    p.add_argument("--por-post", type=int, default=15)
    a = p.parse_args()

    token = ler_token(a.config)
    ranking = carregar(a.ranking)
    urls = [x["url"] for x in ranking["posts"] if x.get("url")]
    if not urls:
        print("Nada a buscar.")
        return

    itens = chamar_actor(ACTOR, token, {"directUrls": urls, "resultsLimit": a.por_post})
    por_post = {}
    for c in itens:
        if c.get("error"):
            continue
        por_post.setdefault(shortcode(c.get("postUrl")), []).append(
            {"texto": c.get("text", ""), "autor": c.get("ownerUsername"), "curtidas": c.get("likesCount")}
        )

    total = 0
    for post in ranking["posts"]:
        novos = por_post.get(shortcode(post["url"]))
        if novos:
            novos.sort(key=lambda x: x.get("curtidas") or 0, reverse=True)
            post["comentarios_amostra"] = novos
            total += len(novos)
    salvar(a.ranking, ranking)
    print(f"OK: {total} comentários em {len(por_post)} posts -> {a.ranking}")


if __name__ == "__main__":
    main()
