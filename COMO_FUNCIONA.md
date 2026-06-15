# Como funciona o sistema de busca semântica

A pessoa pergunta em português natural (com sinônimo, erro de digitação, do
jeito que quiser) e o sistema interpreta e devolve as imagens certas. Por
dentro, são **7 passos**, como uma esteira. Em cada passo está indicado o
**arquivo e a linha** onde aquilo acontece.

> Tudo é coordenado pela função `identificar_consulta()` —
> 📂 `busca/busca_semantica.py:22`

---

## 1️⃣ Pergunta

Entra a frase em texto puro (ex: *"imagens de vegetasao por drone"*).

📂 `app.py:56` — a rota `index()` recebe o texto do formulário e chama
`identificar_consulta()`.

---

## 2️⃣ Pré-processamento (limpeza + correção ortográfica)

Normaliza o texto (minúsculas, tira pontuação, **mantém os acentos**) e
corrige erros de digitação com o RapidFuzz: compara cada palavra por
similaridade de caracteres (ignorando acento) e devolve a forma certa →
*"vegetasao" vira "vegetação"*.

📂 `busca/preprocessamento.py`
- `normalizar()` → linha **27** (minúsculas, remove pontuação, mantém acento)
- `corrigir_ortografia()` → linha **35** (RapidFuzz, ignora palavras curtas)
- `preprocessar()` → linha **60** (junta as duas etapas)
- Limiar de aceitação da correção: `LIMIAR_CORRECAO = 85` em `busca/config.py:44`
- Vocabulário conhecido: `busca/vocabulario.py` (listas de sinônimos e palavras)

---

## 3️⃣ Vetorização (Word2Vec + Transformer)

Cada palavra vira um **embedding** (vetor de números que representa o
significado), de duas formas:
- **Word2Vec (spaCy)**: vetores a nível de **palavra** → captura sinônimos
  (água ≈ rio ≈ lago).
- **Transformer / LLM (sentence-transformers)**: embedding que entende o
  **contexto da frase**.

📂 `busca/modelos.py`
- Carregamento dos modelos: `_nlp` (Word2Vec) na linha **20** e `_transformer`
  (LLM) na linha **21**
- `embeddings()` → linha **25** (transforma a lista de palavras em vetores)
- Nomes dos modelos em `busca/config.py:24` e `:26`

---

## 4️⃣ Detecção de entidades

Cada categoria/origem tem uma lista de sinônimos já vetorizada. O sistema
calcula a **similaridade de cosseno** entre as palavras da pergunta e esses
sinônimos e **funde os dois modelos** numa média ponderada
(`0.5 × Word2Vec + 0.5 × Transformer`). Se passa do **limiar (0.70)**, a
entidade é detectada.

📂 `busca/modelos.py`
- `max_similaridade()` → linha **36** (cosseno + fusão 50/50; o peso é
  `PESO_WORD2VEC = 0.5` em `busca/config.py:33`)

📂 `busca/entidades.py` (cada "coisa" que ele entende)
- `detectar_categorias()` → linha **69** (devolve lista: 1 = filtro, 2+ = OU)
- `detectar_origens()` → linha **74**
- `detectar_intencao()` → linha **125** (contar vs listar)
- `detectar_meta()` → linha **90** ("quais categorias existem")
- `detectar_ranking()` → linha **104** ("qual tem mais/menos")
- `detectar_agrupamento()` → linha **156** ("quantas de cada categoria")
- `detectar_negacao()` → linha **132** ("não são de drone")
- `detectar_ordenacao_temporal()` → linha **138** ("mais antiga/recente")
- `eh_sobre_imagens()` → linha **79** (barra perguntas fora do escopo)
- Limiar de detecção: `LIMIAR_ENTIDADE = 0.70` em `busca/config.py:38`

📂 `busca/datas.py` (datas são tratadas por regras/regex, não por embedding)
- `detectar_data()` → linha **157** (orquestra os tipos abaixo)
- `_relativas()` → linha **31** ("hoje", "esse ano", "mês passado"...)
- `_intervalos()` → linha **72** ("entre 1 e 10 de maio", "antes de", "depois de")
- `_data_completa()` → linha **119** ("7 de maio", "05/05/2026")
- `_componentes()` → linha **125** ("dia 10", "mês 6", "2026" soltos)

---

## 5️⃣ Montagem dinâmica do SQL

A sacada: **não existe query pronta**, o sistema **constrói a SQL na hora**,
peça por peça.

📂 `busca/busca_semantica.py:22` (`identificar_consulta`) coleta tudo em
**campos preenchidos** (slots): `categorias`, `origens`, `condicao_data`,
`intencao`, `negado`, `ordenacao`.

📂 `busca/sql_builder.py` monta a query a partir desses slots:
- `_filtro_lista()` → linha **12** — transforma uma lista num pedaço de filtro:
  - 1 valor → `categoria = 'vegetação'`
  - 2+ valores → `categoria IN ('água','vegetação')`
  - com negação → `!=` / `NOT IN`
- `montar_sql()` → linha **22** — cola os pedaços com `AND`, monta o `WHERE`
  (ou nenhum, se não houver filtro) e escolhe o tipo pela intenção:
  - listar → `SELECT *`
  - contar → `SELECT COUNT(*)`
  - mais antiga/recente → `ORDER BY data_imagem ... LIMIT 1`
- `montar_ranking()` → linha **54** — `GROUP BY ... ORDER BY total` ("qual tem mais")
- `montar_breakdown()` → linha **70** — `GROUP BY` ("quantas de cada categoria")

É como **montar a frase do SQL com blocos de Lego** — por isso aceita
**qualquer combinação**. A mesma lógica gera:

| Pergunta | SQL gerado |
|---|---|
| "imagens de drone" | `SELECT * ... WHERE origem='drone'` |
| "água por satélite em maio" | `... WHERE categoria='água' AND origem='satélite' AND (EXTRACT(MONTH...)=5)` |
| "imagens que não são de drone" | `... WHERE origem != 'drone'` |
| "água ou vegetação" | `... WHERE categoria IN ('água','vegetação')` |
| "quantas fotos de drone" | `SELECT COUNT(*) ... WHERE origem='drone'` |
| "qual categoria tem mais imagens" | `SELECT categoria, COUNT(*) ... GROUP BY categoria ORDER BY total DESC` |

---

## 6️⃣ Banco de dados

O SQL roda no PostgreSQL, que devolve as linhas.

📂 `busca/database.py`
- `conectar()` → linha **13**
- `executar_consulta()` → linha **18** (roda o SQL e devolve os resultados)

---

## 7️⃣ Resultado

As imagens aparecem numa galeria (categoria/data/origem) e um painel mostra
**o que o sistema entendeu**.

📂 `app.py`
- `index()` → linha **56** decide a resposta conforme a intenção:
  - contagem/ranking/breakdown → frase de texto
  - listagem → galeria de imagens
- `_resposta_ranking()` → linha **29** e `_resposta_breakdown()` → linha **47**
  (montam as frases das perguntas analíticas)
- A galeria em si está em `templates/index.html`

---

## Resumo em uma frase

Texto → **corrige** (`preprocessamento.py`) → vira **embeddings**
(`modelos.py`) → **similaridade de cosseno** detecta as entidades
(`entidades.py` + `datas.py`) → **monta o SQL dinamicamente** com "blocos de
Lego" (`sql_builder.py`) → **consulta o banco** (`database.py`) → **exibe as
imagens** (`app.py` + `index.html`). O usuário fala natural; o sistema entende
e responde. 🚀

> Observação: os números de linha referem-se ao estado atual do código; se
> alguém editar os arquivos, eles podem mudar um pouco — mas os nomes das
> funções continuam os mesmos.
