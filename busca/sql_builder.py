"""
Construtor de SQL.

Monta a consulta final juntando apenas os filtros que foram detectados na
pergunta. É isso que torna o sistema genérico: qualquer combinação de
categoria, origem e data vira uma query válida.
"""

TABELA = "metadata_table"


def montar_sql(categoria, origem, condicao_data, intencao):
    filtros = []
    if categoria:
        filtros.append(f"categoria = '{categoria}'")
    if origem:
        filtros.append(f"origem = '{origem}'")
    if condicao_data:
        filtros.append(f"({condicao_data})")

    where = ""
    if filtros:
        where = " WHERE " + " AND ".join(filtros)

    if intencao == "contagem":
        return f"SELECT COUNT(*) FROM {TABELA}{where}"
    return f"SELECT * FROM {TABELA}{where}"
