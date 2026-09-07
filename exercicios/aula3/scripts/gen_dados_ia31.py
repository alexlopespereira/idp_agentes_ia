#!/usr/bin/env python3
"""Gera os CSVs de insumo do exercicio ia-3.1 (curso Agentes de IA - IDP).

Saidas: data/vendas.csv e data/lojas.csv

Os dados sao SINTETICOS e DETERMINISTICOS: `random.seed(7)` e a ordem exata das
chamadas a `random` definem os valores, entao qualquer pessoa que rode este
script obtem os mesmos arquivos byte a byte. Nao reordene os loops.

Uso:
    python scripts/gen_dados_ia31.py
"""

import csv
import os
import random

# ---------------------------------------------------------------------------
# Caminhos (relativos a raiz do exercicio, nao ao diretorio de trabalho)
# ---------------------------------------------------------------------------
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DADOS = os.path.join(RAIZ, "data")
ARQ_VENDAS = os.path.join(DIR_DADOS, "vendas.csv")
ARQ_LOJAS = os.path.join(DIR_DADOS, "lojas.csv")

# ---------------------------------------------------------------------------
# Constantes do gerador
# ---------------------------------------------------------------------------
LOJAS = [
    [101, "Asa Norte", "Centro-Oeste", "DF", "Marina Alves"],
    [102, "Taguatinga", "Centro-Oeste", "DF", "Bruno Sato"],
    [103, "Moema", "Sudeste", "SP", "Carla Nunes"],
    [104, "Tijuca", "Sudeste", "RJ", "Diego Prado"],
    [105, "Boa Viagem", "Nordeste", "PE", "Elisa Rocha"],
    [106, "Meireles", "Nordeste", "CE", "Fabio Lima"],
    [107, "Moinhos", "Sul", "RS", "Gisele Kunz"],
    [108, "Batel", "Sul", "PR", "Heitor Braga"],
]

MESES = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
CATEGORIAS = ["Bebidas", "Higiene", "Limpeza", "Mercearia", "Padaria"]
PRECO_BASE = {
    "Bebidas": 38.0,
    "Higiene": 24.5,
    "Limpeza": 19.9,
    "Mercearia": 15.4,
    "Padaria": 12.8,
}

# Armadilhas pedagogicas propositais (ver data/README.md)
LOJA_SEM_VENDAS = 108
LOJA_ORFA = 999


def gerar_vendas():
    """Gera as linhas de vendas.csv na ordem exata que define o seed."""
    random.seed(7)

    linhas = []
    vid = 1

    for mes in MESES:
        for loja in LOJAS:
            id_loja = loja[0]
            if id_loja == LOJA_SEM_VENDAS:
                continue  # essa loja nao tera vendas - e intencional
            for categoria in CATEGORIAS:
                for _ in range(2):
                    un = random.randint(20, 180)
                    preco = PRECO_BASE[categoria] * random.uniform(0.9, 1.15)
                    dia = random.randint(1, 28)
                    linhas.append(
                        [
                            "V{:05d}".format(vid),
                            "{}-{:02d}".format(mes, dia),
                            id_loja,
                            categoria,
                            un,
                            round(un * preco, 2),
                        ]
                    )
                    vid += 1

    # 3 vendas orfas: id_loja=999 nao existe em lojas.csv
    for k in range(3):
        un = random.randint(20, 120)
        linhas.append(
            [
                "V{:05d}".format(vid),
                "2026-0{}-15".format(k + 2),
                LOJA_ORFA,
                "Bebidas",
                un,
                round(un * 40, 2),
            ]
        )
        vid += 1

    return linhas


def escrever_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)


# ---------------------------------------------------------------------------
# Conferencia dos invariantes
# ---------------------------------------------------------------------------
REGIOES_ESPERADAS = 4
MESES_ESPERADOS = 6
TOTAL_VENDAS = 423
TOTAL_LOJAS = 8
TOTAL_INNER_JOIN = 420
RECEITA_INNER_JOIN = 931274.06
RECEITA_SUDESTE = 265077.49


def conferir_com_pandas(pd):
    vendas = pd.read_csv(ARQ_VENDAS)
    lojas = pd.read_csv(ARQ_LOJAS)

    n_vendas = len(vendas)
    n_lojas = len(lojas)

    inner = vendas.merge(lojas, on="id_loja", how="inner")
    n_inner = len(inner)
    receita_inner = round(float(inner["receita_brl"].sum()), 2)

    inner = inner.copy()
    inner["mes"] = inner["data"].str.slice(0, 7)
    pivot = inner.pivot_table(
        index="regiao", columns="mes", values="receita_brl", aggfunc="sum", fill_value=0.0
    ).round(2)
    shape = pivot.shape

    por_regiao = inner.groupby("regiao")["receita_brl"].sum().round(2).sort_values(ascending=False)
    regiao_top = str(por_regiao.index[0])
    receita_top = float(por_regiao.iloc[0])

    loja_108_em_vendas = int(LOJA_SEM_VENDAS) in set(vendas["id_loja"])
    loja_999_em_lojas = int(LOJA_ORFA) in set(lojas["id_loja"])

    tabela_pivot = pivot.to_string()
    return {
        "motor": "pandas",
        "n_vendas": n_vendas,
        "n_lojas": n_lojas,
        "n_inner": n_inner,
        "receita_inner": receita_inner,
        "shape": shape,
        "regiao_top": regiao_top,
        "receita_top": receita_top,
        "loja_108_em_vendas": loja_108_em_vendas,
        "loja_999_em_lojas": loja_999_em_lojas,
        "tabela_pivot": tabela_pivot,
        "por_regiao": [(str(r), float(v)) for r, v in por_regiao.items()],
    }


def conferir_com_stdlib():
    with open(ARQ_VENDAS, encoding="utf-8", newline="") as f:
        vendas = list(csv.DictReader(f))
    with open(ARQ_LOJAS, encoding="utf-8", newline="") as f:
        lojas = list(csv.DictReader(f))

    mapa_lojas = {int(l["id_loja"]): l for l in lojas}

    inner = [v for v in vendas if int(v["id_loja"]) in mapa_lojas]
    receita_inner = round(sum(float(v["receita_brl"]) for v in inner), 2)

    pivot = {}
    por_regiao = {}
    for v in inner:
        regiao = mapa_lojas[int(v["id_loja"])]["regiao"]
        mes = v["data"][:7]
        valor = float(v["receita_brl"])
        pivot.setdefault(regiao, {})
        pivot[regiao][mes] = pivot[regiao].get(mes, 0.0) + valor
        por_regiao[regiao] = por_regiao.get(regiao, 0.0) + valor

    regioes = sorted(pivot)
    colunas = sorted({m for linha in pivot.values() for m in linha})
    shape = (len(regioes), len(colunas))

    ranking = sorted(((r, round(v, 2)) for r, v in por_regiao.items()), key=lambda x: -x[1])
    regiao_top, receita_top = ranking[0]

    larg = max(len(r) for r in regioes)
    cab = "regiao".ljust(larg) + "".join(c.rjust(13) for c in colunas)
    linhas_txt = [cab]
    for r in regioes:
        linhas_txt.append(
            r.ljust(larg) + "".join("{:13.2f}".format(round(pivot[r].get(c, 0.0), 2)) for c in colunas)
        )

    return {
        "motor": "stdlib",
        "n_vendas": len(vendas),
        "n_lojas": len(lojas),
        "n_inner": len(inner),
        "receita_inner": receita_inner,
        "shape": shape,
        "regiao_top": regiao_top,
        "receita_top": receita_top,
        "loja_108_em_vendas": any(int(v["id_loja"]) == LOJA_SEM_VENDAS for v in vendas),
        "loja_999_em_lojas": LOJA_ORFA in mapa_lojas,
        "tabela_pivot": "\n".join(linhas_txt),
        "por_regiao": ranking,
    }


def conferir():
    try:
        import pandas as pd
    except ImportError:
        return conferir_com_stdlib()
    return conferir_com_pandas(pd)


def main():
    os.makedirs(DIR_DADOS, exist_ok=True)

    escrever_csv(
        ARQ_LOJAS,
        ["id_loja", "nome_loja", "regiao", "uf", "gerente"],
        LOJAS,
    )
    escrever_csv(
        ARQ_VENDAS,
        ["id_venda", "data", "id_loja", "categoria", "unidades", "receita_brl"],
        gerar_vendas(),
    )

    r = conferir()

    print("Arquivos gerados:")
    print("  " + ARQ_LOJAS)
    print("  " + ARQ_VENDAS)
    print()
    print("Pivot regiao x mes (soma de receita_brl) - motor de conferencia: " + r["motor"])
    print(r["tabela_pivot"])
    print()
    print("Receita por regiao (desc):")
    for regiao, valor in r["por_regiao"]:
        print("  {:<14} {:>12.2f}".format(regiao, valor))
    print()

    checagens = [
        ("vendas.csv tem 423 linhas de dados", r["n_vendas"], TOTAL_VENDAS),
        ("lojas.csv tem 8 linhas de dados", r["n_lojas"], TOTAL_LOJAS),
        ("inner join por id_loja produz 420 linhas", r["n_inner"], TOTAL_INNER_JOIN),
        ("soma de receita_brl no inner join", r["receita_inner"], RECEITA_INNER_JOIN),
        ("shape do pivot regiao x mes", tuple(r["shape"]), (REGIOES_ESPERADAS, MESES_ESPERADOS)),
        ("regiao com maior receita", r["regiao_top"], "Sudeste"),
        ("receita da regiao Sudeste", round(r["receita_top"], 2), RECEITA_SUDESTE),
        ("loja 108 NAO aparece em vendas.csv", r["loja_108_em_vendas"], False),
        ("id_loja 999 NAO aparece em lojas.csv", r["loja_999_em_lojas"], False),
    ]

    print("Invariantes:")
    for rotulo, obtido, esperado in checagens:
        ok = obtido == esperado
        print("  [{}] {}: {} (esperado {})".format("OK" if ok else "XX", rotulo, obtido, esperado))

    for rotulo, obtido, esperado in checagens:
        assert obtido == esperado, "{}: obtido {!r}, esperado {!r}".format(rotulo, obtido, esperado)

    print()
    print("Todos os invariantes conferidos.")


if __name__ == "__main__":
    main()
