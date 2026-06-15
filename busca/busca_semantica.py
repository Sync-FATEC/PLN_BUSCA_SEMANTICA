from . import entidades, datas, sql_builder, modelos
from .preprocessamento import preprocessar


def identificar_consulta(entrada):
    """
    Interpreta a pergunta e devolve a consulta a executar.

    Retorna um dicionário com o sql, a intenção e as entidades detectadas
    (para exibir na tela) — ou None se a pergunta não for sobre imagens.
    """
    texto = preprocessar(entrada)
    tokens = texto.split()
    if not tokens:
        return None

    ranking = entidades.detectar_ranking(tokens)
    if ranking:
        dimensao, direcao = ranking
        spec = entidades.DIMENSOES[dimensao]
        return {
            "sql": sql_builder.montar_ranking(spec["select"], direcao),
            "intencao": "ranking",
            "rotulo": spec["rotulo"], "tipo": spec["tipo"], "direcao": direcao,
            "categoria": None, "origem": None, "data": None,
            "texto_processado": texto,
        }

    agrupar = entidades.detectar_agrupamento(tokens)
    if agrupar:
        spec = entidades.DIMENSOES[agrupar]
        return {
            "sql": sql_builder.montar_breakdown(spec["select"]),
            "intencao": "breakdown",
            "nome_dimensao": spec["nome"], "tipo": spec["tipo"],
            "categoria": None, "origem": None, "data": None,
            "texto_processado": texto,
        }

    consulta_emb = modelos.embeddings(tokens)

    categorias = entidades.detectar_categorias(consulta_emb)
    origens = entidades.detectar_origens(consulta_emb)
    condicao_data = datas.detectar_data(entrada) 
    intencao = entidades.detectar_intencao(texto)
    negado = entidades.detectar_negacao(tokens)
    ordenacao = entidades.detectar_ordenacao_temporal(tokens)

    meta = entidades.detectar_meta(tokens)
    if meta == "listar_categorias" and not categorias:
        return {
            "sql": "SELECT DISTINCT categoria FROM metadata_table ORDER BY categoria",
            "intencao": meta, "categoria": None, "origem": None,
            "data": None, "texto_processado": texto,
        }
    if meta == "listar_origens" and not origens:
        return {
            "sql": "SELECT DISTINCT origem FROM metadata_table ORDER BY origem",
            "intencao": meta, "categoria": None, "origem": None,
            "data": None, "texto_processado": texto,
        }

    on_topic = bool(categorias or origens) or ordenacao or entidades.eh_sobre_imagens(tokens)
    if not on_topic:
        return None

    sql = sql_builder.montar_sql(categorias, origens, condicao_data, intencao,
                                 negado=negado, ordenacao=ordenacao)

    prefixo = "≠ " if negado else ""
    cat_display = (prefixo + " ou ".join(categorias)) if categorias else None
    org_display = (prefixo + " ou ".join(origens)) if origens else None
    data_display = condicao_data
    if ordenacao and not data_display:
        data_display = "mais recente" if ordenacao == "recente" else "mais antiga"

    return {
        "sql": sql,
        "intencao": intencao,
        "categoria": cat_display,
        "origem": org_display,
        "data": data_display,
        "texto_processado": texto,
    }
