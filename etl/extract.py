"""
Extração: lê todos os CSVs de viagens em data/raw/ e concatena num único DataFrame.
Espera arquivos com padrão viagens_YYYY.csv (sep=';', encoding latin-1).
"""

import glob
import os

import pandas as pd


def extrair_dados(pasta_raw="data/raw"):
    """Lê todos os viagens_*.csv da pasta e retorna DataFrame concatenado."""
    padrao = os.path.join(pasta_raw, "viagens_*.csv")
    arquivos = sorted(glob.glob(padrao))

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo encontrado em '{pasta_raw}'. "
            "Rode primeiro: python download_data.py"
        )

    print(f"Arquivos encontrados: {len(arquivos)}")

    partes = []
    for caminho in arquivos:
        print(f"Lendo: {caminho}")
        try:
            df_parte = pd.read_csv(caminho, sep=";", encoding="latin-1", low_memory=False)
        except UnicodeDecodeError:
            df_parte = pd.read_csv(caminho, sep=";", encoding="utf-8", low_memory=False)

        # Extrai o ano do nome do arquivo (viagens_2023.csv -> 2023)
        nome = os.path.basename(caminho)
        try:
            df_parte["ano_arquivo"] = int(nome.split("_")[1].split(".")[0])
        except Exception:
            df_parte["ano_arquivo"] = None

        print(f"  -> {len(df_parte)} linhas, {len(df_parte.columns)} colunas")
        partes.append(df_parte)

    df = pd.concat(partes, ignore_index=True)
    print(f"\nTotal concatenado: {len(df)} linhas")
    return df
