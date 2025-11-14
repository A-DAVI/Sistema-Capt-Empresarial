import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import json
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ControleGastosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("Controle de Gastos Empresariais")
        self.geometry("780x720")
        self.resizable(False, False)

        # Arquivo de dados
        self.arquivo_dados = "gastos_empresa.json"
        self.gastos = self.carregar_dados()
        self.janela_gestao = None
        self.lista_gastos_frame = None
        self.filtros_colunas = {
            "data": None,
            "forma": None,
            "tipo": None,
            "valor": None,
            "historico": None
        }
        self.dropdown_filtros = {}
        self._atualizando_dropdowns = False
        self.colunas_planilha = [
            {"titulo": "Data", "chave": "data", "peso": 2, "anchor": "center"},
            {"titulo": "Forma de Pagamento (Banco/Caixa)", "chave": "forma", "peso": 3, "anchor": "w"},
            {"titulo": "Despesa", "chave": "tipo", "peso": 3, "anchor": "w"},
            {"titulo": "Valor", "chave": "valor", "peso": 2, "anchor": "e"},
            {"titulo": "Historico (Descricao da Despesa)", "chave": "historico", "peso": 4, "anchor": "w"}
        ]
        self.peso_coluna_acoes = 2

        # Criar interface
        self.criar_widgets()

    def criar_widgets(self):
        # Frame principal com padding
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = ctk.CTkLabel(
            main_frame,
            text="💰 Registro de Despesas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(20, 30))

        # Frame de entrada de dados
        entrada_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        entrada_frame.pack(fill="x", padx=20, pady=(0, 20))

        # DATA
        data_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            data_frame,
            text="📅 Data:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")

        self.entry_data = ctk.CTkEntry(
            data_frame,
            placeholder_text="DD/MM/AAAA",
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.entry_data.pack(fill="x", pady=(5, 0))
        # Preencher com data atual
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # TIPO DE DESPESA
        tipo_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            tipo_frame,
            text="🏷️ Tipo de Despesa:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")

        self.tipos_despesa = [
            "Salários e Encargos",
            "Aluguel",
            "Energia Elétrica",
            "Água",
            "Internet/Telefone",
            "Material de Escritório",
            "Manutenção",
            "Combustível",
            "Alimentação",
            "Marketing",
            "Impostos",
            "Consultoria",
            "Software/Licenças",
            "Equipamentos",
            "Outros"
        ]

        self.combo_tipo = ctk.CTkComboBox(
            tipo_frame,
            values=self.tipos_despesa,
            height=35,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12)
        )
        self.combo_tipo.pack(fill="x", pady=(5, 0))
        self.combo_tipo.set("Selecione o tipo")

        # FORMA DE PAGAMENTO
        pagamento_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        pagamento_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            pagamento_frame,
            text="💳 Forma de Pagamento:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")

        self.formas_pagamento = [
            "Dinheiro",
            "Cartão de Crédito",
            "Cartão de Débito",
            "PIX",
            "Transferência Bancária",
            "Boleto",
            "Cheque"
        ]

        self.combo_pagamento = ctk.CTkComboBox(
            pagamento_frame,
            values=self.formas_pagamento,
            height=35,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12)
        )
        self.combo_pagamento.pack(fill="x", pady=(5, 0))
        self.combo_pagamento.set("Selecione a forma")

        # VALOR
        valor_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        valor_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            valor_frame,
            text="💵 Valor (R$):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")

        self.entry_valor = ctk.CTkEntry(
            valor_frame,
            placeholder_text="0.00",
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.entry_valor.pack(fill="x", pady=(5, 0))

        # Frame de botões
        botoes_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            botoes_frame,
            text="✅ Salvar Despesa",
            command=self.salvar_despesa,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Botão Limpar
        self.btn_limpar = ctk.CTkButton(
            botoes_frame,
            text="🔄 Limpar Campos",
            command=self.limpar_campos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        self.btn_limpar.pack(side="left", expand=True, fill="x", padx=(5, 0))
        # Botão Gerenciar
        self.btn_gerenciar = ctk.CTkButton(
            botoes_frame,
            text="Gerenciar Despesas",
            command=self.abrir_gestao_gastos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#71368a"
        )
        self.btn_gerenciar.pack(side="left", expand=True, fill="x", padx=(5, 0))


        # Frame de estatisticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            stats_frame,
            text="Resumo Financeiro",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(12, 4))

        cards_container = ctk.CTkFrame(stats_frame, fg_color="transparent", height=90)
        cards_container.pack(fill="x", padx=20, pady=(5, 5))
        cards_container.pack_propagate(False)
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_columnconfigure(2, weight=1)

        self.card_total = self.criar_card_resumo(cards_container, "Total registrado", 0)
        self.card_ticket = self.criar_card_resumo(cards_container, "Ticket medio", 1)
        self.card_quantidade = self.criar_card_resumo(cards_container, "Qtd. de registros", 2)

        botoes_stats = ctk.CTkFrame(stats_frame, fg_color="transparent")
        botoes_stats.pack(fill="x", padx=20, pady=(5, 5))

        self.btn_relatorio = ctk.CTkButton(
            botoes_stats,
            text="Ver Relatorio Completo",
            command=self.mostrar_relatorio,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.btn_relatorio.pack(fill="x")

        # Atualizar estatísticas
        self.atualizar_stats()

    def criar_card_resumo(self, parent, titulo, coluna=0):
        """Cria cards do resumo financeiro"""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=coluna, padx=5, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(pady=(8, 2))

        valor_label = ctk.CTkLabel(
            card,
            text="--",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        valor_label.pack(pady=(0, 8))
        return valor_label


    def validar_data(self, data_str):
        """Valida formato de data DD/MM/AAAA"""
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def validar_valor(self, valor_str):
        """Valida e converte valor monetário"""
        try:
            # Remove espaços e substitui vírgula por ponto
            valor_str = valor_str.strip().replace(',', '.')
            valor = float(valor_str)
            if valor <= 0:
                return None
            return valor
        except ValueError:
            return None

    def salvar_despesa(self):
        """Salva a despesa no arquivo JSON"""
        # Validar campos
        data = self.entry_data.get().strip()
        tipo = self.combo_tipo.get()
        pagamento = self.combo_pagamento.get()
        valor_str = self.entry_valor.get().strip()

        # Validações
        if not self.validar_data(data):
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA")
            return

        if tipo == "Selecione o tipo":
            messagebox.showerror("Erro", "Selecione um tipo de despesa!")
            return

        if pagamento == "Selecione a forma":
            messagebox.showerror("Erro", "Selecione uma forma de pagamento!")
            return

        valor = self.validar_valor(valor_str)
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido! Digite um número maior que zero.")
            return

        # Criar registro
        registro = {
            "data": data,
            "tipo": tipo,
            "forma_pagamento": pagamento,
            "valor": valor,
            "timestamp": datetime.now().isoformat()
        }

        # Adicionar aos gastos
        self.gastos.append(registro)

        # Salvar no arquivo
        self.salvar_dados()

        # Atualizar estatísticas
        self.atualizar_stats()
        self.renderizar_lista_gastos()

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso",
            f"Despesa de R$ {valor:.2f} registrada com sucesso!"
        )

        # Limpar campos
        self.limpar_campos()

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.entry_data.delete(0, 'end')
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.combo_tipo.set("Selecione o tipo")
        self.combo_pagamento.set("Selecione a forma")
        self.entry_valor.delete(0, 'end')

    def atualizar_stats(self):
        """Atualiza as estatisticas na interface"""
        total = sum(g['valor'] for g in self.gastos)
        quantidade = len(self.gastos)
        media = total / quantidade if quantidade else 0

        if hasattr(self, 'card_total'):
            self.card_total.configure(text=f"R$ {total:,.2f}")
        if hasattr(self, 'card_ticket'):
            self.card_ticket.configure(text=f"R$ {media:,.2f}")
        if hasattr(self, 'card_quantidade'):
            self.card_quantidade.configure(text=str(quantidade))


    def mostrar_relatorio(self):
        """Mostra janela com relatório completo"""
        if not self.gastos:
            messagebox.showinfo("Info", "Nenhuma despesa registrada ainda.")
            return

        # Criar janela de relatório
        relatorio_window = ctk.CTkToplevel(self)
        relatorio_window.title("Relatório de Despesas")
        relatorio_window.geometry("800x600")

        # Título
        ctk.CTkLabel(
            relatorio_window,
            text="📊 Relatório Completo de Despesas",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        # Frame com scrollbar
        scroll_frame = ctk.CTkScrollableFrame(
            relatorio_window,
            width=750,
            height=450
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Ordenar por data (mais recente primeiro)
        gastos_ordenados = sorted(
            self.gastos,
            key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y"),
            reverse=True
        )

        # Mostrar cada gasto
        for i, gasto in enumerate(gastos_ordenados, 1):
            gasto_frame = ctk.CTkFrame(scroll_frame)
            gasto_frame.pack(fill="x", padx=10, pady=5)

            info_text = f"""
            {i}. Data: {gasto['data']}
               Tipo: {gasto['tipo']}
               Forma: {gasto['forma_pagamento']}
               Valor: R$ {gasto['valor']:,.2f}
                        """.strip()

            ctk.CTkLabel(
                gasto_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                justify="left"
            ).pack(anchor="w", padx=15, pady=10)

        # Botão fechar
        ctk.CTkButton(
            relatorio_window,
            text="Fechar",
            command=relatorio_window.destroy,
            height=35
        ).pack(pady=(0, 20))


    def abrir_gestao_gastos(self):
        """Abre interface para listar, editar e excluir despesas"""
        if not self.gastos:
            messagebox.showinfo("Info", "Nenhuma despesa registrada ainda.")
            return

        if self.janela_gestao and self.janela_gestao.winfo_exists():
            self.janela_gestao.focus_force()
            self.renderizar_lista_gastos()
            return

        self.janela_gestao = ctk.CTkToplevel(self)
        self.janela_gestao.title("Gerenciar Despesas")
        self.janela_gestao.geometry("900x600")

        ctk.CTkLabel(
            self.janela_gestao,
            text="Gestao de Despesas",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        for chave in self.filtros_colunas:
            self.filtros_colunas[chave] = None

        self.dropdown_filtros = {}

        tabela_container = ctk.CTkFrame(self.janela_gestao, corner_radius=12)
        tabela_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        botoes_auxiliares = ctk.CTkFrame(tabela_container, fg_color="transparent")
        botoes_auxiliares.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkButton(
            botoes_auxiliares,
            text="Limpar filtros aplicados",
            command=self.limpar_filtros_gestao,
            height=30,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(anchor="e")

        planilha_frame = ctk.CTkFrame(tabela_container, corner_radius=14, fg_color="#0f131c")
        planilha_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        planilha_frame.grid_rowconfigure(1, weight=1)
        planilha_frame.grid_columnconfigure(0, weight=1)

        header = self.criar_header_tabela(planilha_frame)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=(10, 0))

        self.lista_gastos_frame = ctk.CTkScrollableFrame(
            planilha_frame,
            width=820,
            height=420,
            fg_color="transparent"
        )
        self.lista_gastos_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5, 12))
        self.lista_gastos_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            self.janela_gestao,
            text="Fechar",
            command=self.fechar_janela_gestao,
            height=35
        ).pack(pady=(0, 20))

        self.janela_gestao.protocol("WM_DELETE_WINDOW", self.fechar_janela_gestao)
        self.renderizar_lista_gastos()

    def fechar_janela_gestao(self):
        """Fecha janela de gestao e limpa referencias"""
        if self.janela_gestao and self.janela_gestao.winfo_exists():
            self.janela_gestao.destroy()
        self.janela_gestao = None
        self.lista_gastos_frame = None
        self.filtro_labels = {}

    def limpar_filtros_gestao(self):
        """Limpa filtros ativos no cabeçalho da tabela"""
        for chave in self.filtros_colunas:
            self.filtros_colunas[chave] = None
        for dropdown in self.dropdown_filtros.values():
            dropdown.set("Todos")
        self.renderizar_lista_gastos()

    def obter_gastos_ordenados(self):
        """Retorna lista de tuplas (indice, gasto) ordenada por data desc"""
        def parse_data(gasto):
            try:
                return datetime.strptime(gasto.get('data', ''), "%d/%m/%Y")
            except (ValueError, TypeError):
                return datetime.min

        return sorted(
            enumerate(self.gastos),
            key=lambda item: (parse_data(item[1]), item[1].get('timestamp', '')),
            reverse=True
        )

    def renderizar_lista_gastos(self):
        """Atualiza a listagem na janela de gestao"""
        if not self.lista_gastos_frame:
            return

        for child in self.lista_gastos_frame.winfo_children():
            child.destroy()

        gastos_filtrados = self.filtrar_gastos()

        if not gastos_filtrados:
            ctk.CTkLabel(
                self.lista_gastos_frame,
                text="Nenhuma despesa encontrada com os filtros atuais.",
                font=ctk.CTkFont(size=13)
            ).grid(pady=30, padx=10)
            return

        linha_altura = 42
        divisor_cor = "#b0b9ce"

        for linha_idx, (indice, gasto) in enumerate(gastos_filtrados):
            bg_color = "#ffffff" if linha_idx % 2 == 0 else "#f8fbff"
            linha_wrapper = ctk.CTkFrame(self.lista_gastos_frame, fg_color="transparent")
            linha_wrapper.grid(row=linha_idx * 2, column=0, sticky="ew", padx=18, pady=0)

            linha = ctk.CTkFrame(linha_wrapper, fg_color="transparent")
            linha.pack(fill="x", expand=True)

            total_colunas = len(self.colunas_planilha) + 1
            for col in range(total_colunas):
                peso = self.colunas_planilha[col]["peso"] if col < len(self.colunas_planilha) else self.peso_coluna_acoes
                linha.grid_columnconfigure(col, weight=peso)

            for col_idx, coluna in enumerate(self.colunas_planilha):
                cell = ctk.CTkFrame(
                    linha,
                    fg_color=bg_color,
                    border_color=divisor_cor,
                    border_width=1,
                    corner_radius=0,
                    height=linha_altura
                )
                cell.grid(row=0, column=col_idx, sticky="nsew")
                cell.grid_propagate(False)
                cell.grid_columnconfigure(0, weight=1)

                texto = self.obter_valor_coluna(gasto, coluna["chave"])
                padding = (8, 0) if coluna.get("anchor") == "center" else (12, 0)
                fonte = ctk.CTkFont(
                    size=12,
                    weight="bold" if coluna["chave"] in ("data", "valor") else "normal"
                )
                ctk.CTkLabel(
                    cell,
                    text=texto,
                    anchor=coluna.get("anchor", "w"),
                    font=fonte,
                    text_color="#1c7d5f" if coluna["chave"] == "valor" else "#293347"
                ).grid(row=0, column=0, padx=padding, pady=6, sticky="nsew")

            acoes_cell = ctk.CTkFrame(
                linha,
                fg_color=bg_color,
                border_color=divisor_cor,
                border_width=1,
                corner_radius=0,
                height=linha_altura
            )
            acoes_cell.grid(row=0, column=len(self.colunas_planilha), sticky="nsew")
            acoes_cell.grid_propagate(False)

            botoes = ctk.CTkFrame(acoes_cell, fg_color="transparent")
            botoes.pack(expand=True, padx=10, pady=4)

            ctk.CTkButton(
                botoes,
                text="Editar",
                width=90,
                height=28,
                command=lambda idx=indice: self.abrir_editor_gasto(idx)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                botoes,
                text="Excluir",
                width=90,
                height=28,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda idx=indice: self.excluir_gasto(idx)
            ).pack(side="left")

            ctk.CTkFrame(
                self.lista_gastos_frame,
                height=1,
                fg_color=divisor_cor
            ).grid(row=linha_idx * 2 + 1, column=0, sticky="ew", padx=18)

    def filtrar_gastos(self):
        """Aplica filtros ativos ao dataset ordenado"""
        resultado = []
        for indice, gasto in self.obter_gastos_ordenados():
            if self.registro_corresponde_filtros(gasto):
                resultado.append((indice, gasto))
        return resultado

    def registro_corresponde_filtros(self, gasto):
        """Retorna True quando o gasto atende todos os filtros aplicados"""
        for coluna, filtro in self.filtros_colunas.items():
            if not filtro:
                continue
            if self.obter_valor_coluna(gasto, coluna) != filtro:
                return False
        return True

    def obter_valor_coluna(self, gasto, coluna):
        """Retorna o texto exibido para determinada coluna"""
        if coluna == "data":
            return gasto.get('data', '--')
        if coluna == "tipo":
            return gasto.get('tipo', '--')
        if coluna == "forma":
            return gasto.get('forma_pagamento', '--')
        if coluna == "valor":
            return self.formatar_moeda(gasto.get('valor', 0))
        if coluna == "historico":
            return gasto.get('historico') or gasto.get('descricao') or '--'
        return "--"

    def formatar_moeda(self, valor):
        """Formata os valores monetários utilizados na planilha"""
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            numero = 0
        return f"R$ {numero:,.2f}"

    def criar_header_tabela(self, parent):
        """Constroi cabeçalho estilo planilha com dropdowns embutidos"""
        header = ctk.CTkFrame(parent, fg_color="#f0f0f0", corner_radius=0, border_width=1, border_color="#a6a6a6")
        for idx, coluna in enumerate(self.colunas_planilha):
            header.grid_columnconfigure(idx, weight=coluna["peso"])
        header.grid_columnconfigure(len(self.colunas_planilha), weight=self.peso_coluna_acoes)

        fonte_titulo = ctk.CTkFont(size=12, weight="bold")
        for idx, coluna in enumerate(self.colunas_planilha):
            bloco = ctk.CTkFrame(
                header,
                fg_color="#d9d9d9",
                corner_radius=0,
                border_color="#a6a6a6",
                border_width=1
            )
            margem_esq = 14 if idx == 0 else 4
            margem_dir = 14 if idx == len(self.colunas_planilha) - 1 else 4
            bloco.grid(row=0, column=idx, sticky="nsew", padx=(margem_esq, margem_dir), pady=(6, 0))
            bloco.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                bloco,
                text=coluna["titulo"],
                font=fonte_titulo,
                text_color="#1f1f1f",
                anchor=coluna.get("anchor", "w")
            ).pack(fill="x", padx=10, pady=(4, 2))

            filtro_btn = ctk.CTkButton(
                bloco,
                text="▼",
                width=30,
                height=24,
                font=ctk.CTkFont(size=12),
                fg_color="#c4c4c4",
                hover_color="#b0b0b0",
                text_color="#1f1f1f",
                command=lambda chave=coluna["chave"]: self.mostrar_menu_filtro(chave)
            )
            filtro_btn.pack(padx=10, pady=(0, 4), anchor="e")

        bloco_acoes = ctk.CTkFrame(
            header,
            fg_color="#d9d9d9",
            corner_radius=0,
            border_color="#a6a6a6",
            border_width=1
        )
        bloco_acoes.grid(
            row=0,
            column=len(self.colunas_planilha),
            sticky="nsew",
            padx=(4, 14),
            pady=(6, 0)
        )
        ctk.CTkLabel(
            bloco_acoes,
            text="Acoes",
            font=fonte_titulo,
            text_color="#1f1f1f",
            anchor="center"
        ).pack(fill="both", pady=10)

        ctk.CTkFrame(header, height=1, fg_color="#a6a6a6").grid(
            row=1,
            column=0,
            columnspan=len(self.colunas_planilha) + 1,
            sticky="ew",
            padx=10,
            pady=(0, 6)
        )

        return header

    def mostrar_menu_filtro(self, coluna):
        """Exibe popup simples de filtro ao estilo Excel"""
        if not self.janela_gestao:
            return

        valores = ["Todos"] + self.coletar_valores_para_dropdown(coluna)
        popup = ctk.CTkToplevel(self.janela_gestao)
        popup.title(f"Filtrar por {coluna}")
        popup.geometry("220x150")
        popup.resizable(False, False)
        popup.transient(self.janela_gestao)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="Selecione um valor",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))

        combo = ctk.CTkOptionMenu(
            popup,
            values=valores or ["Todos"],
            width=160
        )
        combo.pack(pady=(0, 12))
        combo.set(self.filtros_colunas.get(coluna) or "Todos")

        def aplicar():
            selecionado = combo.get()
            self.filtros_colunas[coluna] = None if selecionado == "Todos" else selecionado
            self.renderizar_lista_gastos()
            popup.destroy()

        ctk.CTkButton(
            popup,
            text="Aplicar",
            command=aplicar,
            width=120
        ).pack()

    def coletar_valores_para_dropdown(self, coluna):
        """Lista itens disponíveis considerando outros filtros ativos"""
        valores = set()
        for gasto in self.gastos:
            if not self.registro_corresponde_filtros_exceto(gasto, coluna):
                continue
            valor = self.obter_valor_coluna(gasto, coluna)
            if valor:
                valores.add(valor)
        return sorted(valores)

    def registro_corresponde_filtros_exceto(self, gasto, coluna_ignorada):
        """Verifica se gasto respeita filtros exceto coluna fornecida"""
        for chave, filtro in self.filtros_colunas.items():
            if chave == coluna_ignorada or not filtro:
                continue
            if self.obter_valor_coluna(gasto, chave) != filtro:
                return False
        return True

    def abrir_editor_gasto(self, indice):
        """Abre modal para editar um gasto especifico"""
        gasto = self.gastos[indice]

        editor = ctk.CTkToplevel(self)
        editor.title("Editar Despesa")
        editor.geometry("460x520")
        editor.resizable(False, False)
        editor.transient(self)
        editor.grab_set()

        ctk.CTkLabel(
            editor,
            text="Editar registro selecionado",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        destaque = ctk.CTkFrame(editor, corner_radius=12)
        destaque.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(
            destaque,
            text=gasto.get('tipo', '--'),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(12, 2))
        ctk.CTkLabel(
            destaque,
            text=f"Valor atual: R$ {gasto.get('valor', 0):,.2f}",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(0, 12))

        form_frame = ctk.CTkFrame(editor, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 10))

        def criar_campo(rotulo, widget_factory):
            bloco = ctk.CTkFrame(form_frame, fg_color="transparent")
            bloco.pack(fill="x", pady=8)
            ctk.CTkLabel(
                bloco,
                text=rotulo,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w")
            widget = widget_factory(bloco)
            widget.pack(fill="x", pady=(5, 0))
            return widget

        entry_data = criar_campo(
            "Data (DD/MM/AAAA)",
            lambda parent: ctk.CTkEntry(parent, height=36)
        )
        entry_data.insert(0, gasto.get('data', ''))

        tipos = self.tipos_despesa.copy()
        if gasto.get('tipo') and gasto['tipo'] not in tipos:
            tipos.append(gasto['tipo'])

        combo_tipo = criar_campo(
            "Tipo de Despesa",
            lambda parent: ctk.CTkComboBox(parent, values=tipos)
        )
        combo_tipo.set(gasto.get('tipo', "Selecione o tipo"))

        formas = self.formas_pagamento.copy()
        if gasto.get('forma_pagamento') and gasto['forma_pagamento'] not in formas:
            formas.append(gasto['forma_pagamento'])

        combo_pagamento = criar_campo(
            "Forma de Pagamento",
            lambda parent: ctk.CTkComboBox(parent, values=formas)
        )
        combo_pagamento.set(gasto.get('forma_pagamento', "Selecione a forma"))

        entry_valor = criar_campo(
            "Valor (R$)",
            lambda parent: ctk.CTkEntry(parent, height=36)
        )
        entry_valor.insert(0, f"{gasto.get('valor', 0):.2f}")

        def salvar_edicao():
            nova_data = entry_data.get().strip()
            if not self.validar_data(nova_data):
                messagebox.showerror("Erro", "Data invalida. Use o formato DD/MM/AAAA.")
                return

            novo_tipo = combo_tipo.get().strip()
            if not novo_tipo or novo_tipo == "Selecione o tipo":
                messagebox.showerror("Erro", "Escolha um tipo de despesa.")
                return

            novo_pagamento = combo_pagamento.get().strip()
            if not novo_pagamento or novo_pagamento == "Selecione a forma":
                messagebox.showerror("Erro", "Escolha uma forma de pagamento.")
                return

            novo_valor = self.validar_valor(entry_valor.get())
            if novo_valor is None:
                messagebox.showerror("Erro", "Valor invalido! Digite um numero maior que zero.")
                return

            gasto.update({
                "data": nova_data,
                "tipo": novo_tipo,
                "forma_pagamento": novo_pagamento,
                "valor": novo_valor
            })

            self.salvar_dados()
            self.atualizar_stats()
            self.renderizar_lista_gastos()
            messagebox.showinfo("Sucesso", "Despesa atualizada com sucesso!")
            editor.destroy()

        botoes_modal = ctk.CTkFrame(editor, fg_color="transparent")
        botoes_modal.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkButton(
            botoes_modal,
            text="Salvar alteracoes",
            command=salvar_edicao,
            height=40
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkButton(
            botoes_modal,
            text="Cancelar",
            command=editor.destroy,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def excluir_gasto(self, indice):
        """Remove gasto apos confirmacao"""
        gasto = self.gastos[indice]
        valor = gasto.get('valor', 0)
        data = gasto.get('data', "--")
        tipo = gasto.get('tipo', "--")

        confirmar = messagebox.askyesno(
            "Confirmar exclusao",
            f"Deseja excluir a despesa de {data} ({tipo}) no valor de R$ {valor:,.2f}?"
        )
        if not confirmar:
            return

        del self.gastos[indice]
        self.salvar_dados()
        self.atualizar_stats()
        self.renderizar_lista_gastos()
        messagebox.showinfo("Sucesso", "Despesa removida com sucesso!")

    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.gastos, f, indent=2, ensure_ascii=False)

# Executar aplicação
if __name__ == "__main__":
    app = ControleGastosApp()
    app.mainloop()
