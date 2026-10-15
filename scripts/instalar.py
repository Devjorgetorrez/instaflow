"""Confere e instala tudo de que o agente precisa para rodar, conforme as escolhas do cadastro.

    python scripts/instalar.py checar [--rascunho]   -> lista o que esta pronto e o que falta
    python scripts/instalar.py instalar              -> instala o que da para instalar sozinho

Cada linha da checagem comeca com:
    OK        esta pronto
    FALTA     falta, e o agente instala (rode 'instalar')
    VOCE      falta, e so o cliente resolve (conta, login ou chave): a linha diz o passo
    AVISO     nao impede de rodar
Saida 0 = tudo pronto. 1 = falta algo.
"""
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

from cadastro import CAMINHO, R2, RASCUNHO, ROOT, ler, ler_env

faltas = 0


def linha(estado, texto):
    global faltas
    if estado in ("FALTA", "VOCE"):
        faltas += 1
    print(f"{estado:<6}{texto}")


def tem_modulo(nome):
    return importlib.util.find_spec(nome) is not None


def rodar(cmd, **kw):
    """Roda um comando; no Windows o npm e o npx sao .cmd e precisam do shell."""
    return subprocess.run(cmd, cwd=str(ROOT), shell=(os.name == "nt"), **kw)


def chromium_instalado():
    base = pathlib.Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or
                        (pathlib.Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright" if os.name == "nt"
                         else pathlib.Path.home() / ".cache" / "ms-playwright"))
    if sys.platform == "darwin":
        base = pathlib.Path.home() / "Library" / "Caches" / "ms-playwright"
    return base.is_dir() and any(base.glob("chromium*"))


def modelo_de_voz_baixado():
    cache = pathlib.Path.home() / ".cache" / "huggingface" / "hub"
    return cache.is_dir() and any(cache.glob("models--Systran--faster-whisper-*"))


def checar(cad):
    if not (ROOT / ".env").exists() and (ROOT / ".env.example").exists():
        shutil.copy(ROOT / ".env.example", ROOT / ".env")
        print("criado: .env (vazio, a partir do .env.example)")
    env = ler_env()
    # --- base: todo mundo precisa
    linha("OK" if shutil.which("node") else "VOCE", "Node.js (desenha os slides)" +
          ("" if shutil.which("node") else ": instale em nodejs.org, versao LTS, e abra o Claude Code de novo"))
    linha("OK" if (ROOT / "node_modules" / "playwright").is_dir() else "FALTA", "Playwright (biblioteca que desenha os slides)")
    linha("OK" if chromium_instalado() else "FALTA", "Navegador interno do Playwright (Chromium)")
    linha("OK" if tem_modulo("PIL") else "FALTA", "Pillow (confere e ajusta imagens)")
    linha("OK" if tem_modulo("yt_dlp") else "FALTA", "yt-dlp (baixa os videos dos concorrentes)")
    linha("OK" if tem_modulo("faster_whisper") else "FALTA", "faster-whisper (transcreve os videos)")
    if tem_modulo("faster_whisper"):
        linha("OK" if modelo_de_voz_baixado() else "AVISO",
              "Modelo de transcricao" + ("" if modelo_de_voz_baixado() else ": sera baixado na primeira transcricao (cerca de 500 MB, uma vez so)"))

    # --- coleta
    if cad.get("coleta_modo") == "apify":
        if not env.get("APIFY_TOKEN"):
            linha("VOCE", "Apify: crie a conta gratis em apify.com, copie a chave em Settings > API & Integrations "
                          "e cole depois de APIFY_TOKEN= no arquivo .env")
        else:
            try:
                req = urllib.request.Request("https://api.apify.com/v2/users/me",
                                             headers={"Authorization": "Bearer " + env["APIFY_TOKEN"]})
                with urllib.request.urlopen(req, timeout=30) as r:
                    dados = json.loads(r.read().decode()).get("data", {})
                linha("OK", f"Apify: chave valida (conta {dados.get('username', '?')})")
            except urllib.error.HTTPError as e:
                linha("VOCE", f"Apify: a chave do .env foi recusada (HTTP {e.code}). Copie de novo em apify.com e cole no .env")
            except Exception as e:
                linha("AVISO", f"Apify: nao deu para testar a chave agora ({e})")
    elif cad.get("coleta_modo") == "navegador":
        linha("AVISO", "Coleta pelo navegador: deixe o Instagram logado no navegador do Claude e o computador ligado na hora da rotina")

    # --- publicacao
    if cad.get("publicacao_modo") == "metricool":
        faltam = [k for k in R2 if not env.get(k)]
        if faltam:
            linha("VOCE", "Cloudflare R2: faltam no .env " + ", ".join(faltam) + ". Passo a passo em docs/pipeline-publicacao.md")
        else:
            linha("OK", "Cloudflare R2: chaves no .env")
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "r2_limpeza.py"), "checar"], capture_output=True, text=True)
            texto = (r.stdout.strip().splitlines() or [""])[0]
            if r.returncode == 0:
                linha("OK", "Cloudflare R2: " + texto)
            elif r.returncode == 1:
                linha("FALTA", "Cloudflare R2: sem regra de limpeza de 30 dias (rode: python scripts/r2_limpeza.py configurar)")
            else:
                linha("AVISO", "Cloudflare R2: " + texto)
        if not cad.get("metricool_blog_id"):
            linha("VOCE", "Metricool: falta o ID da marca no cadastro")
        linha("AVISO", "Metricool: confira na sessao se o conector do Metricool esta ligado no Claude (o agente testa listando as marcas). Passo a passo em docs/metricool.md")

    # --- resposta aos comentarios
    if cad.get("isca_palavra"):
        linha("AVISO", f"Resposta aos comentarios (opcional): quem comenta {cad['isca_palavra']} recebe o direct a mao, pelo ManyChat ou por outra automacao. Textos prontos e passo a passo em docs/manychat.md")

    # --- opcionais
    if env.get("OPENROUTER_API_KEY"):
        linha("OK" if tem_modulo("requests") and tem_modulo("dotenv") else "FALTA", "Bibliotecas da imagem por IA (requests, python-dotenv)")
    if precisa_recorte(cad):
        linha("OK" if tem_modulo("rembg") else "FALTA",
              "rembg (recorta o fundo de foto de pessoa)" + ("" if tem_modulo("rembg") else ": sem ele, a capa do tipo recorte nao e oferecida"))

    # --- rotina
    r = cad.get("rotina")
    if r == "pedida":
        linha("FALTA", "Rotina pedida no cadastro e ainda nao criada (crie agora, ou grave rotina = manual)")
    elif r == "criada":
        linha("OK", f"Rotina diaria criada para {cad.get('rotina_horario')}")
    elif r == "manual":
        linha("AVISO", "Rotina: voce escolheu criar a mao. Sem ela, o agente so roda quando alguem digita /instaflow")
    elif r == "nao":
        linha("AVISO", "Sem rotina: o agente so roda quando alguem digita /instaflow")


def precisa_recorte(cad):
    return bool(cad.get("fotos")) and cad.get("perfil_tipo") in ("pessoa", "misto")


def instalar(cad):
    passos = []
    if not (ROOT / "node_modules" / "playwright").is_dir():
        passos.append(("Playwright", ["npm", "install"]))
    if not chromium_instalado():
        passos.append(("Chromium do Playwright", ["npx", "playwright", "install", "chromium"]))
    libs = [pip for mod, pip in (("PIL", "pillow"), ("yt_dlp", "yt-dlp"), ("faster_whisper", "faster-whisper")) if not tem_modulo(mod)]
    if ler_env().get("OPENROUTER_API_KEY"):
        libs += [pip for mod, pip in (("requests", "requests"), ("dotenv", "python-dotenv")) if not tem_modulo(mod)]
    if precisa_recorte(cad) and not tem_modulo("rembg"):
        libs.append("rembg[cpu]")
    if libs:
        passos.append(("Bibliotecas Python: " + ", ".join(libs), [sys.executable, "-m", "pip", "install", "--quiet"] + libs))
    if not (ROOT / ".env").exists() and (ROOT / ".env.example").exists():
        shutil.copy(ROOT / ".env.example", ROOT / ".env")
        print("criado: .env (vazio, a partir do .env.example)")
    if not passos:
        print("nada para instalar")
    for nome, cmd in passos:
        print(f"instalando: {nome} ...")
        r = rodar(cmd) if cmd[0] in ("npm", "npx") else subprocess.run(cmd, cwd=str(ROOT))
        print(("  ok" if r.returncode == 0 else f"  FALHOU (codigo {r.returncode})"))


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("checar", "instalar"):
        sys.exit(__doc__)
    origem = RASCUNHO if "--rascunho" in args and RASCUNHO.exists() else CAMINHO
    if args[0] == "instalar":
        instalar(ler(origem))
        print()
    checar(ler(origem))
    print("PRONTO" if not faltas else f"FALTAM {faltas} ITEM(NS)")
    return 1 if faltas else 0


if __name__ == "__main__":
    sys.exit(main())
