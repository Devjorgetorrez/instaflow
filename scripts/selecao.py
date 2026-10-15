"""Selecao de capas: os 5 melhores posts dos concorrentes, 3 opcoes de capa para cada, o usuario escolhe.

    python scripts/selecao.py situacao                 -> a selecao mais recente e o status dela
    python scripts/selecao.py relatorio [--data D]     -> monta relatorio.html a partir de selecao.json e da fila
    python scripts/selecao.py escolher 1B 3A [--data D]-> grava as escolhas (hook 1 opcao B, hook 3 opcao A)
    python scripts/selecao.py produzido [--data D]     -> fecha a selecao depois de produzir as escolhidas
    python scripts/selecao.py descartar [--data D]     -> abandona a selecao sem produzir (a proxima rodada gera outra)

Arquivos em conteudo/_selecao/<data>/: selecao.json, relatorio.html, h<n>/<letra>/slide-01.png, h<n>/origem.jpg
Status: em_montagem -> aguardando_escolha -> escolhido -> produzido (ou descartada)

    python scripts/selecao.py liberar                  -> depois do guardiao de capas aprovar: em_montagem vira aguardando_escolha
    python scripts/selecao.py pendentes                -> as escolhas que ainda nao foram publicadas, com a pasta de cada uma
    python scripts/selecao.py feita 1B --slug SLUG     -> marca uma escolha como publicada
"""
import argparse
import datetime
import html
import json
import pathlib
import re
import shutil
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "conteudo" / "_selecao"
FILA = ROOT / "pesquisa-instagram" / "fila.json"
TIPOS = {
    "simbolo": "símbolo grande no centro",
    "foto": "foto ocupando o slide",
    "recorte": "pessoa recortada de um lado, título do outro",
    "objeto": "objeto ou tela simplificada",
    "numero": "número gigante com apoio visual",
    "dividida": "slide partido em dois",
    "card": "post, notícia ou avaliação em forma de card",
    "print": "tela real recortada",
}
FORMATO = {"reel": "Reel (vídeo)", "carrossel": "Carrossel", "imagem": "Imagem"}
# o que o relatorio guarda do post de origem, para continuar completo depois que a fila mudar
CAMPOS_ORIGEM = ["url", "perfil", "tipo", "data", "views", "curtidas", "comentarios", "alcance", "alcance_estimado",
                 "alcance_relativo", "comentarios_relativo", "taxa_comentarios", "mediana_perfil_alcance",
                 "mediana_perfil_comentarios", "criterio", "motivo", "posicao", "legenda", "transcricao",
                 "transcricao_pt", "idioma"]


def pasta(data=None):
    if data:
        return BASE / data
    pastas = sorted(p for p in BASE.glob("*") if (p / "selecao.json").is_file()) if BASE.is_dir() else []
    return pastas[-1] if pastas else None


def carregar(p):
    return json.loads((p / "selecao.json").read_text(encoding="utf-8"))


def salvar(p, sel):
    (p / "selecao.json").write_text(json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")


def num(n):
    if n is None:
        return "não informado"
    return f"{int(n):,}".replace(",", ".")


def vezes(v):
    return "não calculado" if v is None else f"{v:.1f}".replace(".", ",") + " vezes a média do perfil"


def juntar_origem(p, sel):
    """Copia para a selecao os dados e a capa do post de origem de cada hook."""
    fila = json.loads(FILA.read_text(encoding="utf-8")) if FILA.exists() else []
    por_id = {str(x.get("id")): x for x in fila}
    for h in sel["hooks"]:
        post = por_id.get(str(h.get("fonte_id")))
        if not post:
            continue
        h["origem"] = {k: post.get(k) for k in CAMPOS_ORIGEM}
        h["url"] = post.get("url") or h.get("url")
        an = post.get("analise") or {}
        h["origem"]["tema_central"] = an.get("tema_central")
        capa = next((c for c in post.get("imagens_locais") or [] if (ROOT / c).is_file()), None)
        if capa:
            destino = p / f"h{h['n']}" / "origem.jpg"
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / capa, destino)
            h["origem"]["capa"] = f"h{h['n']}/origem.jpg"


def contar_apresentacao(sel):
    """Hook mostrado e nao escolhido conta uma apresentacao na fila; na segunda, o post sai de cena."""
    if not FILA.exists():
        return
    escolhidos = {str(e["fonte_id"]) for e in sel.get("escolhas") or []}
    mostrados = {str(h.get("fonte_id")) for h in sel.get("hooks") or []} - escolhidos
    fila = json.loads(FILA.read_text(encoding="utf-8"))
    for post in fila:
        if str(post.get("id")) in mostrados:
            post["apresentacoes"] = (post.get("apresentacoes") or 0) + 1
    FILA.write_text(json.dumps(fila, ensure_ascii=False, indent=2), encoding="utf-8")


def pecas_da_selecao(sel):
    """Pastas de carrossel ja criadas para esta selecao: {(n, letra): pasta}."""
    achadas = {}
    for esc in (ROOT / "conteudo").glob("*/escolha.json"):
        try:
            d = json.loads(esc.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if str(d.get("data")) == str(sel["data"]):
            achadas[(int(d.get("n") or 0), str(d.get("letra")))] = esc.parent
    return achadas


def curto(n):
    """4.700 -> 4,7 mil; 1.250.000 -> 1,2 mi."""
    if n is None:
        return "?"
    n = float(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}".replace(".", ",") + " mi"
    if n >= 1_000:
        return f"{n / 1_000:.1f}".replace(".", ",") + " mil"
    return str(int(n))


def montar_relatorio(p, sel):
    """Um cartao por hook, tudo junto: o post de referencia, por que entrou, a URL e as 3 opcoes de capa."""
    e = html.escape
    cartoes = []
    for h in sel["hooks"]:
        o = h.get("origem") or {}
        url = h.get("url") or o.get("url") or ""
        perfil = str(o.get("perfil") or h.get("perfil") or "")
        porque = o.get("criterio") or o.get("motivo") or h.get("motivo") or ""
        alc_rotulo = "alcance estimado" if o.get("alcance_estimado") else "visualizações"
        vezes_a = o.get("alcance_relativo")
        vezes_c = o.get("comentarios_relativo")
        chips = [f'<span class="chip"><b>{curto(o.get("alcance") or o.get("views"))}</b> {alc_rotulo}'
                 + (f' · {str(vezes_a).replace(".", ",")}x o normal' if vezes_a else "") + "</span>",
                 f'<span class="chip"><b>{curto(o.get("comentarios"))}</b> comentários'
                 + (f' · {str(vezes_c).replace(".", ",")}x o normal' if vezes_c else "") + "</span>"]
        capa = (f'<img src="{e(o["capa"])}" alt="Post de referência">' if o.get("capa")
                else '<div class="sem-capa">capa do post não disponível</div>')
        opcoes = "".join(
            f'<figure><div class="cod">{h["n"]}{e(op["letra"])}</div><img src="{e(op["arquivo"])}" alt="Opção {h["n"]}{e(op["letra"])}">'
            f'<figcaption>{e(TIPOS.get(op["tipo"], op["tipo"]))}</figcaption></figure>'
            for op in h.get("opcoes") or [])
        original = o.get("transcricao") or o.get("legenda") or ""
        traducao = o.get("transcricao_pt") or ""
        detalhes = ""
        if h.get("mantido") or h.get("mudou") or original:
            detalhes = ("<details><summary>Ver detalhes: o que foi mantido, o que mudou e o texto original</summary>"
                        + (f'<p><b>Mantido:</b> {e(str(h.get("mantido") or ""))}</p>' if h.get("mantido") else "")
                        + (f'<p><b>Mudou:</b> {e(str(h.get("mudou") or ""))}</p>' if h.get("mudou") else "")
                        + (f'<p><b>Texto original:</b> {e(original)}</p>' if original else "")
                        + (f'<p><b>Tradução:</b> {e(traducao)}</p>' if traducao else "")
                        + "".join(f'<p><b>{h["n"]}{e(op["letra"])}:</b> {e(op.get("imagem", ""))}</p>' for op in h.get("opcoes") or [])
                        + "</details>")
        cartoes.append(f"""<section class="cartao" id="hook-{h["n"]}">
  <header><span class="num">{h["n"]}</span><h2>{e(h["hook"])}</h2></header>
  <div class="corpo">
    <div class="ref">
      <div class="rotulo">Modelado deste post</div>
      <a class="thumb" href="{e(url)}">{capa}</a>
      <div class="perfil">@{e(perfil)} · {e(FORMATO.get(o.get("tipo"), o.get("tipo") or ""))}</div>
      <div class="chips">{"".join(chips)}</div>
      <div class="porque"><b>Por que entrou:</b> {e(porque)}</div>
      <a class="url" href="{e(url)}">{e(url)}</a>
    </div>
    <div class="opcoes">
      <div class="rotulo">Escolha uma capa</div>
      <div class="tres">{opcoes}</div>
    </div>
  </div>
  {detalhes}
</section>""")
    exemplo = " ".join(f"{h['n']}{h['opcoes'][0]['letra']}" for h in sel["hooks"][:2] if h.get("opcoes"))
    doc = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Escolha das capas · {e(str(sel["data"]))}</title><style>
*{{box-sizing:border-box}}body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;padding:28px 16px;background:#eeeeeb;color:#151515;line-height:1.4}}
main{{max-width:1500px;margin:0 auto}}h1{{font-size:26px;margin:0 0 6px}}
.como{{font-size:17px;margin:0 0 22px;color:#333}}code{{background:#151515;color:#fff;padding:3px 8px;border-radius:5px;font-size:15px}}
.cartao{{background:#fff;border-radius:14px;padding:22px 24px;margin-bottom:22px;width:1500px;max-width:100%}}
.cartao header{{display:flex;align-items:center;gap:16px;margin-bottom:18px}}
.num{{flex:none;width:52px;height:52px;border-radius:50%;background:#151515;color:#fff;font-weight:800;font-size:26px;display:flex;align-items:center;justify-content:center}}
.cartao h2{{font-size:27px;line-height:1.2;margin:0;font-weight:800}}
.corpo{{display:grid;grid-template-columns:330px 1fr;gap:26px;align-items:start}}
.rotulo{{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#777;margin-bottom:10px}}
.ref{{background:#f5f5f2;border-radius:10px;padding:14px}}
.thumb{{display:block}}.thumb img{{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:8px;display:block}}
.sem-capa{{aspect-ratio:4/5;border-radius:8px;background:#dededb;display:flex;align-items:center;justify-content:center;color:#777;font-size:14px;text-align:center;padding:10px}}
.perfil{{font-weight:700;font-size:16px;margin:10px 0 8px}}
.chips{{display:flex;flex-direction:column;gap:6px;margin-bottom:10px}}.chip{{background:#fff;border-radius:6px;padding:6px 9px;font-size:14px}}.chip b{{font-size:16px}}
.porque{{font-size:15px;margin-bottom:10px}}
.url{{display:block;font-size:14px;font-weight:700;color:#0b57d0;word-break:break-all}}
.tres{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
figure{{margin:0;position:relative}}figure img{{width:100%;display:block;border-radius:8px;border:1px solid #ddd}}
.cod{{display:inline-block;background:#151515;color:#fff;font-weight:800;font-size:24px;padding:4px 14px;border-radius:8px;margin-bottom:8px}}
figcaption{{font-size:14px;color:#555;margin-top:6px;text-align:center}}
details{{margin-top:14px;font-size:14px;color:#333}}summary{{cursor:pointer;color:#555}}details p{{margin:8px 0}}
@media(max-width:900px){{.corpo{{grid-template-columns:1fr}}.cartao{{width:auto}}}}
</style></head><body><main>
<h1>Escolha das capas · seleção {e(str(sel["data"]))}</h1>
<p class="como">Cada cartão é um post: à esquerda o original que serviu de modelo, à direita as 3 capas. Responda com os códigos, por exemplo <code>/instaflow escolher {e(exemplo)}</code>.</p>
{"".join(cartoes)}
</main></body></html>"""
    (p / "relatorio.html").write_text(doc, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["situacao", "relatorio", "liberar", "escolher", "pendentes", "feita", "produzido", "descartar"])
    ap.add_argument("--slug", default="")
    ap.add_argument("codigos", nargs="*")
    ap.add_argument("--data")
    a = ap.parse_args()

    p = pasta(a.data)
    if not p or not (p / "selecao.json").is_file():
        print(json.dumps({"status": "sem_selecao"}))
        return 0 if a.acao == "situacao" else 1
    sel = carregar(p)

    if a.acao == "situacao":
        try:
            dias = (datetime.date.today() - datetime.date.fromisoformat(str(sel["data"])[:10])).days
        except ValueError:
            dias = None
        print(json.dumps({"data": sel["data"], "status": sel.get("status"), "dias_esperando": dias, "hooks": len(sel.get("hooks", [])),
                          "escolhas": sel.get("escolhas", []), "relatorio": (p / "relatorio.html").relative_to(ROOT).as_posix()},
                         ensure_ascii=False, indent=2))
        return 0

    if a.acao == "relatorio":
        juntar_origem(p, sel)
        salvar(p, sel)
        montar_relatorio(p, sel)
        print((p / "relatorio.html").relative_to(ROOT).as_posix())
        # cartoes em imagem, um por hook, para mostrar direto na conversa
        import subprocess
        r = subprocess.run(["node", str(ROOT / "scripts" / "cartoes_selecao.js"), str(p)], capture_output=True, text=True,
                           cwd=str(ROOT), encoding="utf-8")
        print(r.stdout.strip() if r.returncode == 0 else "AVISO: nao foi possivel gerar os cartoes em imagem: " + (r.stderr or r.stdout).strip()[:200])
        return 0

    if a.acao == "liberar":
        if sel.get("status") != "em_montagem":
            print(f"ERRO: a selecao esta com status {sel.get('status')}, nao em_montagem")
            return 1
        sel["status"] = "aguardando_escolha"
        salvar(p, sel)
        print("selecao liberada para escolha")
        return 0

    if a.acao == "pendentes":
        pastas = pecas_da_selecao(sel)
        saida = []
        for esc in sel.get("escolhas") or []:
            pasta_peca = pastas.get((esc["n"], esc["letra"]))
            publicada = bool(esc.get("feita")) or bool(pasta_peca and (pasta_peca / "publicacao.json").exists()
                                                       and json.loads((pasta_peca / "publicacao.json").read_text(encoding="utf-8")).get("conferida"))
            if not publicada:
                saida.append({"codigo": f"{esc['n']}{esc['letra']}", "fonte_id": esc["fonte_id"], "tipo": esc["tipo"],
                              "peca_existente": pasta_peca.relative_to(ROOT).as_posix() if pasta_peca else None})
        print(json.dumps({"selecao": sel["data"], "pendentes": saida}, ensure_ascii=False, indent=2))
        return 0

    if a.acao == "feita":
        cod = (a.codigos[0] if a.codigos else "").upper()
        alvo = next((x for x in sel.get("escolhas") or [] if f"{x['n']}{x['letra']}" == cod), None)
        if not alvo:
            print(f"ERRO: {cod} nao esta entre as escolhas")
            return 1
        alvo["feita"], alvo["slug"] = True, a.slug
        salvar(p, sel)
        print(f"escolha {cod} marcada como publicada")
        return 0

    if a.acao in ("produzido", "descartar"):
        if sel.get("status") not in ("produzido", "descartada"):
            contar_apresentacao(sel)
        sel["status"] = "produzido" if a.acao == "produzido" else "descartada"
        salvar(p, sel)
        print("selecao fechada" if a.acao == "produzido" else "selecao descartada")
        return 0

    if sel.get("status") in ("produzido", "descartada", "em_montagem"):
        motivo = {"produzido": "ja foi produzida", "descartada": "foi descartada", "em_montagem": "ainda nao foi aprovada pelo guardiao"}[sel["status"]]
        print(f"ERRO: a selecao {sel['data']} {motivo}. Rode /instaflow para gerar ou concluir uma selecao.")
        return 1
    escolhas, vistos = [], set()
    for cod in a.codigos:
        m = re.fullmatch(r"(\d+)\s*([A-Ca-c])", cod.strip())
        if not m:
            print(f"ERRO: codigo invalido: {cod} (use numero do hook + letra, ex.: 2B)")
            return 1
        n, letra = int(m.group(1)), m.group(2).upper()
        hook = next((h for h in sel["hooks"] if int(h["n"]) == n), None)
        opcao = next((o for o in (hook or {}).get("opcoes", []) if o["letra"] == letra), None)
        if not opcao:
            print(f"ERRO: nao existe a opcao {n}{letra}")
            return 1
        if n in vistos:
            print(f"ERRO: duas opcoes para o hook {n}. E uma por hook.")
            return 1
        vistos.add(n)
        escolhas.append({"n": n, "letra": letra, "tipo": opcao["tipo"], "fonte_id": hook["fonte_id"], "fonte_url": hook.get("url")})
    if not escolhas:
        print("ERRO: nenhuma escolha informada")
        return 1
    sel["escolhas"], sel["status"] = escolhas, "escolhido"
    salvar(p, sel)
    print(f"escolhas gravadas na selecao {sel['data']}:")
    for x in escolhas:
        hk = next(h for h in sel["hooks"] if int(h["n"]) == x["n"])
        print(f"  {x['n']}{x['letra']} ({x['tipo']}): {hk.get('hook')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
