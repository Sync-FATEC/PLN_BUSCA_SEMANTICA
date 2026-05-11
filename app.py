from flask import Flask, render_template, request
import psycopg2
import re
import unidecode
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
from typing import Any

load_dotenv()

app = Flask(__name__)

def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unidecode.unidecode(texto)
    texto = re.sub(r"[^a-zA-Z0-9\s]", "", texto)
    return texto

consultas_referencia = [

    {
        "texto": "quantas imagens estao catalogadas",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "ha quantas imagens cadastradas",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "quantas imagens existem no banco",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "mostrar quantidade de imagens",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "quantas imagens existem",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "mostrar total de imagens",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "quantas imagens o sistema possui",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "exibir quantidade de imagens",
        "categoria": "contagem",
        "sql": "SELECT COUNT(*) FROM metadata_table"
    },

    {
        "texto": "mostrar todas as imagens",
        "categoria": "listagem_geral",
        "sql": "SELECT * FROM metadata_table"
    },

    {
        "texto": "listar imagens de vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "quais imagens possuem vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "listar imagens de agua",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "listar imagens de rios",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "buscar imagens de lagos",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "mostrar rios",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "buscar lagos",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "exibir represas",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "exibir regioes com agua",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "quais imagens possuem agua",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "listar imagens de floresta",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "buscar imagens com vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "mostrar regioes com vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "listar imagens de solo exposto",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "quais imagens possuem solo exposto",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "mostrar regioes secas",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "buscar desmatamento",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "buscar solo sem vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "listar areas desmatadas",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "mostrar imagens de desmatamento",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "listar imagens de satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "mostrar imagens de satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "listar imagens capturadas por satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "quais imagens vieram de satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "exibir imagens vindas de satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "exibir imagens capturadas do espaco",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "listar imagens de drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "listar imagens capturadas por drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "mostrar imagens de drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "quais imagens vieram de drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "buscar imagens aereas",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "mostrar imagens obtidas por drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "exibir vegetacao por satelite",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação' AND origem = 'satélite'"
    },

    {
        "texto": "exibir agua por drone",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água' AND origem = 'drone'"
    },

    {
        "texto": "exibir terra exposta por drone",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto' AND origem = 'drone'"
    },

    {
        "texto": "listar imagens de hoje",
        "categoria": "filtro_data",
        "sql": "SELECT * FROM metadata_table WHERE data_imagem = CURRENT_DATE"
    },

    {
        "texto": "quais imagens foram registradas hoje",
        "categoria": "filtro_data",
        "sql": "SELECT * FROM metadata_table WHERE data_imagem = CURRENT_DATE"
    },

    {
        "texto": "exibir imagens cadastradas hoje",
        "categoria": "filtro_data",
        "sql": "SELECT * FROM metadata_table WHERE data_imagem = CURRENT_DATE"
    },

    {
        "texto": "listar imagens do dia",
        "categoria": "filtro_data_dinamica",
        "sql": None
    },

    {
        "texto": "exibir vegetacao por drone",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação' AND origem = 'drone'"
    },

    {
        "texto": "mostrar agua de satelite",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água' AND origem = 'satélite'"
    },

    {
        "texto": "listar solo exposto por drone",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto' AND origem = 'drone'"
    },

    {
        "texto": "mostrar solo exposto de satelite",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto' AND origem = 'satélite'"
    },

    {
        "texto": "imagens de agua e drone",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água' AND origem = 'drone'"
    },

    {
        "texto": "imagens de vegetacao e satelite",
        "categoria": "filtro_combinado",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação' AND origem = 'satélite'"
    }
]

def corrigir_erros(texto):
    # Extrai todas as palavras únicas dos textos de referência
    palavras_conhecidas = set()
    for consulta in consultas_referencia:
        palavras = consulta["texto"].split()
        palavras_conhecidas.update(palavras)
    
    palavras_conhecidas = list(palavras_conhecidas)
    
    tokens = texto.split()
    corrigidos = []

    for token in tokens:
        # Se a palavra já está correta, mantém
        if token in palavras_conhecidas:
            corrigidos.append(token)
        else:
            # Tenta encontrar a palavra mais similar automaticamente
            melhor = process.extractOne(token, palavras_conhecidas)
            if melhor and melhor[1] >= 75:  # 75% de similaridade
                corrigidos.append(melhor[0])
            else:
                # Se não encontrar com alta similaridade, mantém a palavra original
                corrigidos.append(token)

    return " ".join(corrigidos)

def extrair_data(texto):
    """Extrai data no formato DD/MM/YYYY da pergunta"""
    import re
    padrao = r'(\d{1,2})/(\d{1,2})/(\d{4})'
    match = re.search(padrao, texto)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes}-{dia}"
    return None

def identificar_consulta(entrada):
    """
    Identifica a consulta usando BOW e similaridade de cosseno.
    Compara a entrada do usuário com todas as consultas de referência.
    """
    entrada_normalizada = normalizar_texto(entrada)
    entrada_corrigida = corrigir_erros(entrada_normalizada)

    # Normaliza todos os textos de referência
    textos = [normalizar_texto(c["texto"]) for c in consultas_referencia]
    textos.append(entrada_corrigida)

    # Cria representação BOW de todos os textos
    vectorizer = CountVectorizer()
    bow: Any = vectorizer.fit_transform(textos)

    # Extrai BOW da entrada do usuário (última linha)
    entrada_bow = bow.getrow(bow.shape[0] - 1)
    # BOWs das consultas de referência
    referencias_bow = bow[:-1]

    # Calcula similaridade de cosseno
    similaridades = cosine_similarity(
        entrada_bow,
        referencias_bow
    ).flatten()

    # Encontra a consulta mais similar
    indice = similaridades.argmax()
    maior_similaridade = similaridades[indice]

    # Se a similaridade for muito baixa, retorna None
    if maior_similaridade < 0.25:
        return None

    consulta = consultas_referencia[indice]
    
    # Se for filtro de data dinâmica, extrai a data
    if consulta["categoria"] == "filtro_data_dinamica":
        data_extraida = extrair_data(entrada)
        if data_extraida:
            consulta["sql"] = f"SELECT * FROM metadata_table WHERE data_imagem = '{data_extraida}'"
        else:
            return None
    
    return consulta

@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None
    imagens = []
    pergunta_digitada = None

    if request.method == "POST":
        pergunta = request.form["pergunta"]
        pergunta_digitada = pergunta
        consulta = identificar_consulta(pergunta)

        if consulta is None:
            resposta = "Não entendi sua busca. Tente perguntar de outra forma."
        else:
            conn = conectar()
            cursor = conn.cursor()
            
            sql = consulta["sql"]
            cursor.execute(sql)
            resultado = cursor.fetchall()
            conn.close()

            # Se for consulta de contagem, retorna apenas o resultado numérico
            if consulta["categoria"] == "contagem":
                total_imagens = resultado[0][0]
                resposta = f"No total, há {total_imagens} imagens cadastradas."
                imagens = []
            else:
                # Para outras consultas, exibe as imagens
                imagens = resultado
                quantidade = len(imagens)

                if quantidade == 0:
                    resposta = "Nenhuma imagem encontrada."
                elif quantidade == 1:
                    resposta = "Foi encontrada 1 imagem."
                else:
                    resposta = f"Foram encontradas {quantidade} imagens."

    return render_template("index.html", resposta=resposta, imagens=imagens, pergunta_digitada=pergunta_digitada)

if __name__ == "__main__":
    app.run(debug=True)