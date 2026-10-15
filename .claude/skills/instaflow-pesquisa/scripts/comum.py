"""Funções compartilhadas pelos scripts da skill instaflow-pesquisa."""
import json
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

API = "https://api.apify.com/v2"


def raiz_projeto():
    """Sobe a partir desta pasta ate achar a raiz do projeto (onde fica contexto/cadastro.md)."""
    p = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        if os.path.exists(os.path.join(p, "contexto", "cadastro.md")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def ler_token(_caminho_config=None):
    """Token vem da variavel APIFY_TOKEN ou do .env na raiz do projeto. Nunca e impresso."""
    token = os.environ.get("APIFY_TOKEN", "").strip()
    env = os.path.join(raiz_projeto(), ".env")
    if not token and os.path.exists(env):
        with open(env, encoding="utf-8") as f:
            for linha in f:
                if linha.strip().startswith("APIFY_TOKEN="):
                    token = linha.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("ERRO: APIFY_TOKEN nao encontrado no .env.", file=sys.stderr)
        sys.exit(2)
    return token


def numero(valor):
    """Converte '15,3 mil', '1,2 mi', '12.5K', '1.234' etc. para int. None se vazio/oculto."""
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return None if valor < 0 else int(valor)
    s = str(valor).strip().lower().replace(" ", " ")
    if not s or s in {"-", "—", "oculto"}:
        return None
    mult = 1
    for sufixo, m in (("bi", 10**9), ("mi", 10**6), ("mil", 10**3), ("b", 10**9), ("m", 10**6), ("k", 10**3)):
        if re.search(r"\d\s*" + sufixo + r"\b", s) or s.endswith(sufixo):
            mult = m
            s = re.sub(sufixo + r".*$", "", s).strip()
            break
    s = re.sub(r"[^\d.,]", "", s)
    if not s:
        return None
    if mult == 1:
        # sem sufixo: pontos/vírgulas são separadores de milhar
        s = s.replace(".", "").replace(",", "")
        return int(s)
    s = s.replace(",", ".")
    if s.count(".") > 1:
        partes = s.split(".")
        s = "".join(partes[:-1]) + "." + partes[-1]
    return int(round(float(s) * mult))


def shortcode(url):
    m = re.search(r"/(?:p|reel|reels|tv)/([^/?#]+)", url or "")
    return m.group(1) if m else (url or "")


def salvar(caminho, dados):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)
