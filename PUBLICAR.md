# Publicar no GitHub Pages — passo a passo

## 1. Criar o repositório (uma vez)

No computador, dentro desta pasta:

```bash
gh repo create Investimentos --private --source=. --push
```

Sem o GitHub CLI? Crie o repositório `Investimentos` em github.com/new e depois:

```bash
git remote add origin https://github.com/SEU-USUARIO/Investimentos.git
git push -u origin main
```

## 2. Ligar o GitHub Pages (uma vez)

No repositório: **Settings → Pages → Source: GitHub Actions**.

O arquivo `.github/workflows/pages.yml` já está pronto — ele publica a pasta `site/`
a cada push para `main`. O endereço fica:

```
https://SEU-USUARIO.github.io/Investimentos/
```

Esse é o link para enviar. Ele nunca muda.

## 3. Atualizar (sempre que lançar algo)

```bash
./tools/atualizar-site.sh ~/Downloads/livro-patrimonio-2026-09-01.html
```

O script copia o arquivo baixado, regenera o site e faz commit + push.
Em cerca de um minuto o link já mostra os números novos (acompanhe na aba **Actions**).

Se você editou direto pelo Claude Code, sem baixar nada, rode sem argumento:

```bash
./tools/atualizar-site.sh
```

## Público ou privado?

| | Repositório privado | Repositório público |
|---|---|---|
| Código e dados visíveis a estranhos | Não | **Sim — inclusive os saldos** |
| GitHub Pages | Exige plano pago (Pro/Team) | Grátis |

O arquivo publicado contém todos os saldos. Num repositório **público**, qualquer
pessoa pode ler o `site/index.html` direto no GitHub, mesmo sem o link do site.

Alternativas se você não quiser plano pago:

- **Netlify** (grátis): publica a pasta `site/` sem expor o código-fonte a ninguém.
  `npx netlify-cli deploy --dir=site --prod`
- **Cloudflare Pages + Access** (grátis): mesmo esquema do Netlify, mas com login por
  e-mail autorizado — a única opção aqui que realmente restringe quem vê os valores.

Em qualquer caso: o link em si não tem senha. Quem o receber, ou a quem ele for
repassado, vê o patrimônio inteiro.
