# Livro do patrimônio — acompanhamento mensal

Rastreador mensal do patrimônio financeiro líquido de uma família (Gilberto & Karoline),
com contas no Brasil, Canadá e EUA. Página HTML única, autocontida, em pt-BR.

## O que é cada arquivo

| Arquivo | Papel |
|---|---|
| `livro-patrimonio.html` | **O produto e o banco de dados.** Página que o usuário abre no navegador, lança os meses e compartilha por WhatsApp. Os dados moram DENTRO dele. |
| `template/template.html` | Molde sem dados. Só é editado quando se muda funcionalidade/estilo; depois roda-se o gerador. |
| `tools/gerar.py` | Reconstrói `livro-patrimonio.html`: lê os dados do HTML vivo (ou o seed), injeta no template e reescreve o conteúdo estático. |
| `docs/` | Contexto de negócio: modelo Excel de projeção patrimonial até 2080 e relatório de análise. Não fazem parte do app. |

## Arquitetura — o que NÃO mudar sem entender

1. **Dados embutidos no próprio HTML.** O estado (contas + meses) vive num JSON entre
   os marcadores `/*DADOS_INICIO*/ ... /*DADOS_FIM*/` (constante `DADOS_EMBUTIDOS`).
   O botão **"Baixar arquivo atualizado"** serializa o estado, injeta entre os marcadores
   e baixa um HTML novo — que passa a ser o original. Motivo: o usuário envia o arquivo
   por WhatsApp e abre no iPhone; qualquer dependência EXCLUSIVA de armazenamento
   externo fez a página chegar em branco para os outros. Foi o maior bug do projeto.
   Regra atual: o embutido é a fonte que viaja; `localStorage` (chave
   `livro-patrimonio-local-v1`) é uma CAMADA DE CONVENIÊNCIA por cima — cada Salvar
   grava ali automaticamente, então fechar e reabrir o mesmo arquivo no mesmo
   navegador preserva os lançamentos sem download. No load, vence quem tiver
   `atualizadoEm` maior (arquivo novo baixado substitui e realinha a cópia local;
   cópia local mais nova é carregada e o painel marca "Salvo neste aparelho").
   O download continua sendo o ÚNICO caminho para enviar/publicar — nunca depender
   só do localStorage (navegadores podem expurgar dados de páginas locais), e nunca
   remover o embutido. `beforeunload` só avisa se nem o localStorage funcionou.
   "Descartar alterações locais" limpa a chave e recarrega.

2. **Dois modos, detectados no load.** `DADOS_EMBUTIDOS` preenchido → `modoArquivo`
   (arquivo local: sem `window.storage`, botão de restaurar escondido).
   `DADOS_EMBUTIDOS === null` → modo rascunho dentro do claude.ai (usa
   `window.storage` pessoal). O antigo sistema de "publicar/compartilhar com
   código" foi removido por não funcionar fora do claude.ai; não recriar.

3. **Cotação do dia em cascata (5 fontes, sempre todas).** `buscarCotacao` tenta,
   nesta ordem e com timeout de 6 s por fonte (30 s na última): AwesomeAPI
   (comercial BR) → Open ER-API → Frankfurter (BCE) → Currency-API via jsDelivr →
   busca web via `api.anthropic.com`. A lista é a MESMA em todos os ambientes de
   propósito: no iframe do claude.ai as públicas são bloqueadas e a da Anthropic
   funciona; em arquivo local é o inverso — cada ambiente falha rápido nas fontes
   erradas e acerta numa das suas. O status mostra o progresso (n/5 e o nome da
   fonte) e, se todas falharem, orienta a digitar à mão. Cache diário em memória +
   `window.storage` quando existir. A cotação NUNCA sobrescreve o câmbio de um
   lançamento já salvo sozinha — datas novas herdam a cotação do dia; num
   lançamento gravado, só o botão manual preenche os campos, e salvar continua
   sendo ação do usuário.

4. **Conteúdo estático pré-renderizado.** A pré-visualização do app Arquivos do iOS não
   executa JavaScript. Por isso o cabeçalho (total, deltas, decomposição) e o livro
   razão também existem como HTML estático: o `gerar.py` os escreve, e o botão de
   download dentro da página os regenera via `ledgerEstatico()` (tabela SEM inputs).
   Um `<noscript>` avisa quando os botões não respondem. Ao mudar o layout dessas
   áreas, manter os três caminhos em sincronia: render dinâmico, `ledgerEstatico()` no
   JS e o bloco estático do `gerar.py`.

5. **Sem `confirm()`/`prompt()`/`alert()`.** Bloqueados no iframe do claude.ai — botões
   pareciam mortos. Usar o diálogo próprio (`confirmar`/`perguntar`, elemento `#modal`).

6. **Números pt-BR.** `parseNum` aceita "1.234,56" e "1234.56"; exibição via `nf`.
   Percentuais com base 0/indefinida retornam `null` → exibir "—".

## Modelo de dados

```json
{
  "dados": {
    "accounts": [{ "id": "c01", "name": "BTG", "cur": "BRL|CAD|USD" }],
    "months": {
      "2026-08-03": {
        "data": "2026-08-03",
        "fx": { "cad": 3.62, "usd": 5.08 },
        "vals": { "c01": 1291485.31 }
      }
    }
  },
  "atualizadoEm": "ISO-8601"
}
```

**Granularidade diária:** a chave de `months` é a data completa `YYYY-MM-DD` (o campo
`data` interno é mantido igual à chave). O usuário lança quando quiser — uma vez por
mês ou vários dias no mês. Chaves mensais antigas (`YYYY-MM`) são migradas para a data
do campo `data` tanto no `load()` do JS quanto no `gerar.py`; não quebrar essa migração.
Editar a data no livro razão MOVE o registro de chave (com checagem de colisão).
Saldos gravados **na moeda da conta**; conversão BRL na leitura com o `fx` daquele
lançamento — nunca converter com taxa de outro dia.

**Cabeçalho vivo:** o topo (total, deltas, split, efeitos) é um espelho do
FORMULÁRIO da data em foco (`mesInput`), recalculado a cada tecla via
`snapshotForm()`/`totalSnap()` no fim de `atualizarForm()` — nunca chamar
`renderPlate()` antes de `renderForm()` ter montado os campos (`renderAll` respeita
essa ordem). Um selo indica o estado: "prévia — ainda não gravada" (data sem
lançamento), "editando — alterações não gravadas" (`formDifereDoSalvo`), ou
"lançamento antigo". A comparação é sempre contra o maior lançamento salvo ANTERIOR
à data em foco. A página abre com `mesInput` na última data salva (sem selo);
escolher uma data nova herda os campos e recebe a cotação do dia automaticamente.
Clicar numa linha do livro razão põe aquela data em foco (e `selecionado` marca a
linha e o ponto dourado do gráfico); salvar também. "Variação por conta" segue o
maior lançamento salvo até a data em foco.

## Estado atual dos dados (verificação de sanidade)

| Chave | Data | FX CAD/USD | Total BRL |
|---|---|---|---|
| 2026-07-01 | 01/07/2026 | 3,65 / 5,20 | R$ 3.891.524,97 |
| 2026-08-03 | 03/08/2026 | 3,62 / 5,08 | R$ 3.994.527,12 |

Decomposição ago vs jul: Δ por saldo +R$ 117.721,80 · Δ por câmbio −R$ 14.719,66
(identidade: Δ = Σ(v1−v0)·fx0 + Σ v1·(fx1−fx0)).

13 contas: 7 BRL (Sicoob fixa, Sicoob corrente, BTG, Bradesco, XP, Wise, Conta Rio
Fortuna), 5 CAD (RBC, Wealthsimple, NEO Gilberto, NEO Karoline, Depósito casa),
1 USD (Avenue). Escopo deliberado: só ativos líquidos; recebíveis, fazenda, gado e
imóveis ficam fora (não variam mês a mês — estão no modelo Excel em `docs/`).

## Funcionalidades da página

- Lançamento mensal com campos pré-preenchidos do mês anterior, data do levantamento
  e câmbio do dia — buscado automaticamente ao abrir (cascata de fontes públicas,
  cache diário) e sempre editável, inclusive inline no livro razão.
- Cabeçalho: total, Δ mês (R$ e %), acumulado, decomposição BRL/CAD/USD e
  **Δ por saldo × Δ por câmbio**; botão **"ocultar valores"** (blur de privacidade
  para abrir a página em público).
- Gráfico SVG da evolução; "Variação por conta" (Δ% na moeda × em R$ × acumulado).
- Livro razão em 3 modos (R$ / moeda original / Δ%), editar/excluir por mês.
- Exportar CSV (`;`, decimal vírgula, BOM UTF-8) e **impressão A4 paisagem limpa**
  (`@media print` esconde formulários/botões — serve como PDF de relatório).

## Fluxo de trabalho no Code

- Mudou funcionalidade/estilo → editar `template/template.html`, rodar
  `python3 tools/gerar.py` (preserva os dados do HTML vivo), abrir
  `livro-patrimonio.html` no navegador e conferir os totais da tabela acima.
- Estética: paleta verde-papel (`--paper #F3F6F1`, `--ink #16221B`), IBM Plex Mono
  para números (tabular), IBM Plex Sans para texto. O total do topo é IBM Plex Mono
  600 — já foi serifada e a legibilidade era ruim; não voltar.
- Sem build/npm. É um HTML só, e deve continuar assim: abrir em qualquer celular
  sem internet é requisito, não acidente.

## Repositório e publicação

Repositório: **Investimentos** (branch `main`). Já inicializado, com
`.github/workflows/pages.yml` publicando a pasta `site/` via GitHub Actions a cada
push. Ligar uma vez em Settings → Pages → Source: GitHub Actions. Ver `PUBLICAR.md`.

Atualizar tudo (copiar arquivo baixado → regenerar → commit → push):
`./tools/atualizar-site.sh [arquivo.html]`.

ATENÇÃO ao criar o repo: `site/index.html` contém os saldos reais. Em repositório
público eles ficam legíveis por qualquer um direto no GitHub, sem sequer abrir o
site. Sempre confirmar com o usuário antes de tornar público; o padrão sugerido é
`--private` (Pages privado exige plano pago) ou Netlify/Cloudflare Pages.

## Publicação por link (alternativas sem GitHub)

O usuário quer que pessoas com um link vejam o livro sempre atualizado. O caminho é
hospedar `site/index.html` (o `gerar.py` mantém essa cópia em dia) num host estático
de URL fixa. O template já carrega `noindex,nofollow`, mas **o link em si não tem
senha**: quem o tiver vê todos os saldos — reforçar isso ao usuário a cada mudança
de hospedagem.

Fluxo de atualização (executar quando o usuário trouxer um arquivo novo baixado do
navegador, ou após lançar via edição direta):
1. Substituir `livro-patrimonio.html` pelo arquivo mais recente do usuário.
2. `python3 tools/gerar.py` (normaliza, regenera o estático e atualiza `site/index.html`).
3. Publicar `site/` no host escolhido.

Receita A — GitHub Pages (repo público; Pages em repo privado exige plano pago):
```
gh repo create livro-patrimonio --public --source=. --push
gh api -X POST repos/{owner}/livro-patrimonio/pages -f build_type=workflow  # ou via UI: Settings > Pages > branch main /site
```
Mais simples pela UI: Settings → Pages → Deploy from branch → `main` + pasta `/site`.
URL fixa: `https://<user>.github.io/livro-patrimonio/`. Atualização = commit + push.

Receita B — Netlify (aceita arrastar a pasta; URL fixa após criar o site):
```
npx netlify-cli deploy --dir=site --prod
```
Netlify não indexa por padrão e a URL aleatória ajuda, mas continua sem senha.

Nunca publicar o repositório com dados se o usuário pedir privacidade: nesse caso,
sugerir Cloudflare Pages + Access (grátis, exige e-mail autorizado) antes de subir.

## Próximos passos prováveis

- Lançar setembro/2026 quando os saldos fecharem.
- Automatizar o passo "arquivo baixado → site publicado" com um comando só.
- Gráficos por conta ou por moeda; metas; comparação com o modelo Excel de `docs/`.
