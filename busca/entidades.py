import unidecode

from .vocabulario import (
    CATEGORIAS,
    ORIGENS,
    PALAVRAS_CONTAGEM,
    PALAVRAS_DOMINIO,
    PALAVRAS_META_CATEGORIA,
    PALAVRAS_META_ORIGEM,
    PALAVRAS_NEGACAO,
    PALAVRAS_TEMPORAL_ANTIGA,
    PALAVRAS_TEMPORAL_RECENTE,
)
from .config import LIMIAR_ENTIDADE
from . import modelos


# Dimensões sobre as quais se pode perguntar "qual tem mais/menos imagens".
# `select` é a expressão SQL agrupada; `tipo` diz ao app como formatar o valor.
DIMENSOES = {
    "categoria": {"rotulo": "A categoria", "nome": "categoria", "select": "categoria", "tipo": "texto"},
    "origem":    {"rotulo": "A origem", "nome": "origem", "select": "origem", "tipo": "texto"},
    "mes":       {"rotulo": "O mês", "nome": "mês", "select": "EXTRACT(MONTH FROM data_imagem)", "tipo": "mes"},
    "data":      {"rotulo": "A data", "nome": "data", "select": "data_imagem", "tipo": "data"},
}

_DIRECAO_MAIS = {"mais", "maior", "maiores"}
_DIRECAO_MENOS = {"menos", "menor", "menores"}
_PALAVRAS_DIMENSAO = [
    ("categoria", set(PALAVRAS_META_CATEGORIA)),
    ("origem", set(PALAVRAS_META_ORIGEM)),
    ("mes", {"mes", "meses"}),
    ("data", {"data", "datas", "dia", "dias"}),
]


# Embeddings dos sinônimos, pré-calculados UMA vez no início.
def _preparar(grupos):
    return {valor: modelos.embeddings(sinonimos) for valor, sinonimos in grupos.items()}


_CATEGORIAS_EMB = _preparar(CATEGORIAS)
_ORIGENS_EMB = _preparar(ORIGENS)


def _todos_acima(consulta_emb, grupos_emb):
    """Todos os valores cujo grupo de sinônimos passa do limiar (para o 'OU')."""
    return [
        valor
        for valor, emb in grupos_emb.items()
        if modelos.max_similaridade(consulta_emb, emb) >= LIMIAR_ENTIDADE
    ]


def detectar_categorias(consulta_emb):
    """Lista das categorias mencionadas (1 = filtro simples, 2+ = OU)."""
    return _todos_acima(consulta_emb, _CATEGORIAS_EMB)


def detectar_origens(consulta_emb):
    """Lista das origens mencionadas (1 = filtro simples, 2+ = OU)."""
    return _todos_acima(consulta_emb, _ORIGENS_EMB)


def eh_sobre_imagens(tokens):
    """
    True se a pergunta contém alguma palavra do domínio (imagens, fotos,
    mostrar...). A verificação é EXATA por token — a correção ortográfica já
    consertou os erros antes. Comparar por embedding aqui seria perigoso:
    verbos genéricos ("fazer", "ver") se parecem entre si semanticamente e
    deixariam passar perguntas fora do assunto.
    """
    return bool(set(tokens) & set(PALAVRAS_DOMINIO))


def detectar_meta(tokens):
    """
    Detecta perguntas SOBRE os metadados (e não sobre as imagens em si).
    Ex.: "quais são as categorias disponíveis?" -> 'listar_categorias'
         "quais origens existem?"               -> 'listar_origens'
    """
    tokens = set(tokens)
    if tokens & set(PALAVRAS_META_CATEGORIA):
        return "listar_categorias"
    if tokens & set(PALAVRAS_META_ORIGEM):
        return "listar_origens"
    return None


def detectar_ranking(tokens):
    """
    Detecta perguntas analíticas: "qual categoria tem MAIS imagens", "em que
    mês tem MENOS fotos". Precisa de uma DIREÇÃO (mais/menos) e uma DIMENSÃO
    (categoria/origem/mês/data). Devolve (dimensao, direcao) ou None.
    """
    toks = {unidecode.unidecode(t) for t in tokens}

    if toks & _DIRECAO_MAIS:
        direcao = "mais"
    elif toks & _DIRECAO_MENOS:
        direcao = "menos"
    else:
        return None

    for dimensao, palavras in _PALAVRAS_DIMENSAO:
        if toks & palavras:
            return dimensao, direcao
    return None


def detectar_intencao(texto):
    """'contagem' se a pergunta pede um total; senão 'listagem'."""
    if set(texto.split()) & set(PALAVRAS_CONTAGEM):
        return "contagem"
    return "listagem"


def detectar_negacao(tokens):
    """True se há negação ('não', 'sem', 'exceto'): inverte o filtro (=> !=)."""
    toks = {unidecode.unidecode(t) for t in tokens}
    return bool(toks & set(PALAVRAS_NEGACAO))


def detectar_ordenacao_temporal(tokens):
    """'antiga' / 'recente' para 'a imagem mais antiga/recente'; senão None."""
    toks = {unidecode.unidecode(t) for t in tokens}
    if toks & set(PALAVRAS_TEMPORAL_RECENTE):
        return "recente"
    if toks & set(PALAVRAS_TEMPORAL_ANTIGA):
        return "antiga"
    return None


def _qual_dimensao(palavra):
    """Devolve a dimensão de uma única palavra, ou None."""
    for dimensao, palavras in _PALAVRAS_DIMENSAO:
        if palavra in palavras:
            return dimensao
    return None


def detectar_agrupamento(tokens):
    """
    Detecta 'quantas imagens de CADA categoria' / 'imagens POR origem'.
    Devolve a dimensão ou None.

    O 'por' precisa vir IMEDIATAMENTE antes da dimensão ("por categoria"),
    senão "capturado por drone no dia 12" cairia aqui por engano (tem "por"
    e "dia" longe um do outro).
    """
    toks = [unidecode.unidecode(t) for t in tokens]

    # "cada" + dimensão em qualquer posição: "de cada categoria"
    if "cada" in toks:
        for palavra in toks:
            dim = _qual_dimensao(palavra)
            if dim:
                return dim

    # "por <dimensão>" adjacente: "por categoria", "por origem"
    for atual, proximo in zip(toks, toks[1:]):
        if atual == "por":
            dim = _qual_dimensao(proximo)
            if dim:
                return dim

    return None
