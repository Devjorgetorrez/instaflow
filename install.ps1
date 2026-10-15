# install.ps1 - Agente de Instagram (instaflow)
# Instala tudo o que o agente precisa para rodar nesta pasta: a biblioteca que
# desenha os slides (Playwright + Chromium), as bibliotecas Python (imagens,
# download e transcricao dos videos) e o modelo de transcricao. Cria o .env
# vazio. Nao move nada para fora desta pasta.
#
# Sem acentos de proposito: o install.bat chama "powershell -File" (PowerShell
# 5.1), que le o script no codepage do sistema, nao em UTF-8.

param()

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $raiz

function Write-Ok($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "  [ERRO] $msg" -ForegroundColor Red }
function Write-Warn($msg) { Write-Host "  [AVISO] $msg" -ForegroundColor Yellow }
function Write-Step($msg) { Write-Host ""; Write-Host $msg -ForegroundColor Cyan }

# Programa nativo que escreve aviso no stderr (npm, pip) nao pode derrubar o
# instalador: o resultado vem do codigo de saida, nao do stderr.
function Invoke-Nativo([string]$Exe, [string[]]$ArgList) {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Exe @ArgList 2>&1 | Out-Null
        return $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
    }
}

Write-Host ""
Write-Host "Agente de Instagram - Instalador" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$erros = @()
$avisos = @()

# --- 1. Pacote ---------------------------------------------------------------
Write-Step "1. Conferindo o pacote"
foreach ($item in @(".claude\skills\instaflow\SKILL.md", ".claude\skills\instaflow-pesquisa", ".claude\skills\instaflow-redator",
                    ".claude\skills\instaflow-designer", "scripts\instalar.py", "scripts\requirements.txt", "package.json", ".env.example")) {
    if (Test-Path "$raiz\$item") { Write-Ok $item } else { $erros += "$item nao encontrado." }
}
if ($erros.Count -gt 0) {
    Write-Host ""
    foreach ($e in $erros) { Write-Err $e }
    Write-Host "Rode o instalador de dentro da pasta do agente (a que tem este install.bat)." -ForegroundColor Yellow
    Write-Host "Pasta atual: $raiz" -ForegroundColor Yellow
    exit 1
}

# --- 2. Programas de base ----------------------------------------------------
Write-Step "2. Conferindo Claude Code, Node.js e Python"

if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Ok "Claude Code encontrado"
} else {
    $avisos += "Nao achei o Claude Code no terminal. Se voce usa o aplicativo do Claude (aba Code), esta tudo certo. Se nao tem nenhum dos dois, baixe em claude.ai/download."
}

if ((Get-Command node -ErrorAction SilentlyContinue) -and (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Ok "Node.js $(node --version)"
} else {
    $erros += "Node.js nao encontrado. Instale em nodejs.org (versao LTS) e rode este instalador de novo. Ele desenha os slides."
}

$py = $null
foreach ($cand in @("python", "py")) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) {
        $v = & $cand --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$v" -match "Python 3\.(\d+)") {
            if ([int]$Matches[1] -ge 10) { $py = $cand; break }
        }
    }
}
if ($py) {
    Write-Ok "$(& $py --version)"
} else {
    $erros += "Python 3.10 ou mais novo nao encontrado. Instale em python.org, marcando a caixa 'Add Python to PATH' na primeira tela, e rode este instalador de novo."
}

if ($erros.Count -gt 0) {
    Write-Host ""
    foreach ($e in $erros) { Write-Err $e }
    Write-Host ""
    Write-Host "Instale o que falta e rode o install.bat de novo." -ForegroundColor Yellow
    exit 1
}

# --- 3. Desenho dos slides ---------------------------------------------------
Write-Step "3. Instalando a biblioteca que desenha os slides (Playwright)"
$c = Invoke-Nativo "npm" @("install", "--no-fund", "--no-audit")
if ($c -ne 0) { $erros += "npm install falhou (codigo $c). Rode 'npm install' nesta pasta para ver o erro." } else { Write-Ok "Playwright instalado" }

Write-Step "4. Baixando o navegador interno dos slides (Chromium) - pode levar alguns minutos"
$c = Invoke-Nativo "npx" @("playwright", "install", "chromium")
if ($c -ne 0) { $erros += "Download do Chromium falhou (codigo $c). Rode 'npx playwright install chromium' para ver o erro." } else { Write-Ok "Chromium instalado" }

# --- 5. Python -----------------------------------------------------------------
Write-Step "5. Instalando as bibliotecas Python (imagens, download e transcricao dos videos)"
$c = Invoke-Nativo $py @("-m", "pip", "install", "--quiet", "-r", "$raiz\scripts\requirements.txt")
if ($c -ne 0) { $erros += "pip install falhou (codigo $c). Rode '$py -m pip install -r scripts\requirements.txt' para ver o erro." } else { Write-Ok "Bibliotecas Python instaladas" }

Write-Step "6. Baixando o modelo de transcricao (cerca de 500 MB, uma vez so) - pode levar alguns minutos"
if ($erros.Count -eq 0) {
    $c = Invoke-Nativo $py @("-c", "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')")
    if ($c -ne 0) { $avisos += "O modelo de transcricao nao baixou agora. Ele sera baixado na primeira transcricao." } else { Write-Ok "Modelo de transcricao baixado" }
} else {
    $avisos += "Modelo de transcricao nao baixado porque um passo anterior falhou."
}

# --- 7. Arquivo de chaves ------------------------------------------------------
Write-Step "7. Arquivo de chaves (.env)"
if (Test-Path "$raiz\.env") {
    Write-Ok ".env ja existe - nao foi mexido"
} else {
    Copy-Item "$raiz\.env.example" "$raiz\.env"
    Write-Ok ".env criado vazio. As chaves so entram se voce escolher Apify ou Metricool no cadastro; o agente mostra onde colar."
}

# --- Resumo --------------------------------------------------------------------
Write-Host ""
if ($erros.Count -gt 0) {
    Write-Host "INSTALACAO COM ERROS:" -ForegroundColor Red
    foreach ($e in $erros) { Write-Err $e }
    Write-Host ""
    exit 1
}

Write-Step "Conferencia final"
$env:PYTHONIOENCODING = "utf-8"
& $py "$raiz\scripts\instalar.py" checar
Remove-Item -Recurse -Force "$raiz\scripts\__pycache__" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Instalacao concluida!" -ForegroundColor Green
if ($avisos.Count -gt 0) {
    Write-Host ""
    foreach ($a in $avisos) { Write-Warn $a }
}
Write-Host ""
Write-Host "Proximo passo:" -ForegroundColor Cyan
Write-Host "  1. Abra esta pasta no Claude Code." -ForegroundColor White
Write-Host "  2. Digite /instaflow novo para fazer o cadastro do seu perfil." -ForegroundColor White
Write-Host "  3. Depois, /instaflow roda a primeira rodada." -ForegroundColor White
Write-Host ""
exit 0
