def validar_pdf_resultado(datas, alunos):
    """
    Valida o resultado de extrair_tabela_frequencia para um único PDF.
    Retorna True se tudo estiver consistente, False caso contrário.
    """
    if not datas or not alunos:
        return False  # dados ausentes

    for nome, pres in alunos.items():
        # Cada aluno deve ter o mesmo número de registros que o número de datas
        if len(pres) != len(datas):
            return False
        
        # Cada registro deve ser 'C' ou 'F'
        if any(p not in ('C', 'F') for p in pres):
            return False

    return True
