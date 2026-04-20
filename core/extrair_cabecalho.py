import pdfplumber
import re


def extrair_cabecalho(caminho_pdf):
    """
    Extrai informações do cabeçalho do PDF (página 1).
    Retorna dict com: escola, turma, disciplina, trimestre, serie, periodo
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if not pdf.pages:
            return {}
        texto = pdf.pages[0].extract_text() or ""

    linhas = [l.strip() for l in texto.split("\n") if l.strip()]

    info = {
        "escola": "",
        "turma": "",
        "disciplina": "",
        "trimestre": "",
        "serie": "",
        "periodo": "",
    }

    for linha in linhas:
        # ANO LETIVO: 2025-1 3º Trimestre
        m = re.search(r"(\d+[ºo°]\s*Trimestre|\d+[ºo°]\s*Bimestre)", linha, re.IGNORECASE)
        if m and not info["trimestre"]:
            info["trimestre"] = m.group(1).strip()

        # DONADUZZI, C - E F M P ESTADO DO PARANÁ  →  escola = "DONADUZZI"
        if not info["escola"] and re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]+[,\s]", linha):
            # Pega até a vírgula ou espaço seguido de mais texto
            escola = linha.split(",")[0].strip()
            if 3 < len(escola) < 40 and escola.isupper():
                info["escola"] = escola

        # SERIAÇÃO: 1ª Série / TURMA: B
        if "SERIAÇÃO:" in linha.upper():
            m = re.search(r"SERIAÇÃO:\s*(\d+[ªº°]?\s*\w+)", linha, re.IGNORECASE)
            if m:
                info["serie"] = m.group(1).strip()
        if "TURMA:" in linha.upper():
            m = re.search(r"TURMA:\s*(\S+)", linha, re.IGNORECASE)
            if m:
                info["turma"] = m.group(1).strip()

        # Manhã / Tarde / Noite
        if re.match(r"^(Manhã|Tarde|Noite)\b", linha, re.IGNORECASE) and not info["periodo"]:
            info["periodo"] = linha.split()[0]

    # Disciplina: linha isolada em maiúsculas após o período/turma
    for i, linha in enumerate(linhas):
        if re.match(r"^(Manhã|Tarde|Noite)\b", linha, re.IGNORECASE):
            if i + 1 < len(linhas):
                proxima = linhas[i + 1]
                if proxima.isupper() and len(proxima.split()) <= 4:
                    info["disciplina"] = proxima
            break

    return info
