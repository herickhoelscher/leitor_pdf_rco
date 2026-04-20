import csv

MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}

LIMITE_RISCO   = 0.75
LIMITE_ATENCAO = 0.80


def normalizar_data(data_str):
    """Converte '16 set' → '16/09'."""
    partes = data_str.strip().split()
    if len(partes) >= 2:
        dia = partes[0].zfill(2)
        mes = MESES.get(partes[1].lower())
        if mes:
            return f"{dia}/{mes:02d}"
    return data_str


def calcular_status(taxa):
    if taxa >= LIMITE_ATENCAO:
        return "Regular"
    if taxa >= LIMITE_RISCO:
        return "Em Risco"
    return "Reprovado"


def enriquecer_dados(dados_brutos):
    """
    Recebe a lista crua do interface.py e adiciona campos calculados:
      - data_fmt       : '16 set' → '16/09'
      - total_aulas    : total de aulas do aluno naquele PDF
      - taxa_presenca  : float 0.0–1.0
      - status         : 'Regular' / 'Em Risco' / 'Reprovado'

    Agrupa por (arquivo, aluno) para calcular totais corretos.
    """
    from collections import defaultdict

    # Conta total de aulas por (arquivo, aluno)
    # '-' = não matriculado naquela data → excluído do total e das presenças
    totais = defaultdict(lambda: {"total": 0, "presencas": 0})
    for d in dados_brutos:
        chave = (d.get("arquivo"), d.get("aluno"))
        marca = d.get("presenca", "")
        if marca in ("C", "F", "D"):
            totais[chave]["total"] += 1
        if marca == "C":
            totais[chave]["presencas"] += 1

    enriquecidos = []
    for d in dados_brutos:
        nd = dict(d)
        chave = (nd.get("arquivo"), nd.get("aluno"))
        total    = totais[chave]["total"]
        presencas = totais[chave]["presencas"]
        taxa     = presencas / total if total > 0 else 1.0

        nd["data_fmt"]    = normalizar_data(nd.get("data", ""))
        nd["total_aulas"] = total
        nd["taxa_presenca"] = taxa
        nd["status"]      = calcular_status(taxa)
        enriquecidos.append(nd)

    return enriquecidos


def exportar_csv_unificado(dados, caminho_saida):
    """
    Exporta CSV unificado (frequência + conteúdo + campos calculados).
    Separador ';' para abertura direta no Excel PT-BR.
    """
    if not dados:
        return

    dados_ricos = enriquecer_dados(dados)

    with open(caminho_saida, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Arquivo", "Escola", "Turma", "Disciplina", "Trimestre",
            "Série", "Período", "Aluno", "Data", "Data Formatada",
            "Presença", "Total Aulas", "Total Faltas (calc.)",
            "Taxa Presença (%)", "Status",
            "Tipo de Aula", "Conteúdo / Observações", "Responsável",
        ])
        for d in dados_ricos:
            taxa_pct = round(d["taxa_presenca"] * 100, 1)
            writer.writerow([
                d.get("arquivo", ""),
                d.get("escola", ""),
                d.get("turma", ""),
                d.get("disciplina", ""),
                d.get("trimestre", ""),
                d.get("serie", ""),
                d.get("periodo", ""),
                d.get("aluno", ""),
                d.get("data", ""),
                d.get("data_fmt", ""),
                d.get("presenca", ""),
                d.get("total_aulas", ""),
                d.get("total_faltas_calc", ""),
                str(taxa_pct).replace(".", ","),  # Excel PT-BR usa vírgula
                d.get("status", ""),
                d.get("tipo_aula", ""),
                d.get("conteudo_obs", ""),
                d.get("responsavel", ""),
            ])

    return dados_ricos  # retorna enriquecidos para reuso no xlsx
