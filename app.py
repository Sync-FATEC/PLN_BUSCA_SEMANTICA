"""
Ponto de entrada da aplicação web (Flask).

Este arquivo é propositalmente fino: ele só cuida da interface (receber a
pergunta, chamar a busca, montar a resposta e renderizar a página).
Toda a lógica de PLN/busca está no pacote `busca`.
"""

from flask import Flask, render_template, request

from busca.database import executar_consulta
from busca.busca_semantica import identificar_consulta

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None
    imagens = []
    pergunta = None
    detalhe = None            # informações da busca (para exibir na tela)

    if request.method == "POST":
        pergunta = request.form["pergunta"]

        consulta = identificar_consulta(pergunta)

        if consulta is None:
            resposta = "Não entendi sua busca. Tente perguntar de outra forma."
        else:
            resultado = executar_consulta(consulta["sql"])
            detalhe = consulta

            if consulta["intencao"] == "contagem":
                total = resultado[0][0]
                resposta = f"No total, há {total} imagens cadastradas."
            else:
                imagens = resultado
                quantidade = len(imagens)
                if quantidade == 0:
                    resposta = "Nenhuma imagem encontrada."
                elif quantidade == 1:
                    resposta = "Foi encontrada 1 imagem."
                else:
                    resposta = f"Foram encontradas {quantidade} imagens."

    return render_template(
        "index.html",
        resposta=resposta,
        imagens=imagens,
        pergunta_digitada=pergunta,
        detalhe=detalhe,
    )


if __name__ == "__main__":
    # use_reloader=False evita que o Flask carregue os modelos duas vezes.
    app.run(debug=True, use_reloader=False)
