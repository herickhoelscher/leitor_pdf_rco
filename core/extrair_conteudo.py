import pdfplumber


def extrair_conteudo(caminho_pdf):
    """
    Extrai a tabela de conteúdo/observações da página 3.
    Retorna lista de dicts:
        [{"data": "16/set", "tipo": "Conteúdo", "conteudo": "...", "responsavel": "..."}, ...]
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if len(pdf.pages) < 3:
            return []
        page = pdf.pages[2]
        tables = page.extract_tables()

    conteudos = []
    for table in tables:
        if not table or len(table[0]) < 4:
            continue
        # Verifica se é a tabela de conteúdo pelo cabeçalho
        header = [str(c).upper() for c in table[0] if c]
        if not any("CONTEÚDO" in h or "AULA" in h for h in header):
            continue

        for row in table[1:]:
            if not row or len(row) < 4:
                continue
            data = (row[0] or "").strip()
            tipo = (row[2] or "").strip()
            conteudo = (row[3] or "").replace("\n", " ").strip()
            responsavel = (row[4] or "").replace("\n", " ").strip() if len(row) > 4 else ""

            if not data or not conteudo:
                continue
            conteudos.append({
                "data": data,
                "tipo": tipo,
                "conteudo": conteudo,
                "responsavel": responsavel,
            })

    return conteudos
