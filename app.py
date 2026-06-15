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

_MESES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
          "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def _formatar_valor(valor, tipo):
    """Formata o valor de um ranking conforme a dimensão."""
    if tipo == "mes":
        return _MESES[int(valor)]
    if tipo == "data" and hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _resposta_ranking(consulta, resultado):
    """Monta a frase de resposta de uma pergunta analítica (ranking)."""
    if not resultado:
        return "Nenhuma imagem encontrada."

    extremo = resultado[0][1]                       # maior/menor contagem
    empatados = [linha for linha in resultado if linha[1] == extremo]
    valores = [_formatar_valor(linha[0], consulta["tipo"]) for linha in empatados]
    palavra = "mais" if consulta["direcao"] == "mais" else "menos"

    if len(valores) == 1:
        return f"{consulta['rotulo']} com {palavra} imagens é {valores[0]} ({extremo} imagens)."
    if len(valores) <= 4:
        lista = ", ".join(valores[:-1]) + " e " + valores[-1]
        return f"Empate ({palavra} imagens): {lista}, com {extremo} imagens cada."
    return f"Empate: {len(valores)} valores com {extremo} imagens cada."


def _resposta_breakdown(consulta, resultado):
    """Monta a frase de uma contagem por grupo ('quantas de cada categoria')."""
    if not resultado:
        return "Nenhuma imagem encontrada."
    partes = [f"{_formatar_valor(v, consulta['tipo'])}: {n}" for v, n in resultado]
    return f"Imagens por {consulta['nome_dimensao']} — " + ", ".join(partes) + "."


@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None
    imagens = []
    pergunta = None
    detalhe = None

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
            elif consulta["intencao"] == "listar_categorias":
                valores = ", ".join(linha[0] for linha in resultado)
                resposta = f"As categorias disponíveis são: {valores}."
            elif consulta["intencao"] == "listar_origens":
                valores = ", ".join(linha[0] for linha in resultado)
                resposta = f"As origens disponíveis são: {valores}."
            elif consulta["intencao"] == "ranking":
                resposta = _resposta_ranking(consulta, resultado)
            elif consulta["intencao"] == "breakdown":
                resposta = _resposta_breakdown(consulta, resultado)
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
    app.run(debug=True, use_reloader=False)
