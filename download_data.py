"""
Download de dados reais do Portal da Transparência (CGU) - Viagens de Servidores.
Uso: python download_data.py           (baixa 2020-2024)
     python download_data.py --year 2023  (só um ano)
"""

import argparse
import os
import zipfile
import io

import requests
from tqdm import tqdm

# Diretório onde os CSVs brutos ficam
PASTA_RAW = "data/raw"

# URL de download do Portal da Transparência (redireciona para o ZIP real)
URL_BASE = "https://portaldatransparencia.gov.br/download-de-dados/viagens/{ano}"

# Cabeçalho para simular um browser (evita bloqueio por User-Agent)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def baixar_ano(ano):
    """Baixa o ZIP do ano especificado e extrai o CSV para data/raw/."""
    caminho_csv = os.path.join(PASTA_RAW, f"viagens_{ano}.csv")

    # Pula se já existe
    if os.path.exists(caminho_csv):
        print(f"[{ano}] Arquivo já existe, pulando: {caminho_csv}")
        return

    url = URL_BASE.format(ano=ano)
    print(f"[{ano}] Seguindo redirecionamento de: {url}")

    # Segue o redirect para descobrir a URL real do ZIP
    resp = requests.get(url, headers=HEADERS, allow_redirects=True, stream=True, timeout=60)
    resp.raise_for_status()

    url_final = resp.url
    print(f"[{ano}] URL final: {url_final}")

    # Lê o conteúdo do ZIP com barra de progresso
    tamanho = int(resp.headers.get("content-length", 0))
    print(f"[{ano}] Baixando ZIP ({tamanho / 1024 / 1024:.1f} MB)...")

    buffer = io.BytesIO()
    with tqdm(total=tamanho, unit="B", unit_scale=True, desc=f"viagens_{ano}.zip") as barra:
        for chunk in resp.iter_content(chunk_size=8192):
            buffer.write(chunk)
            barra.update(len(chunk))

    buffer.seek(0)

    # Extrai o CSV do ZIP
    print(f"[{ano}] Extraindo CSV do ZIP...")
    with zipfile.ZipFile(buffer) as zf:
        nomes = zf.namelist()
        print(f"[{ano}] Arquivos no ZIP: {nomes}")

        # Pega o primeiro CSV que encontrar
        csvs = [n for n in nomes if n.lower().endswith(".csv")]
        if not csvs:
            raise ValueError(f"Nenhum CSV encontrado no ZIP do ano {ano}. Arquivos: {nomes}")

        nome_csv = csvs[0]
        print(f"[{ano}] Extraindo: {nome_csv}")

        with zf.open(nome_csv) as f_origem:
            conteudo = f_origem.read()

    # Salva o CSV
    os.makedirs(PASTA_RAW, exist_ok=True)
    with open(caminho_csv, "wb") as f_destino:
        f_destino.write(conteudo)

    print(f"[{ano}] Salvo em: {caminho_csv} ({os.path.getsize(caminho_csv) / 1024 / 1024:.1f} MB)")

    # Imprime as colunas para o usuário verificar
    import pandas as pd
    try:
        df_amostra = pd.read_csv(caminho_csv, sep=";", encoding="latin-1", nrows=5)
    except Exception:
        df_amostra = pd.read_csv(caminho_csv, sep=";", encoding="utf-8", nrows=5)

    print(f"\n[{ano}] COLUNAS ENCONTRADAS NO CSV:")
    for i, col in enumerate(df_amostra.columns.tolist()):
        print(f"  {i:2d}. '{col}'")
    print()


def main():
    parser = argparse.ArgumentParser(description="Baixa dados de viagens do Portal da Transparência")
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Ano para baixar (ex: 2023). Sem este argumento, baixa 2020-2024.",
    )
    args = parser.parse_args()

    anos = [args.year] if args.year else list(range(2020, 2025))

    print("=" * 60)
    print("DOWNLOAD - Portal da Transparência / CGU")
    print(f"Anos: {anos}")
    print("=" * 60)

    for ano in anos:
        try:
            baixar_ano(ano)
        except Exception as e:
            print(f"[{ano}] ERRO: {e}")

    print("\nDownload concluído. Rode 'python run_etl.py' para processar.")


if __name__ == "__main__":
    main()
