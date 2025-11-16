# -*- coding: utf-8 -*-
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Any

from app.utils.formatting import format_brl, validar_data, validar_valor
from app.utils.report import generate_pdf_report
from app.data.store import load_data, save_data
from app.ui.widgets import ReadOnlyComboBox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


USE_EMOJI = False


def e(txt: str, emoji: str) -> str:
    return f"{emoji} {txt}" if USE_EMOJI and emoji else txt



class ControleGastosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Controle de Gastos Empresariais")
        self.geometry("700x950")
        self.resizable(False, False)

        self.arquivo_dados = "gastos_empresa.json"
        self.gastos: list[dict[str, Any]] = load_data(self.arquivo_dados)

        # Estado janela de gestão (lista com filtros por campos simples)
        self.janela_gestao = None
        self.lista_gastos_frame = None
        self.filtro_data_entry = None
        self.filtro_tipo_combo = None
        self.filtro_forma_combo = None
        self.filtro_valor_combo = None
        self.logo_empresa = "logo_empresa.png"

        self.criar_widgets()

    def criar_widgets(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            main_frame,
            text=e("Registro de Despesas", "📄"),
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=(20, 30))

        entrada_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        entrada_frame.pack(fill="x", padx=16, pady=(0, 12))

        # Data
        data_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(data_frame, text=e("Data:", "📆"), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.entry_data = ctk.CTkEntry(data_frame, placeholder_text="DD/MM/AAAA", height=32, font=ctk.CTkFont(size=13))
        self.entry_data.pack(fill="x", pady=(5, 0))
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Tipo
        tipo_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(tipo_frame, text=e("Tipo de Despesa:", "🏷"), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
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
            "Outros",
        ]
        self.combo_tipo = ReadOnlyComboBox(tipo_frame, values=self.tipos_despesa, height=32, font=ctk.CTkFont(size=13), dropdown_font=ctk.CTkFont(size=12))
        self.combo_tipo.pack(fill="x", pady=(5, 0))
        self.combo_tipo.set("Selecione o tipo")

        # Forma de pagamento
        pagamento_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        pagamento_frame.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(pagamento_frame, text=e("Forma de Pagamento:", "💳"), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.formas_pagamento = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Transferência Bancária", "Boleto", "Cheque"]
        self.combo_pagamento = ReadOnlyComboBox(pagamento_frame, values=self.formas_pagamento, height=32, font=ctk.CTkFont(size=13), dropdown_font=ctk.CTkFont(size=12))
        self.combo_pagamento.pack(fill="x", pady=(5, 0))
        self.combo_pagamento.set("Selecione a forma")

        # Valor
        valor_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        valor_frame.pack(fill="x", padx=16, pady=(8, 12))
        ctk.CTkLabel(valor_frame, text=e("Valor (R$):", "💰"), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.entry_valor = ctk.CTkEntry(valor_frame, placeholder_text="0,00", height=32, font=ctk.CTkFont(size=13))
        self.entry_valor.pack(fill="x", pady=(5, 0))

        # Botões
        botoes_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=16, pady=(4, 16))
        ctk.CTkButton(botoes_frame, text=e("Salvar Despesa", "💾"), command=self.salvar_despesa, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", hover_color="#27ae60").pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(botoes_frame, text=e("Limpar Campos", "🧹"), command=self.limpar_campos, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#95a5a6", hover_color="#7f8c8d").pack(side="left", expand=True, fill="x", padx=(5, 0))
        ctk.CTkButton(botoes_frame, text="Gerenciar Despesas", command=self.abrir_gestao_gastos, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#8e44ad", hover_color="#71368a").pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Resumo
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        stats_frame.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(
              stats_frame,
              text="Resumo",
              font=ctk.CTkFont(size=16, weight="bold"),
          ).pack(pady=(10, 6))
        self.label_total = ctk.CTkLabel(
              stats_frame,
              text="Total de Despesas: R$ 0,00",
              font=ctk.CTkFont(size=13),
          )
        self.label_total.pack(pady=4)
        self.label_quantidade = ctk.CTkLabel(
              stats_frame,
              text="Quantidade de Registros: 0",
              font=ctk.CTkFont(size=13),
          )
        self.label_quantidade.pack(pady=(2, 10))

          # Botões de relatório
        botoes_relatorio_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botoes_relatorio_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
              botoes_relatorio_frame,
              text="Ver Relatório Completo",
              command=self.mostrar_relatorio,
              height=38,
              font=ctk.CTkFont(size=13, weight="bold"),
              fg_color="#3498db",
              hover_color="#2980b9",
          ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
              botoes_relatorio_frame,
              text="Exportar Relatório em PDF",
              command=self.exportar_relatorio_pdf,
              height=38,
              font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))


    def salvar_despesa(self):
        data = (self.entry_data.get() or "").strip()
        tipo = self.combo_tipo.get()
        pagamento = self.combo_pagamento.get()
        valor_str = (self.entry_valor.get() or "").strip()

        if not validar_data(data):
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA.")
            return
        if tipo == "Selecione o tipo":
            messagebox.showerror("Erro", "Selecione um tipo de despesa!")
            return
        if pagamento == "Selecione a forma":
            messagebox.showerror("Erro", "Selecione uma forma de pagamento!")
            return
        valor = validar_valor(valor_str)
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido! Digite um número maior que zero.")
            return

        registro = {"data": data, "tipo": tipo, "forma_pagamento": pagamento, "valor": valor, "timestamp": datetime.now().isoformat()}
        self.gastos.append(registro)
        if not save_data(self.arquivo_dados, self.gastos):
            messagebox.showerror("Erro", "Não foi possível salvar os dados em disco.")

        self.atualizar_stats()
        try:
            self.renderizar_lista_gastos()
        except Exception:
            pass
        messagebox.showinfo("Sucesso", f"Despesa de {format_brl(valor)} registrada com sucesso!")
        self.limpar_campos()

    def limpar_campos(self):
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.combo_tipo.set("Selecione o tipo")
        self.combo_pagamento.set("Selecione a forma")
        self.entry_valor.delete(0, "end")

    def atualizar_stats(self):
        total = sum((g.get("valor", 0.0) if isinstance(g, dict) else 0.0) for g in self.gastos) if isinstance(self.gastos, list) else 0.0
        quantidade = len(self.gastos) if isinstance(self.gastos, list) else 0
        self.label_total.configure(text=f"Total de Despesas: {format_brl(total)}")
        self.label_quantidade.configure(text=f"Quantidade de Registros: {quantidade}")

    # ------- Gestão com múltiplos filtros simples -------
    def abrir_gestao_gastos(self):
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
        ctk.CTkLabel(self.janela_gestao, text="Gestão de Despesas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        filtros_frame = ctk.CTkFrame(self.janela_gestao, corner_radius=12)
        filtros_frame.pack(fill="x", padx=20, pady=(0, 15))
        filtros_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(filtros_frame, text="Data (DD/MM/AAAA)").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        self.filtro_data_entry = ctk.CTkEntry(filtros_frame, height=32)
        self.filtro_data_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(filtros_frame, text="Tipo").grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        tipos_filtro = ["Todos"] + sorted(self.tipos_despesa)
        self.filtro_tipo_combo = ReadOnlyComboBox(filtros_frame, values=tipos_filtro, height=32)
        self.filtro_tipo_combo.set("Todos")
        self.filtro_tipo_combo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(filtros_frame, text="Forma de Pagamento").grid(row=0, column=2, sticky="w", padx=10, pady=(10, 2))
        formas_filtro = ["Todos"] + sorted(self.formas_pagamento)
        self.filtro_forma_combo = ReadOnlyComboBox(filtros_frame, values=formas_filtro, height=32)
        self.filtro_forma_combo.set("Todos")
        self.filtro_forma_combo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(filtros_frame, text="Valor").grid(row=0, column=3, sticky="w", padx=10, pady=(10, 2))
        self.filtro_valor_combo = ReadOnlyComboBox(filtros_frame, values=["Todos", "Até 100", "100 a 500", "500 a 1000", "Acima de 1000"], height=32)
        self.filtro_valor_combo.set("Todos")
        self.filtro_valor_combo.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")

        botoes_filtro = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        botoes_filtro.grid(row=2, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        ctk.CTkButton(botoes_filtro, text="Aplicar filtros", command=self.renderizar_lista_gastos, height=32).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(botoes_filtro, text="Limpar filtros", command=self.limpar_filtros_gestao, height=32, fg_color="#95a5a6", hover_color="#7f8c8d").pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.lista_gastos_frame = ctk.CTkScrollableFrame(self.janela_gestao, width=850, height=460)
        self.lista_gastos_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        ctk.CTkButton(self.janela_gestao, text="Fechar", command=self.fechar_janela_gestao, height=35).pack(pady=(0, 20))
        self.janela_gestao.protocol("WM_DELETE_WINDOW", self.fechar_janela_gestao)
        self.renderizar_lista_gastos()

    def fechar_janela_gestao(self):
        if self.janela_gestao and self.janela_gestao.winfo_exists():
            self.janela_gestao.destroy()
        self.janela_gestao = None
        self.lista_gastos_frame = None
        self.filtro_data_entry = None
        self.filtro_tipo_combo = None
        self.filtro_forma_combo = None
        self.filtro_valor_combo = None

    def limpar_filtros_gestao(self):
        if self.filtro_data_entry:
            self.filtro_data_entry.delete(0, "end")
        if self.filtro_tipo_combo:
            self.filtro_tipo_combo.set("Todos")
        if self.filtro_forma_combo:
            self.filtro_forma_combo.set("Todos")
        if self.filtro_valor_combo:
            self.filtro_valor_combo.set("Todos")
        self.renderizar_lista_gastos()

    def obter_gastos_ordenados(self):
        def parse_data(gasto):
            try:
                return datetime.strptime(gasto.get("data", ""), "%d/%m/%Y")
            except (ValueError, TypeError):
                return datetime.min
        return sorted(enumerate(self.gastos), key=lambda item: (parse_data(item[1]), item[1].get("timestamp", "")), reverse=True)

    def renderizar_lista_gastos(self):
        if not self.lista_gastos_frame:
            return
        for child in self.lista_gastos_frame.winfo_children():
            child.destroy()

        gastos_filtrados = self.filtrar_gastos(self.obter_gastos_ordenados())
        if not gastos_filtrados:
            ctk.CTkLabel(self.lista_gastos_frame, text="Nenhuma despesa registrada.", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
            return

        for indice, gasto in gastos_filtrados:
            card = ctk.CTkFrame(self.lista_gastos_frame, corner_radius=12)
            card.pack(fill="x", padx=15, pady=7)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=15, pady=(10, 0))
            topo.grid_columnconfigure(0, weight=1)
            topo.grid_columnconfigure(1, weight=0)

            data_txt = gasto.get("data", "--")
            ctk.CTkLabel(topo, text=data_txt, font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(topo, text=f"{format_brl(gasto.get('valor', 0))}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1abc9c").grid(row=0, column=1, sticky="e")

            detalhes = ctk.CTkFrame(card, fg_color="transparent")
            detalhes.pack(fill="x", padx=15, pady=(4, 8))
            detalhes.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(detalhes, text=f"{gasto.get('tipo', '--')}  •  Forma: {gasto.get('forma_pagamento', '--')}", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w")

            timestamp = gasto.get("timestamp")
            exibicao = timestamp.replace("T", " ")[:16] if timestamp else "Sem registro de horário"
            ctk.CTkLabel(detalhes, text=f"Registrado em {exibicao}", font=ctk.CTkFont(size=11), text_color="#bdc3c7").grid(row=1, column=0, sticky="w", pady=(2, 0))

            botoes_frame = ctk.CTkFrame(card, fg_color="transparent")
            botoes_frame.pack(fill="x", padx=10, pady=(0, 8))
            ctk.CTkButton(botoes_frame, text="Editar", width=80, command=lambda idx=indice: self.abrir_editor_gasto(idx)).pack(side="left", padx=(0, 6))
            ctk.CTkButton(botoes_frame, text="Excluir", width=80, fg_color="#e74c3c", hover_color="#c0392b", command=lambda idx=indice: self.excluir_gasto(idx)).pack(side="left")

    def filtrar_gastos(self, gastos_ordenados):
        data_filtro = self.filtro_data_entry.get().strip() if self.filtro_data_entry else ""
        tipo_filtro = self.filtro_tipo_combo.get() if self.filtro_tipo_combo else "Todos"
        forma_filtro = self.filtro_forma_combo.get() if self.filtro_forma_combo else "Todos"
        valor_filtro = self.filtro_valor_combo.get() if self.filtro_valor_combo else "Todos"

        def corresponde_valor(valor, criterio):
            if criterio == "Todos":
                return True
            if criterio == "Até 100":
                return valor <= 100
            if criterio == "100 a 500":
                return 100 < valor <= 500
            if criterio == "500 a 1000":
                return 500 < valor <= 1000
            if criterio == "Acima de 1000":
                return valor > 1000
            return True

        resultado = []
        for indice, gasto in gastos_ordenados:
            if data_filtro and gasto.get("data") != data_filtro:
                continue
            if tipo_filtro != "Todos" and gasto.get("tipo") != tipo_filtro:
                continue
            if forma_filtro != "Todos" and gasto.get("forma_pagamento") != forma_filtro:
                continue
            try:
                valor_float = float(gasto.get("valor", 0) or 0)
            except (TypeError, ValueError):
                valor_float = 0
            if not corresponde_valor(valor_float, valor_filtro):
                continue
            resultado.append((indice, gasto))
        return resultado

    def abrir_editor_gasto(self, indice):
        gasto = self.gastos[indice]
        editor = ctk.CTkToplevel(self)
        editor.title("Editar Despesa")
        editor.geometry("460x560")
        editor.resizable(False, False)
        editor.transient(self)
        editor.grab_set()

        ctk.CTkLabel(editor, text="Editar registro selecionado", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))
        destaque = ctk.CTkFrame(editor, corner_radius=12)
        destaque.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(destaque, text=gasto.get("tipo", "--"), font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(12, 2))
        ctk.CTkLabel(destaque, text=f"Valor atual: {format_brl(gasto.get('valor', 0))}", font=ctk.CTkFont(size=13)).pack(pady=(0, 12))

        form_frame = ctk.CTkFrame(editor, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 6))

        def criar_campo(rotulo, widget_factory):
            bloco = ctk.CTkFrame(form_frame, fg_color="transparent")
            bloco.pack(fill="x", pady=6)
            ctk.CTkLabel(bloco, text=rotulo, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            widget = widget_factory(bloco)
            widget.pack(fill="x", pady=(5, 0))
            return widget

        entry_data = criar_campo("Data (DD/MM/AAAA)", lambda parent: ctk.CTkEntry(parent, height=32))
        entry_data.insert(0, gasto.get("data", ""))

        tipos = self.tipos_despesa.copy()
        if gasto.get("tipo") and gasto["tipo"] not in tipos:
            tipos.append(gasto["tipo"])
        combo_tipo = criar_campo("Tipo de Despesa", lambda parent: ReadOnlyComboBox(parent, values=tipos))
        combo_tipo.set(gasto.get("tipo", "Selecione o tipo"))

        formas = self.formas_pagamento.copy()
        if gasto.get("forma_pagamento") and gasto["forma_pagamento"] not in formas:
            formas.append(gasto["forma_pagamento"])
        combo_pagamento = criar_campo("Forma de Pagamento", lambda parent: ReadOnlyComboBox(parent, values=formas))
        combo_pagamento.set(gasto.get("forma_pagamento", "Selecione a forma"))

        entry_valor = criar_campo("Valor (R$)", lambda parent: ctk.CTkEntry(parent, height=32))
        entry_valor.insert(0, f"{float(gasto.get('valor', 0) or 0):.2f}".replace(".", ","))

        def salvar_edicao():
            nova_data = entry_data.get().strip()
            if not validar_data(nova_data):
                messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
                return
            novo_tipo = combo_tipo.get().strip()
            if not novo_tipo or novo_tipo == "Selecione o tipo":
                messagebox.showerror("Erro", "Escolha um tipo de despesa.")
                return
            novo_pagamento = combo_pagamento.get().strip()
            if not novo_pagamento or novo_pagamento == "Selecione a forma":
                messagebox.showerror("Erro", "Escolha uma forma de pagamento.")
                return
            novo_valor = validar_valor(entry_valor.get())
            if novo_valor is None:
                messagebox.showerror("Erro", "Valor inválido! Digite um número maior que zero.")
                return
            gasto.update({"data": nova_data, "tipo": novo_tipo, "forma_pagamento": novo_pagamento, "valor": novo_valor})
            save_ok = save_data(self.arquivo_dados, self.gastos)
            self.atualizar_stats()
            self.renderizar_lista_gastos()
            if not save_ok:
                messagebox.showerror("Erro", "Não foi possível salvar os dados em disco.")
            else:
                messagebox.showinfo("Sucesso", "Despesa atualizada com sucesso!")
            editor.destroy()

        botoes_modal = ctk.CTkFrame(editor, fg_color="transparent")
        botoes_modal.pack(fill="x", padx=24, pady=(8, 8))
        ctk.CTkButton(
            botoes_modal,
            text="Salvar alterações",
            command=salvar_edicao,
            height=38,
            width=140,
        ).pack(side="left", expand=True, padx=(0, 6))
        ctk.CTkButton(
            botoes_modal,
            text="Cancelar",
            command=editor.destroy,
            height=38,
            width=140,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
        ).pack(side="left", expand=True, padx=(6, 0))

    def excluir_gasto(self, indice):
        gasto = self.gastos[indice]
        valor = gasto.get("valor", 0)
        data = gasto.get("data", "--")
        tipo = gasto.get("tipo", "--")
        confirmar = messagebox.askyesno("Confirmar exclusão", f"Deseja excluir a despesa de {data} ({tipo}) no valor de {format_brl(valor)}?")
        if not confirmar:
            return
        del self.gastos[indice]
        save_ok = save_data(self.arquivo_dados, self.gastos)
        self.atualizar_stats()
        self.renderizar_lista_gastos()
        if not save_ok:
            messagebox.showerror("Erro", "Não foi possível salvar os dados em disco.")
        else:
            messagebox.showinfo("Sucesso", "Despesa removida com sucesso!")

    def mostrar_relatorio(self):
        if not self.gastos:
            messagebox.showinfo("Info", "Nenhuma despesa registrada ainda.")
            return
        relatorio_window = ctk.CTkToplevel(self)
        relatorio_window.title("Relatório Completo de Despesas")
        relatorio_window.geometry("1000x700")
        relatorio_window.transient(self)
        relatorio_window.grab_set()

        ctk.CTkLabel(relatorio_window, text=e("Relatório Completo de Despesas", "📈"), font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        scroll_frame = ctk.CTkScrollableFrame(relatorio_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configuração das colunas da grade (spreadsheet-like)
        scroll_frame.grid_columnconfigure(0, weight=2)  # Data
        scroll_frame.grid_columnconfigure(1, weight=4)  # Tipo
        scroll_frame.grid_columnconfigure(2, weight=3)  # Forma
        scroll_frame.grid_columnconfigure(3, weight=2)  # Valor

        # --- Cabeçalho da Tabela ---
        header_font = ctk.CTkFont(size=13, weight="bold")
        headers = ["Data", "Tipo de Despesa", "Forma de Pagamento", "Valor"]
        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(scroll_frame, text=header_text, font=header_font, text_color=("#3498db", "#5dade2"))
            sticky = "e" if header_text == "Valor" else ""  # Centraliza os outros cabeçalhos
            header_label.grid(row=0, column=col, padx=10, pady=(5, 10), sticky=sticky)

        # Linha separadora do cabeçalho
        separator = ctk.CTkFrame(scroll_frame, height=2, fg_color=("#bdc3c7", "#2c3e50"))
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5)

        # --- Dados da Tabela ---
        try:
            gastos_ordenados = sorted(self.gastos, key=lambda x: datetime.strptime(x.get("data", "01/01/1970"), "%d/%m/%Y"), reverse=True)
        except Exception:
            gastos_ordenados = list(self.gastos)

        row_font = ctk.CTkFont(size=12)
        row_font_large = ctk.CTkFont(size=14)
        for i, gasto in enumerate(gastos_ordenados, start=2): # Começa na linha 2, após o cabeçalho e separador
            data_label = ctk.CTkLabel(scroll_frame, text=gasto.get("data", "--"), font=row_font_large)
            tipo_label = ctk.CTkLabel(scroll_frame, text=gasto.get("tipo", "--"), font=row_font_large)
            forma_label = ctk.CTkLabel(scroll_frame, text=gasto.get("forma_pagamento", "--"), font=row_font_large)
            valor_label = ctk.CTkLabel(scroll_frame, text=format_brl(gasto.get("valor", 0.0)), font=row_font_large)

            data_label.grid(row=i, column=0, padx=10, pady=8, sticky="") # Centralizado
            tipo_label.grid(row=i, column=1, padx=10, pady=8, sticky="") # Centralizado
            forma_label.grid(row=i, column=2, padx=10, pady=8, sticky="") # Centralizado
            valor_label.grid(row=i, column=3, padx=10, pady=8, sticky="e")

            row_separator = ctk.CTkFrame(scroll_frame, height=1, fg_color=("#ecf0f1", "#34495e"))
            row_separator.grid(row=i + 1, column=0, columnspan=4, sticky="ew", padx=10)

        botoes_frame = ctk.CTkFrame(relatorio_window, fg_color="transparent")
        botoes_frame.pack(pady=(0, 20))
        ctk.CTkButton(
            botoes_frame,
            text="Exportar PDF",
            command=self.exportar_relatorio_pdf,
            height=32,
            width=140,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            botoes_frame,
            text="Fechar",
            command=relatorio_window.destroy,
            height=32,
            width=100,
        ).pack(side="left")

    def exportar_relatorio_pdf(self):
        if not self.gastos:
            messagebox.showinfo("Info", "Nenhuma despesa registrada para exportar.")
            return
        try:
            caminho = generate_pdf_report(
                self.gastos,
                "relatorios/relatorio_despesas.pdf",
                company_name="Controle de Gastos Empresariais",
                logo_path=self.logo_empresa,
            )
        except RuntimeError as exc:
            messagebox.showerror(
                "Erro ao gerar PDF",
                f"{exc}\n\nInstale a dependência e tente novamente.",
            )
            return
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro ao gerar PDF", f"Ocorreu um erro inesperado:\n{exc}")
            return

        messagebox.showinfo(
            "Relatório gerado",
            f"Relatório em PDF gerado com sucesso em:\n{caminho}",
        )


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ControleGastosApp()
    app.mainloop()
