#!/usr/bin/env python3
"""
Regenera o livro-patrimonio.html a partir do template.

Fonte de verdade dos dados: o bloco entre /*DADOS_INICIO*/ e /*DADOS_FIM*/
dentro do próprio livro-patrimonio.html. Este script:

  1. lê os dados do HTML vivo (ou usa o seed de jul/ago-2026 se ele não existir);
  2. injeta os dados no template (template/evolucao-patrimonio-v9.html);
  3. reescreve o conteúdo estático (total do topo + livro razão) para que a
     página mostre os números mesmo em visualizadores sem JavaScript,
     como a pré-visualização do app Arquivos do iOS;
  4. grava o resultado em livro-patrimonio.html.

Uso:  python3 tools/gerar.py          (a partir da raiz do projeto)
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEMPLATE = RAIZ / "template" / "template.html"
SAIDA = RAIZ / "livro-patrimonio.html"

MESES_PT = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
MARCADOR = re.compile(r"/\*DADOS_INICIO\*/([\s\S]*?)/\*DADOS_FIM\*/")

# ------------------------------------------------------------------ seed
def seed():
    contas = [("Sicoob – aplicação fixa","BRL"),("Sicoob – conta corrente","BRL"),
              ("BTG","BRL"),("Bradesco","BRL"),("XP","BRL"),("Wise","BRL"),
              ("RBC","CAD"),("Wealthsimple – Gilberto + Karoline","CAD"),
              ("NEO – Gilberto","CAD"),("NEO – Karoline","CAD"),
              ("Depósito casa","CAD"),("Avenue","USD"),("Conta Rio Fortuna","BRL")]
    ids = ["c%02d" % i for i in range(1, 14)]
    jul = [221531.06,914.52,1267614.87,119.20,23026.92,0.36,
           34.89,137419.88,3.43,23.00,1600.00,86716.47,1419746.02]
    ago = [224234.62,3201.52,1291485.31,213.67,23309.21,0.36,
           102.94,139148.83,3.43,23.56,1600.00,87444.11,1497885.24]
    return {
        "accounts": [{"id":ids[i],"name":n,"cur":c} for i,(n,c) in enumerate(contas)],
        "months": {
            "2026-07-01": {"data":"2026-07-01","fx":{"cad":3.65,"usd":5.20},
                        "vals":{ids[i]:jul[i] for i in range(13)}},
            "2026-08-03": {"data":"2026-08-03","fx":{"cad":3.62,"usd":5.08},
                        "vals":{ids[i]:ago[i] for i in range(13)}},
        },
    }

# ------------------------------------------------------------------ util
def nf(n, d=2):
    return f"{n:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")

def rotulo(k):
    partes = k.split("-")
    y, m = partes[0], partes[1]
    d = partes[2] + " " if len(partes) > 2 else ""
    return d + MESES_PT[int(m)-1] + "/" + y[2:]

def data_br(iso):
    return f"{iso[8:]}/{iso[5:7]}/{iso[:4]}"

def extrair_dados(html):
    m = MARCADOR.search(html)
    if not m:
        return None
    bruto = m.group(1).strip()
    if bruto == "null":
        return None
    return json.loads(bruto)  # \uXXXX é JSON válido; json.loads decodifica sozinho

# ------------------------------------------------------------------ main
def main():
    carga = None
    if SAIDA.exists():
        try:
            carga = extrair_dados(SAIDA.read_text(encoding="utf-8"))
            if carga:
                print(f"dados lidos de {SAIDA.name}")
        except Exception as e:
            print("aviso: não consegui ler os dados do HTML vivo:", e)
    if not carga:
        carga = {"dados": seed(), "atualizadoEm": "2026-08-03T09:40:00"}
        print("usando o seed de jul/ago-2026")

    dados = carga["dados"]
    accounts, months = dados["accounts"], dados["months"]
    for k in list(months):                       # migra chave mensal antiga -> data completa
        if len(k) == 7:
            nova = months[k].get("data") or (k + "-28")
            if nova not in months:
                months[nova] = months.pop(k)
    for k in months:
        months[k]["data"] = k

    def taxa(m, cur):
        return m["fx"]["cad"] if cur == "CAD" else m["fx"]["usd"] if cur == "USD" else 1
    def reais(k, a):
        return months[k]["vals"].get(a["id"], 0) * taxa(months[k], a["cur"])
    def total(k):
        return sum(reais(k, a) for a in accounts)

    ks = sorted(months)
    src = TEMPLATE.read_text(encoding="utf-8")

    # -------- conteúdo estático (aparece mesmo sem JavaScript) --------
    # Regra 4 do CLAUDE.md: o que o renderPlate() escreve em JS precisa existir
    # aqui também, senão o site publicado e a pré-visualização do app Arquivos do
    # iOS (que não roda script) mostram o total em reais ao lado de "US$ —".
    def total_usd(k):
        u = months[k]["fx"].get("usd") or 0
        return total(k) / u if u > 0 else None

    ult = ks[-1]
    t = total(ult)
    tu = total_usd(ult)
    fxu = months[ult]["fx"].get("usd") or 0
    src = src.replace('<p class="total" id="totalNow"><span class="cifra">R$</span>—</p>',
        f'<p class="total" id="totalNow"><span class="cifra">R$</span>{nf(t)}</p>')
    src = src.replace('<p class="total sec" id="totalUsd"><span class="cifra">US$</span>—</p>',
        f'<p class="total sec" id="totalUsd"><span class="cifra">US$</span>{nf(tu) if tu is not None else "—"}</p>')
    src = src.replace('<span class="cot" id="capUsd"></span>',
        '<span class="cot" id="capUsd">'
        + (f'US$ 1 = R$ {nf(fxu,4)}' if tu is not None else 'sem câmbio')
        + '</span>')
    src = src.replace('<span id="mesRef" class="muted">sem lançamentos</span>',
        f'<span id="mesRef" class="muted">{rotulo(ult)}</span>')
    if len(ks) > 1:
        ant = ks[-2]
        d = t - total(ant); p = (t/total(ant) - 1) * 100
        sinal = "+" if d >= 0 else "−"
        classe = "up" if d > 0 else "down" if d < 0 else "flat"
        src = src.replace('<span id="deltaMes" class="delta flat"></span>',
            f'<span id="deltaMes" class="delta {classe}">{sinal}R$ {nf(abs(d))}  ({sinal}{nf(abs(p))}%) vs {rotulo(ant)}</span>')
        # Com um unico lancamento anterior o acumulado E' a variacao do periodo;
        # repetir o mesmo numero custa uma linha inteira do cabecalho no celular.
        # Mesma regra do renderPlate() -- os dois caminhos precisam concordar.
        if len(ks) > 2:
            pa = (t/total(ks[0]) - 1) * 100
            sa = "+" if pa >= 0 else "−"
            src = src.replace('<span id="deltaAcum" class="muted"></span>',
                f'<span id="deltaAcum" class="muted">acumulado desde {rotulo(ks[0])}: R$ {sa}{nf(abs(pa))}%</span>')

        tu_ant, tu_ini = total_usd(ant), total_usd(ks[0])
        if tu is not None and tu_ant:
            du = tu - tu_ant; pu = (tu/tu_ant - 1) * 100
            su = "+" if du >= 0 else "−"
            cu = "up" if du > 0 else "down" if du < 0 else "flat"
            src = src.replace('<span id="deltaMesUsd" class="delta flat"></span>',
                f'<span id="deltaMesUsd" class="delta {cu}">{su}US$ {nf(abs(du))}  ({su}{nf(abs(pu))}%) vs {rotulo(ant)}</span>')
            if tu_ini and len(ks) > 2:
                pau = (tu/tu_ini - 1) * 100
                sau = "+" if pau >= 0 else "−"
                src = src.replace('<span id="deltaAcumUsd" class="muted"></span>',
                    f'<span id="deltaAcumUsd" class="muted">US$ {sau}{nf(abs(pau))}%</span>')
            fx0 = months[ant]["fx"].get("usd") or 0
            if fx0 > 0 and abs(pu - p) >= 0.05:
                dif = pu - p
                pfx = (fxu/fx0 - 1) * 100
                spfx = "+" if pfx > 0 else "−" if pfx < 0 else ""
                src = src.replace('<p class="duo-nota" id="duoNota"></p>',
                    f'<p class="duo-nota" id="duoNota">Dólar <b>{spfx}{nf(abs(pfx))}%</b> desde '
                    f'{rotulo(ant)} — por isso a leitura em dólares fica <b>{nf(abs(dif))} p.p. '
                    f'{"acima" if dif > 0 else "abaixo"}</b> da leitura em reais.</p>')

    fx = months[ult]["fx"]
    brl_tot = sum(months[ult]["vals"].get(a["id"],0) for a in accounts if a["cur"]=="BRL")
    cad = sum(months[ult]["vals"].get(a["id"],0) for a in accounts if a["cur"]=="CAD")
    usd = sum(months[ult]["vals"].get(a["id"],0) for a in accounts if a["cur"]=="USD")
    src = src.replace('<div class="split" id="split"></div>',
        '<div class="split" id="split">'
        f'<span>R$ {nf(brl_tot)} em reais</span>'
        f'<span>C$ {nf(cad)} × {nf(fx["cad"],4)} = R$ {nf(cad*fx["cad"])}</span>'
        f'<span>US$ {nf(usd)} × {nf(fx["usd"],4)} = R$ {nf(usd*fx["usd"])}</span></div>')
    if len(ks) > 1:
        a0 = ks[-2]
        ef_s = ef_c = 0.0
        for a in accounts:
            v0 = months[a0]["vals"].get(a["id"], 0)
            v1 = months[ult]["vals"].get(a["id"], 0)
            ef_s += (v1 - v0) * taxa(months[a0], a["cur"])
            ef_c += v1 * (taxa(months[ult], a["cur"]) - taxa(months[a0], a["cur"]))
        fmt = lambda v: ("+" if v >= 0 else "−") + "R$ " + nf(abs(v))
        cor = lambda v: "up" if v > 0 else "down" if v < 0 else "flat"
        src = src.replace('<div class="split" id="efeitos"></div>',
            '<div class="split" id="efeitos">'
            f'<span>Δ por saldo: <b class="{cor(ef_s)}">{fmt(ef_s)}</b></span>'
            f'<span>Δ por câmbio: <b class="{cor(ef_c)}">{fmt(ef_c)}</b></span></div>')

    th = "".join(f'<th>{a["name"]}{" ("+a["cur"]+")" if a["cur"]!="BRL" else ""}</th>'
                 for a in accounts)
    rows = ""
    for i, k in enumerate(reversed(ks)):
        ant = ks[-(i+2)] if i + 2 <= len(ks) else None
        m, tk = months[k], total(k)
        if ant:
            dd = tk - total(ant)
            dc = "up" if dd > 0 else "down" if dd < 0 else "flat"
            dtxt = ("+" if dd > 0 else "−") + nf(abs(dd))
            pv = (tk/total(ant) - 1) * 100
            ptxt = ("+" if pv >= 0 else "−") + nf(abs(pv)) + "%"
        else:
            dc, dtxt, ptxt = "flat", "—", "—"
        cells = "".join(f"<td>{nf(reais(k,a))}</td>" for a in accounts)
        rows += (f'<tr><td class="mes">{rotulo(k)}</td><td>{data_br(m["data"])}</td>'
                 f'<td class="tot">{nf(tk)}</td><td class="{dc}">{dtxt}</td>'
                 f'<td class="{dc}">{ptxt}</td>'
                 f'<td class="fxtd">{nf(m["fx"]["cad"],4)}</td>'
                 f'<td class="fxtd">{nf(m["fx"]["usd"],4)}</td>'
                 f'{cells}<td class="act"></td></tr>')
    tabela = ('<div class="scroller"><table><thead><tr><th class="mes">Lançamento</th>'
              '<th>Data</th><th class="tot">Total R$</th><th>Δ R$</th><th>Δ%</th>'
              f'<th>CAD</th><th>USD</th>{th}<th></th></tr></thead>'
              f'<tbody>{rows}</tbody></table></div>')
    src = src.replace('<div id="ledgerWrap"></div>', f'<div id="ledgerWrap">{tabela}</div>')

    # -------- injetar os dados --------
    js = json.dumps(carga, ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e")
    assert MARCADOR.search(src), "template sem marcadores DADOS_INICIO/FIM"
    src = MARCADOR.sub(lambda _: "/*DADOS_INICIO*/" + js + "/*DADOS_FIM*/", src, count=1)

    SAIDA.write_text(src, encoding="utf-8")
    site = RAIZ / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(src, encoding="utf-8")
    print(f"gerado: {SAIDA.name} e site/index.html · {len(src):,} bytes · último {rotulo(ult)} · total R$ {nf(t)}")

if __name__ == "__main__":
    main()
