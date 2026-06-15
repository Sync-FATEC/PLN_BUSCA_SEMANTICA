"""
Pipeline de pré-processamento de texto (PLN).

Aplica, na ordem:
  1. Normalização         -> minúsculas e remoção de pontuação (MANTÉM acentos)
  2. Correção ortográfica  -> conserta erros e restaura acentos (RapidFuzz)

Por que manter os acentos? Porque os vetores do word2vec (spaCy) são
indexados nas palavras acentuadas ("água", "vegetação"). Sem acento, o
word2vec não acharia o vetor. A correção ortográfica compara as palavras
SEM acento (tolerante a digitação), mas devolve sempre a forma correta,
acentuada — pronta para o word2vec.
"""

import re
import unidecode
from rapidfuzz import process, fuzz

from .vocabulario import VOCABULARIO
from .config import LIMIAR_CORRECAO

# Palavras muito curtas (de, do, no, e, a, as...) não são corrigidas, para
# evitar trocas absurdas tipo "e" -> "aérea".
_TAMANHO_MINIMO = 4


def normalizar(texto):
    """minúsculas e remoção de pontuação, preservando letras acentuadas."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def corrigir_ortografia(texto):
    """
    Troca cada palavra desconhecida pela mais parecida do vocabulário.
    A comparação ignora acentos (processor=unidecode), então "agua" e
    "vegetasao" viram "água" e "vegetação".
    """
    corrigidos = []
    for token in texto.split():
        if token in VOCABULARIO or len(token) < _TAMANHO_MINIMO:
            corrigidos.append(token)
            continue

        melhor = process.extractOne(
            token, VOCABULARIO,
            scorer=fuzz.ratio,
            processor=unidecode.unidecode,
        )
        if melhor and melhor[1] >= LIMIAR_CORRECAO:
            corrigidos.append(melhor[0])
        else:
            corrigidos.append(token)

    return " ".join(corrigidos)


def preprocessar(texto):
    """Pipeline completa: normalização + correção ortográfica."""
    return corrigir_ortografia(normalizar(texto))
