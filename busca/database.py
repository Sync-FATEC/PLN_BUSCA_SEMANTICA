import psycopg2
from .config import DB_CONFIG


def conectar():
    """Abre uma conexão com o PostgreSQL usando os dados do config."""
    return psycopg2.connect(**DB_CONFIG)


def executar_consulta(sql):
    """Executa um SELECT e devolve todas as linhas. Sempre fecha a conexão."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()
