import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk

from .extrair_tabela_frequencia import extrair_tabela_frequencia
from .extrair_total_faltas import extrair_total_faltas
from .extrair_conteudo import extrair_conteudo
from .extrair_cabecalho import extrair_cabecalho
from .exportar_csv import exportar_csv_unificado, enriquecer_dados
from .exportar_xlsx import exportar_xlsx

# ── Paleta ────────────────────────────────────────────────────────
BG        = "#f5f7fa"
CARD      = "#ffffff"
ACCENT    = "#2563eb"
ACCENT_HV = "#1d4ed8"
TEXT      = "#1e293b"
TEXT_DIM  = "#64748b"
BORDER    = "#e2e8f0"
SUCCESS   = "#16a34a"
DANGER    = "#dc2626"
TAG_F     = "#dc2626"
TAG_D     = "#d97706"
TAG_C     = "#16a34a"
TAG_HEAD  = "#2563eb"
TAG_RISK  = "#d97706"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor RCO")
        self.root.geometry("1020x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(800, 540)

        icone = os.path.join(os.path.dirname(__file__), "..", "assents", "logo.ico")
        if os.path.exists(icone):
            self.root.iconbitmap(icone)

        self._pdfs = []          # lista final de caminhos PDF a processar
        self.txt_relatorio = ""
        self._dados_brutos = []
        self._dados_ricos  = []

        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Barra superior ──────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=ACCENT, height=52)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.columnconfigure(1, weight=1)

        tk.Label(topbar, text="  RCO", font=("Segoe UI", 15, "bold"),
                 bg=ACCENT, fg="white").grid(row=0, column=0, sticky="w", padx=(16, 0), pady=12)
        tk.Label(topbar, text="Leitor de Registro de Classe Online",
                 font=("Segoe UI", 10), bg=ACCENT, fg="#bfdbfe").grid(
                 row=0, column=1, sticky="w", padx=8, pady=14)

        # Área central ────────────────────────────────────────────
        centro = tk.Frame(self.root, bg=BG)
        centro.grid(row=1, column=0, sticky="nsew", padx=20, pady=16)
        centro.columnconfigure(0, weight=1)
        centro.rowconfigure(1, weight=1)

        # Card de controles ───────────────────────────────────────
        card = tk.Frame(centro, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        card.columnconfigure(1, weight=1)

        # Linha 1 — seleção de origem
        tk.Label(card, text="PDFs selecionados", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT_DIM).grid(row=0, column=0, padx=(16, 8), pady=(14, 4), sticky="w")

        self.lbl_pasta = tk.Label(card, text="Nenhum arquivo selecionado",
                                  font=("Segoe UI", 9), bg=CARD, fg=TEXT_DIM,
                                  anchor="w", cursor="hand2")
        self.lbl_pasta.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(14, 4))

        sel_frame = tk.Frame(card, bg=CARD)
        sel_frame.grid(row=0, column=2, padx=(0, 16), pady=(12, 4))
        self._btn(sel_frame, "Escolher Pasta", self.escolher_pasta,
                  style="sec").pack(side="left", padx=(0, 4))
        self._btn(sel_frame, "Escolher Arquivos", self.escolher_arquivos,
                  style="sec").pack(side="left")

        # Separador
        tk.Frame(card, bg=BORDER, height=1).grid(row=1, column=0, columnspan=3, sticky="ew", padx=16)

        # Linha 2 — ações
        acoes = tk.Frame(card, bg=CARD)
        acoes.grid(row=2, column=0, columnspan=3, sticky="w", padx=16, pady=12)

        self._btn(acoes, "▶  Processar PDFs", self.processar_pdfs,
                  style="primary").pack(side="left", padx=(0, 10))

        tk.Frame(acoes, bg=BORDER, width=1, height=24).pack(side="left", padx=6)

        self._btn(acoes, "Exportar Excel (.xlsx)", self.salvar_xlsx,
                  style="xlsx").pack(side="left", padx=(0, 6))
        self._btn(acoes, "Exportar CSV", self.salvar_csv,
                  style="sec").pack(side="left", padx=(0, 6))
        self._btn(acoes, "Salvar .TXT", self.salvar_txt,
                  style="sec").pack(side="left")

        # Barra de progresso (oculta até processar)
        self._progresso_frame = tk.Frame(card, bg=CARD)
        self._progresso_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 10))

        self.lbl_progresso = tk.Label(self._progresso_frame, text="",
                                      font=("Segoe UI", 8), bg=CARD, fg=TEXT_DIM)
        self.lbl_progresso.pack(side="top", anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Azul.Horizontal.TProgressbar",
                        troughcolor=BORDER, background=ACCENT,
                        thickness=6, borderwidth=0)

        self.progressbar = ttk.Progressbar(self._progresso_frame, length=400,
                                           style="Azul.Horizontal.TProgressbar")
        self._progresso_frame.grid_remove()

        # Área de saída ───────────────────────────────────────────
        frame_text = tk.Frame(centro, bg=CARD,
                              highlightbackground=BORDER, highlightthickness=1)
        frame_text.grid(row=1, column=0, sticky="nsew")
        frame_text.columnconfigure(0, weight=1)
        frame_text.rowconfigure(0, weight=1)

        self.textbox = scrolledtext.ScrolledText(
            frame_text,
            font=("Consolas", 10),
            bg=CARD, fg=TEXT,
            insertbackground=TEXT,
            bd=0, relief="flat",
            padx=14, pady=12,
            selectbackground="#bfdbfe",
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.tag_config("head",    foreground=TAG_HEAD, font=("Consolas", 10, "bold"))
        self.textbox.tag_config("subhead", foreground=TEXT_DIM, font=("Consolas", 9, "italic"))
        self.textbox.tag_config("falta",   foreground=TAG_F, font=("Consolas", 10, "bold"))
        self.textbox.tag_config("disp",    foreground=TAG_D)
        self.textbox.tag_config("ok",      foreground=TAG_C)
        self.textbox.tag_config("dim",     foreground=TEXT_DIM)
        self.textbox.tag_config("label",   foreground=TEXT_DIM)
        self.textbox.tag_config("risco",   foreground=TAG_RISK, font=("Consolas", 10, "bold"))
        self.textbox.tag_config("resumo",  foreground=TEXT,     font=("Consolas", 9))

        # Barra de status ─────────────────────────────────────────
        statusbar = tk.Frame(self.root, bg=BORDER, height=26)
        statusbar.grid(row=2, column=0, sticky="ew")
        statusbar.grid_propagate(False)

        self.lbl_status = tk.Label(statusbar, text="Pronto",
                                   font=("Segoe UI", 8), bg=BORDER, fg=TEXT_DIM, anchor="w")
        self.lbl_status.pack(side="left", padx=12)

        tk.Label(statusbar, text="C = Presença   F = Falta   D = Dispensado  |  "
                                 "Regular ≥80%   Em Risco ≥75%   Reprovado <75%",
                 font=("Segoe UI", 8), bg=BORDER, fg=TEXT_DIM).pack(side="right", padx=12)

    def _btn(self, parent, text, cmd, style="sec"):
        cores = {
            "primary": dict(bg=ACCENT,    fg="white",  activebackground=ACCENT_HV, activeforeground="white",
                            font=("Segoe UI", 9, "bold"), padx=14, pady=6),
            "xlsx":    dict(bg="#16a34a", fg="white",  activebackground="#15803d", activeforeground="white",
                            font=("Segoe UI", 9, "bold"), padx=12, pady=6),
            "sec":     dict(bg=CARD,      fg=TEXT,     activebackground="#f1f5f9", activeforeground=ACCENT,
                            font=("Segoe UI", 9), padx=12, pady=6,
                            highlightbackground=BORDER, highlightthickness=1),
        }
        cfg = cores.get(style, cores["sec"])
        return tk.Button(parent, text=text, command=cmd,
                         relief="flat", bd=0, cursor="hand2", **cfg)

    # ── Ações ──────────────────────────────────────────────────────
    def escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecionar pasta com PDFs do RCO")
        if pasta:
            pdfs = sorted(
                os.path.join(pasta, f)
                for f in os.listdir(pasta)
                if f.lower().endswith(".pdf")
            )
            self._pdfs = pdfs
            nome = os.path.basename(pasta) or pasta
            n = len(pdfs)
            self.lbl_pasta.config(text=f"{nome}  ({n} PDF{'s' if n != 1 else ''})", fg=ACCENT)
            self._status(f"Pasta: {pasta}  —  {n} PDF(s) encontrado(s)")

    def escolher_arquivos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecionar PDFs do RCO",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if arquivos:
            self._pdfs = sorted(arquivos)
            n = len(self._pdfs)
            if n == 1:
                nome = os.path.basename(self._pdfs[0])
            else:
                pasta = os.path.dirname(self._pdfs[0])
                nome = f"{os.path.basename(pasta)}/  ({n} arquivos)"
            self.lbl_pasta.config(text=nome, fg=ACCENT)
            self._status(f"{n} arquivo(s) selecionado(s)")

    def processar_pdfs(self):
        if not self._pdfs:
            messagebox.showwarning("Atenção", "Selecione uma pasta ou arquivos primeiro.")
            return

        pdfs = self._pdfs  # lista de caminhos completos

        self.textbox.delete("1.0", tk.END)
        self.txt_relatorio = ""
        self._dados_brutos = []
        self._dados_ricos  = []

        # Mostra barra de progresso
        self._progresso_frame.grid()
        self.progressbar.pack(side="top", fill="x", pady=(4, 0))
        self.progressbar["maximum"] = len(pdfs)
        self.progressbar["value"]   = 0
        self.root.update_idletasks()

        alunos_risco = []

        pdfs_sem_dados = []

        for idx, caminho in enumerate(pdfs, 1):
            pdf = os.path.basename(caminho)
            self.lbl_progresso.config(text=f"Lendo {idx}/{len(pdfs)}: {pdf}")
            self.root.update_idletasks()

            try:
                cabec        = extrair_cabecalho(caminho)
                datas, alunos, mensagem = extrair_tabela_frequencia(caminho)
                total_faltas = extrair_total_faltas(caminho)
                conteudos    = extrair_conteudo(caminho)
            except Exception as e:
                self._log(f"\n◆  {pdf}\n", "head")
                self._log(f"   ✖  Erro ao ler: {e}\n\n", "falta")
                self.progressbar["value"] = idx
                self.root.update_idletasks()
                continue

            cont_por_data = {c["data"].replace("/", " "): c for c in conteudos}

            # Cabeçalho do PDF
            info = "  ".join(filter(None, [
                cabec.get("disciplina"),
                cabec.get("turma") and f"Turma {cabec['turma']}",
                cabec.get("serie"),
                cabec.get("trimestre"),
            ]))
            self._log(f"\n◆  {pdf}\n", "head")
            if info:
                self._log(f"   {info}\n", "subhead")

            if not datas:
                self._log("   ⚠  Tabela de frequência não encontrada.\n", "dim")
                pdfs_sem_dados.append(pdf)
                self.progressbar["value"] = idx
                self.root.update_idletasks()
                continue

            from .exportar_csv import calcular_status

            for nome_aluno, pres in alunos.items():
                faltas_dias = [datas[i] for i, p in enumerate(pres) if p == "F"]
                disp_dias   = [datas[i] for i, p in enumerate(pres) if p == "D"]
                total_calc  = len(faltas_dias)
                total_ofc   = total_faltas.get(nome_aluno, "")
                # '-' = não matriculado naquela data → não conta no total
                aulas_validas = len([p for p in pres if p in ("C", "F", "D")])
                presencas     = len([p for p in pres if p == "C"])
                taxa          = presencas / aulas_validas if aulas_validas > 0 else 1.0
                st            = calcular_status(taxa)
                taxa_str      = f"{taxa * 100:.1f}%"

                if faltas_dias or disp_dias:
                    tag_nome = "risco" if taxa < 0.80 else "falta"
                    self._log(f"   {nome_aluno}\n", tag_nome)
                    if faltas_dias:
                        self._log(f"      Faltou:     {', '.join(faltas_dias)}\n", "label")
                    if disp_dias:
                        self._log(f"      Dispensado: {', '.join(disp_dias)}\n", "disp")
                    ofc_str = f"  (oficial: {total_ofc})" if total_ofc != "" else ""
                    tag_st  = "ok" if st == "Regular" else ("risco" if st == "Em Risco" else "falta")
                    self._log(f"      Faltas: {total_calc}{ofc_str}  |  Presença: {taxa_str}  |  {st}\n\n", tag_st)
                    if st in ("Em Risco", "Reprovado"):
                        alunos_risco.append((nome_aluno, cabec.get("turma",""), cabec.get("disciplina",""), st, taxa_str))
                else:
                    # Aluno sem faltas — aparece no relatório e no CSV normalmente
                    self._log(f"   {nome_aluno}\n", "ok")
                    self._log(f"      Presença: {taxa_str}  |  {st}\n", "dim")

                for i, data in enumerate(datas):
                    cont = cont_por_data.get(data, {})
                    self._dados_brutos.append({
                        "arquivo":           pdf,
                        "escola":            cabec.get("escola", ""),
                        "turma":             cabec.get("turma", ""),
                        "disciplina":        cabec.get("disciplina", ""),
                        "trimestre":         cabec.get("trimestre", ""),
                        "serie":             cabec.get("serie", ""),
                        "periodo":           cabec.get("periodo", ""),
                        "aluno":             nome_aluno,
                        "data":              data,
                        "presenca":          pres[i] if i < len(pres) else "",
                        "tipo_aula":         cont.get("tipo", ""),
                        "conteudo_obs":      cont.get("conteudo", ""),
                        "responsavel":       cont.get("responsavel", ""),
                        "total_faltas_calc": total_calc,
                        "total_faltas_oficial": total_ofc,
                    })

            self.progressbar["value"] = idx
            self.root.update_idletasks()

        # Enriquece dados (campos calculados)
        self._dados_ricos = enriquecer_dados(self._dados_brutos)

        # Resumo de atenção
        self._log("\n" + "─" * 60 + "\n", "dim")
        if alunos_risco:
            self._log("  ⚠  Alunos que precisam de atenção:\n", "risco")
            for nome, turma, disc, st, taxa in alunos_risco:
                self._log(f"     • {nome}  [{turma} / {disc}]  — {st} ({taxa})\n", "risco")
        else:
            self._log("  ✔  Nenhum aluno em situação de risco.\n", "ok")
        self._log("\n  Processamento concluído.\n", "dim")

        self._progresso_frame.grid_remove()
        n_reg = len(self._dados_ricos)
        self._status(f"{len(pdfs)} PDF(s)  —  {n_reg} registros  —  {len(alunos_risco)} em atenção")

        if n_reg == 0:
            detalhe = ""
            if pdfs_sem_dados:
                detalhe = (f"\n\n{len(pdfs_sem_dados)} PDF(s) sem dados extraídos:\n"
                           + "\n".join(f"  • {p}" for p in pdfs_sem_dados[:5]))
            messagebox.showwarning("Nenhum dado extraído",
                f"O processamento terminou mas nenhum dado foi encontrado.\n"
                f"Verifique se os PDFs são do formato RCO correto.{detalhe}")
        else:
            messagebox.showinfo("Concluído",
                f"Processamento finalizado!\n\n"
                f"PDFs: {len(pdfs)}   Registros: {n_reg}\n"
                f"Alunos em atenção: {len(alunos_risco)}\n\n"
                f"Use 'Exportar Excel' para gerar o arquivo completo.")

    def _log(self, texto, tag=None):
        self.textbox.insert(tk.END, texto, tag or "")
        self.txt_relatorio += texto
        self.textbox.see(tk.END)

    def _status(self, msg):
        self.lbl_status.config(text=msg)
        self.root.update_idletasks()

    # ── Exportações ────────────────────────────────────────────────
    def _verificar_dados(self):
        if not self._dados_brutos:
            messagebox.showwarning("Atenção", "Processe os PDFs primeiro.")
            return False
        return True

    def salvar_xlsx(self):
        if not self._verificar_dados():
            return
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Exportar Excel",
            initialfile="relatorio_rco.xlsx",
        )
        if arquivo:
            dados = self._dados_ricos or enriquecer_dados(self._dados_brutos)
            exportar_xlsx(dados, arquivo)
            self._status(f"Excel salvo: {arquivo}")
            messagebox.showinfo("Exportado",
                f"Excel salvo em:\n{arquivo}\n\n"
                f"Contém 3 abas:\n"
                f"  • Frequência Detalhada\n"
                f"  • Resumo por Aluno\n"
                f"  • Conteúdos")

    def salvar_csv(self):
        if not self._verificar_dados():
            return
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Exportar CSV",
            initialfile="relatorio_rco.csv",
        )
        if arquivo:
            exportar_csv_unificado(self._dados_brutos, arquivo)
            self._status(f"CSV salvo: {arquivo}")
            messagebox.showinfo("Exportado", f"CSV salvo em:\n{arquivo}\n\nAbrir no Excel com separador ';'")

    def salvar_txt(self):
        if not self.txt_relatorio.strip():
            messagebox.showwarning("Atenção", "Processe os PDFs primeiro.")
            return
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            title="Salvar relatório",
        )
        if arquivo:
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(self.txt_relatorio)
            self._status(f"TXT salvo: {arquivo}")
            messagebox.showinfo("Salvo", f"Relatório salvo em:\n{arquivo}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
