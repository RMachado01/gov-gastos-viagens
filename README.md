# Gastos com Viagens do Governo Federal

[![CI](https://github.com/RMachado01/gov-gastos-viagens/actions/workflows/ci.yml/badge.svg)](https://github.com/RMachado01/gov-gastos-viagens/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)

ETL e dashboard dos gastos com viagens de servidores públicos federais, com os
**arquivos oficiais** de viagens do Portal da Transparência (CGU).

## Como funciona

```text
download_data.py   baixa o ZIP de cada ano no Portal e extrai o CSV em data/raw/
etl/extract.py     lê todos os viagens_AAAA.csv (latin-1, separador ;)
etl/transform.py   converte "R$ 1.234,56", agrega os pagamentos por processo
                   de viagem e separa diárias, passagens e outros
etl/load.py        grava a tabela "viagens" num SQLite
dashboard/app.py   Streamlit + Plotly: totais, média por viagem, ranking de
                   órgãos e composição dos gastos, com filtros de ano e órgão
```

O arquivo oficial tem **uma linha por tipo de pagamento** (diária, passagem,
seguro...) de cada processo de viagem. A transformação agrupa por processo pra
chegar ao custo de cada viagem.

## Rodando

```bash
pip install -r requirements.txt

python download_data.py --year 2023   # ou sem --year pra baixar 2020 a 2024
python run_etl.py
streamlit run dashboard/app.py
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

Cobrem a conversão de valores no formato brasileiro, a agregação por processo
(com o tipo de pagamento no singular ou no plural) e a remoção de valores
zerados ou inválidos.

## Limitações

- O arquivo de pagamentos não traz a data da viagem, só o ano, então não há
  análise mensal.
- Para análise de despesas federais com API, testes de ponta a ponta e warehouse
  analítico, veja o projeto
  [despesas-federais-transparencia](https://github.com/RMachado01/despesas-federais-transparencia).

## Fonte dos dados

[Portal da Transparência — Viagens a serviço](https://portaldatransparencia.gov.br/download-de-dados/viagens)
— Controladoria-Geral da União (CGU).
