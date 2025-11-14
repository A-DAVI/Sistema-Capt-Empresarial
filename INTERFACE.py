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
        self.geometry("700x650")
        self.resizable(False, False)

        # Arquivo de dados
        self.arquivo_dados = "gastos_empresa.json"
        self.gastos = self.carregar_dados()
        self.janela_gestao = None
        self.lista_gastos_frame = None

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


        # Frame de estatísticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            stats_frame,
            text="📊 Resumo",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # Labels de estatísticas
        self.label_total = ctk.CTkLabel(
            stats_frame,
            text="Total de Despesas: R$ 0,00",
            font=ctk.CTkFont(size=13)
        )
        self.label_total.pack(pady=5)

        self.label_quantidade = ctk.CTkLabel(
            stats_frame,
            text="Quantidade de Registros: 0",
            font=ctk.CTkFont(size=13)
        )
        self.label_quantidade.pack(pady=(5, 15))

        # Botão Ver Relatório
        self.btn_relatorio = ctk.CTkButton(
            main_frame,
            text="📋 Ver Relatório Completo",
            command=self.mostrar_relatorio,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.btn_relatorio.pack(fill="x", padx=20, pady=(0, 20))

        # Atualizar estatísticas
        self.atualizar_stats()

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
        """Atualiza as estatísticas na interface"""
        total = sum(g['valor'] for g in self.gastos)
        quantidade = len(self.gastos)

        self.label_total.configure(text=f"Total de Despesas: R$ {total:,.2f}")
        self.label_quantidade.configure(text=f"Quantidade de Registros: {quantidade}")

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

        self.lista_gastos_frame = ctk.CTkScrollableFrame(
            self.janela_gestao,
            width=850,
            height=460
        )
        self.lista_gastos_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

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

        gastos_ordenados = self.obter_gastos_ordenados()

        if not gastos_ordenados:
            ctk.CTkLabel(
                self.lista_gastos_frame,
                text="Nenhuma despesa registrada.",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=20)
            return

        for indice, gasto in gastos_ordenados:
            gasto_frame = ctk.CTkFrame(self.lista_gastos_frame, corner_radius=8)
            gasto_frame.pack(fill="x", padx=10, pady=5)

            info_text = (
                f"Data: {gasto.get('data', '--')} | "
                f"Tipo: {gasto.get('tipo', '--')}\n"
                f"Forma: {gasto.get('forma_pagamento', '--')} | "
                f"Valor: R$ {gasto.get('valor', 0):,.2f}"
            )

            ctk.CTkLabel(
                gasto_frame,
                text=info_text,
                justify="left",
                font=ctk.CTkFont(size=13)
            ).pack(side="left", fill="x", expand=True, padx=(15, 5), pady=10)

            botoes_frame = ctk.CTkFrame(gasto_frame, fg_color="transparent")
            botoes_frame.pack(side="right", padx=10, pady=10)

            ctk.CTkButton(
                botoes_frame,
                text="Editar",
                width=90,
                command=lambda idx=indice: self.abrir_editor_gasto(idx)
            ).pack(side="left", padx=(0, 5))

            ctk.CTkButton(
                botoes_frame,
                text="Excluir",
                width=90,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda idx=indice: self.excluir_gasto(idx)
            ).pack(side="left")

    def abrir_editor_gasto(self, indice):
        """Abre modal para editar um gasto especifico"""
        gasto = self.gastos[indice]

        editor = ctk.CTkToplevel(self)
        editor.title("Editar Despesa")
        editor.geometry("400x450")

        ctk.CTkLabel(
            editor,
            text="Editar Despesa",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        ctk.CTkLabel(editor, text="Data (DD/MM/AAAA)").pack(anchor="w", padx=20)
        entry_data = ctk.CTkEntry(editor)
        entry_data.pack(fill="x", padx=20, pady=(5, 15))
        entry_data.insert(0, gasto.get('data', ''))

        tipos = self.tipos_despesa.copy()
        if gasto.get('tipo') and gasto['tipo'] not in tipos:
            tipos.append(gasto['tipo'])

        ctk.CTkLabel(editor, text="Tipo de Despesa").pack(anchor="w", padx=20)
        combo_tipo = ctk.CTkComboBox(editor, values=tipos)
        combo_tipo.pack(fill="x", padx=20, pady=(5, 15))
        combo_tipo.set(gasto.get('tipo', "Selecione o tipo"))

        formas = self.formas_pagamento.copy()
        if gasto.get('forma_pagamento') and gasto['forma_pagamento'] not in formas:
            formas.append(gasto['forma_pagamento'])

        ctk.CTkLabel(editor, text="Forma de Pagamento").pack(anchor="w", padx=20)
        combo_pagamento = ctk.CTkComboBox(editor, values=formas)
        combo_pagamento.pack(fill="x", padx=20, pady=(5, 15))
        combo_pagamento.set(gasto.get('forma_pagamento', "Selecione a forma"))

        ctk.CTkLabel(editor, text="Valor (R$)").pack(anchor="w", padx=20)
        entry_valor = ctk.CTkEntry(editor)
        entry_valor.pack(fill="x", padx=20, pady=(5, 20))
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

        ctk.CTkButton(
            editor,
            text="Salvar alteracoes",
            command=salvar_edicao,
            height=40
        ).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(
            editor,
            text="Cancelar",
            command=editor.destroy,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(fill="x", padx=20)

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
