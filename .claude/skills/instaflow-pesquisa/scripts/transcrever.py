"""Baixa e transcreve os vídeos do ranking (yt-dlp + faster-whisper, tudo local e grátis).

Grava o texto em 'transcricao' de cada post de vídeo no próprio ranking.json.
Carrosséis/imagens são ignorados aqui (o agente le as imagens na Etapa 6).
"""
import argparse
import os
import sys
import urllib.request

from comum import carregar, salvar, shortcode

INSTALAR = "pip install yt-dlp faster-whisper"


def checar_dependencias():
    faltando = []
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        faltando.append("faster-whisper")
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        faltando.append("yt-dlp")
    if faltando:
        print(f"Faltam dependências: {', '.join(faltando)}\nInstale com:  {INSTALAR}", file=sys.stderr)
        sys.exit(5)


def baixar(post, pasta, cookies_navegador):
    destino = os.path.join(pasta, f"{shortcode(post['url'])}.mp4")
    if os.path.exists(destino) and os.path.getsize(destino) > 0:
        return destino
    # 1) link direto (Apify) — rápido, mas expira em algumas horas
    if post.get("video_url"):
        try:
            urllib.request.urlretrieve(post["video_url"], destino)
            if os.path.getsize(destino) > 0:
                return destino
        except Exception:
            pass
    # 2) yt-dlp pelo link do post
    import yt_dlp

    opcoes = {"outtmpl": destino, "format": "best[ext=mp4]/best", "quiet": True, "no_warnings": True}
    if cookies_navegador:
        opcoes["cookiesfrombrowser"] = (cookies_navegador,)
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([post["url"]])
    return destino if os.path.exists(destino) else None


def carregar_modelo(nome):
    """Usa a placa de video quando ela funciona de verdade; senao, o processador.

    Em maquina com placa NVIDIA sem as bibliotecas CUDA o modelo carrega e so quebra na
    hora de transcrever. Por isso o teste e uma transcricao de 1 segundo de silencio.
    """
    import numpy as np
    from faster_whisper import WhisperModel
    modelo = WhisperModel(nome, device="auto", compute_type="int8")
    try:
        trechos, _ = modelo.transcribe(np.zeros(16000, dtype=np.float32), language="pt")
        list(trechos)
    except Exception:
        modelo = WhisperModel(nome, device="cpu", compute_type="int8")
    return modelo


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ranking", required=True)
    p.add_argument("--pasta", required=True)
    p.add_argument("--modelo", default="small", help="tiny | base | small | medium (maior = melhor e mais lento)")
    p.add_argument("--cookies-navegador", help="chrome | edge | firefox (modo navegador)")
    a = p.parse_args()

    checar_dependencias()

    ranking = carregar(a.ranking)
    videos = [x for x in ranking["posts"] if x.get("tipo") == "reel" and not x.get("transcricao")]
    if not videos:
        print("Nenhum vídeo para transcrever.")
        return

    os.makedirs(a.pasta, exist_ok=True)
    modelo = carregar_modelo(a.modelo)
    ok = 0
    for post in videos:
        try:
            arquivo = baixar(post, a.pasta, a.cookies_navegador)
            if not arquivo:
                raise RuntimeError("download falhou")
            segmentos, info = modelo.transcribe(arquivo, vad_filter=True)  # idioma detectado sozinho
            post["idioma"] = info.language
            post["transcricao"] = " ".join(s.text.strip() for s in segmentos).strip()
            ok += 1
            print(f"  ok   {post['url']}")
        except Exception as e:
            post["transcricao"] = None
            print(f"  erro {post['url']}: {e}")
        salvar(a.ranking, ranking)  # salva a cada vídeo (não perde progresso)

    print(f"OK: {ok}/{len(videos)} vídeos transcritos -> {a.ranking}")


if __name__ == "__main__":
    main()
