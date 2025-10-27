import pdfplumber
import re

def extrair_tabela_frequencia(caminho_pdf):
    """
    Lê a tabela de frequência da página 1.
    Retorna:
        datas: lista de strings "16 set", "18 set", ...
        alunos: dict {nome: [C, F, C, ...]}
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if len(pdf.pages) < 1:
            return None, None

        pagina = pdf.pages[0]
        texto = pagina.extract_text()
        if not texto:
            return None, None

        linhas = [linha.strip() for linha in texto.split("\n") if linha.strip()]

        print("\n=== DEBUG: Linhas extraídas da página 1 ===")
        for i, linha in enumerate(linhas):
            print(f"{i+1:02}: {linha}")
        print("===========================================\n")

        # === ENCONTRA LINHAS DAS DATAS (dias e meses) ===
        linha_dias = None
        linha_meses = None
        for i, linha in enumerate(linhas):
            if re.match(r"^\d{2}(\s+\d{2}){3,}", linha):  # ex: 16 18 23 25 30 ...
                linha_dias = linha
            if re.match(r"^(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)(\s+\w{3})+", linha, re.IGNORECASE):
                linha_meses = linha
            if linha_dias and linha_meses:
                break

        if not (linha_dias and linha_meses):
            return None, None

        # === COMBINA DIAS E MESES ===
        dias = linha_dias.split()
        meses = linha_meses.split()
        datas = []
        for i in range(min(len(dias), len(meses))):
            datas.append(f"{dias[i]} {meses[i]}")

        if len(datas) < 5:
            return None, None

        # === EXTRAI ALUNOS E PRESENÇAS ===
        alunos = {}
        for linha in linhas:
            linha = linha.strip()

            # ignora cabeçalhos
            if any(x in linha.upper() for x in ["NOME DO ALUNO", "HISTORIA", "TURMA", "REGISTRO"]):
                continue

            # Exemplo: "ANNA CLARA WERNER DE MORAES 1 C C C C C..."
            match = re.match(r"(.+?)\s+\d+\s+([CF\s-]+)$", linha)
            if match:
                nome = match.group(1).strip()
                presencas_raw = match.group(2).replace(" ", "").replace("-", "")
                presencas = [c for c in presencas_raw if c in "CF"]
                alunos[nome] = presencas[:len(datas)]

        return datas, alunos
