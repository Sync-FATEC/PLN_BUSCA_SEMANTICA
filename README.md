# Busca Semântica em Banco de Imagens — word2vec + Transformers (LLM)

## 1. Descrição

Sistema que permite consultar, em **linguagem natural** (português), um banco
de imagens de sensoriamento remoto. O usuário escreve uma pergunta qualquer
(ex.: *"fotos de drone no mês 6"*) e o sistema **interpreta** a frase e gera a
consulta SQL correspondente, exibindo as imagens encontradas.

Em vez de casar a pergunta com uma lista de consultas prontas, o sistema
**extrai entidades** (categoria, origem, data, intenção) e **monta o SQL
dinamicamente**. Por isso aceita **qualquer combinação** desses elementos.

As duas tecnologias do enunciado são usadas **juntas** para entender o texto:

- **word2vec** — vetores de palavras pré-treinados em português (spaCy)
- **Transformers (LLM)** — modelo de sentenças (sentence-transformers)

---

## 2. Tecnologias

| Tecnologia | Papel no projeto |
|------------|------------------|
| Python + Flask | Servidor web e interface |
| PostgreSQL (psycopg2) | Armazena os metadados das imagens |
| **spaCy** (`pt_core_news_md`) | Fornece os vetores **word2vec** |
| **sentence-transformers** (`paraphrase-multilingual-MiniLM-L12-v2`) | Fornece os embeddings do **transformer (LLM)** |
| scikit-learn | Calcula a **similaridade de cosseno** |
| RapidFuzz + Unidecode | **Correção ortográfica** tolerante a acento |
| HTML/CSS | Interface visual (galeria de imagens) |

---

## 3. Estrutura do projeto

```
PLN_BUSCA_SEMANTICA/
├── app.py                      # Interface web (Flask) — apenas as rotas
├── requirements.txt
├── database.sql                # Criação da tabela + dados de exemplo
├── templates/index.html        # Página + painel do que foi entendido
├── static/images/              # Imagens (vegetação, água, solo exposto)
└── busca/                      # Toda a lógica do sistema
    ├── __init__.py             # Ativa o modo offline dos modelos (se há cache)
    ├── config.py               # Configurações (banco, modelos, limiares)
    ├── vocabulario.py          # Sinônimos de cada categoria/origem
    ├── modelos.py              # Carrega word2vec + transformer e mede similaridade
    ├── preprocessamento.py     # Normalização + correção ortográfica
    ├── entidades.py            # Detecta categoria, origem e intenção
    ├── datas.py                # Detecta a expressão de data → condição SQL
    ├── sql_builder.py          # Monta o SQL a partir das entidades
    ├── busca_semantica.py      # Orquestra tudo (identificar_consulta)
    └── database.py             # Conexão e execução de queries
```

A separação segue a ideia de **uma responsabilidade por arquivo**, o que
facilita explicar cada etapa isoladamente.

---

## 4. A pipeline passo a passo (no código)

Visão geral do caminho de uma pergunta:

```
pergunta do usuário
  1. pré-processamento        (preprocessamento.py)
  2. vetorização das palavras (modelos.py)
  3. detecção de entidades    (entidades.py + datas.py)
  4. verificação de domínio    (entidades.py)
  5. montagem do SQL           (sql_builder.py)
  6. execução e exibição       (database.py + app.py)
```

Tudo é coordenado pela função `identificar_consulta()` em
`busca/busca_semantica.py`.

### 4.1. Pré-processamento — `preprocessamento.py`

Duas etapas, aplicadas em sequência por `preprocessar()`:

**a) Normalização** — `normalizar()`
- passa tudo para minúsculas;
- remove pontuação com `re.sub(r"[^\w\s]", " ", texto)`;
- **mantém os acentos** de propósito (ver seção 5.1).

**b) Correção ortográfica** — `corrigir_ortografia()`
- usa o **RapidFuzz** para trocar cada palavra desconhecida pela mais
  parecida do `VOCABULARIO`;
- a comparação é feita **sem acento** (`processor=unidecode`) e por
  similaridade de caracteres (`scorer=fuzz.ratio`), mas a palavra devolvida
  é a forma **correta e acentuada**. Ex.: `"vegetasao"` → `"vegetação"`,
  `"agua"` → `"água"`;
- palavras com menos de 4 letras (de, do, no, e, as...) **não** são
  corrigidas, para evitar trocas absurdas como `"e"` → `"aérea"`;
- só aceita a correção se a similaridade for ≥ `LIMIAR_CORRECAO` (80).

Resultado: um texto limpo, acentuado e sem erros, pronto para virar vetor.

### 4.2. Vetorização — `modelos.py`

Aqui as **duas tecnologias** entram em ação. A função `embeddings(textos)`
recebe uma lista de palavras e devolve dois conjuntos de vetores:

- **word2vec** (`_nlp(t).vector`): cada palavra vira um vetor de números
  pré-treinado (spaCy). Palavras com sentido parecido têm vetores próximos.
- **transformer** (`_transformer.encode(...)`): o modelo de sentenças (LLM)
  gera outro vetor, que captura o significado considerando o contexto.

Os modelos são carregados **uma única vez**, quando o módulo é importado.

### 4.3. Similaridade de cosseno + fusão — `modelos.py`

A função `max_similaridade(consulta, referencia)`:

1. calcula a **similaridade de cosseno** entre os vetores da pergunta e os
   vetores de referência, separadamente para word2vec e para o transformer;
2. **combina** os dois numa média ponderada:

   ```
   similaridade = PESO_WORD2VEC * word2vec + (1 - PESO_WORD2VEC) * transformer
   ```

   (com `PESO_WORD2VEC = 0.5`, peso igual para os dois);
3. devolve o **maior** valor encontrado — ou seja, "a palavra mais parecida
   da pergunta com o sinônimo mais parecido da categoria".

> A comparação é **palavra a palavra** (cada token da pergunta contra cada
> sinônimo). Isso é mais robusto do que comparar a frase inteira, porque o
> tamanho da frase não dilui o sinal do termo importante.

### 4.4. Detecção de entidades — `entidades.py`

Os sinônimos de cada categoria/origem ficam em `vocabulario.py` e têm seus
embeddings **pré-calculados** no início (`_CATEGORIAS_EMB`, `_ORIGENS_EMB`).

- **`detectar_categoria()`** e **`detectar_origem()`**: para cada valor
  possível (vegetação, água, solo exposto / satélite, drone), calculam a
  similaridade combinada com as palavras da pergunta e escolhem o melhor.
  Se ficar acima de `LIMIAR_ENTIDADE` (0.60), a entidade foi detectada;
  senão, retorna `None` (aquele filtro não se aplica).
- **`detectar_intencao()`**: olha se a pergunta tem palavras como "quantas",
  "total", "quantidade" (`PALAVRAS_CONTAGEM`). Se sim → `"contagem"`;
  senão → `"listagem"`.
- **`detectar_meta()`**: reconhece perguntas **sobre os metadados** em vez de
  sobre as imagens — ex.: *"quais são as categorias disponíveis?"* →
  `SELECT DISTINCT categoria`. Só vale quando nenhum valor específico foi
  citado (assim *"imagens da categoria água"* não cai aqui por engano).
- **`detectar_ranking()`**: reconhece perguntas **analíticas** — uma
  **direção** (mais/menos) + uma **dimensão** (categoria/origem/mês/data).
  Ex.: *"qual categoria tem mais imagens"*, *"em que mês tem menos fotos"*.
  Gera um `GROUP BY ... COUNT(*) ... ORDER BY` (ver 4.7).
- **`detectar_agrupamento()`**: *"quantas imagens de cada categoria"* →
  contagem por grupo (`GROUP BY`), listando todos os valores e seus totais.
- **`detectar_negacao()`**: detecta "não", "sem", "exceto" → inverte o filtro
  (`!=` / `NOT IN`). Ex.: *"imagens que não são de drone"*.
- **`detectar_categorias()` / `detectar_origens()`** devolvem **listas**: se
  o usuário citar mais de um valor (*"água ou vegetação"*), vira `IN (...)`.
- **`detectar_ordenacao_temporal()`**: *"a imagem mais antiga/recente"* →
  `ORDER BY data_imagem` + `LIMIT 1`.
- **`eh_sobre_imagens()`**: verifica se a pergunta contém alguma palavra do
  domínio (imagens, fotos, mostrar...). A checagem é **exata por token** —
  de propósito: por embedding, verbos genéricos ("fazer", "ver") se parecem
  entre si e deixariam passar perguntas fora do assunto, como
  *"como fazer bolo de chocolate"*. Serve de "guarda" (seção 4.6).

### 4.5. Detecção de data — `datas.py`

A função `detectar_data()` recebe o **texto original** (não o corrigido) e
tenta, nesta ordem:

1. **Relativas ao agora** (`_relativas`): "hoje", "ontem", "esse mês",
   "mês passado", "esse ano", "ano passado", "essa/semana passada".
2. **Data completa** (`_data_completa`): "05/05/2026", "05/05",
   "7 de maio de 2026", "7 de maio" (ano opcional).
3. **Intervalos e comparadores** (`_intervalos`): "entre 1 e 10 de maio"
   (`BETWEEN`), "antes de 10 de maio" (`<`), "depois de 5 de maio" (`>`),
   "a partir de ..." (`>=`), "até ..." (`<=`).
4. **Componentes soltos** (`_componentes`): combina o que achar — "dia 10"
   (só o dia), "mês 6" ou "maio" (só o mês), "2026" (só o ano).

O retorno é a **condição SQL** sobre a coluna `data_imagem`. As condições
usam funções do PostgreSQL (`CURRENT_DATE`, `make_date`, `EXTRACT`,
`date_trunc`), então o "agora" é sempre o dia em que a consulta roda — sem
datas fixas no código. Exemplos:

| Pergunta | Condição gerada |
|----------|-----------------|
| "imagens de hoje" | `data_imagem = CURRENT_DATE` |
| "esse ano" | `EXTRACT(YEAR FROM data_imagem) = EXTRACT(YEAR FROM CURRENT_DATE)` |
| "mês 6" | `EXTRACT(MONTH FROM data_imagem) = 6` |
| "dia 10" | `EXTRACT(DAY FROM data_imagem) = 10` |
| "7 de maio" | `data_imagem = make_date(EXTRACT(YEAR FROM CURRENT_DATE)::int, 5, 7)` |
| "em 2026" | `EXTRACT(YEAR FROM data_imagem) = 2026` |

### 4.6. Verificação de domínio (on-topic) — `busca_semantica.py`

Antes de montar o SQL, o sistema decide se a pergunta é mesmo sobre imagens:

```python
on_topic = bool(categoria or origem) or eh_sobre_imagens(tokens)
```

- se detectou categoria ou origem → claramente é do domínio;
- senão, exige que a pergunta contenha alguma **palavra do domínio**
  (imagens, fotos, mostrar...) — verificação exata por token.

Se nada disso valer, retorna `None` e a interface responde *"Não entendi sua
busca"*. É isso que rejeita *"qual a cotação do dólar hoje"* (mesmo contendo
"hoje"), *"como fazer bolo de chocolate"* e *"quantas casas tem no brasil"*
(mesmo contendo "quantas").

### 4.7. Montagem dinâmica do SQL — `sql_builder.py`

`montar_sql()` junta **apenas os filtros detectados** com `AND`:

- `categoria = '...'` se houver categoria;
- `origem = '...'` se houver origem;
- a condição de data, se houver;
- `SELECT COUNT(*)` se a intenção for contagem, senão `SELECT *`.

Exemplo: *"fotos de drone no mês 6"* →
```sql
SELECT * FROM metadata_table
WHERE origem = 'drone' AND (EXTRACT(MONTH FROM data_imagem) = 6)
```

Para perguntas **analíticas**, `montar_ranking()` gera uma agregação. Exemplo:
*"qual categoria tem mais imagens"* →
```sql
SELECT categoria AS valor, COUNT(*) AS total
FROM metadata_table GROUP BY categoria ORDER BY total DESC, valor
```
O `app.py` pega o extremo (mais/menos) e trata empates na resposta.

### 4.8. Execução e exibição — `database.py` + `app.py`

- `database.executar_consulta(sql)` abre a conexão, roda a query e devolve as
  linhas (sempre fechando a conexão no final).
- `app.py` decide a resposta: se for **contagem**, mostra só o número; senão,
  monta a **galeria** de imagens. O painel azul exibe o que o sistema
  entendeu (categoria, origem, data, ação).

---

## 5. Detalhes importantes (decisões de projeto)

### 5.1. Por que manter os acentos?

Os vetores word2vec do spaCy são indexados nas palavras **acentuadas**
("água", "vegetação"). Se removêssemos o acento (com `unidecode`), essas
palavras virariam "desconhecidas" e o word2vec devolveria um vetor nulo —
ou seja, **o word2vec deixaria de funcionar** e só o transformer contribuiria.

Por isso o pré-processamento mantém os acentos, e a correção ortográfica é
quem **restaura** o acento quando o usuário digita sem (comparando sem acento,
mas devolvendo a forma correta).

### 5.2. Limiares calibrados com medições

Os limiares não foram chutados: medimos os scores reais de várias perguntas.
Termos corretos pontuam **≥ 0.79** (ex.: "regiões secas"→solo exposto 0.79,
"matas"→vegetação 1.0); falsos positivos ficam **≤ 0.63** (ex.: "casas"→
vegetação 0.62). O corte em **0.70** fica no meio do vão, com folga dos dois
lados.

### 5.3. Embeddings pré-calculados

Os vetores dos sinônimos e do vocabulário de domínio são calculados **uma
vez** no início (em `entidades.py`). A cada pergunta, só os vetores da
pergunta são calculados — deixando a busca rápida.

### 5.4. Funciona offline

`busca/__init__.py` ativa o modo offline do HuggingFace **se o modelo já
estiver em cache**. Assim, depois do primeiro download, o sistema roda sem
internet (importante para o dia da apresentação). Numa máquina nova, mantém
online para baixar o modelo na primeira vez.

### 5.5. Observação de segurança

Como é um trabalho acadêmico com vocabulário controlado, o SQL é montado por
interpolação de strings. Em produção, o ideal seria usar **queries
parametrizadas** para evitar injeção de SQL.

---

## 6. Como executar

### 6.1. Ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 6.2. Dependências

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_md
```

> Na **primeira** execução, o sentence-transformers baixa o modelo (precisa de
> internet). Depois funciona **offline**.

### 6.3. Banco de dados

Crie o arquivo `.env` na raiz:

```env
DB_HOST=localhost
DB_DATABASE=busca_semantica
DB_USER=postgres
DB_PASSWORD=sua_senha
```

Crie o banco e carregue os dados:

```sql
CREATE DATABASE busca_semantica;
```

Depois execute o conteúdo de `database.sql`.

### 6.4. Rodar

```bash
python app.py
```

Acesse: http://127.0.0.1:5000

---

## 7. Exemplos de perguntas

**Categoria:** "quais imagens possuem vegetação", "mostrar lagos e rios",
"buscar áreas de desmatamento", "vegetasao por satelite" (com erro)

**Origem:** "imagens de drone", "fotos vindas de satélite"

**Data:** "imagens de hoje", "fotos do mês passado", "imagens do dia 10",
"imagens do mês 5", "7 de maio", "05/05/2026", "em 2026", "desse ano"

**Combinações:** "fotos de drone esse ano", "água por satélite no mês 5",
"vegetação por drone no dia 2 de maio", "solo exposto do ano passado"

**Contagem:** "quantas imagens existem", "quantas fotos de satélite"

**Sobre os metadados:** "quais são as categorias disponíveis?",
"quais origens existem?", "quais os tipos de imagens?"

**Analíticas (ranking):** "qual categoria tem mais imagens",
"qual origem é mais usada", "em que mês tem mais fotos",
"qual é a data com menos imagens"

**Contagem por grupo:** "quantas imagens de cada categoria",
"imagens por origem"

**Negação e "ou":** "imagens que não são de drone",
"imagens de água ou vegetação"

**Intervalos de data:** "imagens entre 1 e 10 de maio",
"imagens antes de 10 de maio", "imagens depois de 5 de maio"

**Mais antiga/recente:** "qual a imagem mais antiga", "a imagem mais recente"

**Fora do escopo (responde "não entendi"):** "como fazer bolo de chocolate",
"qual a cotação do dólar hoje", "quantas casas tem no brasil"

> **Atenção aos dados:** as imagens de exemplo são de **maio/2026**. Logo,
> "imagens de hoje"/"esse mês" funcionam, mas devolvem vazio (não há imagem do
> mês atual). Para demonstrar data, prefira "esse ano", "mês 5" ou "7 de maio".

---

## 8. Limitações conhecidas

- O reconhecimento de sinônimos depende do `vocabulario.py`; termos muito
  diferentes podem não ser detectados (basta adicioná-los lá).
- O SQL usa interpolação de strings (ver 5.5).
- Datas por extenso assumem o ano atual quando o ano não é informado.
- A negação inverte **todos** os filtros detectados; uma frase que misture
  positivo e negativo ("vegetação que não é de drone") não é tratada.
- Não há suporte a: busca por id ("imagem 3"), limite N ("as 3 primeiras"),
  porcentagem nem ordenação livre — fora do escopo atual.
