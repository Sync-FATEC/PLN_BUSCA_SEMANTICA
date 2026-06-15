"""
Configurações centrais do sistema.

Mantém num só lugar tudo que pode ser ajustado: credenciais do banco,
nomes dos modelos e os limiares de similaridade. Assim nenhum outro
arquivo precisa lidar com variáveis de ambiente ou "números mágicos".
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Banco de dados (lido do arquivo .env) ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# --- Modelos de linguagem ---
# word2vec: vetores de palavras pré-treinados em português (spaCy)
MODELO_WORD2VEC = "pt_core_news_md"
# transformers (LLM): modelo de sentenças multilíngue
MODELO_TRANSFORMERS = "paraphrase-multilingual-MiniLM-L12-v2"

# --- Fusão das duas técnicas ---
# Para classificar categoria/origem, combinamos a similaridade do word2vec
# com a do transformer numa média ponderada:
#     final = PESO_WORD2VEC * word2vec + (1 - PESO_WORD2VEC) * transformer
# 0.5 = peso igual para os dois. Aumente para dar mais força ao word2vec.
PESO_WORD2VEC = 0.5

# Limiar para considerar que uma categoria/origem foi mencionada.
# Calibrado com medições: termos verdadeiros pontuam >= 0.79 e falsos
# positivos <= 0.63 — 0.70 fica no meio do vão, com folga dos dois lados.
LIMIAR_ENTIDADE = 0.70

# --- Correção ortográfica ---
# Similaridade mínima (0-100) para o RapidFuzz aceitar uma correção.
# Calibrado com medições: typos reais pontuam >= 85.7; falsos positivos como
# "alguma"->"agua" ficam em 80. O corte em 85 separa os dois.
LIMIAR_CORRECAO = 85
