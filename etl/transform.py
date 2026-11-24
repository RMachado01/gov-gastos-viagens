"""
Transformação: adapta os dados reais do Portal da Transparência.

Estrutura real do arquivo de viagens:
- Uma linha por tipo de pagamento (PASSAGEM, DIÁRIA, OUTROS) por processo de viagem
- Precisa agrupar por processo para obter o total por viagem
"""

import pandas as pd


def _converter_real(serie):
    """Converte 'R$ 1.234,56' ou '1.234,56' para float."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    return (
        serie.astype(str)
        .str.strip()
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )


PREPOSICOES = {"Da", "De", "Do", "Das", "Dos", "E", "Em", "Para"}


def _nome_proprio(serie):
    """'MINISTÉRIO DA SAÚDE' -> 'Ministério da Saúde' (preposições em minúsculo)."""
    def ajustar(nome):
        palavras = str(nome).strip().title().split()
        return " ".join(p.lower() if i > 0 and p in PREPOSICOES else p for i, p in enumerate(palavras))
    return serie.map(ajustar)


def transformar_dados(df):
    print("Iniciando transformação dos dados...")
    print(f"Colunas disponíveis: {df.columns.tolist()}")
    print(f"Total de linhas brutas: {len(df):,}")

    # ---- Mapeia colunas reais ----
    # Estrutura real: Identificador, Nome do órgão superior, Tipo de pagamento, Valor
    mapa = {
        "Identificador do processo de viagem": "id_processo",
        "Nome do órgão superior":              "orgao",
        "Nome do órgao pagador":               "orgao_pagador",
        "Tipo de pagamento":                   "tipo_pagamento",
        "Valor":                               "valor",
        "Número da Proposta (PCDP)":           "num_proposta",
        "ano_arquivo":                         "ano",
    }

    # Só renomeia as que existem
    renomear = {k: v for k, v in mapa.items() if k in df.columns}
    df = df.rename(columns=renomear)

    # ---- Converte valor ----
    if "valor" in df.columns:
        df["valor"] = _converter_real(df["valor"])

    # ---- Garante coluna ano ----
    # Usa ano_arquivo (do nome do CSV) — mais confiável que tentar parsear a proposta
    if "ano" not in df.columns:
        print("  AVISO: coluna 'ano' não encontrada.")

    # ---- Remove valores nulos ou zerados ----
    antes = len(df)
    df = df[df["valor"].notna() & (df["valor"] > 0)]
    print(f"Removidos sem valor válido: {antes - len(df):,} linhas")

    # ---- Normaliza órgão ----
    if "orgao" in df.columns:
        df["orgao"] = _nome_proprio(df["orgao"])
    elif "orgao_pagador" in df.columns:
        # Fallback: usa o órgão pagador se não tiver o superior
        df["orgao"] = _nome_proprio(df["orgao_pagador"])

    # ---- Normaliza tipo de pagamento ----
    if "tipo_pagamento" in df.columns:
        df["tipo_pagamento"] = df["tipo_pagamento"].astype(str).str.strip().str.upper()

    # ---- Agrega por processo de viagem ----
    # Cada processo tem N linhas (uma por tipo de pagamento)
    # Agrupa para ter uma linha por viagem com o total
    if "id_processo" in df.columns and "orgao" in df.columns:
        print("Agrupando por processo de viagem...")

        # Pivot: colunas separadas por tipo de pagamento
        if "tipo_pagamento" in df.columns:
            pivot = (
                df.groupby(["id_processo", "orgao", "ano"])["valor"]
                .sum()
                .reset_index()
                .rename(columns={"valor": "valor_total"})
            )

            # Adiciona breakdown diárias vs passagens
            # comparo pelo começo da palavra pra aceitar singular e plural
            # ("DIÁRIA"/"DIÁRIAS", "PASSAGEM"/"PASSAGENS") e grafia sem acento
            tipo_normalizado = df["tipo_pagamento"].str.replace("Á", "A", regex=False)
            for prefixo, col_nome in [("DIARIA", "valor_diarias"), ("PASSAGE", "valor_passagens")]:
                sub = df[tipo_normalizado.str.startswith(prefixo)].groupby("id_processo")["valor"].sum()
                pivot = pivot.merge(sub.rename(col_nome), on="id_processo", how="left")
                pivot[col_nome] = pivot[col_nome].fillna(0)

            df = pivot
        else:
            df = (
                df.groupby(["id_processo", "orgao", "ano"])["valor"]
                .sum()
                .reset_index()
                .rename(columns={"valor": "valor_total"})
            )

    # ---- Adiciona coluna mes (não temos data, usa None) ----
    # o arquivo de pagamentos não tem a data da viagem, só o ano
    df["mes"] = None

    print(f"\nTransformação concluída: {len(df):,} viagens únicas")
    if "ano" in df.columns:
        anos = sorted(df["ano"].dropna().unique().astype(int))
        print(f"Período: {anos[0]} a {anos[-1]}")
        print(f"Distribuição por ano:")
        print(df.groupby("ano").size().to_string())

    return df
