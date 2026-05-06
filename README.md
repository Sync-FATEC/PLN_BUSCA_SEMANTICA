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

- `schema.sql`

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
- Total de imagens registradas?
- Quantas imagens existem no banco?
- Mostrar quantidade de imagens
- Quantidade total de imagens
- Quantas imagens foram armazenadas?
- Número de imagens cadastradas
- Quantas imagens existem?
- Mostrar total de imagens
- Quantos registros existem?
- Quantidade de registros
- Quantidade total cadastrada
- Quantas imagens o sistema possui?
- Exibir quantidade de imagens

## Categoria: Vegetação

### Tipo de consulta:
Filtro por categoria vegetação

- Mostrar imagens de vegetação
- Quais imagens possuem vegetação?
- Listar imagens com vegetação
- Exibir áreas verdes
- Buscar imagens de floresta
- Mostrar florestas
- Buscar vegetação
- Mostrar imagens de mata
- Exibir plantações
- Listar áreas agrícolas
- Mostrar cobertura vegetal
- Buscar regiões verdes
- Mostrar imagens vegetais
- Exibir vegetação por satélite
- Listar imagens de floresta

## Categoria: Água

### Tipo de consulta:
Filtro por categoria água

- Mostrar imagens de água
- Quais imagens possuem água?
- Listar imagens de rios
- Exibir imagens aquáticas
- Buscar imagens de lagos
- Mostrar rios
- Buscar lagos
- Exibir represas
- Mostrar imagens marítimas
- Buscar áreas alagadas
- Mostrar reservatórios
- Exibir regiões com água
- Listar imagens aquáticas
- Mostrar oceano
- Buscar imagens de rios e lagos

## Categoria: Solo Exposto

### Tipo de consulta:
Filtro por categoria solo exposto

- Mostrar imagens de solo exposto
- Quais imagens possuem terra exposta?
- Listar áreas desmatadas
- Exibir regiões sem vegetação
- Buscar imagens de solo seco
- Mostrar áreas áridas
- Buscar desmatamento
- Exibir solo descoberto
- Mostrar regiões secas
- Buscar áreas degradadas
- Exibir mineração
- Mostrar terra exposta
- Buscar solo sem vegetação
- Exibir áreas marrons
- Mostrar imagens de desmatamento

## Categoria: Origem Satélite

### Tipo de consulta:
Filtro por origem satélite

- Mostrar imagens de satélite
- Listar imagens capturadas por satélite
- Quais imagens vieram de satélite?
- Buscar imagens orbitais
- Exibir imagens espaciais
- Mostrar registros de satélite
- Buscar imagens via satélite
- Exibir capturas orbitais
- Mostrar imagens espaciais
- Buscar imagens de origem satélite
- Mostrar fotos de satélite
- Exibir imagens capturadas do espaço
- Buscar registros espaciais
- Mostrar imagens orbitais
- Exibir imagens vindas de satélite

## Categoria: Origem Drone

### Tipo de consulta:
Filtro por origem drone

- Mostrar imagens de drone
- Listar imagens capturadas por drone
- Quais imagens vieram de drone?
- Buscar imagens aéreas
- Exibir imagens de drone
- Mostrar capturas aéreas
- Buscar registros de drone
- Exibir imagens aéreas
- Mostrar fotos de drone
- Buscar imagens capturadas do ar
- Exibir registros aéreos
- Mostrar imagens obtidas por drone
- Buscar imagens voadoras
- Exibir imagens capturadas por voo
- Mostrar imagens de origem drone

## Categoria: Data

### Tipo de consulta:
Filtro por data

- Mostrar imagens de hoje
- Listar imagens do dia 05/05/2026
- Quais imagens foram registradas hoje?
- Buscar imagens recentes
- Exibir imagens por data
- Mostrar imagens do dia
- Buscar registros recentes
- Exibir imagens cadastradas hoje
- Mostrar imagens antigas
- Buscar imagens por período
- Exibir registros por data
- Mostrar imagens do mês
- Buscar imagens da semana
- Exibir imagens recentes
- Mostrar imagens cadastradas recentemente

## Pipeline de PLN Utilizada

O sistema utiliza:

1. Normalização de texto
2. Remoção de caracteres especiais
3. Conversão para minúsculas
4. Correção de erros ortográficos
5. Tokenização
6. Representação Bag of Words
7. Similaridade de cosseno

