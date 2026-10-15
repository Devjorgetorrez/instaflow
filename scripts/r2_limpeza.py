"""Regra de limpeza do bucket no Cloudflare R2: apagar as imagens de post depois de 30 dias.

Depois de publicado, o Metricool ja copiou as imagens para o servidor dele. Guardar no bucket
so acumula armazenamento. A regra apaga sozinha o que esta em carrosseis/ e stories/.

    python scripts/r2_limpeza.py checar       -> diz se a regra esta ativa
    python scripts/r2_limpeza.py configurar   -> cria a regra de 30 dias

Le as chaves do .env. Saida 0 = regra ativa. 1 = regra ausente. 2 = nao foi possivel conferir
(chave sem permissao de administrar o bucket: nesse caso a regra e criada pelo painel da Cloudflare,
passo a passo em docs/pipeline-publicacao.md).
"""
import base64
import datetime
import hashlib
import hmac
import re
import sys
import urllib.error
import urllib.request

from cadastro import R2, ler_env

DIAS = 30
PREFIXOS = ["carrosseis/", "stories/"]


def assinar(chave, msg):
    return hmac.new(chave, msg.encode("utf-8"), hashlib.sha256).digest()


def requisicao(env, metodo, corpo=b""):
    host = f"{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    caminho, consulta = "/" + env["R2_BUCKET"], "lifecycle="
    agora = datetime.datetime.now(datetime.timezone.utc)
    amz, dia = agora.strftime("%Y%m%dT%H%M%SZ"), agora.strftime("%Y%m%d")
    hash_corpo = hashlib.sha256(corpo).hexdigest()
    cab = {"host": host, "x-amz-content-sha256": hash_corpo, "x-amz-date": amz}
    if corpo:
        cab["content-md5"] = base64.b64encode(hashlib.md5(corpo).digest()).decode()
        cab["content-type"] = "application/xml"
    nomes = ";".join(sorted(cab))
    canonico = "\n".join([metodo, caminho, consulta, "".join(f"{k}:{cab[k]}\n" for k in sorted(cab)), nomes, hash_corpo])
    escopo = f"{dia}/auto/s3/aws4_request"
    a_assinar = "\n".join(["AWS4-HMAC-SHA256", amz, escopo, hashlib.sha256(canonico.encode()).hexdigest()])
    k = assinar(("AWS4" + env["R2_SECRET_ACCESS_KEY"]).encode(), dia)
    for parte in ("auto", "s3", "aws4_request"):
        k = assinar(k, parte)
    assinatura = hmac.new(k, a_assinar.encode(), hashlib.sha256).hexdigest()
    cab["authorization"] = (f"AWS4-HMAC-SHA256 Credential={env['R2_ACCESS_KEY_ID']}/{escopo}, "
                            f"SignedHeaders={nomes}, Signature={assinatura}")
    req = urllib.request.Request(f"https://{host}{caminho}?lifecycle", data=corpo or None, method=metodo, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def regras_ativas(xml):
    """Devolve {prefixo: dias} das regras de expiracao habilitadas."""
    achadas = {}
    for regra in re.findall(r"<Rule>(.*?)</Rule>", xml, flags=re.S):
        if "<Status>Enabled</Status>" not in regra:
            continue
        dias = re.search(r"<Expiration>.*?<Days>(\d+)</Days>", regra, flags=re.S)
        prefixo = re.search(r"<Prefix>(.*?)</Prefix>", regra, flags=re.S)
        if dias:
            achadas[prefixo.group(1) if prefixo else ""] = int(dias.group(1))
    return achadas


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("checar", "configurar"):
        sys.exit(__doc__)
    env = ler_env()
    faltam = [k for k in R2 if not env.get(k)]
    if faltam:
        print("NAO CONFERIDO: faltam chaves do R2 no .env: " + ", ".join(faltam))
        return 2

    if sys.argv[1] == "configurar":
        status, texto = requisicao(env, "GET")
        if status == 200 and regras_ativas(texto):
            print("NAO CONFIGURADO: o bucket ja tem regras de limpeza. Para nao apagar as que existem, "
                  "acrescente a de 30 dias pelo painel da Cloudflare: bucket > Settings > Object Lifecycle Rules.")
            return 2
        regras = "".join(
            f"<Rule><ID>limpar-{p.strip('/')}-{DIAS}d</ID><Filter><Prefix>{p}</Prefix></Filter>"
            f"<Status>Enabled</Status><Expiration><Days>{DIAS}</Days></Expiration></Rule>" for p in PREFIXOS)
        corpo = f'<?xml version="1.0" encoding="UTF-8"?><LifecycleConfiguration>{regras}</LifecycleConfiguration>'.encode()
        status, texto = requisicao(env, "PUT", corpo)
        if status not in (200, 204):
            print(f"NAO CONFIGURADO (HTTP {status}): a chave do .env nao pode administrar o bucket. "
                  "Crie a regra pelo painel da Cloudflare: docs/pipeline-publicacao.md, 'Limpeza automatica'.")
            return 2

    status, texto = requisicao(env, "GET")
    if status == 404 or "NoSuchLifecycleConfiguration" in texto:
        print(f"AUSENTE: o bucket nao tem regra de limpeza. As imagens vao acumular.")
        return 1
    if status != 200:
        print(f"NAO CONFERIDO (HTTP {status}): a chave do .env nao pode ler a configuracao do bucket. "
              "Confira pelo painel da Cloudflare: bucket > Settings > Object Lifecycle Rules.")
        return 2
    regras = regras_ativas(texto)
    cobre = {p: next((d for pref, d in regras.items() if p.startswith(pref)), None) for p in PREFIXOS[:1]}
    dias = cobre[PREFIXOS[0]]
    if dias is None:
        print("AUSENTE: ha regra no bucket, mas nenhuma cobre a pasta carrosseis/.")
        return 1
    print(f"ATIVA: imagens de carrosseis/ sao apagadas depois de {dias} dias.")
    if dias > DIAS:
        print(f"AVISO: o padrao e {DIAS} dias.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
