"""Coleta posts dos concorrentes via Apify (actor apify/instagram-scraper).

Saída: posts.json no schema comum (ver referencias/schema.md).
Códigos de saída: 0 ok | 2 token inválido | 3 sem crédito | 4 outro erro
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from comum import API, ler_token, salvar

ACTOR = "apify~instagram-scraper"


def tipo_post(item):
    t = (item.get("type") or "").lower()
    if t == "video" or item.get("productType") == "clips":
        return "reel"
    if t == "sidecar":
        return "carrossel"
    return "imagem"


def normalizar(item):
    url = item.get("url") or ""
    curtidas = item.get("likesCount")
    if isinstance(curtidas, int) and curtidas < 0:
        curtidas = None
    views = item.get("videoPlayCount") or item.get("videoViewCount")
    imagens = list(item.get("images") or [])
    if not imagens and item.get("displayUrl"):
        imagens = [item["displayUrl"]]
    for filho in item.get("childPosts") or []:
        if filho.get("displayUrl") and filho["displayUrl"] not in imagens:
            imagens.append(filho["displayUrl"])
    return {
        "id": item.get("shortCode") or item.get("id"),
        "url": url,
        "perfil": item.get("ownerUsername"),
        "tipo": tipo_post(item),
        "data": item.get("timestamp"),
        "legenda": item.get("caption") or "",
        "views": views if views else None,
        "curtidas": curtidas,
        "comentarios": item.get("commentsCount"),
        "duracao": item.get("videoDuration"),
        "video_url": item.get("videoUrl"),
        "imagens": imagens[:10],
        "comentarios_amostra": [
            {"texto": c.get("text", ""), "autor": c.get("ownerUsername"), "curtidas": c.get("likesCount")}
            for c in (item.get("latestComments") or [])
        ],
        "fonte": "apify",
    }


def chamar_actor(actor, token, entrada, timeout=300):
    url = f"{API}/acts/{actor}/run-sync-get-dataset-items?" + urllib.parse.urlencode(
        {"token": token, "timeout": timeout}
    )
    req = urllib.request.Request(
        url, data=json.dumps(entrada).encode(), headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout + 30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="ignore")[:300]
        if e.code == 401:
            print("ERRO: token da Apify inválido.", file=sys.stderr)
            sys.exit(2)
        if e.code in (402, 403) and ("credit" in corpo.lower() or "usage" in corpo.lower() or e.code == 402):
            print("ERRO: sem crédito na Apify neste mês.", file=sys.stderr)
            sys.exit(3)
        print(f"ERRO Apify HTTP {e.code}: {corpo}", file=sys.stderr)
        sys.exit(4)
    except Exception as e:  # timeout, rede
        print(f"ERRO ao chamar a Apify: {e}", file=sys.stderr)
        sys.exit(4)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config")
    p.add_argument("--perfis", nargs="+", required=True)
    p.add_argument("--dias", type=int, required=True)
    p.add_argument("--limite-por-perfil", type=int, default=30)
    p.add_argument("--saida", required=True)
    a = p.parse_args()

    token = ler_token(a.config)
    perfis = [x.strip().lstrip("@").strip("/").split("/")[-1] for x in a.perfis if x.strip()]
    entrada = {
        "directUrls": [f"https://www.instagram.com/{u}/" for u in perfis],
        "resultsType": "posts",
        "resultsLimit": a.limite_por_perfil,
        "onlyPostsNewerThan": f"{a.dias} days",
        "addParentData": False,
    }
    itens = chamar_actor(ACTOR, token, entrada)
    posts, erros = [], []
    for it in itens:
        if it.get("error"):
            erros.append(f"{it.get('inputUrl', '?')}: {it.get('errorDescription') or it['error']}")
            continue
        posts.append(normalizar(it))

    salvar(a.saida, posts)
    print(f"OK: {len(posts)} posts de {len(perfis)} perfis -> {a.saida}")
    for e in erros:
        print(f"AVISO: {e}")


if __name__ == "__main__":
    main()
