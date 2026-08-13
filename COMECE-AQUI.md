# Comece aqui

## Para criar o site (uma vez só)

Abra o Terminal **nesta pasta** e cole:

```bash
./tools/publicar-primeira-vez.sh
```

O script faz tudo: entra na sua conta do GitHub, pergunta se o repositório deve ser
privado ou público, cria o repositório `Investment`, liga o GitHub Pages e publica.
No fim ele mostra o seu link, que é sempre:

```
https://SEU-USUARIO.github.io/Investment/
```

Esse link nunca muda. É ele que você envia para as pessoas.

> **Como abrir o Terminal nesta pasta**
> - **macOS:** clique com o botão direito na pasta → Serviços → Novo Terminal na Pasta
> - **Windows:** clique com o botão direito dentro da pasta → Abrir no Terminal
> - Ou, no Claude Code, é só pedir: "rode o publicar-primeira-vez"

## Para atualizar (sempre que lançar saldos novos)

1. Abra o `livro-patrimonio.html`, lance os valores e clique em **Salvar lançamento**.
2. Clique em **Baixar para o site (index.html)**.
3. No Terminal, nesta pasta:

```bash
./tools/atualizar-site.sh ~/Downloads/index.html
```

Em cerca de um minuto o link já mostra os números novos. Quem tiver o endereço
só precisa recarregar a página.

## Duas coisas que valem saber

**O link não tem senha.** Quem o receber — ou a quem ele for repassado — vê todos os
saldos. Se quiser restringir a pessoas específicas, veja a seção final do `PUBLICAR.md`
(Cloudflare Access, grátis, com login por e-mail autorizado).

**Repositório público expõe os saldos no próprio GitHub**, mesmo sem o link do site.
Por isso o script pergunta e sugere privado. Pages em repositório privado exige plano
Pro; se preferir não pagar, o `PUBLICAR.md` mostra como usar o Netlify de graça sem
expor o código.
