#!/usr/bin/env python3
"""Sobe arquivos para um bucket Cloudflare R2 e imprime as URLs publicas.

Le as credenciais do .env na raiz do projeto. Nao recebe segredo por argumento,
para nao deixar token no historico do shell.

Uso:
    python scripts/r2_upload.py <prefixo> <arquivo> [arquivo ...]
    python scripts/r2_upload.py carrosseis/2026-08-21 conteudo/.../upload/*.jpg

Saida: uma URL publica por linha, na ordem dos arquivos.
Com --json, imprime {"urls": [...]} para consumo por outro processo.
"""
import datetime
import glob
import hashlib
import hmac
import json
import mimetypes
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET", "R2_PUBLIC_BASE"]


def load_env():
    env = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in REQUIRED:
        if os.environ.get(k):
            env[k] = os.environ[k]
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        sys.exit(
            "Faltam chaves no .env: " + ", ".join(missing) + "\n"
            "Veja docs/pipeline-publicacao.md para o passo a passo."
        )
    return env


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def signing_key(secret, datestamp, region, service):
    k = sign(("AWS4" + secret).encode("utf-8"), datestamp)
    k = sign(k, region)
    k = sign(k, service)
    return sign(k, "aws4_request")


def put_object(env, key, body, content_type):
    region, service = "auto", "s3"
    host = f"{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    canonical_uri = "/" + env["R2_BUCKET"] + "/" + key
    now = datetime.datetime.now(datetime.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(body).hexdigest()

    canonical_headers = (
        f"content-type:{content_type}\n"
        f"host:{host}\n"
        f"x-amz-content-sha256:{payload_hash}\n"
        f"x-amz-date:{amzdate}\n"
    )
    signed_headers = "content-type;host;x-amz-content-sha256;x-amz-date"
    canonical_request = "\n".join(
        ["PUT", canonical_uri, "", canonical_headers, signed_headers, payload_hash]
    )
    scope = f"{datestamp}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join(
        ["AWS4-HMAC-SHA256", amzdate, scope,
         hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()]
    )
    signature = hmac.new(
        signing_key(env["R2_SECRET_ACCESS_KEY"], datestamp, region, service),
        string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    authorization = (
        f"AWS4-HMAC-SHA256 Credential={env['R2_ACCESS_KEY_ID']}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    req = urllib.request.Request(
        f"https://{host}{canonical_uri}", data=body, method="PUT",
        headers={
            "Authorization": authorization,
            "Content-Type": content_type,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amzdate,
            "Content-Length": str(len(body)),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Falhou o upload de {key}: HTTP {e.code} {e.read()[:400].decode(errors='replace')}")

    return env["R2_PUBLIC_BASE"].rstrip("/") + "/" + key


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if len(args) < 2:
        sys.exit(__doc__)

    env = load_env()
    prefix, files = args[0].strip("/"), []
    for padrao in args[1:]:  # o PowerShell nao expande slide-*.jpg; expande aqui
        achados = sorted(glob.glob(padrao))
        files += achados if achados else [padrao]
    urls = []
    for f in files:
        p = pathlib.Path(f)
        if not p.is_file():
            sys.exit(f"Arquivo nao encontrado: {f}")
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        url = put_object(env, f"{prefix}/{p.name}", p.read_bytes(), ctype)
        urls.append(url)
        if not as_json:
            print(url)

    if as_json:
        print(json.dumps({"urls": urls}, ensure_ascii=False))


if __name__ == "__main__":
    main()
