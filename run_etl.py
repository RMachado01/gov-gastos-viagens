"""
Orquestra o pipeline ETL completo:
1. Extrai os CSVs de data/raw/
2. Transforma (limpa e mapeia colunas reais)
3. Carrega no SQLite
"""

from etl.extract import extrair_dados
from etl.transform import transformar_dados
from etl.load import carregar_dados

CAMINHO_DB = "data/processed/viagens.db"

print("=" * 50)
print("INICIANDO PIPELINE ETL")
print("=" * 50)

# Passo 1: Extração (lê todos viagens_*.csv de data/raw/)
print("\n[1/3] EXTRAÇÃO")
df = extrair_dados(pasta_raw="data/raw")

# Passo 2: Transformação
print("\n[2/3] TRANSFORMAÇÃO")
df_transformado = transformar_dados(df)

# Passo 3: Carregamento
print("\n[3/3] CARREGAMENTO")
carregar_dados(df_transformado, CAMINHO_DB)

print("\n" + "=" * 50)
print("ETL CONCLUÍDO COM SUCESSO!")
print("=" * 50)
