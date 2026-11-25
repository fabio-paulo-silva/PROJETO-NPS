"""Cruza os pedidos do Clique e Retire com as respostas do NPS e gera os dados do painel.

Entradas (ficam só no computador, fora do Git):
- Base_Pedidos_Clique&Retire/*.xlsx : pedidos do Clique e Retire (coluna PEDIDO, ex.: 168206009BOT)
- base_nps/*.xlsx                   : exportação do survey de NPS (cabeçalho na linha 3; coluna "Código do pedido")
- dCentros/dCentros_1.xlsx          : nome e praça de cada loja (BCPS = código do PDV)

Saídas:
- dados.js              : público; só contagens por loja e por dia, sem nomes nem telefones
- ativacao_cripto.js    : nominal (nome, telefone, pedido), criptografado por senha de praça (ver cripto_ativacao.py)

Uso: python atualizar_dados.py
"""
import glob
import json
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd

import cripto_ativacao

PASTA = os.path.dirname(os.path.abspath(__file__))
TIPO_VENDA = "Clique & Retire"      # valor da coluna "Tipo de Venda" no NPS
PROMOTOR, DETRATOR = 9, 6           # nota >= 9 promotor; nota <= 6 detrator; 7 e 8 neutros


def _arquivos(sub, exts=("xlsx",)):
    arqs = [a for e in exts for a in glob.glob(os.path.join(PASTA, sub, f"*.{e}"))]
    return sorted((a for a in arqs if not os.path.basename(a).startswith("~$")), key=os.path.getmtime)


def ler_nps():
    partes = []
    for a in _arquivos("base_nps"):
        bruto = pd.read_excel(a, header=None)
        # a exportação tem um título acima do cabeçalho: procura a linha com "ID da Pesquisa"
        lin = next(i for i in range(10) if "ID da Pesquisa" in bruto.iloc[i].astype(str).tolist())
        d = bruto.iloc[lin + 1:].copy()
        d.columns = [str(c).strip() for c in bruto.iloc[lin]]
        d = d.loc[:, ~d.columns.duplicated()]
        partes.append(d)
        print("NPS:", os.path.basename(a), len(d), "respostas")
    n = pd.concat(partes, ignore_index=True).drop_duplicates("ID da Pesquisa", keep="last")
    n["ped"] = pd.to_numeric(n["Código do pedido"], errors="coerce").astype("Int64").astype(str)
    n["nota"] = pd.to_numeric(n["Pontuação principal"], errors="coerce")
    n["dia_resp"] = pd.to_datetime(n["Data da resposta"], errors="coerce")
    n["loja"] = pd.to_numeric(n["Loja"], errors="coerce")
    n["em"] = n["Email"].astype(str).str.lower().str.strip()
    return n


def ler_pedidos():
    partes = []
    for a in _arquivos("Base_Pedidos_Clique&Retire"):
        d = pd.read_excel(a, sheet_name=0)
        partes.append(d)
        print("Pedidos:", os.path.basename(a), len(d))
    c = pd.concat(partes, ignore_index=True).drop_duplicates("PEDIDO", keep="last")
    c["ped"] = c["PEDIDO"].astype(str).str.replace(r"\D", "", regex=True)
    c["dia"] = pd.to_datetime(c["DATA_COMPRA"]).dt.strftime("%Y-%m-%d")
    return c


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", "-", s).strip("-")


def ler_lojas():
    arq = os.path.join(PASTA, "dCentros", "dCentros_1.xlsx")
    d = pd.read_excel(arq, dtype=str)
    d.columns = [c.strip() for c in d.columns]
    lojas, pracas, pessoas = {}, {}, {}
    for _, r in d.iterrows():
        # gestores do cadastro de lojas: a lista de quem pode se identificar no painel (aba Uso)
        for papel in ("GVO", "GCVO/GPVO", "GRVO"):
            nome = str(r.get(papel) or "").strip()
            if nome and nome.lower() != "nan":
                pessoas.setdefault(nome, set()).add(papel)
        cod = str(r["BCPS"]).strip().lstrip("0")
        pk = slug(r["PRAÇA"])
        lojas[cod] = {"nome": str(r["LOJA"]).strip().title(), "praca": pk}
        pracas[pk] = {"nome": " ".join(w.upper() if len(w) <= 3 and w.isalpha() and w.lower() not in ("sul", "são") else w.title()
                                       for w in str(r["PRAÇA"]).split())}
    return lojas, pracas, [{"nome": n, "papeis": sorted(p)} for n, p in sorted(pessoas.items())]


def fone(v):
    """Celular com DDI: 55 + DDD + 9 dígitos, ou None se não der para usar no WhatsApp."""
    if v is None or pd.isna(v):
        return None
    d = re.sub(r"\D", "", str(v)).lstrip("0")
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    if len(d) == 10 and d[2] in "6789":
        d = d[:2] + "9" + d[2:]
    if len(d) != 11 or d[2] != "9" or d[:2] < "11":
        return None
    return "55" + d


def cat(nota):
    return 0 if nota >= PROMOTOR else (2 if nota <= DETRATOR else 1)   # 0 promotor, 1 neutro, 2 detrator


def main():
    nps, ped = ler_nps(), ler_pedidos()
    lojas, pracas, pessoas = ler_lojas()

    # --- cruzamento pelo número do pedido (mesma chave nas duas bases) ---
    com_ped = nps[nps["ped"].str.len() >= 8].sort_values("dia_resp").drop_duplicates("ped", keep="first").set_index("ped")
    ped["nota"] = ped["ped"].map(com_ped["nota"])
    ped["dia_resp"] = ped["ped"].map(com_ped["dia_resp"])
    ped["respondeu"] = ped["nota"].notna()
    emails_nps = set(nps["em"])
    ped["outra"] = ped["EMAIL"].astype(str).str.lower().str.strip().isin(emails_nps) & ~ped["respondeu"]
    ped["pdv"] = ped["PDV"].astype(int)
    ped["loja"] = ped["pdv"].astype(str).map(lambda c: lojas.get(c, {}).get("nome", f"Loja {c}"))
    ped["praca"] = ped["pdv"].astype(str).map(lambda c: lojas.get(c, {}).get("praca", "OUTRAS"))

    # --- público: por loja x dia da compra ---
    base = []
    for (pdv, dia), g in ped.groupby(["pdv", "dia"]):
        r = g[g["respondeu"]]
        cs = r["nota"].map(cat).value_counts()
        base.append([int(pdv), dia, len(g), len(r), int(cs.get(0, 0)), int(cs.get(1, 0)), int(cs.get(2, 0))])

    # --- público: NPS de todas as respostas Clique e Retire do export (todas as lojas) ---
    cr = nps[(nps["Tipo de Venda"] == TIPO_VENDA) & nps["nota"].notna() & nps["loja"].notna()]
    geral = []
    for loja, g in cr.groupby("loja"):
        cs = g["nota"].map(cat).value_counts()
        geral.append([int(loja), len(g), int(cs.get(0, 0)), int(cs.get(1, 0)), int(cs.get(2, 0))])

    usados = {str(b[0]) for b in base} | {str(g[0]) for g in geral}
    lj = {c: lojas.get(c, {"nome": f"Loja {c}", "praca": "OUTRAS"}) for c in usados}
    pr = {p: pracas.get(p, {"nome": "Outras"}) for p in {v["praca"] for v in lj.values()}}
    corte = (nps["dia_resp"].max() or pd.Timestamp.now()).strftime("%Y-%m-%d")
    dados = {"gerado": datetime.now().strftime("%d/%m/%Y %H:%M"), "corte": corte,
             "ini": ped["dia"].min(), "fim": ped["dia"].max(),
             "tipo": TIPO_VENDA, "promotor": PROMOTOR, "detrator": DETRATOR,
             "pracas": pr, "lojas": lj, "pessoas": pessoas, "base": base, "nps_geral": geral}
    with open(os.path.join(PASTA, "dados.js"), "w", encoding="utf-8") as f:
        f.write("// Gerado por atualizar_dados.py - só contagens, sem nomes nem telefones\nwindow.DADOS = ")
        json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    # --- nominal (vai criptografado): uma linha por pedido ---
    ped = ped.sort_values("DATA_COMPRA", ascending=False)
    ped["cli"] = ped["CPF"].astype(str).factorize()[0]          # id interno do cliente; o CPF não sai daqui
    pacotes = {}
    for pk, g in ped.groupby("praca"):
        rows = []
        for x in g.itertuples():
            rows.append([x.ped, str(x.pdv), str(x.CLIENTE).strip().title(), fone(x.TELEFONE), x.dia,
                         int(x.QTD_ITENS), int(x.QTD_SKUS),
                         x.dia_resp.strftime("%Y-%m-%d") if x.respondeu else None,
                         int(x.nota) if x.respondeu else None, int(x.cli), 1 if x.outra else 0])
        pacotes[pk] = {"gerado": dados["gerado"], "corte": corte, "pedidos": rows}
    cripto_ativacao.gravar(PASTA, pacotes)

    resp = int(ped["respondeu"].sum())
    print(f"pedidos {len(ped)} | responderam {resp} ({resp / len(ped):.1%}) | pendentes {len(ped) - resp} "
          f"({ped[~ped['respondeu']]['CPF'].nunique()} clientes) | corte das respostas {corte}")
    sem = ped[~ped["respondeu"] & ped["TELEFONE"].map(fone).isna()]
    print(f"pendentes sem telefone válido: {len(sem)}")


if __name__ == "__main__":
    main()
