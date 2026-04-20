import pdfplumber
import re

_TAG_RE = re.compile(
    r'\s+(?:Rema|Remanejad\w*|Trans|Transf\w*|Nova|Nov|Ex|EX)\b',
    re.IGNORECASE,
)

_IGNORAR = {
    "NOME DO ALUNO", "HISTORIA", "ARTE", "MOV", "ANO LETIVO",
    "ESTADO DO", "SECRETARIA", "ENSINO", "SERIAÇÃO", "ATENDIMENTOS",
    "DONADUZZI", "TOLEDO", "CURSO", "TURMA", "TRIMESTRE", "BIMESTRE",
}


def extrair_total_faltas(caminho_pdf):
    """
    Extrai total de faltas por aluno da última página (Registro de Classe).
    Formato esperado por linha: NOME [TAG] NUMERO [NOTA] FALTAS
    Retorna: dict {nome: int}
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if not pdf.pages:
            return {}
        # Última página = Registro de Classe
        texto = pdf.pages[-1].extract_text() or ""

    total_faltas = {}

    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha or not linha[0].isupper():
            continue
        if any(x in linha.upper() for x in _IGNORAR):
            continue

        # Remove tag de movimentação (Rema, Trans, etc.)
        linha_limpa = _TAG_RE.sub('', linha)

        # Padrão: NOME(sem dígitos)  NUMERO  [NOTA]  FALTAS
        # [^\d]+ garante que o nome não inclui o número do aluno
        m = re.match(r'^([^\d]+?)\s+\d+(?:\s+[\d.,]+)?\s+(\d+)$', linha_limpa)
        if m:
            nome = m.group(1).strip()
            if len(nome) > 3:
                total_faltas[nome] = int(m.group(2))

    return total_faltas
