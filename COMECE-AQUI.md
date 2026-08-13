# Comece aqui

## O site já está no ar

```
https://gilbertosiebertfilho.github.io/Investimentos/
```

Esse é o link que você envia para as pessoas. **Ele nunca muda** — sempre mostra o
último lançamento publicado. Quem já tem o endereço só precisa recarregar a página.

O passo de criação já foi feito (o `publicar-primeira-vez.sh` não é mais necessário).

## Para atualizar (sempre que lançar saldos novos)

1. Abra o `livro-patrimonio.html`, lance os valores e clique em **Salvar lançamento**.
2. Clique em **Baixar para o site (index.html)**.
3. No Terminal, nesta pasta:

**Windows (PowerShell):**

```powershell
.\tools\atualizar-site.ps1 $HOME\Downloads\index.html
```

**macOS / Linux:**

```bash
./tools/atualizar-site.sh ~/Downloads/index.html
```

> No Windows o Python se chama `python`, não `python3` — por isso existe a versão
> `.ps1`. As duas fazem exatamente a mesma coisa: copiar o arquivo baixado,
> regenerar o site e publicar.

Em cerca de um minuto o link já mostra os números novos. Quem tiver o endereço
só precisa recarregar a página.

## O que você precisa saber sobre privacidade

Isto aqui foi uma escolha consciente, não um descuido — mas convém ter em mente:

**O repositório é público.** Os saldos estão legíveis por qualquer pessoa em
`github.com/GilbertoSiebertFilho/Investimentos`, sem precisar do link do site. A
alternativa (repositório privado com Pages) exige plano GitHub Pro, pago.

**O link não tem senha.** Quem o receber — ou a quem ele for repassado — vê os 13
saldos e o patrimônio total.

Se um dia quiser fechar isso, o caminho é **Cloudflare Pages + Access**: grátis, e a
única opção que trava de verdade — só entram os e-mails que você autorizar, que
recebem um código de acesso. Nesse cenário o repositório do GitHub volta a ser
privado e deixa de expor os números. Veja a seção final do `PUBLICAR.md`.
