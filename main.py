import os
from core.extrair_tabela_frequencia import extrair_tabela_frequencia
from core.extrair_total_faltas import extrair_total_faltas
from core.relatorio import gerar_relatorio

def main():
    # Pasta onde estão todos os PDFs
    pasta = r"C:\Users\heric\OneDrive\Desktop\leitordepdf - Copia\PDFsacademicos"

    
    # Lista todos os arquivos PDF
    pdfs = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("Nenhum PDF encontrado na pasta.")
        return

    # Percorre todos os PDFs
    for pdf in pdfs:
        caminho = os.path.join(pasta, pdf)
        print(f"\n📄 Lendo: {pdf}")

        # Extrai datas e presenças
        datas, alunos = extrair_tabela_frequencia(caminho)
        if not datas:
            print("ERRO: Tabela de frequência não encontrada.")
            continue

        # Extrai total de faltas
        total_faltas = extrair_total_faltas(caminho)

        # Gera relatório para este PDF
        gerar_relatorio(datas, alunos, total_faltas)

    print("\n✅ CONCLUÍDO!")

# Executa o main somente se o arquivo for rodado diretamente
if __name__ == "__main__":
    main()
