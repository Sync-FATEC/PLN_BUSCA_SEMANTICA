# Motor de Busca Semântica com BOW

## Descrição

Este projeto consiste no desenvolvimento de um motor de busca semântica utilizando técnicas de Processamento de Linguagem Natural (PLN), representação Bag of Words (BOW) e similaridade de cosseno.

A aplicação permite que o usuário realize buscas textuais em um banco de dados de imagens de sensoriamento remoto, retornando resultados com base na similaridade semântica entre a consulta do usuário e consultas de referência previamente cadastradas.

## Tecnologias Utilizadas

- Python
- Flask
- PostgreSQL
- Scikit-learn
- RapidFuzz
- HTML/CSS

## Funcionalidades

- Busca textual semântica
- Pré-processamento de texto
- Correção de erros de digitação
- Representação Bag of Words (BOW)
- Similaridade de cosseno
- Integração com PostgreSQL
- Exibição de imagens na interface

## Metadados das Imagens

Cada imagem cadastrada possui:

- Categoria da imagem
  - Vegetação
  - Água
  - Solo exposto

- Data da imagem

- Origem da imagem
  - Satélite
  - Drone

- Caminho do arquivo da imagem

## Como Executar

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
```

### 2. Ativar ambiente virtual

```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## Configuração do Banco de Dados

### Criar banco

```sql
CREATE DATABASE busca_semantica;
```

### Executar scripts SQL

Executar:

- `database.sql`

## Executar Aplicação

```bash
python app.py
```

A aplicação estará disponível em:

```txt
http://127.0.0.1:5000
```

## Exemplos de Perguntas

## Categoria: Contagem de Imagens

### Tipo de consulta:
Contagem de registros cadastrados

- Quantas imagens estão catalogadas?
- Há quantas imagens cadastradas?
- Quantas imagens existem no banco?
- Mostrar quantidade de imagens
- Quantas imagens existem?
- Mostrar total de imagens
- Quantas imagens o sistema possui?
- Exibir quantidade de imagens
- Mostrar todas as imagens

## Categoria: Vegetação

### Tipo de consulta:
Filtro por categoria vegetação

- Mostrar imagens de vegetação
- Quais imagens possuem vegetação?
- Listar imagens com vegetação
- Buscar imagens de floresta
- Buscar vegetação
- Mostrar imagens de mata
- Listar áreas agrícolas
- Listar imagens de floresta
- Exibir vegetação por satélite


## Categoria: Água

### Tipo de consulta:
Filtro por categoria água

- Mostrar imagens de água
- Quais imagens possuem água?
- Exibir regiões com água
- Buscar imagens de rios e lagos
- Listar imagens de rios
- Buscar imagens de lagos
- Mostrar rios
- Buscar lagos
- Exibir represas
- Exibir água por drone

## Categoria: Solo Exposto

### Tipo de consulta:
Filtro por categoria solo exposto

- Mostrar terra exposta
- Mostrar imagens de solo exposto
- Mostrar regiões secas
- Buscar desmatamento
- Buscar solo sem vegetação
- Listar áreas desmatadas
- Mostrar imagens de desmatamento
- Exibir terra exposta por drone


## Categoria: Origem Satélite

### Tipo de consulta:
Filtro por origem satélite

- Mostrar imagens de satélite
- Listar imagens capturadas por satélite
- Quais imagens vieram de satélite?
- Exibir imagens vindas de satélite
- Exibir imagens capturadas do espaço

## Categoria: Origem Drone

### Tipo de consulta:
Filtro por origem drone

- Mostrar imagens de drone
- Listar imagens capturadas por drone
- Mostrar imagens obtidas por drone
- Quais imagens vieram de drone?
- Buscar imagens aéreas

## Categoria: Data

### Tipo de consulta:
Filtro por data

- Mostrar imagens de hoje
- Quais imagens foram registradas hoje?
- Exibir imagens cadastradas hoje
- Listar imagens do dia 02/05/2026
- Listar imagens do dia 05/05/2026
- Listar imagens do dia 11/05/2026



## Pipeline de PLN Utilizada

O sistema utiliza:

1. Normalização de texto
2. Remoção de caracteres especiais
3. Conversão para minúsculas
4. Correção de erros ortográficos
5. Tokenização
6. Representação Bag of Words
7. Similaridade de cosseno

