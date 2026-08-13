# Versao Windows do atualizar-site.sh (mesmo comportamento, PowerShell nativo).
# Uso:  .\tools\atualizar-site.ps1 [caminho-do-arquivo-baixado.html]
#
# No Windows o executavel e' "python", nao "python3" — foi por isso que o .sh
# original nao rodava aqui fora do Git Bash.

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if ($args.Count -ge 1) {
    if (-not (Test-Path $args[0])) { throw "Arquivo nao encontrado: $($args[0])" }
    Copy-Item $args[0] 'livro-patrimonio.html' -Force
    Write-Host "copiado: $($args[0])" -ForegroundColor Green
}

$py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { 'py' }
$env:PYTHONIOENCODING = 'utf-8'
& $py tools/gerar.py
if ($LASTEXITCODE -ne 0) { throw "gerar.py falhou" }

git add -A
git commit -m "Atualiza livro: $(Get-Date -Format 'dd/MM/yyyy-HHmm')"
if ($LASTEXITCODE -ne 0) { Write-Host "nada novo para commitar" -ForegroundColor Yellow }
git push
if ($LASTEXITCODE -ne 0) { throw "git push falhou" }

Write-Host ""
Write-Host "Enviado — o site atualiza em ~1 minuto." -ForegroundColor Green
Write-Host "Acompanhe em: https://github.com/$(git config user.github 2>$null)/Investment/actions"
