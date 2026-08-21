# Gastos com Viagens do Governo Federal

Projeto de estudo em engenharia de dados analisando os gastos com viagens de servidores públicos federais com base nos dados abertos do Portal da Transparência (CGU).

## O que o projeto faz

- **Download** dos dados reais direto do Portal da Transparência
- **ETL** simples com pandas: extração, transformação e carga em SQLite
- **Dashboard** interativo com Streamlit, Bootstrap 5 e Plotly

## Tecnologias

- Python 3.10+
- pandas
- Streamlit
- Plotly
- SQLAlchemy
- requests + tqdm

## Como rodar

```bash
pip install -r requirements.txt

# 1. Baixa os dados (escolha o ano ou deixa baixar tudo de 2021-2024)
python download_data.py --year 2023

# 2. Roda o ETL
python run_etl.py

# 3. Abre o dashboard
streamlit run dashboard/app.py
```

## Fonte dos dados

Portal da Transparência — Controladoria-Geral da União (CGU)  
https://portaldatransparencia.gov.br/download-de-dados/viagens
