"""
Extração de entidades da pergunta.

A partir do texto já pré-processado, descobre:
  - categoria (vegetação / água / solo exposto)  -> word2vec + transformer
  - origem    (satélite / drone)                  -> word2vec + transformer
  - intenção  (contagem ou listagem)              -> palavras-chave

A ideia: para cada valor possível (ex.: "drone") temos uma lista de
sinônimos. Comparamos as palavras da pergunta com esses sinônimos usando a
similaridade combinada. Se alguma ficar acima do limiar, o valor foi
mencionado.
"""

from .vocabulario import CATEGORIAS, ORIGENS, PALAVRAS_CONTAGEM, PALAVRAS_DOMINIO
from .config import LIMIAR_ENTIDADE, LIMIAR_DOMINIO
from . import modelos


# Embeddings dos sinônimos, pré-calculados UMA vez no início.
def _preparar(grupos):
    return {valor: modelos.embeddings(sinonimos) for valor, sinonimos in grupos.items()}


_CATEGORIAS_EMB = _preparar(CATEGORIAS)
_ORIGENS_EMB = _preparar(ORIGENS)
_DOMINIO_EMB = modelos.embeddings(PALAVRAS_DOMINIO)


def _melhor_valor(consulta_emb, grupos_emb):
    """Devolve (valor, score) do grupo de sinônimos mais parecido."""
    melhor_valor, melhor_score = None, -1.0
    for valor, emb in grupos_emb.items():
        score = modelos.max_similaridade(consulta_emb, emb)
        if score > melhor_score:
            melhor_valor, melhor_score = valor, score
    return melhor_valor, melhor_score


def detectar_categoria(consulta_emb):
    valor, score = _melhor_valor(consulta_emb, _CATEGORIAS_EMB)
    return valor if score >= LIMIAR_ENTIDADE else None


def detectar_origem(consulta_emb):
    valor, score = _melhor_valor(consulta_emb, _ORIGENS_EMB)
    return valor if score >= LIMIAR_ENTIDADE else None


def eh_sobre_imagens(consulta_emb):
    """True se a pergunta tem a ver com o domínio (imagens)."""
    return modelos.max_similaridade(consulta_emb, _DOMINIO_EMB) >= LIMIAR_DOMINIO


def detectar_intencao(texto):
    """'contagem' se a pergunta pede um total; senão 'listagem'."""
    if set(texto.split()) & set(PALAVRAS_CONTAGEM):
        return "contagem"
    return "listagem"
