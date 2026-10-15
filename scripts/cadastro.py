"""Le e grava o cadastro do perfil.

Durante o /instaflow novo as respostas vao para um RASCUNHO (contexto/cadastro-rascunho.md).
So depois da revisao geral e do OK do cliente o rascunho vira contexto/cadastro.md, que e o
unico arquivo que as outras etapas leem.

    python scripts/cadastro.py                              -> cadastro confirmado, em JSON
    python scripts/cadastro.py --rascunho                   -> rascunho em andamento, em JSON
    python scripts/cadastro.py novo                         -> abre um rascunho em branco, com os padroes
    python scripts/cadastro.py gravar <campo> "<valor>"     -> grava um campo no rascunho
    python scripts/cadastro.py foto "<arquivo>" "<o que e>" -> registra uma foto de uso no rascunho
    python scripts/cadastro.py restricao <TIPO> "<regra>"   -> TIPO: OBRIGATORIO | PROIBIDO | PERMITIDO
    python scripts/cadastro.py termo "<expressao>"          -> expressao que nunca pode aparecer no texto
    python scripts/cadastro.py confirmar                    -> o rascunho vira o cadastro (guarda o anterior)
    python scripts/cadastro.py corrigir <campo> "<valor>"   -> muda um campo do cadastro ja confirmado
"""
import datetime
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
CAMINHO = ROOT / "contexto" / "cadastro.md"
RASCUNHO = ROOT / "contexto" / "cadastro-rascunho.md"
PERFIL = ROOT / "assets" / "perfil"
PERFIL_RASCUNHO = PERFIL / "rascunho"   # imagens recebidas no cadastro ficam aqui ate o confirmar

LISTAS = {"horarios", "concorrentes"}
INTEIROS = {"posts_por_dia", "slides_max", "coleta_a_cada_dias", "periodo_dias"}
# Todo campo abaixo precisa de valor. Onde "nao tenho" e resposta valida, um campo sim/nao registra isso.
OBRIGATORIOS = [
    "perfil_tipo", "perfil_arroba", "perfil_nome", "avatar",
    "tem_logo", "cor_fundo_escuro", "cor_fundo_claro", "cor_destaque", "fonte_titulo", "fonte_texto", "tem_fotos",
    "nicho", "publico", "produto", "tom_de_voz",
    "regulado", "proibido",
    "isca_palavra", "isca_entrega", "posts_por_dia", "horarios",
    "concorrentes", "coleta_modo",
    "escolha_capa", "publicacao_modo", "publicacao_aprovacao", "rotina",
    "idioma", "fuso", "slides_max", "metrica", "coleta_a_cada_dias", "periodo_dias",
]
CAMPOS = OBRIGATORIOS + ["logo", "metricool_blog_id", "orgao", "registro_profissional", "especialidade",
                         "restricao_norma", "restricao_fonte", "restricao_consultada_em", "rotina_horario"]
# Nao sao perguntados: o agente grava o padrao e mostra na revisao geral.
PADROES = {"idioma": "portugues", "fuso": "America/Sao_Paulo", "slides_max": "10", "metrica": "ambos",
           "coleta_a_cada_dias": "7", "periodo_dias": "15"}
TIPOS_RESTRICAO = ("OBRIGATORIO", "PROIBIDO", "PERMITIDO")
R2 = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET", "R2_PUBLIC_BASE"]

MODELO = """# Cadastro

Escrito pelo agente no `/instaflow novo`, depois da sua revisao. E a unica fonte de verdade do perfil: toda etapa rele este arquivo antes de agir.

Para corrigir um valor, peca ao agente ou escreva depois dos dois-pontos, na mesma linha, sem mudar o nome do campo.

## 1. Perfil

perfil_tipo:
perfil_arroba:
perfil_nome:
avatar:

## 2. Marca

tem_logo:
logo:
cor_fundo_escuro:
cor_fundo_claro:
cor_destaque:
fonte_titulo:
fonte_texto:
tem_fotos:

## 3. Negocio

nicho:
publico:
produto:
tom_de_voz:

## 4. Regras do que pode e nao pode

regulado:
orgao:
registro_profissional:
especialidade:
restricao_norma:
restricao_fonte:
restricao_consultada_em:
proibido:

## 5. Posts

isca_palavra:
isca_entrega:
posts_por_dia:
horarios:

## 6. Concorrentes

concorrentes:
coleta_modo:

## 7. Automacao

escolha_capa:
publicacao_modo:
publicacao_aprovacao:
metricool_blog_id:
rotina:
rotina_horario:

## 8. Padroes (nao perguntados)

idioma:
fuso:
slides_max:
metrica:
coleta_a_cada_dias:
periodo_dias:

## Restricoes legais (inviolaveis)

Valem acima do tom de voz, do post de referencia e de qualquer outra regra. Texto e imagem.

## Fotos para usar nos posts

"""


def ler(caminho=CAMINHO):
    dados = {"fotos": [], "restricoes": [], "termos_proibidos": []}
    caminho = pathlib.Path(caminho)
    if not caminho.exists():
        return dados
    em_bloco = False
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.strip().startswith("```"):
            em_bloco = not em_bloco
            continue
        if em_bloco:
            continue
        m = re.match(r"^([a-z][a-z0-9_]*):[ \t]*(.*)$", linha)
        if not m:
            continue
        chave, valor = m.group(1), m.group(2).strip()
        if chave == "foto":
            arq, _, desc = valor.partition("|")
            if arq.strip():
                dados["fotos"].append({"arquivo": arq.strip(), "descricao": desc.strip()})
        elif chave == "restricao":
            tipo, _, regra = valor.partition("|")
            if regra.strip():
                dados["restricoes"].append({"tipo": tipo.strip().upper(), "regra": regra.strip()})
        elif chave == "termo_proibido":
            if valor:
                dados["termos_proibidos"].append(valor)
        elif chave in LISTAS:
            dados[chave] = [v.strip().lstrip("@") if chave == "concorrentes" else v.strip()
                            for v in valor.split(",") if v.strip()]
        elif chave in INTEIROS:
            dados[chave] = int(valor) if valor.isdigit() else None
        else:
            dados[chave] = valor
    if dados.get("perfil_arroba"):
        dados["perfil_arroba"] = "@" + dados["perfil_arroba"].lstrip("@")
    return dados


def ler_env():
    env = {}
    caminho = ROOT / ".env"
    if caminho.exists():
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def exigir(caminho):
    if not caminho.exists():
        qual = "rascunho" if caminho == RASCUNHO else "cadastro"
        sys.exit(f"ERRO: nao existe {qual}. Rode: python scripts/cadastro.py novo")


def gravar(campo, valor, caminho=RASCUNHO, quieto=False):
    if campo not in CAMPOS:
        sys.exit(f"ERRO: campo desconhecido: {campo}. Campos: {', '.join(CAMPOS)}")
    exigir(caminho)
    valor = " ".join(str(valor).split())
    texto = caminho.read_text(encoding="utf-8")
    novo_texto, n = re.subn(rf"(?m)^{campo}:.*$", lambda _m: f"{campo}: {valor}", texto, count=1)
    if n == 0:
        novo_texto = texto.rstrip("\n") + f"\n{campo}: {valor}\n"
    caminho.write_text(novo_texto, encoding="utf-8")
    if not quieto:
        print(f"gravado: {campo}")


def inserir_na_secao(titulo, linha, caminho=RASCUNHO):
    """Poe a linha no fim da secao '## <titulo>' (antes da proxima secao)."""
    exigir(caminho)
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    ini = next((i for i, l in enumerate(linhas) if l.startswith("## " + titulo)), None)
    if ini is None:
        linhas += ["", "## " + titulo, ""]
        ini = len(linhas) - 2
    fim = next((i for i in range(ini + 1, len(linhas)) if linhas[i].startswith("## ")), len(linhas))
    while fim > ini + 1 and not linhas[fim - 1].strip():
        fim -= 1
    if not re.match(r"^[a-z_]+:", linhas[fim - 1]):
        linhas.insert(fim, "")
        fim += 1
    linhas[fim:fim] = [linha]
    if fim + 1 < len(linhas) and linhas[fim + 1].startswith("## "):
        linhas.insert(fim + 1, "")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def registrar_foto(arquivo, descricao):
    arquivo = arquivo.replace("\\", "/")
    if not (ROOT / arquivo).is_file():
        sys.exit(f"ERRO: arquivo nao encontrado: {arquivo}")
    if not descricao.strip():
        sys.exit("ERRO: descreva o que e a foto")
    if any(f["arquivo"] == arquivo for f in ler(RASCUNHO)["fotos"]):
        sys.exit(f"ERRO: foto ja registrada: {arquivo}")
    inserir_na_secao("Fotos para usar nos posts", f"foto: {arquivo} | {' '.join(descricao.split())}")
    print(f"foto registrada: {arquivo}")


def registrar_restricao(tipo, regra):
    tipo = tipo.upper()
    if tipo not in TIPOS_RESTRICAO:
        sys.exit("ERRO: tipo precisa ser OBRIGATORIO, PROIBIDO ou PERMITIDO")
    if len(regra.strip()) < 12:
        sys.exit("ERRO: escreva a regra por extenso")
    inserir_na_secao("Restricoes legais", f"restricao: {tipo} | {' '.join(regra.split())}")
    print(f"restricao registrada ({tipo})")


def registrar_termo(expressao):
    expressao = " ".join(expressao.split())
    if len(expressao) < 3:
        sys.exit("ERRO: expressao curta demais")
    inserir_na_secao("Restricoes legais", f"termo_proibido: {expressao}")
    print(f"termo registrado: {expressao}")


def novo():
    RASCUNHO.parent.mkdir(parents=True, exist_ok=True)
    if PERFIL_RASCUNHO.exists():
        shutil.rmtree(PERFIL_RASCUNHO)
    RASCUNHO.write_text(MODELO, encoding="utf-8")
    for campo, valor in PADROES.items():
        gravar(campo, valor, quieto=True)
    print("rascunho em branco aberto, com os padroes gravados (nada muda no cadastro atual ate o 'confirmar')")


def confirmar():
    exigir(RASCUNHO)
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "guardiao.py"), "cadastro", "--rascunho"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout.strip())
        sys.exit("ERRO: o guardiao reprovou o rascunho. Nada foi gravado.")
    # as imagens do rascunho passam a valer: substituem avatar, logo e fotos anteriores
    if PERFIL_RASCUNHO.is_dir():
        for antigo in ("avatar.jpg", "logo.png"):
            if (PERFIL_RASCUNHO / antigo).exists() and (PERFIL / antigo).exists():
                (PERFIL / antigo).unlink()
        if (PERFIL / "fotos").is_dir():
            shutil.rmtree(PERFIL / "fotos")
        for item in PERFIL_RASCUNHO.iterdir():
            shutil.move(str(item), str(PERFIL / item.name))
        PERFIL_RASCUNHO.rmdir()
        RASCUNHO.write_text(RASCUNHO.read_text(encoding="utf-8").replace("assets/perfil/rascunho/", "assets/perfil/"), encoding="utf-8")
    if CAMINHO.exists() and re.search(r"(?m)^[a-z_]+:[ \t]*\S", CAMINHO.read_text(encoding="utf-8")):
        destino = CAMINHO.with_name(f"cadastro-anterior-{datetime.datetime.now():%Y-%m-%d-%H%M}.md")
        shutil.copy(CAMINHO, destino)
        print(f"cadastro anterior guardado em contexto/{destino.name}")
    shutil.move(str(RASCUNHO), str(CAMINHO))
    print("cadastro gravado em contexto/cadastro.md")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--rascunho"]:
        json.dump(ler(RASCUNHO if args else CAMINHO), sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif args[0] == "gravar" and len(args) == 3:
        gravar(args[1], args[2])
    elif args[0] == "corrigir" and len(args) == 3:
        gravar(args[1], args[2], caminho=CAMINHO)
    elif args[0] == "foto" and len(args) == 3:
        registrar_foto(args[1], args[2])
    elif args[0] == "restricao" and len(args) == 3:
        registrar_restricao(args[1], args[2])
    elif args[0] == "termo" and len(args) == 2:
        registrar_termo(args[1])
    elif args[0] == "novo" and len(args) == 1:
        novo()
    elif args[0] == "confirmar" and len(args) == 1:
        confirmar()
    else:
        sys.exit(__doc__)
