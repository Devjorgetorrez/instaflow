"""Fila de posts de concorrente prontos para modelar, e a memoria dos ja modelados.

    python fila.py situacao --a-cada-dias 7      -> tamanho da fila e se esta na hora de coletar
    python fila.py adicionar --ranking R         -> poe na fila os posts do ranking que ainda nao entraram
    python fila.py proximos --n 5 [--max-por-perfil 2] -> os N melhores da fila, sem deixar um perfil dominar
    python fila.py atualizar --ranking R         -> copia para posts que ja estao na fila os numeros e o criterio do ranking
    python fila.py marcar --id ID --slug SLUG    -> tira da fila e grava na memoria (post modelado)
    python fila.py descartar --id ID --motivo "..."  -> tira da fila sem modelar (nao volta mais)

Arquivos em pesquisa-instagram/ na raiz do projeto: fila.json, modelados.json, ultima_coleta.txt
"""
import argparse
import datetime
import json
import os
import sys

from comum import carregar, raiz_projeto, salvar

TRABALHO = os.path.join(raiz_projeto(), "pesquisa-instagram")
FILA = os.path.join(TRABALHO, "fila.json")
MODELADOS = os.path.join(TRABALHO, "modelados.json")
ULTIMA = os.path.join(TRABALHO, "ultima_coleta.txt")


def ler(caminho):
    return carregar(caminho) if os.path.exists(caminho) else []


def pronto(post):
    an = post.get("analise") or {}
    basico = (post.get("transcricao") or "").strip() and (an.get("gancho") or "").strip() and (an.get("rehook") or "").strip()
    tema = (an.get("tema_central") or "").strip() and len(an.get("termos_centrais") or []) >= 6
    nomes = isinstance(an.get("nomes_conferidos"), list) and an.get("gancho_categoria") in (
        "tela", "numero", "comparacao", "citacao", "pessoa", "conceito")
    idioma = (post.get("idioma") or "").strip()
    traducao = idioma[:2] == "pt" or (post.get("transcricao_pt") or "").strip()
    url = (post.get("url") or "").startswith("http")
    return bool(basico and tema and nomes and idioma and traducao and url)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("acao", choices=["situacao", "adicionar", "atualizar", "proximos", "marcar", "descartar"])
    p.add_argument("--ranking")
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--id")
    p.add_argument("--slug", default="")
    p.add_argument("--motivo", default="")
    p.add_argument("--a-cada-dias", type=int, default=7)
    p.add_argument("--max-por-perfil", type=int, default=2)
    a = p.parse_args()

    fila, modelados = ler(FILA), ler(MODELADOS)
    hoje = datetime.date.today()

    if a.acao == "situacao":
        ultima = open(ULTIMA).read().strip() if os.path.exists(ULTIMA) else None
        dias = (hoje - datetime.date.fromisoformat(ultima)).days if ultima else None
        print(json.dumps({
            "coletou_hoje": dias == 0,
            "na_fila": len(fila),
            "prontos": sum(1 for x in fila if pronto(x)),
            "modelados": len(modelados),
            "ultima_coleta": ultima,
            "dias_desde_a_coleta": dias,
            "coletar_agora": dias is None or dias >= a.a_cada_dias,
        }, ensure_ascii=False, indent=2))
        return 0

    if a.acao == "adicionar":
        conhecidos = {str(x.get("id")) for x in fila} | {str(x.get("id")) for x in modelados}
        novos = [x for x in carregar(a.ranking)["posts"] if x.get("id") and str(x["id"]) not in conhecidos]
        for x in novos:
            x["entrou_na_fila"] = hoje.isoformat()
        fila.extend(novos)
        fila.sort(key=lambda x: x.get("score") or 0, reverse=True)
        salvar(FILA, fila)
        with open(ULTIMA, "w") as f:
            f.write(hoje.isoformat())
        print(f"OK: {len(novos)} post(s) novos na fila, {len(fila)} no total")
        return 0

    if a.acao == "atualizar":
        campos = ["alcance", "alcance_estimado", "alcance_relativo", "comentarios_relativo", "taxa_comentarios",
                  "mediana_perfil_alcance", "mediana_perfil_comentarios", "nota_alcance", "nota_comentarios",
                  "criterio", "motivo", "views", "curtidas", "comentarios"]
        novos = {str(x["id"]): x for x in carregar(a.ranking)["posts"]}
        n = 0
        for post in fila:
            origem = novos.get(str(post["id"]))
            if origem:
                post.update({k: origem[k] for k in campos if origem.get(k) is not None})
                n += 1
        salvar(FILA, fila)
        print(f"OK: {n} post(s) da fila atualizados com os numeros do ranking")
        return 0

    if a.acao == "proximos":
        # post ja mostrado 2 vezes sem ser escolhido sai de cena, para o relatorio nao repetir os mesmos hooks
        cansados = [x for x in fila if (x.get("apresentacoes") or 0) >= 2]
        for x in cansados:
            fila.remove(x)
            modelados.append({"id": x["id"], "url": x.get("url"), "perfil": x.get("perfil"), "data": hoje.isoformat(), "slug": "",
                              "situacao": "descartado", "motivo": "mostrado 2 vezes sem ser escolhido"})
        if cansados:
            salvar(FILA, fila)
            salvar(MODELADOS, modelados)
        prontos = sorted((x for x in fila if pronto(x)), key=lambda x: (x.get("apresentacoes") or 0, -(x.get("score") or 0)))
        escolhidos, por_perfil = [], {}
        for x in prontos:  # primeira passada: respeita o limite por perfil
            if por_perfil.get(x.get("perfil"), 0) < a.max_por_perfil and len(escolhidos) < a.n:
                escolhidos.append(x)
                por_perfil[x.get("perfil")] = por_perfil.get(x.get("perfil"), 0) + 1
        for x in prontos:  # segunda passada: completa, se faltou post de outros perfis
            if len(escolhidos) >= a.n:
                break
            if x not in escolhidos:
                escolhidos.append(x)
        escolhidos.sort(key=lambda x: x.get("score") or 0, reverse=True)
        escolhidos = escolhidos[: a.n]
        print(json.dumps(escolhidos, ensure_ascii=False, indent=2))
        return 0

    alvo = next((x for x in fila if str(x["id"]) == str(a.id)), None)
    if not alvo:
        print(f"ERRO: post {a.id} nao esta na fila", file=sys.stderr)
        return 1
    fila.remove(alvo)
    modelados.append({
        "id": alvo["id"], "url": alvo.get("url"), "perfil": alvo.get("perfil"),
        "data": hoje.isoformat(), "slug": a.slug,
        "situacao": "modelado" if a.acao == "marcar" else "descartado", "motivo": a.motivo,
    })
    salvar(FILA, fila)
    salvar(MODELADOS, modelados)
    print(f"OK: {a.id} -> {modelados[-1]['situacao']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
