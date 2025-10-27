# extrair_total_faltas.py
import pdfplumber
import re

def extrair_total_faltas(caminho_pdf):
    """
    Lê APENAS o total de faltas da página 4.
    Retorna: dict {nome: faltas}
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if len(pdf.pages) < 4:
            return {}
        texto = pdf.pages[3].extract_text()
        if not texto:
            return {}

        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        total_faltas = {}

        for linha in linhas:
            if re.search(r"\d+$", linha) and linha[0].isalpha():
                match = re.search(r"(.+?)\s+(\d+)$", linha)
                if match:
                    nome = match.group(1).strip()
                    try:
                        total_faltas[nome] = int(match.group(2))
                    except:
                        continue
        return total_faltas