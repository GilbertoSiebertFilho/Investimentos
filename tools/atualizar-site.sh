#!/usr/bin/env bash
# Uso: ./tools/atualizar-site.sh [arquivo-baixado.html]
# Copia o arquivo (se dado), regenera livro + site e publica no GitHub.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ $# -ge 1 ]; then cp "$1" livro-patrimonio.html; fi
python3 tools/gerar.py
git add -A
git commit -m "Atualiza livro: $(date +%d/%m/%Y-%H%M)" || echo "nada novo para commitar"
git push
echo "Enviado — o site atualiza em ~1 minuto (aba Actions mostra o progresso)."
