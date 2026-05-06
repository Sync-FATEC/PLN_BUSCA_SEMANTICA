from flask import Flask, render_template, request
import psycopg2
import re
import unidecode
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process
from typing import Any

app = Flask(__name__)

def conectar():
    return psycopg2.connect(
        host="localhost",
        database="busca_semantica",
        user="postgres",
        password="admin"
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
        "texto": "listar imagens de vegetacao",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'vegetação'"
    },

    {
        "texto": "listar imagens de agua",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'água'"
    },

    {
        "texto": "listar imagens de solo exposto",
        "categoria": "filtro_categoria",
        "sql": "SELECT * FROM metadata_table WHERE categoria = 'solo exposto'"
    },

    {
        "texto": "listar imagens de satelite",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'satélite'"
    },

    {
        "texto": "listar imagens de drone",
        "categoria": "filtro_origem",
        "sql": "SELECT * FROM metadata_table WHERE origem = 'drone'"
    },

    {
        "texto": "listar imagens de hoje",
        "categoria": "filtro_data",
        "sql": "SELECT * FROM metadata_table WHERE data_imagem = CURRENT_DATE"
    },

    {
        "texto": "listar todas as imagens",
        "categoria": "listagem_geral",
        "sql": "SELECT * FROM metadata_table"
    }
]

def corrigir_erros(texto):
    palavras_validas = [
        "quantas", "imagens", "catalogadas", "listar", "vegetacao",
        "agua", "solo", "exposto", "satelite", "drone", "todas"
    ]

    tokens = texto.split()
    corrigidos = []

    for token in tokens:
        melhor = process.extractOne(token, palavras_validas)
        if melhor and melhor[1] >= 80:
            corrigidos.append(melhor[0])
        else:
            corrigidos.append(token)

    return " ".join(corrigidos)

def identificar_consulta(entrada):
    entrada = normalizar_texto(entrada)
    entrada = corrigir_erros(entrada)

    textos = [normalizar_texto(c["texto"]) for c in consultas_referencia]
    textos.append(entrada)

    vectorizer = CountVectorizer()

    bow: Any = vectorizer.fit_transform(textos)

    entrada_bow = bow.getrow(bow.shape[0] - 1)
    referencias_bow = bow[:-1]

    similaridades = cosine_similarity(
        entrada_bow,
        referencias_bow
    ).flatten()

    indice = similaridades.argmax()
    maior_similaridade = similaridades[indice]

    if maior_similaridade < 0.25:
        return None

    return consultas_referencia[indice]

@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None
    imagens = []

    if request.method == "POST":
        pergunta = request.form["pergunta"]
        consulta = identificar_consulta(pergunta)

        if consulta is None:
            resposta = "Não entendi sua busca. Tente perguntar de outra forma."
        else:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(consulta["sql"])
            resultado = cursor.fetchall()
            conn.close()

            if consulta["categoria"] == "contagem":
                resposta = f"No total, há {resultado[0][0]} imagens cadastradas."
            else:
                imagens = resultado
                quantidade = len(imagens)

                if quantidade == 0:
                    resposta = "Nenhuma imagem encontrada."
                elif quantidade == 1:
                    resposta = "Foi encontrada 1 imagem."
                else:
                    resposta = f"Foram encontradas {quantidade} imagens."

    return render_template("index.html", resposta=resposta, imagens=imagens)

if __name__ == "__main__":
    app.run(debug=True)