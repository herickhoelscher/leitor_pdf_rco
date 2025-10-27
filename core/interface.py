import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from .extrair_tabela_frequencia import extrair_tabela_frequencia
from .extrair_total_faltas import extrair_total_faltas
from .relatorio import gerar_relatorio



class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de Frequência")
        self.root.geometry("850x600")
        self.root.configure(bg="#e8ebf2")  # Fundo suave   

        # ✅ Caminho seguro para o arquivo .ico
        caminho_icone = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(caminho_icone):
            self.root.iconbitmap(caminho_icone)
        else:
            print("⚠️ Arquivo logo.ico não encontrado. Verifique a pasta.")

        self.pasta = ""
        self.txt_relatorio = ""

        # Título centralizado
        self.titulo = tk.Label(root, text="Leitor de Frequência",
                               font=("Helvetica", 18, "bold"), bg="#e8ebf2")
        self.titulo.pack(pady=(20, 10))

        # Botão principal (Processar PDFs)
        self.btn_processar = tk.Button(root, text="Processar PDFs",
                                       font=("Helvetica", 10, "bold"),
                                       bg="#2a4d69", fg="white", activebackground="#1b3550",
                                       width=25, height=2, bd=0, relief="raised",
                                       command=self.processar_pdfs)
        self.btn_processar.pack(pady=10)

        # Frame para botões secundários
        self.frame_botoes = tk.Frame(root, bg="#e8ebf2")
        self.frame_botoes.pack(pady=10)

        # Botões Escolher Pasta e Salvar
        btn_style = {"font": ("Helvetica", 12, "bold"), "bg": "#ffffff", "fg": "#2a4d69",
                     "width": 20, "height": 1, "bd": 1, "relief": "groove", "activebackground": "#dbe3ee"}
        self.btn_pasta = tk.Button(self.frame_botoes, text="Escolher Pasta de PDFs", command=self.escolher_pasta, **btn_style)
        self.btn_pasta.pack(side="left", padx=10)

        self.btn_salvar = tk.Button(self.frame_botoes, text="Salvar Relatório", command=self.salvar_relatorio, **btn_style)
        self.btn_salvar.pack(side="left", padx=10)

        # Área de texto
        self.textbox = scrolledtext.ScrolledText(root, width=95, height=25,
                                                 font=("Courier", 11),
                                                 bg="#ffffff", fg="#333333",
                                                 bd=2, relief="groove")
        self.textbox.pack(pady=20, padx=20)

    def escolher_pasta(self):
        self.pasta = filedialog.askdirectory()
        if self.pasta:
            messagebox.showinfo("Pasta selecionada", f"Pasta escolhida:\n{self.pasta}")

    def processar_pdfs(self):
        if not self.pasta:
            messagebox.showwarning("Atenção", "Escolha uma pasta antes de processar!")
            return

        self.textbox.delete("1.0", tk.END)
        self.txt_relatorio = ""

        pdfs = [f for f in os.listdir(self.pasta) if f.lower().endswith(".pdf")]
        if not pdfs:
            messagebox.showwarning("Aviso", "Nenhum PDF encontrado na pasta!")
            return

        for pdf in pdfs:
            caminho = os.path.join(self.pasta, pdf)
            self._adicionar_relatorio(f"\n📄 Lendo: {pdf}\n")

            datas1, alunos1, mensagem = extrair_tabela_frequencia(caminho)
            datas2, alunos2, mensagem2 = extrair_tabela_frequencia(caminho)

            if datas1 != datas2 or alunos1 != alunos2:
                self._adicionar_relatorio("⚠️ Inconsistência detectada entre leituras do PDF!\n")
                continue

            datas = datas1
            alunos = alunos1

            total_faltas = extrair_total_faltas(caminho)

            if mensagem:
                self._adicionar_relatorio(f"{mensagem}\n")
                
            if not datas:
                self._adicionar_relatorio("⚠️  Tabela de frequência não encontrada.\n")
                continue

            total_faltas = extrair_total_faltas(caminho)

            for nome, pres in alunos.items():
                faltas_dias = [datas[i] for i, p in enumerate(pres) if p == "F"]
                if faltas_dias:
                    calc = len(faltas_dias)
                    ofc = total_faltas.get(nome, "")
                    self._adicionar_relatorio(f"{nome}\n")
                    self._adicionar_relatorio(f"   Faltou: {', '.join(faltas_dias)}\n")
                    self._adicionar_relatorio(f"   Total: {calc} \n\n")

        messagebox.showinfo("Concluído", "Processamento finalizado! Agora você pode salvar o relatório.")

    def _adicionar_relatorio(self, texto):
        self.textbox.insert(tk.END, texto)
        self.txt_relatorio += texto

    def salvar_relatorio(self):
        if not self.txt_relatorio:
            messagebox.showwarning("Atenção", "Não há relatório para salvar! Primeiro processe os PDFs.")
            return

        arquivo_saida = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt")],
            title="Salvar relatório como"
        )

        if arquivo_saida:
            with open(arquivo_saida, "w", encoding="utf-8") as f:
                f.write(self.txt_relatorio)
            messagebox.showinfo("Salvo", f"Relatório salvo com sucesso em:\n{arquivo_saida}")

# Executa a GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
