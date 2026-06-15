"""
Orquestrador do pipeline de busca semântica.

Junta todas as etapas e é o único ponto que o app precisa chamar:

    pergunta
       -> preprocessar              (normalização + correção ortográfica)
       -> embeddings das palavras   (word2vec + transformer)
       -> detectar categoria/origem (similaridade combinada)
       -> detectar data             (regras: relativa/extenso/numérica/intervalo)
       -> detectar intenção         (contar vs listar)
       -> montar o SQL dinamicamente

Não há mais "consultas-modelo" com SQL fixo: a query é construída a partir
das entidades encontradas, então qualquer combinação é aceita.
"""

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

    # Pergunta analítica: "qual categoria tem mais imagens", "em que mês tem
    # menos fotos". Não precisa dos embeddings, então é resolvida primeiro.
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

    # Contagem por grupo: "quantas imagens de cada categoria".
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

    # Vetores (word2vec + transformer) de cada palavra da pergunta.
    consulta_emb = modelos.embeddings(tokens)

    # Entidades (categorias/origens são listas: 1 = filtro, 2+ = OU)
    categorias = entidades.detectar_categorias(consulta_emb)
    origens = entidades.detectar_origens(consulta_emb)
    condicao_data = datas.detectar_data(entrada)        # usa o texto original
    intencao = entidades.detectar_intencao(texto)
    negado = entidades.detectar_negacao(tokens)
    ordenacao = entidades.detectar_ordenacao_temporal(tokens)

    # Pergunta-meta: "quais são as categorias disponíveis?" pergunta SOBRE os
    # metadados. Só vale se nenhum valor específico foi citado.
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

    # A pergunta é mesmo sobre imagens? Precisa de um filtro forte, ordenação
    # temporal, OU alguma palavra do domínio. Senão -> "não entendi".
    on_topic = bool(categorias or origens) or ordenacao or entidades.eh_sobre_imagens(tokens)
    if not on_topic:
        return None

    sql = sql_builder.montar_sql(categorias, origens, condicao_data, intencao,
                                 negado=negado, ordenacao=ordenacao)

    # Texto para o painel (com "≠" quando negado).
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
