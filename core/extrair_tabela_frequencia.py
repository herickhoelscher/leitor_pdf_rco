import pdfplumber
import re

MESES_PAT = r'(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)'
MESES_NUM = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12,
}

_TAG_RE = re.compile(
    r'\s+(?:Rema|Remanejad\w*|Trans|Transf\w*|Nova|Nov|Ex|EX)\b',
    re.IGNORECASE,
)


def _normalizar_datas(texto):
    """'10fev' → '10 fev', '03mar' → '03 mar'."""
    return re.sub(
        r'(\d{1,2})(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)',
        r'\1 \2', texto, flags=re.IGNORECASE,
    )


def _extrair_datas(linhas):
    """
    Tenta encontrar as datas por dois métodos:
    1) Linha com pares dia+mês: '10 fev 24 fev 03 mar ...'
    2) Duas linhas separadas: '10 24 03 ...' e 'fev fev mar ...'
    Retorna lista de strings como '10 fev', '03 mar', etc.
    """
    # Método 1 — datas combinadas numa linha (formato atual)
    for linha in linhas:
        encontradas = re.findall(
            r'\b(\d{1,2})\s+(' + MESES_PAT + r')\b',
            linha, re.IGNORECASE,
        )
        if len(encontradas) >= 3:
            return [f"{d} {m.lower()}" for d, m in encontradas]

    # Método 2 — dias e meses em linhas separadas (formato antigo)
    linha_dias = None
    linha_meses = None
    for linha in linhas:
        if re.match(r'^\d{2}(\s+\d{2}){3,}', linha):
            linha_dias = linha
        if re.match(r'^(' + MESES_PAT + r')(\s+\w{3})+', linha, re.IGNORECASE):
            linha_meses = linha
        if linha_dias and linha_meses:
            break

    if linha_dias and linha_meses:
        dias = linha_dias.split()
        meses = linha_meses.split()
        datas = [f"{dias[i]} {meses[i].lower()}"
                 for i in range(min(len(dias), len(meses)))]
        if len(datas) >= 3:
            return datas

    return []


def extrair_tabela_frequencia(caminho_pdf):
    """
    Lê a tabela de frequência da página 1.
    Retorna:
        datas:    lista de strings ['10 fev', '24 fev', '03 mar', ...]
        alunos:   dict {nome: ['C', 'F', 'D', '-', ...]}
        mensagem: string ou None
    """
    with pdfplumber.open(caminho_pdf) as pdf:
        if not pdf.pages:
            return [], {}, None
        texto = pdf.pages[0].extract_text() or ""

    # Normaliza '10fev' → '10 fev'
    texto = _normalizar_datas(texto)
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]

    datas = _extrair_datas(linhas)
    if not datas:
        return [], {}, None

    # ── Extrai alunos ─────────────────────────────────────────────
    ignorar = {
        "NOME DO ALUNO", "HISTORIA", "TURMA", "REGISTRO", "ARTE",
        "MATEMATICA", "PORTUGUÊS", "CIENCIAS", "GEOGRAFIA", "FISICA",
        "QUIMICA", "BIOLOGIA", "EDUCAÇÃO", "FILOSOFIA", "SOCIOLOGIA",
        "INGLES", "ESPANHOL", "PRODUCAO", "SECRETARIA", "DONADUZZI",
        "SERIAÇÃO", "ANO LETIVO", "ESTADO DO", "CURSO FUND",
    }

    alunos = {}
    for linha in linhas:
        if any(x in linha.upper() for x in ignorar):
            continue
        if re.match(
            r'^(Manhã|Tarde|Noite|quarta|segunda|terça|quinta|sexta|sábado)\b',
            linha, re.IGNORECASE,
        ):
            continue

        linha_limpa = _TAG_RE.sub('', linha)

        m = re.match(r'^(.+?)\s+(\d+)\s+((?:[CFD\-]\s*)+)$', linha_limpa.strip())
        if not m:
            continue

        nome = m.group(1).strip()
        if len(nome) < 5 or not re.search(r'[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}', nome):
            continue

        tokens = re.findall(r'[CFD\-]', m.group(3))
        if tokens:
            alunos[nome] = tokens[:len(datas)]

    if not alunos:
        return datas, {}, "Nenhum aluno encontrado"

    mensagem = None
    if all(all(p == "C" for p in pres) for pres in alunos.values()):
        mensagem = "Nenhum aluno faltou"

    return datas, alunos, mensagem
