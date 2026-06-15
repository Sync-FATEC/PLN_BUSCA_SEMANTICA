"""
Vocabulário do domínio: tudo que o sistema "conhece".

Usado em dois lugares:
  - correção ortográfica (todas as palavras conhecidas)
  - detecção de entidades (sinônimos de cada categoria/origem)

IMPORTANTE: os termos ficam COM acento, porque os vetores do word2vec
(spaCy em português) são indexados nas palavras acentuadas. A correção
ortográfica é tolerante a acento, então o usuário pode digitar sem.

Para reconhecer uma nova forma de falar (ex.: "riacho" para água), basta
acrescentar a palavra na lista correspondente aqui.
"""

CATEGORIAS = {
    "vegetação": ["vegetação", "floresta", "florestas", "mata", "matas",
                   "árvores", "plantas", "verde", "matagal"],
    "água": ["água", "rio", "rios", "lago", "lagos", "represa", "represas",
              "mar", "oceano", "lagoa", "lagoas", "córrego", "riacho"],
    "solo exposto": ["solo exposto", "terra exposta", "desmatamento",
                      "área desmatada", "áreas desmatadas", "região seca",
                      "regiões secas", "solo sem vegetação", "terra", "seca"],
}

# Origem -> formas de se referir a ela
ORIGENS = {
    "satélite": ["satélite", "satélites", "espaço", "orbital", "órbita"],
    "drone": ["drone", "drones", "aérea", "aéreo", "aéreas", "voo", "sobrevoo"],
}

# Palavras que indicam intenção de CONTAR (em vez de listar)
PALAVRAS_CONTAGEM = ["quantas", "quantos", "quantidade", "total", "contar", "número"]

# Palavras genéricas do domínio (ajudam na correção e a saber se é sobre imagens)
PALAVRAS_DOMINIO = [
    "imagens", "imagem", "fotos", "foto", "mostrar", "listar", "exibir",
    "buscar", "ver", "todas", "todos", "cadastradas", "registradas",
    "capturadas", "obtidas", "possuem", "existem", "banco", "catalogadas",
]

# Palavras que indicam pergunta SOBRE os metadados (e não sobre as imagens)
# ex.: "quais são as categorias disponíveis?"
PALAVRAS_META_CATEGORIA = ["categorias", "categoria", "tipos", "tipo", "classes"]
PALAVRAS_META_ORIGEM = ["origens", "origem", "fontes"]

# Palavras de perguntas analíticas (ranking): "qual tem MAIS/MENOS imagens"
PALAVRAS_RANKING = ["mais", "menos", "maior", "menor", "maiores", "menores",
                    "data", "datas", "meses"]

# Negação: "imagens que NÃO são de drone", "SEM vegetação"
PALAVRAS_NEGACAO = ["nao", "sem", "exceto", "fora"]

# Ordenação temporal: "imagem mais ANTIGA / mais RECENTE"
PALAVRAS_TEMPORAL_ANTIGA = ["antiga", "antigo", "antigas", "antigos",
                             "velha", "velho", "primeira", "primeiro"]
PALAVRAS_TEMPORAL_RECENTE = ["recente", "recentes", "nova", "novo", "novas",
                              "novos", "ultima", "ultimo", "ultimas", "ultimos"]

# Agrupamento: "quantas imagens de CADA categoria", "imagens POR origem"
PALAVRAS_AGRUPAR = ["cada", "por"]

# Palavras ligadas a datas (para a correção ortográfica não as estragar)
PALAVRAS_DATA = [
    "hoje", "ontem", "dia", "semana", "mês", "ano", "esse", "este", "essa",
    "esta", "deste", "desta", "passado", "passada",
    "entre", "antes", "depois", "apos", "até", "partir",
    "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
    "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _coletar_vocabulario():
    """Junta todas as palavras únicas conhecidas (para a correção ortográfica)."""
    palavras = set()
    for sinonimos in list(CATEGORIAS.values()) + list(ORIGENS.values()):
        for frase in sinonimos:
            palavras.update(frase.split())
    palavras.update(PALAVRAS_CONTAGEM)
    palavras.update(PALAVRAS_DOMINIO)
    palavras.update(PALAVRAS_META_CATEGORIA)
    palavras.update(PALAVRAS_META_ORIGEM)
    palavras.update(PALAVRAS_RANKING)
    palavras.update(PALAVRAS_NEGACAO)
    palavras.update(PALAVRAS_TEMPORAL_ANTIGA)
    palavras.update(PALAVRAS_TEMPORAL_RECENTE)
    palavras.update(PALAVRAS_AGRUPAR)
    palavras.update(PALAVRAS_DATA)
    return sorted(palavras)


VOCABULARIO = _coletar_vocabulario()
