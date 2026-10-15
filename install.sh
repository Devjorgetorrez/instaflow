#!/bin/bash
# install.sh - Agente de Instagram (instaflow), Linux e macOS
# Instala tudo o que o agente precisa para rodar nesta pasta: Playwright e
# Chromium (desenham os slides), as bibliotecas Python (imagens, download e
# transcricao dos videos) e o modelo de transcricao. Cria o .env vazio.

set -uo pipefail
RAIZ="$(cd "$(dirname "$0")" && pwd)"
cd "$RAIZ"
ERROS=()
AVISOS=()

ok()   { echo "  [OK] $1"; }
err()  { echo "  [ERRO] $1"; }
warn() { echo "  [AVISO] $1"; }
step() { echo ""; echo "$1"; }

echo ""
echo "Agente de Instagram - Instalador"
echo "================================"

step "1. Conferindo o pacote"
for item in .claude/skills/instaflow/SKILL.md .claude/skills/instaflow-pesquisa .claude/skills/instaflow-redator \
            .claude/skills/instaflow-designer scripts/instalar.py scripts/requirements.txt package.json .env.example; do
    if [ -e "$RAIZ/$item" ]; then ok "$item"; else err "$item nao encontrado"; ERROS+=("$item"); fi
done
if [ ${#ERROS[@]} -gt 0 ]; then
    echo "Rode o instalador de dentro da pasta do agente. Pasta atual: $RAIZ"
    exit 1
fi

step "2. Conferindo Claude Code, Node.js e Python"
if command -v claude >/dev/null 2>&1; then ok "Claude Code encontrado"
else AVISOS+=("Nao achei o Claude Code no terminal. Se voce usa o aplicativo do Claude (aba Code), esta tudo certo. Se nao, baixe em claude.ai/download."); fi

if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then ok "Node.js $(node --version)"
else err "Node.js nao encontrado. Instale em nodejs.org (versao LTS) e rode de novo."; ERROS+=("node"); fi

PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
        PY="$cand"; break
    fi
done
if [ -n "$PY" ]; then ok "$($PY --version)"
else err "Python 3.10 ou mais novo nao encontrado. Instale em python.org e rode de novo."; ERROS+=("python"); fi

if [ ${#ERROS[@]} -gt 0 ]; then
    echo ""
    echo "Instale o que falta e rode o install.sh de novo."
    exit 1
fi

step "3. Instalando a biblioteca que desenha os slides (Playwright)"
if npm install --no-fund --no-audit >/dev/null 2>&1; then ok "Playwright instalado"
else err "npm install falhou. Rode 'npm install' nesta pasta para ver o erro."; ERROS+=("npm"); fi

step "4. Baixando o navegador interno dos slides (Chromium) - pode levar alguns minutos"
if npx playwright install chromium >/dev/null 2>&1; then ok "Chromium instalado"
else err "Download do Chromium falhou. Rode 'npx playwright install chromium' para ver o erro."; ERROS+=("chromium"); fi

step "5. Instalando as bibliotecas Python (imagens, download e transcricao dos videos)"
if "$PY" -m pip install --quiet -r "$RAIZ/scripts/requirements.txt"; then ok "Bibliotecas Python instaladas"
else err "pip install falhou. Rode '$PY -m pip install -r scripts/requirements.txt' para ver o erro."; ERROS+=("pip"); fi

step "6. Baixando o modelo de transcricao (cerca de 500 MB, uma vez so) - pode levar alguns minutos"
if [ ${#ERROS[@]} -eq 0 ] && "$PY" -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')" >/dev/null 2>&1; then
    ok "Modelo de transcricao baixado"
else
    AVISOS+=("O modelo de transcricao nao baixou agora. Ele sera baixado na primeira transcricao.")
fi

step "7. Arquivo de chaves (.env)"
if [ -f "$RAIZ/.env" ]; then ok ".env ja existe - nao foi mexido"
else cp "$RAIZ/.env.example" "$RAIZ/.env"; ok ".env criado vazio. O agente mostra onde colar cada chave, se precisar."; fi

echo ""
if [ ${#ERROS[@]} -gt 0 ]; then
    echo "INSTALACAO COM ERROS."
    exit 1
fi

step "Conferencia final"
PYTHONIOENCODING=utf-8 "$PY" "$RAIZ/scripts/instalar.py" checar
rm -rf "$RAIZ/scripts/__pycache__"

echo ""
echo "Instalacao concluida!"
for a in "${AVISOS[@]}"; do warn "$a"; done
echo ""
echo "Proximo passo:"
echo "  1. Abra esta pasta no Claude Code."
echo "  2. Digite /instaflow novo para fazer o cadastro do seu perfil."
echo "  3. Depois, /instaflow roda a primeira rodada."
echo ""
