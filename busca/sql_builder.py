TABELA = "metadata_table"

def _filtro_lista(coluna, valores, negado):
    """Monta 'coluna = x', 'coluna != x' ou 'coluna IN/NOT IN (...)'."""
    if len(valores) == 1:
        operador = "!=" if negado else "="
        return f"{coluna} {operador} '{valores[0]}'"
    lista = ", ".join(f"'{v}'" for v in valores)
    operador = "NOT IN" if negado else "IN"
    return f"{coluna} {operador} ({lista})"


def montar_sql(categorias, origens, condicao_data, intencao,
               negado=False, ordenacao=None):
    """
    Monta SELECT/COUNT com os filtros detectados.

    categorias/origens são listas (1 valor = filtro simples, 2+ = OU/IN).
    negado inverte os filtros de categoria e origem (=> != / NOT IN).
    ordenacao ('antiga'/'recente') ordena por data e pega só 1 (a imagem
    mais antiga/recente).
    """
    filtros = []
    if categorias:
        filtros.append(_filtro_lista("categoria", categorias, negado))
    if origens:
        filtros.append(_filtro_lista("origem", origens, negado))
    if condicao_data:
        filtros.append(f"({condicao_data})")

    where = " WHERE " + " AND ".join(filtros) if filtros else ""

    if intencao == "contagem":
        return f"SELECT COUNT(*) FROM {TABELA}{where}"

    ordem = ""
    if ordenacao == "antiga":
        ordem = " ORDER BY data_imagem ASC LIMIT 1"
    elif ordenacao == "recente":
        ordem = " ORDER BY data_imagem DESC LIMIT 1"

    return f"SELECT * FROM {TABELA}{where}{ordem}"


def montar_ranking(select_expr, direcao):
    """
    Monta a query analítica: conta as imagens por dimensão e ordena.
    Ex.: 'qual categoria tem mais imagens' ->
        SELECT categoria AS valor, COUNT(*) AS total
        FROM metadata_table GROUP BY categoria ORDER BY total DESC, valor
    Sem LIMIT: o app pega o extremo e trata empates.
    """
    ordem = "DESC" if direcao == "mais" else "ASC"
    return (
        f"SELECT {select_expr} AS valor, COUNT(*) AS total "
        f"FROM {TABELA} GROUP BY {select_expr} "
        f"ORDER BY total {ordem}, valor"
    )


def montar_breakdown(select_expr):
    """
    Conta as imagens por dimensão, ordenado pelo próprio valor.
    Ex.: 'quantas imagens de cada categoria' ->
        SELECT categoria AS valor, COUNT(*) AS total
        FROM metadata_table GROUP BY categoria ORDER BY valor
    """
    return (
        f"SELECT {select_expr} AS valor, COUNT(*) AS total "
        f"FROM {TABELA} GROUP BY {select_expr} ORDER BY valor"
    )
