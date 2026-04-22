# Leitor RCO

Aplicação desktop para leitura e análise automática dos PDFs do **Registro de Classe Online (RCO)** do Estado do Paraná.

Extrai frequência, conteúdos e observações de múltiplos PDFs e exporta tudo em **Excel (.xlsx)** pronto para uso no Power BI ou diretamente no controle de qualidade escolar.

## Funcionalidades

- Selecionar uma pasta inteira de PDFs ou arquivos individuais
- Extrai de cada PDF:
  - Tabela de frequência completa (Presença / Falta / Dispensa)
  - Conteúdo das aulas e observações
  - Cabeçalho: escola, turma, disciplina, série, trimestre, período
  - Total oficial de faltas (última página)
- Calcula automaticamente taxa de presença e classifica o aluno:
  - **Regular** (presença >= 80%)
  - **Em Risco** (presença entre 75% e 79%)
  - **Reprovado** (presença < 75%, mínimo legal)
- Exibe relatório na tela com destaque visual por situação
- Lista alunos em atenção ao final do processamento
- Exporta para **Excel (.xlsx)** com 3 abas:
  - *Frequência Detalhada* (uma linha por aluno por aula, ideal para Power BI)
  - *Resumo por Aluno* (totais consolidados por turma/disciplina)
  - *Conteúdos* (registro de aulas e observações)
- Exporta para **CSV** (separador `;`, encoding UTF-8 BOM, abre direto no Excel PT-BR)
- Salva relatório textual em **.TXT**

## Estrutura do projeto

```
leitor_pdf_rco/
├── run.py                            # Entrada da aplicação
├── core/
│   ├── interface.py                  # Interface gráfica (Tkinter)
│   ├── extrair_tabela_frequencia.py  # Extração da frequência (página 1)
│   ├── extrair_total_faltas.py       # Extração do total de faltas (última página)
│   ├── extrair_conteudo.py           # Extração dos conteúdos (página 3)
│   ├── extrair_cabecalho.py          # Extração do cabeçalho do PDF
│   ├── exportar_csv.py               # Exportação CSV + campos calculados
│   ├── exportar_xlsx.py              # Exportação Excel com 3 abas
│   └── __init__.py
├── assets/
│   ├── logo.ico
│   └── logo.png
├── pdfs_rco/                         # Pasta padrão para os PDFs (não versionada)
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.10+

```bash
pip install pdfplumber openpyxl
```

## Como usar

```bash
python run.py
```

1. Clique em **Escolher Pasta** para selecionar uma pasta com PDFs do RCO ou **Escolher Arquivos** para selecionar arquivos individuais
2. Clique em **Processar PDFs**
3. Aguarde o processamento (barra de progresso)
4. Use **Exportar Excel (.xlsx)** para gerar o arquivo completo ou **Exportar CSV** para usar diretamente no Power BI

## Colunas do CSV / Excel

| Coluna | Descrição |
|---|---|
| Arquivo | Nome do PDF de origem |
| Escola | Nome da instituição |
| Turma | Identificador da turma |
| Disciplina | Nome da disciplina |
| Trimestre | Período letivo |
| Série | Série/ano do aluno |
| Período | Manhã / Tarde / Noite |
| Aluno | Nome completo |
| Data | Data da aula (ex: `16 set`) |
| Data Formatada | Data no formato `DD/MM` |
| Presença | C = Presença, F = Falta, D = Dispensado, `-` = Não matriculado |
| Total Aulas | Total de aulas no período |
| Total Faltas (calc.) | Faltas contadas pelo sistema |
| Taxa Presença (%) | Percentual de presença |
| Status | Regular / Em Risco / Reprovado |
| Tipo de Aula | Conteúdo / Nivelamento / Aula Extracurricular etc. |
| Conteúdo / Observações | Descrição do conteúdo e observações da aula |
| Responsável | Professor responsável |

## Observações sobre o formato dos PDFs

O sistema suporta os dois formatos de data que o RCO gera:

- Formato combinado: `10fev`, `24fev`, `03mar`
- Formato separado: linha de dias + linha de meses

Alunos com marcação `-` (matriculados após o início do período) têm essas datas excluídas do cálculo de presença para não distorcer a taxa.

## Licença

MIT
