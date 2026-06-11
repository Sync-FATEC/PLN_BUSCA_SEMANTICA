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

    # Vetores (word2vec + transformer) de cada palavra da pergunta.
    consulta_emb = modelos.embeddings(tokens)

    # Entidades
    categoria = entidades.detectar_categoria(consulta_emb)
    origem = entidades.detectar_origem(consulta_emb)
    condicao_data = datas.detectar_data(entrada)        # usa o texto original
    intencao = entidades.detectar_intencao(texto)

    # Pergunta-meta: "quais são as categorias disponíveis?" pergunta SOBRE os
    # metadados. Só vale se nenhum valor específico foi citado (senão
    # "imagens da categoria água" cairia aqui por engano).
    meta = entidades.detectar_meta(tokens)
    if meta == "listar_categorias" and categoria is None:
        return {
            "sql": "SELECT DISTINCT categoria FROM metadata_table ORDER BY categoria",
            "intencao": meta, "categoria": None, "origem": None,
            "data": None, "texto_processado": texto,
        }
    if meta == "listar_origens" and origem is None:
        return {
            "sql": "SELECT DISTINCT origem FROM metadata_table ORDER BY origem",
            "intencao": meta, "categoria": None, "origem": None,
            "data": None, "texto_processado": texto,
        }

    # A pergunta é mesmo sobre imagens? Precisa ter detectado um filtro forte
    # OU conter alguma palavra do domínio (imagens, fotos, mostrar...).
    # Senão, respondemos "não entendi" — é o que barra perguntas fora do
    # escopo como "como fazer bolo de chocolate".
    on_topic = bool(categoria or origem) or entidades.eh_sobre_imagens(tokens)
    if not on_topic:
        return None

    sql = sql_builder.montar_sql(categoria, origem, condicao_data, intencao)

    return {
        "sql": sql,
        "intencao": intencao,
        "categoria": categoria,
        "origem": origem,
        "data": condicao_data,
        "texto_processado": texto,
    }
