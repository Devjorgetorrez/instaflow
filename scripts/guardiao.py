"""Guardiao de etapa: confere o que da para conferir por regra, sem opiniao.

Uso:
    python scripts/guardiao.py cadastro [--rascunho]   (--rascunho: confere as respostas antes de gravar o cadastro)
    python scripts/guardiao.py pesquisa --n 2
    python scripts/guardiao.py capas
    python scripts/guardiao.py escolha    --peca conteudo/<data>-<slug>
    python scripts/guardiao.py copy       --peca conteudo/<data>-<slug>
    python scripts/guardiao.py design     --peca conteudo/<data>-<slug>
    python scripts/guardiao.py publicacao --peca conteudo/<data>-<slug>

Saida 3 = nao conferiu: falta abrir a tentativa (estado.py tentar) ou o limite acabou.
Saida 0 = aprovado. Saida 1 = reprovado (cada motivo numa linha "FALHA ...").
Linhas "AVISO ..." nao reprovam: sao repassadas ao usuario no relatorio.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys
import unicodedata
import urllib.request

from cadastro import CAMINHO, OBRIGATORIOS, R2, RASCUNHO, ROOT, ler, ler_env
from selecao import TIPOS, carregar as carregar_selecao, pasta as pasta_selecao

TRABALHO = ROOT / "pesquisa-instagram"
falhas, avisos = [], []


def falha(msg):
    falhas.append(msg)


def aviso(msg):
    avisos.append(msg)


def carregar_json(p, padrao):
    p = pathlib.Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao


def sem_acento(t):
    t = unicodedata.normalize("NFD", (t or "").lower())
    return " ".join("".join(c for c in t if unicodedata.category(c) != "Mn").split())


def checar_restricoes(texto, cad, onde):
    """Procura no texto as expressoes vetadas pela regulamentacao da profissao."""
    if cad.get("regulado") != "sim":
        return
    limpo = sem_acento(texto)
    for termo in cad.get("termos_proibidos") or []:
        if sem_acento(termo) in limpo:
            falha(f'{onde}: traz "{termo}", vetado pela regulamentacao ({cad.get("orgao")})')


def checar_registro(texto, cad, onde):
    """Profissao regulada: o numero de registro precisa aparecer."""
    reg = cad.get("registro_profissional") or ""
    if cad.get("regulado") == "sim" and reg and sem_acento(reg) not in sem_acento(texto):
        falha(f"{onde}: falta o registro profissional ({reg}), exigido pelo {cad.get('orgao')}")


LIGACAO = {"de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "um", "uma", "uns", "que", "com", "por", "para",
           "pra", "pro", "ao", "aos", "se", "os", "as", "ou", "seu", "sua", "meu", "ele", "ela", "mas", "nao", "sem", "sob", "ate"}


def radicais(texto):
    """Radicais das palavras, sem acento: 5 primeiras letras; siglas e palavras curtas (IA, SEO, CRM) entram inteiras."""
    return {w[:5] for w in re.findall(r"[a-z0-9]+", sem_acento(texto)) if len(w) >= 2 and w not in LIGACAO}


def tem_termo(termo, radicais_do_texto):
    alvo = radicais(termo)
    return bool(alvo) and alvo <= radicais_do_texto


def termos_da_fonte(fonte, cad):
    """Termos centrais do post de origem, menos os que a regulamentacao ou o cadastro vetam."""
    vetados = [sem_acento(t) for t in (cad.get("termos_proibidos") or [])]
    termos = (fonte.get("analise") or {}).get("termos_centrais") or []
    return [t for t in termos if not any(v and v in sem_acento(t) for v in vetados)]


def fidelidade(texto, fonte, cad):
    """Proporcao dos termos centrais da fonte que aparecem no texto. None se a fonte nao tem termos."""
    termos = termos_da_fonte(fonte, cad)
    if not termos:
        return None, []
    rad = radicais(texto)
    faltam = [t for t in termos if not tem_termo(t, rad)]
    return 1 - len(faltam) / len(termos), faltam


def nivel_de_automacao(cad, env):
    """Uma frase dizendo ate onde o agente vai sem ninguem."""
    pontos = []
    if cad.get("rotina") == "pedida":
        pontos.append("a rotina diaria sera criada logo depois de gravar o cadastro")
    elif cad.get("rotina") != "criada":
        pontos.append("alguem precisa digitar /instaflow (nao ha rotina)")
    if cad.get("coleta_modo") == "navegador":
        pontos.append("a busca depende do Instagram logado e do computador ligado")
    if cad.get("escolha_capa") == "usuario":
        pontos.append("para no relatorio de capas e espera a escolha")
    modo = modo_publicacao(cad, env)
    if modo == "manual":
        pontos.append("entrega os arquivos para postagem manual")
    elif cad.get("publicacao_aprovacao") == "rascunho":
        pontos.append("deixa o post em rascunho no Metricool para aprovar")
    if not pontos:
        return "total: busca, escolhe a capa, produz e publica sem ninguem"
    if pontos == ["a rotina diaria sera criada logo depois de gravar o cadastro"]:
        return "total, assim que a rotina for criada: busca, escolhe a capa, produz e publica sem ninguem"
    return "parcial: " + "; ".join(pontos)


def r2_completo(env):
    return all(env.get(k) for k in R2)


def modo_publicacao(cad, env):
    """Modo efetivo: metricool sem R2 vira manual."""
    if cad.get("publicacao_modo") == "metricool" and r2_completo(env) and cad.get("metricool_blog_id"):
        return "metricool"
    return "manual"


# ---------------------------------------------------------------- cadastro
def g_cadastro(a):
    origem = RASCUNHO if a.rascunho else CAMINHO
    if not origem.exists():
        falha("nao ha rascunho de cadastro: rode python scripts/cadastro.py novo" if a.rascunho
              else "nao ha cadastro: rode /instaflow novo")
        return
    cad, env = ler(origem), ler_env()
    for campo in OBRIGATORIOS:
        if cad.get(campo) in (None, "", []):
            falha(f"campo vazio no cadastro: {campo}")
    if cad.get("avatar") and not (ROOT / cad["avatar"]).is_file():
        falha(f"arquivo do avatar nao encontrado: {cad['avatar']}")
    elif cad.get("avatar"):
        from PIL import Image
        with Image.open(ROOT / cad["avatar"]) as im:
            if im.size[0] != im.size[1] or im.size[0] < 400:
                falha(f"avatar com {im.size[0]}x{im.size[1]}: precisa ser quadrado, com pelo menos 400x400")
    if cad.get("tem_logo") not in ("sim", "nao"):
        falha("sem resposta: tem_logo precisa ser sim ou nao")
    elif cad["tem_logo"] == "sim" and not (cad.get("logo") and (ROOT / cad["logo"]).is_file()):
        falha("tem_logo e sim, mas o arquivo do logo nao foi gravado")
    if cad.get("tem_fotos") not in ("sim", "nao"):
        falha("sem resposta: tem_fotos precisa ser sim ou nao")
    elif cad["tem_fotos"] == "sim" and not cad.get("fotos"):
        falha("tem_fotos e sim, mas nenhuma foto foi registrada")
    for f in cad.get("fotos") or []:
        if not (ROOT / f["arquivo"]).is_file():
            falha(f"foto registrada nao existe: {f['arquivo']}")
        if not f["descricao"]:
            falha(f"foto sem descricao: {f['arquivo']}")
    if cad.get("escolha_capa") not in ("usuario", "automatica"):
        falha("sem resposta: escolha_capa precisa ser usuario ou automatica")
    validas = ("pedida", "manual", "nao") if a.rascunho else ("criada", "manual", "nao")
    if cad.get("rotina") == "pedida" and not a.rascunho:
        falha("a rotina foi pedida no cadastro e nao foi criada: crie a rotina, ou grave rotina = manual")
    elif cad.get("rotina") not in validas:
        falha("falta decidir a rotina: " + ", ".join(validas))
    elif cad["rotina"] == "criada" and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", cad.get("rotina_horario") or ""):
        falha("rotina criada sem horario registrado (rotina_horario, formato HH:MM)")
    if cad.get("perfil_tipo") not in ("pessoa", "negocio", "misto"):
        falha("sem resposta: perfil_tipo precisa ser pessoa, negocio ou misto")
    elif cad["perfil_tipo"] == "negocio" and cad.get("tem_logo") != "sim":
        aviso("perfil do negocio sem logo: o topo dos slides usa a marca de texto com as iniciais. Mande o logo quando tiver.")
    if cad.get("regulado") not in ("sim", "nao"):
        falha("sem resposta: regulado precisa ser sim ou nao")
    elif cad["regulado"] == "sim":
        for campo, o_que in (("orgao", "o orgao ou conselho"), ("registro_profissional", "o numero de registro"),
                             ("especialidade", "a area ou especialidade"), ("restricao_norma", "o nome da norma"),
                             ("restricao_fonte", "a fonte da norma"), ("restricao_consultada_em", "a data da consulta")):
            if not cad.get(campo):
                falha(f"profissao regulada: falta {o_que} ({campo})")
        regras = cad.get("restricoes") or []
        if len(regras) < 3 or not any(r["tipo"] == "PROIBIDO" for r in regras):
            falha("profissao regulada: registre as restricoes (pelo menos 3, com ao menos uma do tipo PROIBIDO)")
        if any(r["tipo"] not in ("OBRIGATORIO", "PROIBIDO", "PERMITIDO") for r in regras):
            falha("restricao com tipo invalido: use OBRIGATORIO, PROIBIDO ou PERMITIDO")
        if not cad.get("termos_proibidos"):
            falha("profissao regulada: registre as expressoes vetadas (termo_proibido) para o guardiao conferir o texto")
        fonte = cad.get("restricao_fonte") or ""
        if fonte and not fonte.lower().startswith("http"):
            aviso("as restricoes legais foram informadas pelo usuario, sem norma oficial localizada: confirme com o conselho")
        try:
            dias = (datetime.date.today() - datetime.date.fromisoformat(cad.get("restricao_consultada_em") or "")).days
            if dias > 90:
                aviso(f"as restricoes legais foram consultadas ha {dias} dias: refaca a busca da norma")
        except ValueError:
            if cad.get("restricao_consultada_em"):
                falha("restricao_consultada_em precisa estar no formato AAAA-MM-DD")
    if cad.get("perfil_nome") and cad["perfil_nome"].lstrip("@").lower() == (cad.get("perfil_arroba") or "").lstrip("@").lower():
        falha("perfil_nome esta igual ao @: precisa ser o nome que aparece ao lado da foto")
    for campo in ("cor_fundo_escuro", "cor_fundo_claro", "cor_destaque"):
        v = cad.get(campo) or ""
        if v and not re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
            falha(f"{campo} precisa ser hexadecimal de 6 digitos (ex.: #111111), veio: {v}")
    n = cad.get("posts_por_dia") or 0
    if cad.get("posts_por_dia") is not None and n < 1:
        falha("posts_por_dia precisa ser pelo menos 1")
    if n and len(cad.get("horarios") or []) != n:
        falha(f"posts_por_dia e {n}, mas ha {len(cad.get('horarios') or [])} horario(s)")
    for h in cad.get("horarios") or []:
        if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", h):
            falha(f"horario invalido: {h} (use HH:MM)")
    sm = cad.get("slides_max")
    if sm is not None and not 4 <= sm <= 10:
        falha("slides_max precisa ficar entre 4 e 10 (o padrao e 10)")
    if cad.get("coleta_modo") not in ("apify", "navegador"):
        falha("coleta_modo precisa ser apify ou navegador")
    if cad.get("metrica") not in ("views", "comentarios", "ambos"):
        falha("metrica precisa ser views, comentarios ou ambos")
    if cad.get("publicacao_modo") not in ("metricool", "manual"):
        falha("publicacao_modo precisa ser metricool ou manual")
    if cad.get("publicacao_aprovacao") not in ("direto", "rascunho"):
        falha("publicacao_aprovacao precisa ser direto ou rascunho")
    if cad.get("isca_palavra") and len(cad["isca_palavra"].split()) != 1:
        falha("isca_palavra precisa ser uma palavra so")

    if cad.get("coleta_modo") == "apify" and not env.get("APIFY_TOKEN"):
        if a.rascunho:  # a chave e colada na instalacao, depois de gravar o cadastro
            aviso("coleta pela Apify: a chave sera pedida na instalacao (linha APIFY_TOKEN= do arquivo .env)")
        else:
            falha("coleta_modo e apify, mas falta APIFY_TOKEN no .env")
    if cad.get("coleta_modo") == "navegador":
        aviso("coleta pelo navegador: precisa do Instagram logado no navegador do Claude e do computador ligado na hora da rotina")
    conc = cad.get("concorrentes") or []
    if len(conc) > 5:
        aviso(f"{len(conc)} concorrentes: acima de 5 a coleta fica mais cara e mais lenta")
    if cad.get("publicacao_modo") == "metricool" and not cad.get("metricool_blog_id"):
        falha("sem resposta: publicacao pelo Metricool exige metricool_blog_id")
    if cad.get("publicacao_modo") == "metricool" and modo_publicacao(cad, env) == "manual":
        faltam = [k for k in R2 if not env.get(k)]
        if not cad.get("metricool_blog_id"):
            faltam.append("metricool_blog_id (cadastro)")
        aviso("publicacao pedida no Metricool, mas falta " + ", ".join(faltam) + ": os posts serao entregues em entrega/ para postagem manual")
    print("MODO_PUBLICACAO " + modo_publicacao(cad, env))
    print("AUTOMACAO " + nivel_de_automacao(cad, env))


# ---------------------------------------------------------------- pesquisa
def g_pesquisa(a):
    fila = carregar_json(TRABALHO / "fila.json", [])
    modelados = {m["id"] for m in carregar_json(TRABALHO / "modelados.json", [])}
    prontos = []
    for post in fila:
        pid = post.get("id")
        if pid in modelados:
            falha(f"post {pid} esta na fila e ja foi modelado")
            continue
        problemas = []
        if not (post.get("transcricao") or "").strip():
            problemas.append("sem transcricao")
        if not ((post.get("analise") or {}).get("gancho") or "").strip():
            problemas.append("sem analise de gancho")
        if not ((post.get("analise") or {}).get("rehook") or "").strip():
            problemas.append("sem analise de rehook")
        an = post.get("analise") or {}
        if not (an.get("tema_central") or "").strip():
            problemas.append("sem tema_central")
        if len(an.get("termos_centrais") or []) < 6:
            problemas.append("menos de 6 termos_centrais")
        if not isinstance(an.get("nomes_conferidos"), list):
            problemas.append("nomes de ferramentas e marcas nao conferidos (nomes_conferidos)")
        if an.get("gancho_categoria") not in CATEGORIAS:
            problemas.append("sem gancho_categoria (" + ", ".join(CATEGORIAS) + ")")
        if post.get("tipo") in ("carrossel", "imagem") and post.get("imagens_locais"):
            if an.get("criativo_tipo") not in list(TIPOS) + ["texto"]:
                problemas.append("carrossel sem criativo_tipo (o tipo da capa da referencia)")
            if post.get("tipo") == "carrossel" and not an.get("criativo_slides"):
                problemas.append("carrossel sem criativo_slides (o layout de cada slide da referencia)")
        if not (post.get("idioma") or "").strip():
            problemas.append("sem o idioma do post")
        elif post["idioma"][:2] != "pt" and not (post.get("transcricao_pt") or "").strip():
            problemas.append(f"post em {post.get('idioma')} sem traducao (transcricao_pt)")
        if not (post.get("url") or "").startswith("http"):
            problemas.append("sem a URL do post")
        if problemas:
            aviso(f"post {pid} fora de uso: " + ", ".join(problemas))
        else:
            prontos.append(pid)
    if len(prontos) < a.n:
        falha(f"a fila tem {len(prontos)} post(s) pronto(s) para modelar, a rodada precisa de {a.n}")
    print(f"PRONTOS {len(prontos)}")


# ---------------------------------------------------------------- capas
def checar_layout(pasta):
    """Roda checar_slides.js numa pasta com carrossel.html; devolve a lista de problemas."""
    r = subprocess.run(["node", str(ROOT / "scripts" / "checar_slides.js"), str(pasta)],
                       capture_output=True, text=True, cwd=str(ROOT), shell=False)
    saida = [l[6:] for l in (r.stdout + r.stderr).splitlines() if l.startswith("FALHA ")]
    if r.returncode == 2:
        saida.append("nao foi possivel conferir o layout: " + (r.stderr.strip() or r.stdout.strip())[:200])
    return saida


CATEGORIAS = ("tela", "numero", "comparacao", "citacao", "pessoa", "conceito")
# referencia em video: o tipo de capa sai do que o hook faz. Primeiro item = opcao A.
TABELA_VIDEO = {
    "tela": (["print", "objeto"], ["card", "dividida"]),
    "numero": (["numero"], ["objeto", "card"]),
    "comparacao": (["dividida"], ["card", "objeto"]),
    "citacao": (["card"], ["print", "simbolo"]),
    "pessoa": (["foto", "recorte", "simbolo"], ["card", "objeto"]),
    "conceito": (["simbolo"], ["objeto", "card"]),
}
SEM_FOTO = {"recorte": ["objeto"], "foto": ["card", "print"]}   # referencia com pessoa, cadastro sem foto
LAYOUTS = ("padrao", "imagem-topo", "lado", "destaque", "cheia")


def ultimas_capas(quantas=2):
    """Tipos de capa dos ultimos carrosseis publicados."""
    pecas = sorted((e for e in (ROOT / "conteudo").glob("*/escolha.json") if (e.parent / "publicacao.json").exists()),
                   key=lambda e: e.stat().st_mtime, reverse=True)
    return [carregar_json(e, {}).get("tipo") for e in pecas[:quantas]]


def tipos_permitidos(fonte, cad):
    """Para um post de referencia: (tipos aceitos na opcao A, alternativas aceitas em B e C, explicacao)."""
    an = fonte.get("analise") or {}
    tem_foto = bool(cad.get("fotos")) and cad.get("perfil_tipo") in ("pessoa", "misto")
    if fonte.get("tipo") in ("carrossel", "imagem") and an.get("criativo_tipo") in TIPOS:
        ref = an["criativo_tipo"]
        if ref in SEM_FOTO and not tem_foto:
            return SEM_FOTO[ref], [t for t in TIPOS if t not in ("foto", "recorte")], f"a referencia e {ref}, sem foto no cadastro"
        return [ref], [t for t in TIPOS if tem_foto or t not in ("foto", "recorte")], f"a capa da referencia e do tipo {ref}"
    cat = an.get("gancho_categoria")
    if cat not in TABELA_VIDEO:
        return None, None, "a referencia nao tem gancho_categoria"
    primeira, alternativas = TABELA_VIDEO[cat]
    if not tem_foto:
        primeira = [t for t in primeira if t not in ("foto", "recorte")] or ["simbolo"]
    return primeira, primeira + alternativas, f"hook da categoria {cat}"


def post_pronto(x):
    an = x.get("analise") or {}
    return bool((x.get("transcricao") or "").strip() and (an.get("gancho") or "").strip() and (an.get("rehook") or "").strip()
                and (an.get("tema_central") or "").strip() and len(an.get("termos_centrais") or []) >= 6
                and isinstance(an.get("nomes_conferidos"), list)
                and an.get("gancho_categoria") in CATEGORIAS
                and (x.get("idioma") or "").strip()
                and (x["idioma"][:2] == "pt" or (x.get("transcricao_pt") or "").strip())
                and (x.get("url") or "").startswith("http"))


def g_capas(_a):
    from PIL import Image

    cad = ler()
    p = pasta_selecao()
    if not p:
        falha("nao existe selecao de capas (conteudo/_selecao/<data>/selecao.json)")
        return
    sel = carregar_selecao(p)
    if sel.get("status") not in ("em_montagem", "aguardando_escolha"):
        falha(f"a selecao mais recente ({sel.get('data')}) esta com status {sel.get('status')!r}: nao ha capas em montagem para conferir")
        return
    if str(sel.get("data")) != p.name:
        falha(f"o campo data da selecao ({sel.get('data')}) precisa ser igual ao nome da pasta ({p.name})")
    fila = carregar_json(TRABALHO / "fila.json", [])
    na_fila = {str(x.get("id")) for x in fila}
    prontos = sum(1 for x in fila if post_pronto(x))
    hooks = sel.get("hooks") or []
    retirados = sel.get("retirados") or []
    for r in retirados:
        if len(str(r.get("motivo") or "")) < 10:
            falha("hook retirado da selecao sem motivo registrado")
        if str(r.get("fonte_id")) in {str(h.get("fonte_id")) for h in hooks}:
            falha(f"o post {r.get('fonte_id')} foi retirado da selecao mas continua entre os hooks")
        aviso(f"hook retirado da selecao: {r.get('motivo')}")
    # o post retirado continua na fila (e conta em 'prontos'): a selecao fica menor na mesma medida, com minimo de 1
    esperado = max(1, min(5, prontos) - len(retirados)) if prontos else 0
    if len(hooks) != esperado:
        falha(f"a selecao tem {len(hooks)} hook(s); com {prontos} post(s) pronto(s) na fila, precisa ter {esperado}")
    if esperado < 5:
        aviso(f"so ha {prontos} post(s) pronto(s) na fila: a selecao sai com {esperado} hook(s), nao 5")
    fontes = [str(h.get("fonte_id")) for h in hooks]
    if len(set(fontes)) != len(fontes):
        falha("dois hooks da selecao vem do mesmo post")
    por_id = {str(x.get("id")): x for x in fila}
    # equilibrio entre concorrentes: no maximo 2 hooks do mesmo perfil enquanto houver post pronto de outro
    usados = {}
    for h in hooks:
        usados[h.get("perfil")] = usados.get(h.get("perfil"), 0) + 1
    escolhidos = set(fontes)
    sobrando = {x.get("perfil") for x in fila if str(x.get("id")) not in escolhidos and post_pronto(x)}
    for perfil, qtd in usados.items():
        if qtd > 2 and (sobrando - {perfil}):
            falha(f"{qtd} hooks vem de {perfil}: o limite e 2 por perfil enquanto houver post pronto de outro concorrente")
    # variedade: nenhum tipo de capa em mais de 3 hooks, nenhuma foto repetida em mais de 2 opcoes
    por_tipo, por_foto = {}, {}
    for h in hooks:
        for t in {o.get("tipo") for o in h.get("opcoes") or []}:
            por_tipo[t] = por_tipo.get(t, 0) + 1
        for o in h.get("opcoes") or []:
            if o.get("origem_imagem") == "foto":
                if not o.get("foto_arquivo"):
                    falha(f"opcao {h.get('n')}{o.get('letra')}: diga em foto_arquivo qual foto do cadastro foi usada")
                else:
                    por_foto[o["foto_arquivo"]] = por_foto.get(o["foto_arquivo"], 0) + 1
    if len(hooks) >= 4:
        for t, qtd in por_tipo.items():
            if qtd > 3:
                falha(f"o tipo de capa {t} aparece em {qtd} hooks: o limite e 3, para as opcoes nao ficarem iguais")
    for f, qtd in por_foto.items():
        if qtd > 2:
            falha(f"a foto {f} aparece em {qtd} capas: o limite e 2")
    arroba = cad.get("perfil_arroba") or ""
    for h in hooks:
        n = h.get("n")
        if str(h.get("fonte_id")) not in na_fila:
            falha(f"hook {n}: o post de origem nao esta na fila")
        fonte = por_id.get(str(h.get("fonte_id")), {})
        if fonte.get("url") and h.get("url") != fonte.get("url"):
            falha(f"hook {n}: a url nao e a do post de origem ({fonte.get('url')})")
        for campo in ("tema", "mantido", "mudou"):
            if len(str(h.get(campo) or "").strip()) < 15:
                falha(f"hook {n}: falta {campo} (o tema do carrossel, o que foi mantido da referencia e o que mudou)")
        aceitos_a, aceitos_bc, porque = tipos_permitidos(fonte, cad)
        ops_h = h.get("opcoes") or []
        if aceitos_a is None:
            falha(f"hook {n}: {porque}; sem isso nao ha criterio para o tipo de capa")
        elif ops_h:
            tipo_a = ops_h[0].get("tipo")
            repetidos = [t for t in ultimas_capas() if t]
            exige = fonte.get("tipo") in ("carrossel", "imagem")
            if tipo_a not in aceitos_a and not (tipo_a in aceitos_bc and not exige and all(t in repetidos for t in aceitos_a)):
                falha(f"hook {n}: a opcao A e do tipo {tipo_a}, mas {porque}: precisa ser {' ou '.join(aceitos_a)}")
            for o in ops_h[1:]:
                if o.get("tipo") not in aceitos_bc:
                    falha(f"hook {n}: a opcao {o.get('letra')} ({o.get('tipo')}) nao esta entre as alternativas para {porque}: {', '.join(t for t in aceitos_bc if t != tipo_a)}")
            if not exige and tipo_a in repetidos and len(aceitos_a) > 1:
                aviso(f"hook {n}: a opcao A repete o tipo de capa de um dos 2 ultimos carrosseis publicados ({tipo_a})")
        if not isinstance(h.get("criterio_capa"), dict) or len(str((h.get("criterio_capa") or {}).get("regra") or "")) < 12:
            falha(f"hook {n}: falta criterio_capa, dizendo por que a opcao A e desse tipo")
        termos = termos_da_fonte(fonte, cad)
        if termos:
            rad = radicais(f"{h.get('hook')} {h.get('rehook')} {h.get('tema')}")
            presentes = [t for t in termos if tem_termo(t, rad)]
            if len(presentes) < 2:
                falha(f"hook {n}: mudou de assunto. Hook, rehook e tema precisam trazer ao menos 2 termos centrais "
                      f"da referencia ({', '.join(termos[:8])})")
        for campo in ("hook", "hook_original", "rehook", "perfil", "url", "motivo"):
            if not str(h.get(campo) or "").strip():
                falha(f"hook {n}: falta {campo}")
        checar_restricoes(" ".join([str(h.get("hook")), str(h.get("rehook")), str(h.get("tema"))]
                                   + [str(o.get("imagem")) for o in h.get("opcoes") or []]), cad, f"hook {n} (texto ou descricao das capas)")
        orig = h.get("origem") or {}
        if not str(orig.get("criterio") or orig.get("motivo") or "").strip():
            falha(f"hook {n}: o relatorio nao diz por que o post foi escolhido (rode selecao.py relatorio depois de completar a fila)")
        ops = h.get("opcoes") or []
        if [o.get("letra") for o in ops] != ["A", "B", "C"]:
            falha(f"hook {n}: precisa de exatamente 3 opcoes, A, B e C")
        tipos = [o.get("tipo") for o in ops]
        if len(set(tipos)) != len(tipos):
            falha(f"hook {n}: as 3 opcoes precisam ser de tipos de capa diferentes (vieram {tipos})")
        for o in ops:
            cod = f"{n}{o.get('letra')}"
            if o.get("tipo") not in TIPOS:
                falha(f"opcao {cod}: tipo de capa invalido ({o.get('tipo')}). Validos: {', '.join(TIPOS)}")
            if o.get("origem_imagem") not in ("foto", "print", "ilustracao", "ia"):
                falha(f"opcao {cod}: origem_imagem precisa ser foto, print, ilustracao ou ia")
            if len(str(o.get("imagem") or "")) < 25:
                falha(f"opcao {cod}: descreva em 'imagem' o que aparece e por que tem a ver com o hook")
            png = p / str(o.get("arquivo") or "")
            if not png.is_file():
                falha(f"opcao {cod}: capa nao encontrada ({o.get('arquivo')})")
                continue
            if png.stat().st_size < 50_000:
                falha(f"opcao {cod}: capa com menos de 50 KB")
            with Image.open(png) as im:
                if im.size != (2160, 2700):
                    falha(f"opcao {cod}: capa com {im.size[0]}x{im.size[1]}, esperado 2160x2700")
            html = png.parent / "carrossel.html"
            if not html.is_file():
                falha(f"opcao {cod}: falta carrossel.html ao lado da capa")
                continue
            texto = html.read_text(encoding="utf-8")
            m = re.search(r"<section[^>]*class=\"([^\"]*\bslide\b[^\"]*)\"", texto)
            classes = (m.group(1) if m else "").split()
            if "capa" not in classes or o.get("tipo") not in classes:
                falha(f"opcao {cod}: a <section> precisa ter as classes capa e {o.get('tipo')}")
            if arroba not in texto or 'class="identidade"' not in texto:
                falha(f"opcao {cod}: falta avatar, nome e {arroba} no topo")
            for prob in checar_layout(png.parent):
                falha(f"opcao {cod}: {prob}")
    if not (p / "relatorio.html").is_file():
        falha("falta relatorio.html (rode: python scripts/selecao.py relatorio)")
    else:
        rel = (p / "relatorio.html").read_text(encoding="utf-8")
        for h in hooks:
            if str(h.get("url") or "") not in rel or not h.get("url"):
                falha(f"o relatorio nao mostra a URL do post de referencia do hook {h.get('n')}")
            if "Por que entrou" not in rel:
                falha("o relatorio nao explica por que cada post foi escolhido (refaca: python scripts/selecao.py relatorio)")
            if not (p / f"cartao-hook-{h.get('n')}.jpg").is_file():
                falha(f"falta o cartao em imagem do hook {h.get('n')} (refaca: python scripts/selecao.py relatorio)")
            for o in h.get("opcoes") or []:
                if str(o.get("arquivo")) not in rel:
                    falha(f"o relatorio nao mostra a opcao {h.get('n')}{o.get('letra')}")
    print(f"SELECAO {sel.get('data')} {len(hooks)} hooks")


# ---------------------------------------------------------------- escolha
def ler_escolha(peca):
    """Confere que a peca nasceu de uma escolha registrada. Devolve o registro ou None."""
    esc = carregar_json(pathlib.Path(peca) / "escolha.json", None)
    if not esc:
        falha("falta escolha.json na peca: nenhum carrossel e produzido sem passar pela escolha de capa")
        return None
    p = pasta_selecao(esc.get("data"))
    if not p:
        falha(f"a selecao de {esc.get('data')} nao existe")
        return None
    sel = carregar_selecao(p)
    if sel.get("status") not in ("escolhido", "produzido"):
        falha(f"a selecao esta com status {sel.get('status')!r}: ainda nao houve escolha")
        return None
    ok = next((e for e in sel.get("escolhas") or []
               if str(e["n"]) == str(esc.get("n")) and e["letra"] == esc.get("letra") and str(e["fonte_id"]) == str(esc.get("fonte_id"))), None)
    if not ok:
        falha(f"a opcao {esc.get('n')}{esc.get('letra')} nao esta entre as escolhidas na selecao")
        return None
    hook = next((h for h in sel.get("hooks") or [] if str(h.get("n")) == str(esc.get("n"))), {})
    for campo in ("hook", "rehook"):
        if sem_acento(esc.get(campo)) != sem_acento(hook.get(campo)):
            falha(f"o {campo} em escolha.json nao e o da selecao: copie sem mudar")
    return dict(ok, hook=hook.get("hook"), rehook=hook.get("rehook"))


def g_escolha(a):
    esc = ler_escolha(a.peca)
    fonte = carregar_json(pathlib.Path(a.peca) / "fonte.json", {})
    if esc and str(fonte.get("id")) != str(esc["fonte_id"]):
        falha("fonte.json da peca nao e o post do hook escolhido")


# ---------------------------------------------------------------- copy
def ler_roteiro(caminho):
    texto = pathlib.Path(caminho).read_text(encoding="utf-8")
    front = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", texto, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                front[k.strip()] = v.strip().strip('"')
        texto = texto[m.end():]
    slides = []
    for bloco in re.split(r"^## Slide \d+\s*$", texto, flags=re.M)[1:]:
        campos, atual = {}, None
        for linha in bloco.splitlines():
            mm = re.match(r"^([a-z_]+):\s*(.*)$", linha)
            if mm:
                atual = mm.group(1)
                campos[atual] = mm.group(2).strip().strip('"|').strip()
            elif atual and linha.strip():
                campos[atual] = (campos[atual] + " " + linha.strip()).strip()
        slides.append(campos)
    return front, slides


def texto_do_slide(s):
    return " ".join(v for k, v in s.items() if k not in ("parte", "layout", "imagem", "tipo", "url", "slot", "credito"))


def palavras(t):
    return re.findall(r"[a-zà-ÿ0-9]+", (t or "").lower())


def ngramas(t, n=5):
    p = palavras(t)
    return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}


def g_copy(a):
    cad = ler()
    peca = pathlib.Path(a.peca)
    for nome in ("fonte.json", "roteiro.md", "legenda.txt"):
        if not (peca / nome).is_file():
            falha(f"falta {nome} em {peca}")
    if falhas:
        return
    fonte = carregar_json(peca / "fonte.json", {})
    front, slides = ler_roteiro(peca / "roteiro.md")
    esc = ler_escolha(peca)
    if esc and slides and esc["tipo"] not in (slides[0].get("imagem") or ""):
        falha(f"o slide 1 do roteiro precisa seguir a capa escolhida (tipo {esc['tipo']})")
    if esc and len(slides) >= 2:
        if sem_acento(esc.get("hook")) not in sem_acento(texto_do_slide(slides[0])):
            falha("o slide 1 nao traz o hook escolhido, palavra por palavra")
        if sem_acento(esc.get("rehook")) not in sem_acento(texto_do_slide(slides[1])):
            falha("o slide 2 nao traz o rehook escolhido, palavra por palavra")
    for i, sl in enumerate(slides, 1):
        img = sl.get("imagem") or ""
        if "tipo:" not in img or "descricao:" not in img:
            falha(f"slide {i}: falta o bloco imagem com tipo e descricao (todo slide tem imagem e texto)")
    legenda = (peca / "legenda.txt").read_text(encoding="utf-8").strip()
    isca = (cad.get("isca_palavra") or "").lower()
    maximo = min(cad.get("slides_max") or 10, 10)

    if front.get("fonte_id") != str(fonte.get("id")):
        falha("fonte_id do roteiro nao bate com fonte.json")
    if not 4 <= len(slides) <= maximo:
        falha(f"{len(slides)} slides: precisa ficar entre 4 e {maximo}")
    if slides:
        if slides[0].get("parte") != "capa":
            falha("o slide 1 precisa ser da parte capa")
        if slides[-1].get("parte") != "cta":
            falha("o ultimo slide precisa ser da parte cta")
        for i, s in enumerate(slides, 1):
            if s.get("parte") not in ("capa", "conteudo", "cta"):
                falha(f"slide {i}: parte ausente ou invalida (capa, conteudo ou cta)")
            if not texto_do_slide(s).strip():
                falha(f"slide {i}: sem texto")
        if isca and isca not in texto_do_slide(slides[-1]).lower():
            falha(f"o slide de CTA nao traz a palavra da isca ({cad['isca_palavra']})")

    tudo = " ".join(texto_do_slide(s) for s in slides) + " " + legenda
    if re.search(r"[—–]", tudo):
        falha("ha travessao longo no texto (trocar por ponto, virgula ou dois-pontos)")
    if "[PREENCHER" in tudo or re.search(r"\[[A-ZÇÃÕ ]{4,}\]", tudo):
        falha("sobrou marcador entre colchetes no texto")

    primeira = legenda.splitlines()[0].lower() if legenda else ""
    if isca and isca not in primeira:
        falha("a primeira linha da legenda nao traz a palavra da isca")
    if "**" in legenda:
        falha("a legenda tem asteriscos de negrito, que o Instagram mostra como texto")
    if not 300 <= len(legenda) <= 2200:
        falha(f"legenda com {len(legenda)} caracteres: precisa ficar entre 300 e 2200")

    miolo = [sl for sl in slides if sl.get("parte") == "conteudo"]
    layouts = [(sl.get("layout") or "").strip() for sl in miolo]
    for i, lay in enumerate(layouts, 2):
        if lay not in LAYOUTS:
            falha(f"slide {i}: falta o layout ({', '.join(LAYOUTS)})")
    if len(layouts) >= 3 and all(l in LAYOUTS for l in layouts):
        if len(set(layouts)) < 2:
            falha("todos os slides de conteudo usam o mesmo layout: use pelo menos 2 diferentes")
        for i in range(len(layouts) - 2):
            if layouts[i] == layouts[i + 1] == layouts[i + 2]:
                falha(f"o layout {layouts[i]} se repete 3 vezes seguidas a partir do slide {i + 2}")
                break
    ref = [l for l in ((fonte.get("analise") or {}).get("criativo_slides") or [])]
    if fonte.get("tipo") == "carrossel" and ref and all(l in LAYOUTS for l in layouts):
        esperado = ["padrao" if l == "texto" else l for l in ref][:len(layouts)]
        iguais = sum(1 for a_, b_ in zip(layouts, esperado) if a_ == b_)
        if esperado and iguais / len(esperado) < 0.6:
            falha(f"o layout dos slides nao segue a referencia: so {iguais} de {len(esperado)} batem. Referencia: {', '.join(esperado)}")
    checar_restricoes(tudo, cad, "texto do carrossel ou legenda")
    checar_restricoes(" ".join(sl.get("imagem") or "" for sl in slides), cad, "descricao das imagens")
    checar_registro(legenda, cad, "legenda")
    if slides:
        checar_registro(texto_do_slide(slides[-1]), cad, "ultimo slide")

    concorrente = (fonte.get("perfil") or "").lstrip("@").lower()
    if concorrente and re.search(r"(?<![a-z0-9_.])@?" + re.escape(concorrente) + r"(?![a-z0-9_.])", tudo.lower()):
        falha(f"o texto cita o perfil de origem ({concorrente})")

    # semelhanca com a fonte: o miolo nao pode ser copia. Hook e rehook (slides 1 e 2) ficam fora da conta.
    origem = ngramas(" ".join([fonte.get("transcricao") or "", fonte.get("transcricao_pt") or "", fonte.get("legenda") or ""]))
    miolo = ngramas(" ".join(texto_do_slide(s) for s in slides[2:]))
    if origem and miolo:
        taxa = len(miolo & origem) / len(miolo)
        print(f"SEMELHANCA_MIOLO {taxa:.0%}")
        if taxa > 0.20:
            falha(f"{taxa:.0%} do miolo repete trechos da fonte palavra por palavra (limite 20%)")
    taxa_fid, faltam = fidelidade(" ".join(texto_do_slide(s) for s in slides), fonte, cad)
    if taxa_fid is not None:
        print(f"FIDELIDADE_AO_TEMA {taxa_fid:.0%}")
        if taxa_fid < 0.60:
            falha(f"o carrossel se afastou da referencia: so {taxa_fid:.0%} dos termos centrais aparecem (minimo 60%). "
                  f"Faltam: {', '.join(faltam)}")
    capa_legenda = ngramas(legenda) & ngramas(fonte.get("legenda") or "")
    if len(capa_legenda) > 3:
        falha("a legenda repete trechos da legenda do post de origem")


# ---------------------------------------------------------------- design
def ultima_versao(peca):
    vs = sorted((p for p in pathlib.Path(peca).glob("v*") if p.is_dir() and p.name[1:].isdigit()),
                key=lambda p: int(p.name[1:]))
    return vs[-1] if vs else None


def g_design(a):
    from PIL import Image

    cad = ler()
    peca = pathlib.Path(a.peca)
    v = ultima_versao(peca)
    if not v or not (v / "carrossel.html").is_file():
        falha(f"nao ha vN/carrossel.html em {peca}")
        return
    _, slides = ler_roteiro(peca / "roteiro.md")
    html = (v / "carrossel.html").read_text(encoding="utf-8")
    secoes = len(re.findall(r"<section[^>]*class=\"[^\"]*\bslide\b", html))
    if secoes != len(slides):
        falha(f"o roteiro tem {len(slides)} slides e o HTML tem {secoes}")
    pngs = sorted(v.glob("slide-*.png"))
    if len(pngs) != len(slides):
        falha(f"esperados {len(slides)} PNGs, encontrados {len(pngs)}")
    for p in pngs:
        if p.stat().st_size < 50_000:
            falha(f"{p.name} com menos de 50 KB (slide vazio ou fonte nao carregou)")
        with Image.open(p) as im:
            if im.size != (2160, 2700):
                falha(f"{p.name} com {im.size[0]}x{im.size[1]}, esperado 2160x2700")
    arroba = cad.get("perfil_arroba") or ""
    if html.count(arroba) < len(slides):
        falha(f"o {arroba} nao aparece em todos os slides")
    if html.count('class="identidade"') < len(slides):
        falha("falta o bloco de identidade (avatar, nome e @) em algum slide")
    if not (v / "imagens" / "avatar.jpg").is_file():
        falha("falta vN/imagens/avatar.jpg")
    for cor in ("cor_fundo_escuro", "cor_fundo_claro", "cor_destaque"):
        css = "".join(p.read_text(encoding="utf-8") for p in v.glob("*.css"))
        if (cad.get(cor) or "").lower() not in css.lower():
            falha(f"a {cor} do cadastro ({cad.get(cor)}) nao esta no CSS da peca")
    if re.search(r"font-style:\s*italic", html):
        falha("ha italico no HTML")
    visivel = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", html, flags=re.S)
    visivel = re.sub(r"<[^>]+>", " ", visivel)
    checar_restricoes(visivel, cad, "texto dos slides")
    checar_registro(visivel, cad, "slides")
    secoes_html = re.findall(r"<section[^>]*class=\"([^\"]*\bslide\b[^\"]*)\"", html)
    for i, (sl, classes) in enumerate(zip(slides, secoes_html), 1):
        lay = (sl.get("layout") or "").strip()
        if sl.get("parte") == "conteudo" and lay in LAYOUTS:
            usados = [l for l in LAYOUTS[1:] if l in classes.split()]
            if (lay == "padrao" and usados) or (lay != "padrao" and usados != [lay]):
                falha(f"slide {i}: o roteiro pede o layout {lay} e o HTML usa {usados[0] if usados else 'padrao'}")
    if cad.get("perfil_tipo") == "misto" and cad.get("tem_logo") == "sim":
        ultimo = html[html.rfind("<section"):]
        if "logo" not in ultimo.lower():
            falha("perfil misto: o logo precisa aparecer, discreto, no ultimo slide (imagem com 'logo' no nome do arquivo)")
    esc = ler_escolha(peca)
    if esc:
        m = re.search(r"<section[^>]*class=\"([^\"]*\bslide\b[^\"]*)\"", html)
        if esc["tipo"] not in (m.group(1) if m else "").split():
            falha(f"a capa nao segue a opcao escolhida: a primeira <section> precisa ter a classe {esc['tipo']}")
    for prob in checar_layout(v):
        falha(prob)


# ---------------------------------------------------------------- publicacao
def g_publicacao(a):
    from PIL import Image

    cad, env = ler(), ler_env()
    peca = pathlib.Path(a.peca)
    _, slides = ler_roteiro(peca / "roteiro.md")
    modo = modo_publicacao(cad, env)
    registro = carregar_json(peca / "publicacao.json", {})
    if modo == "metricool" and registro.get("modo") == "manual" and len(str(registro.get("motivo_fallback") or "")) > 10:
        aviso("entregue para postagem manual porque o Metricool falhou: " + registro["motivo_fallback"])
        modo = "manual"
    if registro.get("modo") != modo:
        falha(f"publicacao.json diz modo {registro.get('modo')!r}, o cadastro pede {modo!r}")

    fonte = carregar_json(peca / "fonte.json", {})
    url_ref = fonte.get("url") or ""
    if registro.get("fonte_url") != url_ref or not url_ref:
        falha("publicacao.json precisa trazer em fonte_url a URL do post de referencia")
    versao = ultima_versao(peca)
    if not versao:
        falha(f"nao ha pasta vN em {peca}")
        return
    pasta = ROOT / "entrega" / peca.name if modo == "manual" else versao / "upload"
    jpgs = sorted(pasta.glob("slide-*.jpg")) if pasta.is_dir() else []
    if len(jpgs) != len(slides):
        falha(f"esperados {len(slides)} JPEGs em {pasta}, encontrados {len(jpgs)}")
    for j in jpgs:
        with Image.open(j) as im:
            if im.format != "JPEG" or im.size != (1080, 1350):
                falha(f"{j.name}: precisa ser JPEG 1080x1350, veio {im.format} {im.size[0]}x{im.size[1]}")

    if modo == "manual":
        if not (pasta / "legenda.txt").is_file():
            falha(f"falta legenda.txt em {pasta}")
        ref = pasta / "referencia.txt"
        if not ref.is_file() or url_ref not in ref.read_text(encoding="utf-8"):
            falha(f"falta referencia.txt com a URL do post de referencia em {pasta}")
        return

    urls = registro.get("urls") or []
    if len(urls) != len(jpgs):
        falha(f"{len(urls)} URL(s) registradas para {len(jpgs)} slide(s)")
    for url, j in zip(urls, jpgs):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as resp:
                tam = int(resp.headers.get("Content-Length") or 0)
                if resp.headers.get("Content-Type") != "image/jpeg":
                    falha(f"{j.name}: a URL nao devolve image/jpeg")
                if tam != j.stat().st_size:
                    falha(f"{j.name}: tamanho no ar ({tam}) diferente do local ({j.stat().st_size})")
        except Exception as e:
            falha(f"{j.name}: URL fora do ar ({e})")
    if not registro.get("metricool_id"):
        falha("publicacao.json sem metricool_id: o agendamento nao foi registrado")
    if not registro.get("horario"):
        falha("publicacao.json sem horario")
    esperado = cad.get("publicacao_aprovacao")
    if registro.get("aprovacao") != esperado:
        falha(f"o post foi agendado como {registro.get('aprovacao')!r}, o cadastro pede {esperado!r}")


MAX_CONFERENCIAS = 5   # por tentativa; com 3 tentativas, uma etapa nunca passa de 15 conferencias


def controle_de_tentativas(a):
    """Impede o laco em codigo. O guardiao so confere dentro de uma tentativa aberta (estado.py tentar),
    e cada tentativa aceita no maximo MAX_CONFERENCIAS conferencias. Devolve None para seguir, ou o codigo de saida."""
    import estado as est

    if a.etapa == "cadastro":
        return None
    if a.etapa == "pesquisa":
        peca = ""
    elif a.etapa == "capas":
        p = pasta_selecao()
        peca = p.name if p else ""
    else:
        peca = pathlib.Path(a.peca).name
    chave = a.etapa + (":" + peca if peca else "")
    comando = f"python scripts/estado.py tentar {a.etapa}" + (f" --peca {peca}" if peca else "")
    dados = est.carregar(peca)
    reg = dados["etapas"].get(chave)
    if not reg or reg.get("status") == "pendente":
        print(f"SEM_TENTATIVA {chave}: nenhuma tentativa aberta. Rode antes: {comando}")
        return 3
    if reg["status"] == "ok":
        return None   # reconferir uma etapa ja aprovada nao gasta tentativa
    if reg["status"] == "bloqueada" or (reg["status"] == "falhou" and reg["tentativas"] >= est.LIMITE):
        print(f"LIMITE {chave}: as {est.LIMITE} tentativas acabaram. PARAR esta etapa e avisar o usuario no relatorio.")
        return 3
    if reg["status"] == "falhou":
        print(f"TENTATIVA_ENCERRADA {chave}: a tentativa {reg['tentativas']} foi reprovada. Abra a proxima: {comando}")
        return 3
    reg["conferencias"] = reg.get("conferencias", 0) + 1
    if reg["conferencias"] > MAX_CONFERENCIAS:
        reg["status"] = "falhou"
        reg["motivos"].append(f"mais de {MAX_CONFERENCIAS} conferencias na tentativa {reg['tentativas']} sem aprovar")
        est.salvar(dados, peca)
        if reg["tentativas"] >= est.LIMITE:
            print(f"LIMITE {chave}: as {est.LIMITE} tentativas acabaram. PARAR esta etapa e avisar o usuario no relatorio.")
        else:
            print(f"TENTATIVA_ENCERRADA {chave}: {MAX_CONFERENCIAS} conferencias sem aprovar. Abra a proxima: {comando}")
        return 3
    est.salvar(dados, peca)
    print(f"TENTATIVA {reg['tentativas']} de {est.LIMITE} · conferencia {reg['conferencias']} de {MAX_CONFERENCIAS}")
    return None


ETAPAS = {"cadastro": g_cadastro, "pesquisa": g_pesquisa, "capas": g_capas, "escolha": g_escolha, "copy": g_copy, "design": g_design, "publicacao": g_publicacao}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("etapa", choices=ETAPAS)
    p.add_argument("--peca")
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--rascunho", action="store_true")
    a = p.parse_args()
    if a.etapa in ("escolha", "copy", "design", "publicacao") and not a.peca:
        p.error("--peca e obrigatorio nesta etapa")
    parar = controle_de_tentativas(a)
    if parar is not None:
        return parar
    try:
        ETAPAS[a.etapa](a)
    except FileNotFoundError as e:
        falha(f"arquivo nao encontrado: {e.filename}")
    for m in avisos:
        print("AVISO " + m)
    for m in falhas:
        print("FALHA " + m)
    print("REPROVADO" if falhas else "APROVADO")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
