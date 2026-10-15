"""Estado das etapas: o que ja passou e quantas tentativas cada uma teve.

Serve para tres coisas: retomar de onde parou, nao fazer duas vezes (nem em outro dia)
e cortar o laco na terceira tentativa.

Uso:
    python scripts/estado.py situacao
    python scripts/estado.py tentar <etapa> [--peca ID]   -> imprime o numero da tentativa
    python scripts/estado.py ok     <etapa> [--peca ID]
    python scripts/estado.py falha  <etapa> [--peca ID] --motivo "..."

Etapas: pesquisa | capas | escolha | copy | design | publicacao
Sem --peca, a etapa e do dia (pesquisa): o registro zera a cada dia.
Com --peca (o ID da selecao ou o slug do carrossel), o registro e permanente: uma peca
concluida continua concluida amanha, e o limite de 3 tentativas nao zera a meia-noite.

Cada tentativa aceita no maximo 5 conferencias do guardiao (scripts/guardiao.py conta sozinho).
Saida 0 = pode seguir. Saida 3 = limite de tentativas estourado: parar e avisar.
Saida 4 = etapa ja concluida: pular.
"""
import argparse
import datetime
import json
import pathlib
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
PASTA = ROOT / "conteudo" / "_estado"
LIMITE = 3
ETAPAS = ["pesquisa", "capas", "escolha", "copy", "design", "publicacao"]


def caminho(peca, data=None):
    return PASTA / ("pecas.json" if peca else f"{data or datetime.date.today().isoformat()}.json")


def carregar(peca, data=None):
    p = caminho(peca, data)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"etapas": {}}


def salvar(estado, peca, data=None):
    PASTA.mkdir(parents=True, exist_ok=True)
    caminho(peca, data).write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("acao", choices=["situacao", "tentar", "ok", "falha"])
    p.add_argument("etapa", nargs="?", choices=ETAPAS)
    p.add_argument("--peca", default="")
    p.add_argument("--motivo", default="")
    p.add_argument("--data")
    a = p.parse_args()

    if a.acao == "situacao":
        print(json.dumps({"hoje": carregar("", a.data)["etapas"], "pecas": carregar("x")["etapas"]}, ensure_ascii=False, indent=2))
        return 0
    if not a.etapa:
        p.error("informe a etapa")

    estado = carregar(a.peca, a.data)
    chave = a.etapa + (":" + a.peca if a.peca else "")
    reg = estado["etapas"].setdefault(chave, {"tentativas": 0, "status": "pendente", "motivos": []})

    if a.acao == "tentar":
        if reg["status"] == "ok":
            print(f"{chave}: ja concluida")
            return 4
        if reg["tentativas"] >= LIMITE:
            reg["status"] = "bloqueada"
            salvar(estado, a.peca, a.data)
            print(f"{chave}: limite de {LIMITE} tentativas estourado. PARAR e avisar o usuario.")
            for m in reg["motivos"]:
                print(f"  - {m}")
            return 3
        reg["tentativas"] += 1
        reg["conferencias"] = 0
        reg["status"] = "em_andamento"
        reg["ultima"] = datetime.datetime.now().isoformat(timespec="seconds")
        salvar(estado, a.peca, a.data)
        print(f"{chave}: tentativa {reg['tentativas']} de {LIMITE}")
        return 0

    if a.acao == "ok":
        reg["status"] = "ok"
    else:
        reg["status"] = "falhou"
        reg["motivos"].append(a.motivo or "sem motivo informado")
    salvar(estado, a.peca, a.data)
    print(f"{chave}: {reg['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
