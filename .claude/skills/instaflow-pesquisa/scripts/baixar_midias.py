"""Baixa as imagens dos posts do ranking logo depois da coleta (em reel, a capa do video).

Os links de imagem do Instagram expiram em poucas horas. Baixando aqui, o texto
das artes pode ser lido depois sem depender do link.

Grava em <pasta>/<id>/NN.jpg e registra os caminhos em 'imagens_locais' no ranking.
"""
import argparse
import os
import urllib.request

from comum import carregar, salvar


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ranking", required=True, help="ranking.json de uma rodada, ou a propria fila.json")
    p.add_argument("--pasta", required=True)
    a = p.parse_args()

    ranking = carregar(a.ranking)
    posts = ranking if isinstance(ranking, list) else ranking["posts"]
    total = falhas = 0
    for post in posts:
        if post.get("imagens_locais"):
            continue
        destino = os.path.join(a.pasta, str(post["id"]))
        os.makedirs(destino, exist_ok=True)
        locais = []
        for i, url in enumerate(post.get("imagens") or [], 1):
            arq = os.path.join(destino, f"{i:02d}.jpg")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r, open(arq, "wb") as f:
                    f.write(r.read())
                if os.path.getsize(arq) > 0:
                    locais.append(arq.replace("\\", "/"))
                    total += 1
            except Exception as e:
                falhas += 1
                print(f"  x {post['id']} imagem {i}: {e}")
        post["imagens_locais"] = locais
        salvar(a.ranking, ranking)
    print(f"OK: {total} imagens baixadas, {falhas} falha(s) -> {a.pasta}")


if __name__ == "__main__":
    main()
