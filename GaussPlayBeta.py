import customtkinter as ctk
from fractions import Fraction
import random
import re
import copy

# Configurações globais de tema
ctk.set_appearance_mode("light")


# --- Lógica Matemática ---
class SistemaLinear:
    def __init__(self, linhas, colunas, matriz_manual=None):
        self.linhas = linhas
        self.colunas = colunas
        self.matriz = []
        if matriz_manual:
            self.matriz = matriz_manual
        else:
            self.gerar_sistema_aleatorio()

    def trocar_linhas(self, idx1, idx2):
        self.matriz[idx1], self.matriz[idx2] = self.matriz[idx2], self.matriz[idx1]

    def gerar_sistema_aleatorio(self):
        self.matriz = []
        for i in range(self.linhas):
            linha = [Fraction(random.randint(-9, 9)) for _ in range(self.colunas + 1)]
            self.matriz.append(linha)

    def aplicar_operacao(self, alvo_idx, aux_idx, fator, eh_multiplicacao=False):
        if eh_multiplicacao:
            for j in range(len(self.matriz[alvo_idx])):
                self.matriz[alvo_idx][j] *= fator
        else:
            for j in range(len(self.matriz[alvo_idx])):
                self.matriz[alvo_idx][j] += fator * self.matriz[aux_idx][j]


# --- Janela de Configuração ---
class JanelaConfiguracao(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("⚙️ Configurar Novo Desafio")
        self.geometry("650x720")
        self.configure(fg_color="#f0f2f5")
        self.callback = callback
        self.entradas = []
        self.setup_ui()
        self.attributes("-topmost", True)

    def setup_ui(self):
        ctk.CTkLabel(self, text="Configuração do Sistema", font=("Segoe UI", 24, "bold"), text_color="#1f538d").pack(
            pady=20)

        f_dim = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="#d1d9e6")
        f_dim.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(f_dim, text="Linhas:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=20, pady=15)
        self.s_lin = ctk.CTkSegmentedButton(f_dim, values=["2", "3", "4", "5"], command=self.atualizar_grade_dinamica,
                                            fg_color="#e0e5ec", selected_color="#1f538d", corner_radius=10)
        self.s_lin.set("3")
        self.s_lin.grid(row=0, column=1, pady=15)

        ctk.CTkLabel(f_dim, text="Colunas:", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=20, pady=15)
        self.s_col = ctk.CTkSegmentedButton(f_dim, values=["2", "3", "4", "5"], command=self.atualizar_grade_dinamica,
                                            fg_color="#e0e5ec", selected_color="#1f538d", corner_radius=10)
        self.s_col.set("3")
        self.s_col.grid(row=1, column=1, pady=15)

        ctk.CTkButton(self, text="🎲 GERAR ALEATÓRIO", fg_color="#2ecc71", hover_color="#27ae60",
                      height=45, font=("Segoe UI", 15, "bold"), corner_radius=12, border_width=2,
                      border_color="#219150",
                      command=self.gerar_auto).pack(pady=15)

        self.frame_manual = ctk.CTkScrollableFrame(self, width=580, height=300, fg_color="white", corner_radius=15,
                                                   border_width=2, border_color="#d1d9e6")
        self.frame_manual.pack(pady=10, padx=20)

        self.btn_confirmar = ctk.CTkButton(self, text="✅ COMEÇAR JOGO MANUAL", fg_color="#3498db",
                                           hover_color="#2980b9",
                                           height=50, font=("Segoe UI", 16, "bold"), corner_radius=12, border_width=2,
                                           border_color="#1c638d",
                                           command=self.conf_manual)
        self.btn_confirmar.pack(pady=20)
        self.atualizar_grade_dinamica()

    def atualizar_grade_dinamica(self, _=None):
        for w in self.frame_manual.winfo_children(): w.destroy()

        l, c = int(self.s_lin.get()), int(self.s_col.get())
        self.entradas = []

        for i in range(l):
            lin_pts = []
            for j in range(c + 1):
                e = ctk.CTkEntry(self.frame_manual, width=65, height=40, font=("Consolas", 15),
                                 justify="center", corner_radius=8, border_color="#d1d9e6")
                col_pos = j + (1 if j == c else 0)
                e.grid(row=i, column=col_pos, padx=5, pady=8)
                lin_pts.append(e)
                if j == c - 1:
                    ctk.CTkLabel(self.frame_manual, text="┃", font=("Arial", 22, "bold"), text_color="#34495e").grid(
                        row=i, column=j + 1)
            self.entradas.append(lin_pts)

    def gerar_auto(self):
        l, c = int(self.s_lin.get()), int(self.s_col.get())
        sys = SistemaLinear(l, c)
        self.callback(l, c, sys.matriz)
        self.destroy()

    def conf_manual(self):
        try:
            l, c = int(self.s_lin.get()), int(self.s_col.get())
            matriz = [[Fraction(self.entradas[i][j].get() or 0) for j in range(c + 1)] for i in range(l)]
            self.callback(l, c, matriz)
            self.destroy()
        except:
            self.btn_confirmar.configure(fg_color="#e74c3c", text="❌ ERRO NOS VALORES")
            self.after(1000, lambda: self.btn_confirmar.configure(fg_color="#3498db", text="✅ COMEÇAR JOGO MANUAL"))


# --- Interface Principal ---
class JogoEscalonamento(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mestre do Escalonamento 3.0")
        self.geometry("1000x950")
        self.configure(fg_color="#f0f2f5")

        self.n_lin, self.n_col = 3, 3
        self.sistema = SistemaLinear(self.n_lin, self.n_col)
        self.comando_atual = []
        self.historico_undo = []
        self.historico_redo = []

        self.setup_ui()
        self.bind_keys()

    def bind_keys(self):
        self.bind("<Key>", self.processar_teclado)
        self.bind("<Return>", lambda e: self.executar())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.limpar())

    def processar_teclado(self, event):
        char, key = event.char, event.keysym
        if char.upper() in ["L", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "*", "/", "(", ")"]:
            self.add(char.upper())
        elif char == "\\":
            self.add("→")
        elif char == "=":
            self.add("↔")
        elif key == "Delete":
            self.backspace()

    def setup_ui(self):
        # Top Bar
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20)

        btn_style = {"font": ("Segoe UI", 13, "bold"), "corner_radius": 10, "height": 40, "border_width": 3}

        ctk.CTkButton(self.frame_top, text="➕ NOVO SISTEMA", fg_color="#1f538d", border_color="#163e6a",
                      command=lambda: JanelaConfiguracao(self, self.iniciar), **btn_style).pack(side="left", padx=8)

        # Cores alteradas para Vermelho (Desfazer) e Verde (Refazer) com bordas 3D
        ctk.CTkButton(self.frame_top, text="⟲ DESFAZER", fg_color="#e74c3c", border_color="#c0392b",
                      command=self.desfazer, **btn_style).pack(side="left", padx=8)

        ctk.CTkButton(self.frame_top, text="⟳ REFAZER", fg_color="#2ecc71", border_color="#27ae60",
                      command=self.refazer, **btn_style).pack(side="left", padx=8)

        # Matriz
        self.f_matriz_container = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=1,
                                               border_color="#d1d9e6")
        self.f_matriz_container.pack(pady=10, padx=40, fill="both")

        ctk.CTkLabel(self.f_matriz_container, text="SISTEMA ATUAL", font=("Segoe UI", 18, "bold"),
                     text_color="#2c3e50").pack(pady=10)

        self.f_matriz = ctk.CTkFrame(self.f_matriz_container, fg_color="transparent")
        self.f_matriz.pack(pady=20)
        self.render_matriz()

        # Visor Neon
        self.lbl_op = ctk.CTkLabel(self, text="Operação: ", font=("Consolas", 24, "bold"), fg_color="#1a1a1a",
                                   text_color="#00ff41", height=70, corner_radius=15)
        self.lbl_op.pack(pady=15, fill="x", padx=60)

        # Teclado
        self.f_ctrls = ctk.CTkFrame(self, fg_color="#e0e5ec", corner_radius=20, border_width=1, border_color="#d1d9e6")
        self.f_ctrls.pack(pady=10, padx=60, fill="both")
        self.render_teclado()

        # Footer
        f_btns = ctk.CTkFrame(self, fg_color="transparent")
        f_btns.pack(pady=25)
        ctk.CTkButton(f_btns, text="EXECUTAR", fg_color="#2ecc71", border_color="#27ae60", hover_color="#27ae60",
                      width=220, height=55, font=("Segoe UI", 18, "bold"), corner_radius=15, border_width=3,
                      command=self.executar).pack(side="left", padx=15)

        ctk.CTkButton(f_btns, text="LIMPAR", fg_color="#e74c3c", border_color="#c0392b", hover_color="#c0392b",
                      width=220, height=55, font=("Segoe UI", 18, "bold"), corner_radius=15, border_width=3,
                      command=self.limpar).pack(side="left", padx=15)

    def render_matriz(self):
        for w in self.f_matriz.winfo_children(): w.destroy()
        for i, linha in enumerate(self.sistema.matriz):
            for j, val in enumerate(linha):
                # Definição de cores e bordas para efeito 3D
                if j == self.n_col:
                    cor, t_cor, b_cor = "#d4edda", "#155724", "#b1cbb6" # Verde
                elif val == 1:
                    cor, t_cor, b_cor = "#339af0", "white", "#2980b9"   # Azul
                elif val == 0:
                    cor, t_cor, b_cor = "#ffec99", "#856404", "#e6d58a" # Amarelo
                else:
                    cor, t_cor, b_cor = "#e9ecef", "#495057", "#bdc3c7" # Cinza

                # Criamos um frame para simular a borda 3D
                borda_3d = ctk.CTkFrame(self.f_matriz,
                                        fg_color=b_cor,
                                        corner_radius=8,
                                        width=95, height=55)
                borda_3d.grid(row=i, column=j + (1 if j == self.n_col else 0), padx=6, pady=6)
                borda_3d.grid_propagate(False) # Mantém o tamanho fixo

                # O Label vai dentro do frame, com uma pequena margem (border_width manual)
                lbl = ctk.CTkLabel(borda_3d,
                                   text=str(val),
                                   fg_color=cor,
                                   text_color=t_cor,
                                   corner_radius=6,
                                   font=("Verdana", 17, "bold"),
                                   width=89, height=49) # Um pouco menor que o frame
                lbl.place(relx=0.5, rely=0.5, anchor="center")

                if j == self.n_col - 1:
                    ctk.CTkLabel(self.f_matriz, text="┃", font=("Arial", 28),
                                 text_color="#34495e").grid(row=i, column=j + 1, padx=15)
    def render_teclado(self):
        for w in self.f_ctrls.winfo_children(): w.destroy()
        btn_3d = {"width": 65, "height": 50, "font": ("Segoe UI", 19, "bold"), "corner_radius": 12, "border_width": 3}

        f1 = ctk.CTkFrame(self.f_ctrls, fg_color="transparent");
        f1.pack(pady=10)
        for i in range(self.n_lin):
            ctk.CTkButton(f1, text=f"L{i + 1}", fg_color="#ffffff", text_color="#2c3e50", border_color="#b2bec3",
                          command=lambda x=i + 1: self.add(f"L{x}"), **btn_3d).pack(side="left", padx=6)

        f2 = ctk.CTkFrame(self.f_ctrls, fg_color="transparent");
        f2.pack(pady=10)
        ops = [("↔", "↔"), ("→", "→"), ("+", "+"), ("-", "-"), ("*", "*"), ("/", "/"), ("(", "("), (")", ")")]
        for label, val in ops:
            ctk.CTkButton(f2, text=label, fg_color="#f8f9fa", text_color="#1f538d", border_color="#bdc3c7",
                          command=lambda x=val: self.add(x), **btn_3d).pack(side="left", padx=6)

        f3 = ctk.CTkFrame(self.f_ctrls, fg_color="transparent");
        f3.pack(pady=10)
        for n in "1234567890":
            ctk.CTkButton(f3, text=n, width=55, height=50, font=("Segoe UI", 18, "bold"), corner_radius=12,
                          border_width=3,
                          fg_color="#34495e", text_color="white", border_color="#2c3e50",
                          command=lambda x=n: self.add(x)).pack(side="left", padx=4)
        ctk.CTkButton(f3, text="⌫", fg_color="#e67e22", text_color="white", border_color="#d35400",
                      width=90, height=50, font=("Segoe UI", 19, "bold"), corner_radius=12, border_width=3,
                      command=self.backspace).pack(side="left", padx=12)

    def executar(self, from_redo=False, redo_cmd=None):
        cmd = redo_cmd if from_redo else "".join(self.comando_atual)
        if not cmd: return

        try:
            self.historico_undo.append((copy.deepcopy(self.sistema.matriz), cmd))
            if not from_redo: self.historico_redo = []

            # 1. Troca de Linhas: L1↔L2
            m_tr = re.match(r"L(\d+)↔L(\d+)", cmd)

            # 2. Combinação Linear: L1→L1+2L2 ou L1→L1-2L2
            m_cb = re.match(r"L(\d+)→L\1([+-])(.*)L(\d+)", cmd)

            # 3. Multiplicação por Escalar: L1→(1/8)L1 ou L1→1/8L1 (CORRIGIDO)
            m_ml = re.match(r"L(\d+)→\(?(.*?)\)?L\1$", cmd)

            if m_tr:
                self.sistema.trocar_linhas(int(m_tr.group(1)) - 1, int(m_tr.group(2)) - 1)

            elif m_cb:
                a, s, f, aux = m_cb.groups()
                # Limpa parênteses extras caso o usuário coloque (1/2)L2
                f_clean = f.replace("(", "").replace(")", "").replace("*", "")
                fat = Fraction(f_clean) if f_clean else Fraction(1)
                if s == "-": fat = -fat
                self.sistema.aplicar_operacao(int(a) - 1, int(aux) - 1, fat)

            elif m_ml:
                a, f = m_ml.groups()
                # Remove o '*' e parênteses que podem vir na captura
                f_clean = f.replace("*", "").replace("(", "").replace(")", "")

                if f_clean == "-":
                    fat = Fraction(-1)
                elif f_clean in ["+", ""]:
                    fat = Fraction(1)
                else:
                    fat = Fraction(f_clean)

                self.sistema.aplicar_operacao(int(a) - 1, 0, fat, True)

            else:
                raise ValueError("Sintaxe não reconhecida")

            self.render_matriz()
            self.limpar()

        except Exception as e:
            self.lbl_op.configure(text="SINTAXE INVÁLIDA", text_color="#ff4757")
            self.after(1000, self.limpar)
    def desfazer(self):
        if self.historico_undo:
            estado_antigo, cmd_realizado = self.historico_undo.pop()
            self.historico_redo.append((copy.deepcopy(self.sistema.matriz), cmd_realizado))
            self.sistema.matriz = estado_antigo
            self.render_matriz()
            self.lbl_op.configure(text=f"Desfeito: {cmd_realizado}", text_color="#f1c40f")

    def refazer(self):
        if self.historico_redo:
            estado_futuro, cmd_para_refazer = self.historico_redo.pop()
            self.executar(from_redo=True, redo_cmd=cmd_para_refazer)
            self.lbl_op.configure(text=f"Refeito: {cmd_para_refazer}", text_color="#00ff41")

    def add(self, t):
        self.comando_atual.append(t)
        self.lbl_op.configure(text="Operação: " + "".join(self.comando_atual), text_color="#00ff41")

    def backspace(self):
        if self.comando_atual:
            self.comando_atual.pop()
            self.lbl_op.configure(text="Operação: " + "".join(self.comando_atual))

    def limpar(self):
        self.comando_atual = []
        self.lbl_op.configure(text="Operação: ", text_color="#00ff41")

    def iniciar(self, l, c, matriz):
        self.n_lin, self.n_col = l, c
        self.sistema = SistemaLinear(l, c, matriz)
        self.historico_undo = []
        self.historico_redo = []
        self.limpar()
        self.render_teclado()
        self.render_matriz()


if __name__ == "__main__":
    app = JogoEscalonamento()
    app.mainloop()