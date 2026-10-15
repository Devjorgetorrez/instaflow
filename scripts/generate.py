#!/usr/bin/env python3
"""
generate.py — Gerador de imagem via OpenRouter.
Modelo: google/gemini-3.1-flash-image-preview
Chave: OPENROUTER_API_KEY (carregada do .env na raiz do projeto)

Uso:
    python scripts/generate.py \\
        --prompt "..." \\
        --output conteudo/.../imagens/s03.png \\
        --aspect-ratio 4:5
"""

from __future__ import annotations
import argparse
import base64
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERRO: 'requests' nao instalado. Rode: pip install requests")

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("ERRO: 'python-dotenv' nao instalado. Rode: pip install python-dotenv")

# Raiz do projeto: 2 niveis acima deste script
# generate.py -> scripts/ -> projeto/
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY   = os.getenv("OPENROUTER_API_KEY")
MODEL     = "google/gemini-3.1-flash-image-preview"
HEADERS   = lambda: {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://instaflow.local",
    "X-Title": "instaflow-image-gen",
}

ASPECT_MAP: dict[str, tuple[int, int]] = {
    "4:5":  (1080, 1350),
    "1:1":  (1080, 1080),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
}


def _try_images_endpoint(prompt: str, w: int, h: int) -> str | None:
    """POST /images/generations — formato padrao para image models no OpenRouter."""
    resp = requests.post(
        "https://openrouter.ai/api/v1/images/generations",
        headers=HEADERS(),
        json={
            "model": MODEL,
            "prompt": prompt,
            "n": 1,
            "size": f"{w}x{h}",
            "response_format": "b64_json",
        },
        timeout=120,
    )
    if not resp.ok:
        print(f"[images/generations] {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        return None
    data = resp.json()
    items = data.get("data", [])
    if items and items[0].get("b64_json"):
        return items[0]["b64_json"]
    print(f"[images/generations] resposta sem b64_json: {str(data)[:400]}", file=sys.stderr)
    return None


def _try_chat_endpoint(prompt: str) -> str | None:
    """POST /chat/completions — fallback para modelos multimodais via chat."""
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS(),
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
        },
        timeout=120,
    )
    if not resp.ok:
        print(f"[chat/completions] {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        return None

    data    = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content")

    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "image_url":
                    url = part["image_url"]["url"]
                    if "base64," in url:
                        return url.split("base64,", 1)[1]
                if part.get("type") == "image_data":
                    return part.get("data")

    if isinstance(content, str) and "base64," in content:
        return content.split("base64,", 1)[1]

    print(f"[chat/completions] sem imagem no content: {repr(content)[:400]}", file=sys.stderr)
    return None


def generate(prompt: str, output: str, aspect_ratio: str = "4:5") -> dict:
    if not API_KEY:
        sys.exit(
            "ERRO: OPENROUTER_API_KEY nao definido.\n"
            f"Verifique o .env em: {ROOT / '.env'}"
        )

    if aspect_ratio not in ASPECT_MAP:
        sys.exit(
            f"ERRO: aspect-ratio '{aspect_ratio}' invalido.\n"
            f"Opcoes: {list(ASPECT_MAP)}"
        )

    w, h = ASPECT_MAP[aspect_ratio]
    print(f"[generate] {MODEL} | {aspect_ratio} ({w}x{h}) -> {output}", file=sys.stderr)

    # Tentativa 1: /images/generations (padrao para image models)
    img_b64 = _try_images_endpoint(prompt, w, h)

    # Tentativa 2: /chat/completions com modalities (fallback multimodal)
    if not img_b64:
        print("[generate] tentando chat/completions como fallback...", file=sys.stderr)
        img_b64 = _try_chat_endpoint(prompt)

    if not img_b64:
        sys.exit(
            f"ERRO: nenhum endpoint retornou imagem para o modelo '{MODEL}'.\n"
            "Verifique se o modelo suporta geracao de imagem no OpenRouter.\n"
            "Alternativa: use svg como modalidade (ver image-gen/svg-guide.md)."
        )

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(img_b64))

    return {
        "output":   str(out),
        "model":    MODEL,
        "cost_usd": "ver OpenRouter dashboard (billing)",
    }


def main() -> None:
    p = argparse.ArgumentParser(
        description="Gera imagem via OpenRouter (google/gemini-3.1-flash-image-preview)"
    )
    p.add_argument("--prompt",       required=True, help="Prompt de geracao da imagem")
    p.add_argument("--output",       required=True, help="Caminho de saida (.png)")
    p.add_argument("--aspect-ratio", default="4:5",
                   help="Aspect ratio: 4:5 | 1:1 | 9:16 | 16:9 (default: 4:5)")
    args = p.parse_args()

    result = generate(args.prompt, args.output, args.aspect_ratio)
    print(f"Salvo:  {result['output']}")
    print(f"Custo:  {result['cost_usd']}")


if __name__ == "__main__":
    main()
