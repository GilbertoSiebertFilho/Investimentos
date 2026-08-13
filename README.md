# Livro do patrimônio

Acompanhamento mensal do patrimônio financeiro da família, num arquivo HTML só.

## Uso do dia a dia (sem programar nada)

1. Abra `livro-patrimonio.html` num navegador (duplo clique no computador).
2. Lance o mês: data, câmbio do dia, saldos — os campos já vêm com o mês anterior.
3. Clique em **Baixar arquivo atualizado** no painel do topo.
4. O arquivo baixado é o novo original: guarde-o, envie por WhatsApp e apague o antigo.

## Para mexer no código (com o Claude Code)

Abra um terminal nesta pasta e rode `claude`. O arquivo `CLAUDE.md` já conta ao
Claude Code toda a história e as regras do projeto — é só pedir o que quiser
("lance setembro com estes números", "adicione um gráfico por moeda", etc.).

Depois de qualquer mudança em `template/template.html`, rode:

    python3 tools/gerar.py

Isso reconstrói o `livro-patrimonio.html` preservando os dados já lançados.

## Link para a família acompanhar

A pasta `site/` contém sempre a última versão pronta para hospedar. Publicando-a
uma vez no GitHub Pages ou Netlify, você ganha um link fixo; daí em diante, cada
atualização é: substituir `livro-patrimonio.html` pelo arquivo baixado, rodar
`python3 tools/gerar.py` e publicar de novo (o Claude Code faz os três passos por
você se pedir "atualize o site"). Atenção: o link não tem senha — quem o tiver vê
todos os saldos.

## Estrutura

    livro-patrimonio.html   ← o app, com os dados dentro (jul e ago/2026)
    CLAUDE.md               ← contexto para o Claude Code
    tools/gerar.py          ← reconstrói o app a partir do template
    template/               ← molde sem dados (template.html)
    site/index.html         ← o que vai para o ar (link da família)
    tools/atualizar-site.sh ← regenera e publica num comando
    PUBLICAR.md             ← como criar o repositório e ligar o GitHub Pages
    docs/                   ← modelo Excel de projeção até 2080 + relatório
