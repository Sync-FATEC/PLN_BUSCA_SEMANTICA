"""
Carrega os modelos de linguagem (word2vec + transformer) e fornece a
similaridade COMBINADA entre conjuntos de textos.

É aqui que as duas tecnologias do enunciado vivem:
  - word2vec   -> spaCy (vetores de palavras pré-treinados em português)
  - transformer-> sentence-transformers (LLM de sentenças)
"""

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .config import MODELO_WORD2VEC, MODELO_TRANSFORMERS, PESO_WORD2VEC


# O modo offline (quando há cache) é ativado em busca/__init__.py.
print("Carregando modelos de linguagem... (a primeira vez pode demorar)")
_nlp = spacy.load(MODELO_WORD2VEC)
_transformer = SentenceTransformer(MODELO_TRANSFORMERS)
print("Modelos prontos.")


def embeddings(textos):
    """
    Calcula os vetores word2vec e transformer de uma lista de textos.
    Devolve um dict {"w2v": matriz, "trf": matriz}.
    """
    textos = list(textos)
    vetores_w2v = np.array([_nlp(t).vector for t in textos])
    vetores_trf = np.array(_transformer.encode(textos))
    return {"w2v": vetores_w2v, "trf": vetores_trf}


def max_similaridade(consulta, referencia):
    """
    Maior similaridade COMBINADA (word2vec + transformer) entre qualquer
    item de `consulta` e qualquer item de `referencia`.

    `consulta` e `referencia` são dicts vindos de embeddings(). Serve para
    perguntar "alguma palavra da pergunta se parece com algum sinônimo?".
    """
    sim_w2v = cosine_similarity(consulta["w2v"], referencia["w2v"])
    sim_trf = cosine_similarity(consulta["trf"], referencia["trf"])
    sim_combinada = PESO_WORD2VEC * sim_w2v + (1 - PESO_WORD2VEC) * sim_trf
    return float(sim_combinada.max())
