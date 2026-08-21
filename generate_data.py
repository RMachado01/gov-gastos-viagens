"""
Gera dados falsos de viagens do governo para estudo.
Salva em data/raw/viagens_governo.csv
"""

import random
import os
import pandas as pd
from faker import Faker

# Inicializa o Faker com locale brasileiro
fake = Faker('pt_BR')

# Listas de opções realistas
orgaos = [
    "Ministério da Saúde",
    "Ministério da Educação",
    "Ministério da Fazenda",
    "Ministério da Justiça",
    "Ministério da Defesa",
    "Ministério da Ciência e Tecnologia",
    "Ministério do Trabalho",
    "Ministério da Agricultura",
    "Ministério do Meio Ambiente",
    "Ministério das Relações Exteriores",
    "Ministério da Infraestrutura",
    "Ministério da Economia",
]

destinos = [
    "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza",
    "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre",
    "Belém", "Goiânia", "Florianópolis", "Maceió", "Natal",
    "Campo Grande", "Teresina", "João Pessoa", "Aracaju", "Macapá",
]

motivos = [
    "Reunião",
    "Capacitação",
    "Missão Oficial",
    "Conferência",
    "Fiscalização",
    "Evento Técnico",
]


def gera_linha(id):
    # Gera uma linha de dados de viagem
    data = fake.date_between(start_date='-6y', end_date='today')
    orgao = random.choice(orgaos)
    servidor = fake.name()
    destino = random.choice(destinos)
    motivo = random.choice(motivos)
    diarias = random.randint(1, 15)
    valor_diaria = round(random.uniform(150, 600), 2)
    passagem = round(random.uniform(200, 2000), 2)
    valor_total = round(diarias * valor_diaria + passagem, 2)

    return {
        "id": id,
        "data_viagem": data,
        "orgao": orgao,
        "servidor": servidor,
        "destino": destino,
        "motivo": motivo,
        "diarias": diarias,
        "valor_diaria": valor_diaria,
        "passagem": passagem,
        "valor_total": valor_total,
    }


print("Gerando 2000 registros de viagens...")

# Cria lista de dicionários e transforma em DataFrame
linhas = [gera_linha(i + 1) for i in range(2000)]
df = pd.DataFrame(linhas)

# Garante que a pasta existe
os.makedirs("data/raw", exist_ok=True)

# Salva o CSV
caminho = "data/raw/viagens_governo.csv"
df.to_csv(caminho, index=False)

print(f"Arquivo salvo em: {caminho}")
print(f"Total de linhas: {len(df)}")
print(df.head(3))
