# Versao Windows do atualizar-site.sh (mesmo comportamento, PowerShell nativo).
#
# Uso:  .\tools\atualizar-site.ps1 [caminho-do-arquivo-baixado.html]
#
# No Windows o executavel do Python e' "python", nao "python3" -- por isso o .sh
# original so roda no Git Bash e este arquivo existe.
#
# DUAS ARMADILHAS DO POWERSHELL 5.1 que ja quebraram este script:
#
# 1. Mantenha o arquivo somente em ASCII. O PowerShell 5.1 le UTF-8 sem BOM como
#    ANSI; um travessao vira aspa curva, que ele trata como delimitador de string,
#    e o parse morre com "a cadeia de caracteres nao tem o terminador".
#
# 2. Nao use $ErrorActionPreference = 'Stop' aqui. O git escreve avisos normais
#    em stderr e, com Stop, o PowerShell promove esses avisos a erro fatal. O
#    controle correto e' checar $LASTEXITCODE, que e' o que este script faz.

Set-Location (Split-Path -Parent $PSScriptRoot)

function Parar($msg) { Write-Host $msg -ForegroundColor Red; exit 1 }

# ---------- 1. copiar o arquivo baixado, se veio um ----------
if ($args.Count -ge 1) {
    if (-not (Test-Path $args[0])) { Parar "Arquivo nao encontrado: $($args[0])" }
    Copy-Item $args[0] 'livro-patrimonio.html' -Force
    Write-Host "copiado: $($args[0])" -ForegroundColor Green
}

# ---------- 2. regenerar o livro e o site ----------
$py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { 'py' }
$env:PYTHONIOENCODING = 'utf-8'
& $py tools/gerar.py
if ($LASTEXITCODE -ne 0) { Parar "gerar.py falhou" }

# ---------- 3. commitar, se houver mudanca ----------
git add -A
if ($LASTEXITCODE -ne 0) { Parar "git add falhou" }

if ([string]::IsNullOrWhiteSpace((git status --porcelain))) {
    Write-Host "nada novo para publicar (o site ja esta em dia)." -ForegroundColor Yellow
    exit 0
}

git commit -m "Atualiza livro: $(Get-Date -Format 'dd/MM/yyyy-HHmm')"
if ($LASTEXITCODE -ne 0) { Parar "git commit falhou" }

# ---------- 4. publicar ----------
git push
if ($LASTEXITCODE -ne 0) { Parar "git push falhou" }

Write-Host ""
Write-Host "Enviado. O site atualiza em cerca de 1 minuto." -ForegroundColor Green
Write-Host "Link:      https://gilbertosiebertfilho.github.io/Investimentos/"
Write-Host "Progresso: https://github.com/GilbertoSiebertFilho/Investimentos/actions"
