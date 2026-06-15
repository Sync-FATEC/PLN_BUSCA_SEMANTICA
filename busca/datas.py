import re
import unidecode

_MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}

# Ano atual segundo o banco, para datas sem ano ("7 de maio").
_ANO_ATUAL = "EXTRACT(YEAR FROM CURRENT_DATE)::int"


def _relativas(t):
    """Datas relativas ao momento atual. Devolve a condição ou None."""
    if "hoje" in t:
        return "data_imagem = CURRENT_DATE"
    if "ontem" in t:
        return "data_imagem = CURRENT_DATE - INTERVAL '1 day'"
    if "semana passada" in t:
        return ("data_imagem >= date_trunc('week', CURRENT_DATE) - INTERVAL '7 days' "
                "AND data_imagem < date_trunc('week', CURRENT_DATE)")
    if "essa semana" in t or "esta semana" in t or "desta semana" in t:
        return ("data_imagem >= date_trunc('week', CURRENT_DATE) "
                "AND data_imagem < date_trunc('week', CURRENT_DATE) + INTERVAL '7 days'")
    if "mes passado" in t:
        return ("data_imagem >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' "
                "AND data_imagem < date_trunc('month', CURRENT_DATE)")
    if "esse mes" in t or "este mes" in t or "deste mes" in t:
        return "date_trunc('month', data_imagem) = date_trunc('month', CURRENT_DATE)"
    if "ano passado" in t:
        return "EXTRACT(YEAR FROM data_imagem) = EXTRACT(YEAR FROM CURRENT_DATE) - 1"
    if "esse ano" in t or "este ano" in t or "deste ano" in t:
        return "EXTRACT(YEAR FROM data_imagem) = EXTRACT(YEAR FROM CURRENT_DATE)"
    return None


def _expr_data(trecho):
    """Extrai UMA data de um trecho e devolve a expressão make_date(...) ou None."""
    m = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", trecho)
    if m:
        dia, mes, ano = m.groups()
        ano_sql = ano if ano else _ANO_ATUAL
        return f"make_date({ano_sql}, {int(mes)}, {int(dia)})"

    m = re.search(r"\b(\d{1,2})\s+de\s+([a-z]+)(?:\s+de\s+(\d{4}))?\b", trecho)
    if m and m.group(2) in _MESES:
        dia, nome, ano = m.groups()
        ano_sql = ano if ano else _ANO_ATUAL
        return f"make_date({ano_sql}, {_MESES[nome]}, {int(dia)})"

    return None


def _intervalos(t):
    """Intervalos e comparadores: entre/antes de/depois de/a partir de."""
    # "entre 1 e 10 de maio" (dois dias, mesmo mês)
    m = re.search(r"entre\s+(\d{1,2})\s+e\s+(\d{1,2})\s+de\s+([a-z]+)(?:\s+de\s+(\d{4}))?", t)
    if m and m.group(3) in _MESES:
        d1, d2, nome, ano = m.groups()
        ano_sql = ano if ano else _ANO_ATUAL
        e1 = f"make_date({ano_sql}, {_MESES[nome]}, {int(d1)})"
        e2 = f"make_date({ano_sql}, {_MESES[nome]}, {int(d2)})"
        return f"data_imagem BETWEEN {e1} AND {e2}"

    # "entre <data> e <data>" (duas datas completas)
    m = re.search(r"entre\s+(.+?)\s+e\s+(.+)", t)
    if m:
        e1, e2 = _expr_data(m.group(1)), _expr_data(m.group(2))
        if e1 and e2:
            return f"data_imagem BETWEEN {e1} AND {e2}"

    # "a partir de <data>" (inclusive)
    m = re.search(r"a partir de\s+(.+)", t)
    if m:
        e = _expr_data(m.group(1))
        if e:
            return f"data_imagem >= {e}"

    # "depois de / apos <data>" (exclusivo)
    m = re.search(r"(?:depois de|apos)\s+(.+)", t)
    if m:
        e = _expr_data(m.group(1))
        if e:
            return f"data_imagem > {e}"

    # "antes de <data>" (exclusivo) / "ate <data>" (inclusive)
    m = re.search(r"antes de\s+(.+)", t)
    if m:
        e = _expr_data(m.group(1))
        if e:
            return f"data_imagem < {e}"
    m = re.search(r"\bate\s+(.+)", t)
    if m:
        e = _expr_data(m.group(1))
        if e:
            return f"data_imagem <= {e}"

    return None


def _data_completa(t):
    """Data exata com dia + mês (e ano opcional). Devolve a condição ou None."""
    expr = _expr_data(t)
    return f"data_imagem = {expr}" if expr else None


def _componentes(t):
    """Dia, mês e ano soltos. Combina o que encontrar. Devolve condição ou None."""
    condicoes = []

    # Dia: "dia 10"
    m = re.search(r"\bdia\s+(\d{1,2})\b", t)
    if m:
        condicoes.append(f"EXTRACT(DAY FROM data_imagem) = {int(m.group(1))}")

    # Mês por nome ("maio") ou por número ("mes 6")
    mes_num = None
    for nome, numero in _MESES.items():
        if re.search(rf"\b{nome}\b", t):
            mes_num = numero
            break
    if mes_num is None:
        m = re.search(r"\bmes\s+(\d{1,2})\b", t)
        if m and 1 <= int(m.group(1)) <= 12:
            mes_num = int(m.group(1))
    if mes_num:
        condicoes.append(f"EXTRACT(MONTH FROM data_imagem) = {mes_num}")

    # Ano: 4 dígitos ("2026")
    m = re.search(r"\b(19|20)\d{2}\b", t)
    if m:
        condicoes.append(f"EXTRACT(YEAR FROM data_imagem) = {m.group(0)}")

    if condicoes:
        return " AND ".join(condicoes)
    return None


def detectar_data(texto):
    t = unidecode.unidecode(texto.lower())
    # _intervalos vem antes de _data_completa: "antes de 10 de maio" contém
    # "10 de maio", que a data exata pegaria como igualdade.
    return _relativas(t) or _intervalos(t) or _data_completa(t) or _componentes(t)
