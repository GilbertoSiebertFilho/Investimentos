#!/usr/bin/env bash
# Cria o repositório no GitHub, liga o GitHub Pages e publica o site.
# Rode uma única vez:  ./tools/publicar-primeira-vez.sh
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="Investment"
verde()   { printf "\033[32m%s\033[0m\n" "$1"; }
amarelo() { printf "\033[33m%s\033[0m\n" "$1"; }
vermelho(){ printf "\033[31m%s\033[0m\n" "$1"; }

echo
echo "======================================================"
echo "  Publicar o Livro do Patrimônio no GitHub Pages"
echo "======================================================"
echo

# ---------- 1. GitHub CLI ----------
if ! command -v gh >/dev/null 2>&1; then
  vermelho "O GitHub CLI (gh) não está instalado."
  echo
  echo "Instale com um destes comandos e rode este script de novo:"
  echo "  macOS:    brew install gh"
  echo "  Windows:  winget install GitHub.cli"
  echo "  Linux:    sudo apt install gh"
  echo
  echo "Sem o gh, siga o passo a passo manual em PUBLICAR.md."
  exit 1
fi

# ---------- 2. login ----------
if ! gh auth status >/dev/null 2>&1; then
  amarelo "Você ainda não entrou na sua conta do GitHub."
  echo "Vai abrir o navegador para você fazer login — é seguro, a senha fica só com o GitHub."
  echo
  gh auth login
fi
USUARIO="$(gh api user --jq .login)"
verde "Conectado como: $USUARIO"
echo

# ---------- 3. público ou privado ----------
echo "O site conterá TODOS os seus saldos (hoje, R$ 3.994.527,12)."
echo
echo "  1) Privado  — ninguém lê o código no GitHub."
echo "                O GitHub Pages exige plano Pro (pago) nesse caso."
echo "  2) Público  — Pages grátis, MAS qualquer pessoa consegue ler os saldos"
echo "                direto no GitHub, sem nem abrir o link do site."
echo
read -r -p "Escolha 1 ou 2 [1]: " ESCOLHA
ESCOLHA="${ESCOLHA:-1}"
if [ "$ESCOLHA" = "2" ]; then
  VIS="--public"
  amarelo "Repositório PÚBLICO — os saldos ficarão legíveis por qualquer pessoa."
  read -r -p "Digite CONFIRMO para prosseguir: " C
  [ "$C" = "CONFIRMO" ] || { echo "Cancelado."; exit 1; }
else
  VIS="--private"
  verde "Repositório privado."
fi
echo

# ---------- 4. commit pendente ----------
git add -A
git commit -q -m "Atualiza livro antes de publicar" 2>/dev/null || true

# ---------- 5. criar/conectar o repositório ----------
if gh repo view "$USUARIO/$REPO" >/dev/null 2>&1; then
  amarelo "O repositório $REPO já existe — vou apenas enviar as mudanças."
  git remote get-url origin >/dev/null 2>&1 || \
    git remote add origin "https://github.com/$USUARIO/$REPO.git"
  git push -u origin main
else
  echo "Criando o repositório $REPO..."
  gh repo create "$REPO" $VIS --source=. --remote=origin --push
fi
verde "Código enviado."
echo

# ---------- 6. ligar o Pages ----------
echo "Ligando o GitHub Pages..."
if gh api -X POST "repos/$USUARIO/$REPO/pages" -f build_type=workflow >/dev/null 2>&1; then
  verde "Pages ativado."
else
  gh api -X PUT "repos/$USUARIO/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 \
    && verde "Pages já estava ativado — configuração conferida." \
    || amarelo "Não consegui ativar automaticamente (comum em repositório privado sem plano Pro).
   Ative em: https://github.com/$USUARIO/$REPO/settings/pages
   → Source: GitHub Actions"
fi
echo

# ---------- 7. fim ----------
echo "======================================================"
verde "  Pronto!"
echo
echo "  Seu link:  https://$USUARIO.github.io/$REPO/"
echo
echo "  A primeira publicação leva 1 a 2 minutos. Acompanhe em:"
echo "  https://github.com/$USUARIO/$REPO/actions"
echo
echo "  Para atualizar depois de lançar novos saldos:"
echo "    ./tools/atualizar-site.sh ~/Downloads/livro-patrimonio-AAAA-MM-DD.html"
echo "======================================================"
echo
