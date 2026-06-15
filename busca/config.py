import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# --- Modelos de linguagem ---
MODELO_WORD2VEC = "pt_core_news_md"
MODELO_TRANSFORMERS = "paraphrase-multilingual-MiniLM-L12-v2"

PESO_WORD2VEC = 0.5
LIMIAR_ENTIDADE = 0.70

# --- Correção ortográfica ---
LIMIAR_CORRECAO = 85
