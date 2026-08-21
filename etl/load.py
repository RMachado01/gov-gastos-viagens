"""
Carregamento: salva o DataFrame transformado em um banco SQLite.
"""

import os
import pandas as pd
from sqlalchemy import create_engine


def carregar_dados(df, caminho_db):
    # Garante que a pasta existe
    os.makedirs(os.path.dirname(caminho_db), exist_ok=True)

    # Cria a conexão com o SQLite
    engine = create_engine(f"sqlite:///{caminho_db}")

    # Salva no banco, substituindo a tabela se já existir
    df.to_sql("viagens", con=engine, if_exists="replace", index=False)

    print(f"Dados salvos no banco: {caminho_db}")
    print(f"Tabela 'viagens' criada com {len(df)} registros")
