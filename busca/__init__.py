"""
Pacote `busca` — toda a lógica do motor de busca semântica.

Módulos:
  - config:           configurações (banco, modelos, limiares)
  - vocabulario:      termos conhecidos (sinônimos de categoria/origem)
  - modelos:          carrega word2vec + transformer e mede similaridade
  - preprocessamento: pipeline PLN (normalização + correção ortográfica)
  - entidades:        detecta categoria, origem e intenção
  - datas:            detecta expressões de data -> condição SQL
  - sql_builder:      monta o SQL a partir das entidades
  - busca_semantica:  orquestra tudo (função identificar_consulta)
  - database:         conexão e execução de queries no PostgreSQL
"""

import os
from pathlib import Path

# Se o modelo transformer já foi baixado, usa o cache local e NÃO checa a
# internet — assim o sistema funciona offline (ex.: no dia da apresentação).
# Numa máquina nova, sem cache, mantém online para o primeiro download.
_cache_hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
_modelo = _cache_hub / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
if _modelo.exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
