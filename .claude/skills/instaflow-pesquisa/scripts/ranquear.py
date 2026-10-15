"""Ranqueia os posts coletados comparando cada um com a mediana do proprio perfil.

Um post de 20 mil views num perfil que faz 5 mil vale mais que um de 80 mil num
perfil que faz 200 mil: o que interessa e o quanto ele saiu da curva.

views        -> alcance do post / mediana de alcance do perfil
comentarios  -> comentarios do post / mediana de comentarios do perfil
ambos        -> 50% alcance relativo + 50% taxa de comentarios (comentarios / alcance)

Imagens e carrosseis nao tem views: o alcance e estimado pelas curtidas vezes a
proporcao views/curtidas mediana dos videos da mesma coleta.
"""
import argparse
import os
from datetime import datetime, timedelta, timezone

from comum import carregar, numero, salvar


def mediana(valores):
    v = sorted(x for x in valores if x)
    return v[len(v) // 2] if v else None


def percentis(valores):
    """Mapa indice -> percentil (0..1) por posicao; empates recebem a media."""
    ordem = sorted(range(len(valores)), key=lambda i: valores[i])
    n = len(valores)
    res = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and valores[ordem[j + 1]] == valores[ordem[i]]:
            j += 1
        p = ((i + j) / 2) / (n - 1) if n > 1 else 1.0
        for k in range(i, j + 1):
            res[ordem[k]] = p
        i = j + 1
    return res


def fmt(n):
    if n is None:
        return "?"
    if n >= 10**6:
        return f"{n / 10**6:.1f} mi".replace(".", ",")
    if n >= 10**3:
        return f"{n / 10**3:.1f} mil".replace(".", ",")
    return str(n)


def parse_data(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--entrada", required=True)
    p.add_argument("--metrica", choices=["views", "comentarios", "ambos"], required=True)
    p.add_argument("--top", type=int, required=True)
    p.add_argument("--dias", type=int)
    p.add_argument("--max-por-perfil", type=int)
    p.add_argument("--excluir", nargs="*", default=[], help="arquivos JSON (lista de objetos com 'id') a deixar de fora")
    p.add_argument("--minimo-comentarios", type=int, default=5, help="post com menos comentarios que isso nao entra")
    p.add_argument("--minimo-relativo", type=float, default=2.0,
                   help="so entra post que rendeu pelo menos isso vezes a mediana do proprio perfil")
    p.add_argument("--saida", required=True)
    a = p.parse_args()

    avisos = []
    brutos = carregar(a.entrada)

    ja_usados = set()
    for arq in a.excluir:
        if os.path.exists(arq):
            ja_usados |= {str(x.get("id")) for x in carregar(arq) if x.get("id")}

    vistos, posts, pulados = set(), [], 0
    for x in brutos:
        chave = x.get("id") or x.get("url")
        if not chave or chave in vistos:
            continue
        vistos.add(chave)
        x = dict(x)
        x["perfil"] = (x.get("perfil") or "").lstrip("@")
        for campo in ("views", "curtidas", "comentarios"):
            x[campo] = numero(x.get(campo))
        posts.append(x)

    if a.dias:
        limite = datetime.now(timezone.utc) - timedelta(days=a.dias)
        antes = len(posts)
        posts = [x for x in posts if (parse_data(x.get("data")) or limite) >= limite]
        if antes - len(posts):
            avisos.append(f"{antes - len(posts)} posts fora do periodo de {a.dias} dias descartados.")

    # alcance: views reais, ou curtidas x fator para imagem e carrossel
    razoes = sorted(x["views"] / x["curtidas"] for x in posts if x["views"] and x["curtidas"])
    fator = razoes[len(razoes) // 2] if razoes else 1.0
    for x in posts:
        if x["views"]:
            x["alcance"], x["alcance_estimado"] = x["views"], False
        elif x["curtidas"]:
            x["alcance"], x["alcance_estimado"] = int(x["curtidas"] * fator), True
        else:
            x["alcance"], x["alcance_estimado"] = None, False
    if any(x["alcance_estimado"] for x in posts):
        avisos.append(f"Alcance de imagens e carrosseis estimado pelas curtidas (x{fator:.1f}).")

    # a mediana do perfil usa TODOS os posts do periodo, inclusive os ja modelados
    perfis = sorted({x["perfil"] for x in posts})
    med_alc = {pf: mediana(x["alcance"] for x in posts if x["perfil"] == pf) for pf in perfis}
    med_com = {pf: mediana(x["comentarios"] for x in posts if x["perfil"] == pf) for pf in perfis}
    for pf in perfis:
        qtd = sum(1 for x in posts if x["perfil"] == pf)
        if qtd < 4:
            avisos.append(f"@{pf} tem so {qtd} post(s) no periodo: a mediana dele e pouco confiavel.")

    candidatos = []
    for x in posts:
        if str(x.get("id")) in ja_usados:
            pulados += 1
            continue
        base = med_alc.get(x["perfil"])
        x["alcance_relativo"] = round(x["alcance"] / base, 2) if x["alcance"] and base else None
        basec = med_com.get(x["perfil"])
        x["comentarios_relativo"] = round(x["comentarios"] / basec, 2) if x["comentarios"] is not None and basec else None
        x["taxa_comentarios"] = round(x["comentarios"] / x["alcance"], 6) if x["comentarios"] is not None and x["alcance"] else None
        x["mediana_perfil_alcance"] = base
        x["mediana_perfil_comentarios"] = basec
        candidatos.append(x)
    if pulados:
        avisos.append(f"{pulados} post(s) ja modelados ou ja na fila ficaram de fora.")

    # post comum nao serve de referencia: so entra quem saiu da curva do proprio perfil
    # com "ambos", entra quem saiu da curva em alcance OU em comentarios
    def fora_da_curva(x):
        if a.metrica == "views":
            return x["alcance_relativo"] or 0
        if a.metrica == "comentarios":
            return x["comentarios_relativo"] or 0
        return max(x["alcance_relativo"] or 0, x["comentarios_relativo"] or 0)

    antes = len(candidatos)
    candidatos = [x for x in candidatos if fora_da_curva(x) >= a.minimo_relativo]
    if antes - len(candidatos):
        avisos.append(f"{antes - len(candidatos)} post(s) dentro do normal do perfil (abaixo de {a.minimo_relativo}x a mediana) ficaram de fora.".replace(".", ",", 1))

    antes = len(candidatos)
    candidatos = [x for x in candidatos if (x["comentarios"] or 0) >= a.minimo_comentarios]
    if antes - len(candidatos):
        avisos.append(f"{antes - len(candidatos)} post(s) com menos de {a.minimo_comentarios} comentarios ficaram de fora.")

    # as duas notas ficam guardadas separadas, para o relatorio dizer por que o post entrou
    com_alc = [x for x in candidatos if x["alcance_relativo"] is not None]
    for x, s1 in zip(com_alc, percentis([x["alcance_relativo"] for x in com_alc])):
        x["nota_alcance"] = round(s1, 4)
    com_com = [x for x in candidatos if x["comentarios_relativo"] is not None]
    for x, s2 in zip(com_com, percentis([x["comentarios_relativo"] for x in com_com])):
        x["nota_comentarios"] = round(s2, 4)

    if a.metrica == "views":
        candidatos = [x for x in candidatos if x["alcance_relativo"] is not None]
        for x, s in zip(candidatos, percentis([x["alcance_relativo"] for x in candidatos])):
            x["score"] = round(s, 4)
    elif a.metrica == "comentarios":
        candidatos = [x for x in candidatos if x["comentarios_relativo"] is not None]
        for x, s in zip(candidatos, percentis([x["comentarios_relativo"] for x in candidatos])):
            x["score"] = round(s, 4)
    else:
        candidatos = [x for x in candidatos if x["alcance_relativo"] is not None and x["taxa_comentarios"] is not None]
        pa = percentis([x["alcance_relativo"] for x in candidatos])
        pt = percentis([x["taxa_comentarios"] for x in candidatos])
        for x, s1, s2 in zip(candidatos, pa, pt):
            x["score"] = round(0.5 * s1 + 0.5 * s2, 4)
    candidatos.sort(key=lambda x: (x["score"], x["alcance_relativo"] or 0), reverse=True)

    selecionados, por_perfil = [], {}
    for x in candidatos:
        if a.max_por_perfil and por_perfil.get(x["perfil"], 0) >= a.max_por_perfil:
            continue
        selecionados.append(x)
        por_perfil[x["perfil"]] = por_perfil.get(x["perfil"], 0) + 1
        if len(selecionados) == a.top:
            break
    if len(selecionados) < a.top:
        avisos.append(f"Pedidos {a.top} posts, encontrados {len(selecionados)} que atendem aos criterios.")

    for i, x in enumerate(selecionados, 1):
        x["posicao"] = i
        partes = []
        if x["alcance"] is not None:
            partes.append(("~" if x["alcance_estimado"] else "") + f"{fmt(x['alcance'])} " + ("alcance estimado" if x["alcance_estimado"] else "views"))
        if x["alcance_relativo"] is not None:
            partes.append(f"{x['alcance_relativo']:.1f}x a mediana do perfil".replace(".", ","))
        if x["comentarios"] is not None:
            partes.append(f"{fmt(x['comentarios'])} comentarios")
        if x["taxa_comentarios"] is not None:
            partes.append(f"{x['taxa_comentarios'] * 100:.2f}% comentarios/alcance".replace(".", ","))
        x["motivo"] = " · ".join(partes)
        vz_a = x.get("alcance_relativo") or 0
        vz_c = x.get("comentarios_relativo") or 0
        fa = f"{vz_a:.1f}".replace(".", ",") + " vezes o alcance normal desse perfil"
        fc = f"{vz_c:.1f}".replace(".", ",") + " vezes os comentarios normais desse perfil"
        if a.metrica == "views":
            x["criterio"] = "Entrou por visualizacao: " + fa + "."
        elif a.metrica == "comentarios":
            x["criterio"] = "Entrou por comentarios: " + fc + "."
        elif vz_a >= 2 and vz_c >= 2:
            x["criterio"] = "Entrou pelos dois: " + fa + " e " + fc + "."
        elif vz_a >= vz_c:
            x["criterio"] = "Entrou principalmente por visualizacao: " + fa + " (comentarios: " + f"{vz_c:.1f}".replace(".", ",") + " vezes)."
        else:
            x["criterio"] = "Entrou principalmente por comentarios: " + fc + " (alcance: " + f"{vz_a:.1f}".replace(".", ",") + " vezes)."
        x.setdefault("transcricao", None)
        x.setdefault("analise", None)

    salvar(a.saida, {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "metrica": a.metrica,
        "dias": a.dias,
        "top": a.top,
        "avisos": avisos,
        "posts": selecionados,
    })
    print(f"OK: {len(selecionados)} posts ranqueados por '{a.metrica}' -> {a.saida}")
    for av in avisos:
        print(f"AVISO: {av}")


if __name__ == "__main__":
    main()
