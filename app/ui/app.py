# -*- coding: utf-8 -*-

from __future__ import annotations


from pathlib import Path
import re

import customtkinter as ctk
from PIL import Image
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from typing import Any, Iterable

from app.utils.formatting import format_brl, validar_data, validar_valor

from app.utils.report import generate_pdf_report

from app.data.store import load_data, save_data

from app.ui.widgets import ReadOnlyComboBox

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("dark-blue")

BRAND_COLORS = {
    "background": "#0B0B0B",
    "surface": "#121212",
    "panel": "#1A1A1A",
    "accent": "#007BFF",
    "accent_hover": "#0056B3",
    "neutral": "#1F1F1F",
    "text_primary": "#FFFFFF",
    "text_secondary": "#CCCCCC",
    "text_muted": "#8A8A8A",
    "success": "#1ABC9C",
    "danger": "#C0392B",
}
FONT_FAMILY = "Segoe UI"

USE_EMOJI = False

def e(txt: str, emoji: str) -> str:

    return f"{emoji} {txt}" if USE_EMOJI and emoji else txt

class ControleGastosApp(ctk.CTk):

    def __init__(self, arquivo_dados: str | None = None, empresa_nome: str | None = None, empresa_id: str | None = None):

        super().__init__()

        self.title("Sistema CAPT Empresarial — Grupo 14D")

        self.geometry("860x1000")

        self.resizable(True, True)

        self.minsize(640, 720)

        self.configure(fg_color=BRAND_COLORS["background"])

        self._icon_photo: tk.PhotoImage | None = None

        self.arquivo_dados = arquivo_dados or "gastos_empresa.json"

        self.empresa_nome = empresa_nome or "Empresa Corporativa"

        self.empresa_id = empresa_id or "empresa"

        self.empresa_slug = self._gerar_slug(self.empresa_nome or self.empresa_id)

        self.gastos: list[dict[str, Any]] = load_data(self.arquivo_dados)

        # Estado janela de gestão (lista com filtros por campos simples)

        self.janela_gestao = None

        self.lista_gastos_frame = None

        self.filtro_data_inicio_entry = None

        self.filtro_data_fim_entry = None

        self.filtro_tipo_combo = None

        self.filtro_forma_combo = None

        self.filtro_valor_combo = None

        self.scroll_container: ctk.CTkScrollableFrame | None = None

        self.resumo_filtros: dict[str, str] | None = None

        self.relatorio_filtros: dict[str, str] | None = None

        self.relatorio_dados_visiveis: list[dict[str, Any]] = []

        self.relatorio_window: ctk.CTkToplevel | None = None

        self.relatorio_scroll_frame: ctk.CTkScrollableFrame | None = None

        raiz = Path(__file__).resolve().parents[2]

        self.logo_path = raiz / "logo_empresa.png"

        self.logo_icon_path = self._encontrar_logo_icon(raiz)

        self.logo_image = self._carregar_logo(self.logo_path)

        self.fonts = {

            "title": ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"),

            "section": ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),

            "subtitle": ctk.CTkFont(family=FONT_FAMILY, size=14),

            "label": ctk.CTkFont(family=FONT_FAMILY, size=13),

            "button": ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),

            "metric": ctk.CTkFont(family=FONT_FAMILY, size=32, weight="bold"),

            "dropdown": ctk.CTkFont(family=FONT_FAMILY, size=12),

        }

        self.total_card_value = None

        self.quantidade_card_value = None

        self.criar_widgets()

        self._aplicar_icone_janela()

    def _encontrar_logo_icon(self, raiz: Path) -> Path | None:

        candidatos = ["logo_icon.ico", "logo_icon.png", "logo_icon.gif"]

        for nome in candidatos:

            caminho = raiz / nome

            if caminho.exists():

                return caminho

        return None

    def _aplicar_icone_janela(self):

        if not self.logo_icon_path:

            return

        try:

            if self.logo_icon_path.suffix.lower() == ".ico":

                self.iconbitmap(default=str(self.logo_icon_path))

            else:

                self._icon_photo = tk.PhotoImage(file=str(self.logo_icon_path))

                self.wm_iconphoto(True, self._icon_photo)

        except Exception:

            pass

    def _carregar_logo(self, caminho: Path, max_size: tuple[int, int] = (260, 120)) -> ctk.CTkImage | None:

        if not caminho.exists():

            return None

        try:

            imagem = Image.open(caminho)

        except Exception:

            return None

        largura, altura = imagem.size

        if largura <= 0 or altura <= 0:

            return None

        max_largura, max_altura = max_size

        escala = min(max_largura / largura, max_altura / altura, 1.0)

        nova_largura = max(1, int(largura * escala))

        nova_altura = max(1, int(altura * escala))

        return ctk.CTkImage(

            light_image=imagem,

            dark_image=imagem,

            size=(nova_largura, nova_altura),

        )

    def _criar_input_group(self, parent: ctk.CTkFrame, titulo: str, widget_factory):

        container = ctk.CTkFrame(parent, fg_color="transparent")

        container.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(

            container,

            text=titulo,

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", pady=(0, 4))

        widget = widget_factory(container)

        widget.pack(fill="x")

        return widget

    def _criar_card_resumo(self, parent: ctk.CTkFrame, titulo: str, valor: str, column: int):

        card = ctk.CTkFrame(

            parent,

            corner_radius=18,

            fg_color=BRAND_COLORS["panel"],

            border_color=BRAND_COLORS["neutral"],

            border_width=1,

        )

        card.grid(row=0, column=column, padx=12, pady=10, sticky="nsew")

        ctk.CTkLabel(

            card,

            text=titulo,

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=16, pady=(16, 6))

        valor_label = ctk.CTkLabel(

            card,

            text=valor,

            font=self.fonts["metric"],

            text_color=BRAND_COLORS["text_primary"],

        )

        valor_label.pack(anchor="w", padx=16, pady=(0, 16))

        return valor_label

    def _criar_botao(self, parent, texto: str, comando, *, fg_color=None, hover_color=None, height: int = 46):

        return ctk.CTkButton(

            parent,

            text=texto,

            command=comando,

            height=height,

            corner_radius=12,

            fg_color=fg_color or BRAND_COLORS["accent"],

            hover_color=hover_color or BRAND_COLORS["accent_hover"],

            font=self.fonts["button"],

            text_color=BRAND_COLORS["text_primary"],

        )
    
    def _priorizar_janela(self, janela: ctk.CTkToplevel):

        try:

            janela.lift()

            janela.focus_force()

            janela.attributes("-topmost", True)

            janela.after(250, lambda: janela.attributes("-topmost", False))

        except Exception:

            pass

    def _parse_data_str(self, valor: str | None) -> datetime | None:

        if not valor:

            return None

        try:

            return datetime.strptime(valor, "%d/%m/%Y")

        except (ValueError, TypeError):

            return None

    def _normalizar_filtros(self, filtros: dict[str, str] | None) -> dict[str, Any]:

        if not filtros:

            return {}

        normalizados: dict[str, Any] = {}

        data_inicio = self._parse_data_str(filtros.get("data_inicio"))

        data_fim = self._parse_data_str(filtros.get("data_fim"))

        if data_inicio:

            normalizados["data_inicio"] = data_inicio

        if data_fim:

            normalizados["data_fim"] = data_fim

        tipo = (filtros.get("tipo") or "").strip()

        if tipo and tipo != "Todos":

            normalizados["tipo"] = tipo

        forma = (filtros.get("forma") or "").strip()

        if forma and forma != "Todos":

            normalizados["forma"] = forma

        return normalizados

    def _gerar_slug(self, texto: str) -> str:

        texto = texto.lower().strip()

        texto = re.sub(r"[^a-z0-9]+", "-", texto)

        texto = re.sub(r"-{2,}", "-", texto).strip("-")

        return texto or "empresa"

    def _registro_atende_filtros(self, gasto: dict[str, Any], filtros: dict[str, Any]) -> bool:

        if not filtros:

            return True

        data_gasto = self._parse_data_str(str(gasto.get("data", "")))

        data_inicio = filtros.get("data_inicio")

        data_fim = filtros.get("data_fim")

        if data_inicio and (not data_gasto or data_gasto < data_inicio):

            return False

        if data_fim and (not data_gasto or data_gasto > data_fim):

            return False

        tipo = filtros.get("tipo")

        if tipo and gasto.get("tipo") != tipo:

            return False

        forma = filtros.get("forma")

        if forma and gasto.get("forma_pagamento") != forma:

            return False

        return True

    def _filtrar_registros(self, registros: Iterable[dict[str, Any]], filtros: dict[str, str] | None) -> list[dict[str, Any]]:

        filtros_norm = self._normalizar_filtros(filtros)

        if not filtros_norm:

            return list(registros)

        filtrados: list[dict[str, Any]] = []

        for registro in registros:

            if self._registro_atende_filtros(registro, filtros_norm):

                filtrados.append(registro)

        return filtrados

    def _abrir_modal_filtros(

        self,

        titulo: str,

        filtros_atuais: dict[str, str] | None,

        on_apply,

        *,

        allow_clear: bool = False,

        parent: ctk.CTk | ctk.CTkToplevel | None = None,

    ):

        alvo = parent or self

        modal = ctk.CTkToplevel(alvo)

        modal.title(titulo)

        modal.geometry("460x440")

        modal.resizable(False, False)

        modal.configure(fg_color=BRAND_COLORS["surface"])

        modal.transient(alvo)

        modal.grab_set()

        self._priorizar_janela(modal)

        conteudo = ctk.CTkFrame(

            modal,

            corner_radius=16,

            fg_color=BRAND_COLORS["panel"],

            border_color=BRAND_COLORS["neutral"],

            border_width=1,

        )

        conteudo.pack(fill="both", expand=True, padx=20, pady=20)

        filtros = filtros_atuais or {}

        ctk.CTkLabel(

            conteudo,

            text="Data Início (DD/MM/AAAA)",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry_inicio = ctk.CTkEntry(conteudo, height=38, font=self.fonts["label"])

        entry_inicio.pack(fill="x", padx=12)

        entry_inicio.insert(0, filtros.get("data_inicio", ""))

        ctk.CTkLabel(

            conteudo,

            text="Data Fim (DD/MM/AAAA)",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry_fim = ctk.CTkEntry(conteudo, height=38, font=self.fonts["label"])

        entry_fim.pack(fill="x", padx=12)

        entry_fim.insert(0, filtros.get("data_fim", ""))

        ctk.CTkLabel(

            conteudo,

            text="Tipo da Despesa",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        tipos_opcoes = ["Todos"] + self.tipos_despesa

        combo_tipo = ReadOnlyComboBox(conteudo, values=tipos_opcoes, height=38, font=self.fonts["label"], dropdown_font=self.fonts["dropdown"])

        combo_tipo.pack(fill="x", padx=12)

        combo_tipo.set(filtros.get("tipo", "Todos") or "Todos")

        ctk.CTkLabel(

            conteudo,

            text="Forma de Pagamento",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        formas_opcoes = ["Todos"] + self.formas_pagamento

        combo_forma = ReadOnlyComboBox(conteudo, values=formas_opcoes, height=38, font=self.fonts["label"], dropdown_font=self.fonts["dropdown"])

        combo_forma.pack(fill="x", padx=12)

        combo_forma.set(filtros.get("forma", "Todos") or "Todos")

        botoes = ctk.CTkFrame(conteudo, fg_color="transparent")

        botoes.pack(fill="x", padx=12, pady=(20, 8))

        def aplicar():

            inicio_val = entry_inicio.get().strip()

            fim_val = entry_fim.get().strip()

            if inicio_val and not validar_data(inicio_val):

                messagebox.showerror("Erro", "Data inicial inválida. Use o formato DD/MM/AAAA.")

                return

            if fim_val and not validar_data(fim_val):

                messagebox.showerror("Erro", "Data final inválida. Use o formato DD/MM/AAAA.")

                return

            dt_inicio = self._parse_data_str(inicio_val)

            dt_fim = self._parse_data_str(fim_val)

            if dt_inicio and dt_fim and dt_inicio > dt_fim:

                messagebox.showerror("Erro", "A data inicial não pode ser posterior à data final.")

                return

            novos_filtros: dict[str, str] = {}

            if inicio_val:

                novos_filtros["data_inicio"] = inicio_val

            if fim_val:

                novos_filtros["data_fim"] = fim_val

            tipo_valor = combo_tipo.get().strip()

            if tipo_valor and tipo_valor != "Todos":

                novos_filtros["tipo"] = tipo_valor

            forma_valor = combo_forma.get().strip()

            if forma_valor and forma_valor != "Todos":

                novos_filtros["forma"] = forma_valor

            on_apply(novos_filtros or None)

            modal.destroy()

        def limpar():

            on_apply(None)

            modal.destroy()

        self._criar_botao(

            botoes,

            "Aplicar filtros",

            aplicar,

            height=42,

        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(

            botoes,

            "Cancelar",

            modal.destroy,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#2C2C2C",

            height=42,

        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        if allow_clear:

            self._criar_botao(

                conteudo,

                "Limpar filtros",

                limpar,

                fg_color=BRAND_COLORS["neutral"],

                hover_color="#2C2C2C",

                height=40,

            ).pack(fill="x", padx=12, pady=(6, 12))

    def criar_widgets(self):

        if self.scroll_container and self.scroll_container.winfo_exists():

            self.scroll_container.destroy()

        self.scroll_container = ctk.CTkScrollableFrame(

            self,

            corner_radius=0,

            fg_color=BRAND_COLORS['background'],

        )

        self.scroll_container.pack(fill='both', expand=True, padx=12, pady=12)

        main_frame = ctk.CTkFrame(self.scroll_container, corner_radius=24, fg_color=BRAND_COLORS['surface'])

        main_frame.pack(fill='both', expand=True, padx=12, pady=12)

        header_frame = ctk.CTkFrame(main_frame, fg_color='transparent')

        header_frame.pack(fill='x', pady=(10, 6))

        top_actions = ctk.CTkFrame(header_frame, fg_color='transparent')

        top_actions.pack(fill='x', pady=(0, 12), padx=16)

        ctk.CTkLabel(

            top_actions,

            text=f"Acesso: {self.empresa_nome}",

            font=ctk.CTkFont(family=FONT_FAMILY, size=13),

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(side='left', padx=(0, 12))

        self._criar_botao(

            top_actions,

            "Mudar de empresa",

            self._reiniciar_aplicacao,

            fg_color=BRAND_COLORS['neutral'],

            hover_color="#2C2C2C",

            height=32,

        ).pack(side='right')

        if self.logo_image:

            logo_wrapper = ctk.CTkFrame(

                header_frame,

                fg_color="#FFFFFF",

                corner_radius=18,

            )

            logo_wrapper.pack(pady=(4, 8), padx=10)

            ctk.CTkLabel(

                logo_wrapper,

                image=self.logo_image,

                text='',

            ).pack(padx=22, pady=12)

        ctk.CTkLabel(

            header_frame,

            text='Captação de Despesas-14D',

            font=self.fonts['title'],

            text_color=BRAND_COLORS['text_primary'],

        ).pack()

        ctk.CTkLabel(

            header_frame,

            text='Controle de Gastos e Relatórios Empresariais',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(pady=(4, 8))

        ctk.CTkLabel(

            main_frame,

            text='Registro de Despesas Operacionais',

            font=self.fonts['section'],

            text_color=BRAND_COLORS['text_primary'],

        ).pack(anchor='w', padx=12, pady=(6, 6))

        formulario_frame = ctk.CTkFrame(

            main_frame,

            corner_radius=18,

            fg_color=BRAND_COLORS['panel'],

            border_color=BRAND_COLORS['neutral'],

            border_width=1,

        )

        formulario_frame.pack(fill='x', padx=12, pady=(0, 16))

        self.entry_data = self._criar_input_group(

            formulario_frame,

            'Data do lançamento',

            lambda container: ctk.CTkEntry(

                container,

                placeholder_text='DD/MM/AAAA',

                height=40,

                font=self.fonts['label'],

            ),

        )

        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        self.tipos_despesa = [
            "Água e esgoto",
            "Energia Elétrica",
            "Telefone",
            "Correios e Malotes",
            "FGTS",
            "DARF INSS",
            "ICMS",
            "Impostos Fiscais (PIS, Cofins, IRP e CSLL)",
            "Simples Nacional",
            "Salários (Funcionários)",
            "Férias (Funcionários)",
            "Rescisão (Funcionários)",
            "13º Salário (Funcionários)",
            "Pro-labore (Sócios)",
            "Aluguel",
        ]

        self.combo_tipo = self._criar_input_group(

            formulario_frame,

            'Tipo de despesa',

            lambda container: ReadOnlyComboBox(

                container,

                values=self.tipos_despesa,

                height=40,

                font=self.fonts['label'],

                dropdown_font=self.fonts['dropdown'],

            ),

        )

        self.combo_tipo.set('Selecione o tipo')

        self.formas_pagamento = [
            "Banco",
            "Dinheiro",
        ]

        self.combo_pagamento = self._criar_input_group(

            formulario_frame,

            'Forma de pagamento',

            lambda container: ReadOnlyComboBox(

                container,

                values=self.formas_pagamento,

                height=40,

                font=self.fonts['label'],

                dropdown_font=self.fonts['dropdown'],

            ),

        )

        self.combo_pagamento.set('Selecione a forma')

        self.entry_valor = self._criar_input_group(

            formulario_frame,

            'Valor (R$)',

            lambda container: ctk.CTkEntry(

                container,

                placeholder_text='0,00',

                height=40,

                font=self.fonts['label'],

            ),

        )

        botoes_frame = ctk.CTkFrame(main_frame, fg_color='transparent')

        botoes_frame.pack(fill='x', padx=12, pady=(0, 16))

        self._criar_botao(

            botoes_frame,

            'Salvar despesa',

            self.salvar_despesa,

            fg_color=BRAND_COLORS['success'],

            hover_color='#17A589',

        ).pack(side='left', expand=True, fill='x', padx=(0, 8))

        self._criar_botao(

            botoes_frame,

            'Limpar campos',

            self.limpar_campos,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#2C2C2C',

        ).pack(side='left', expand=True, fill='x', padx=8)

        self._criar_botao(

            botoes_frame,

            'Gerenciar despesas',

            self.abrir_gestao_gastos,

        ).pack(side='left', expand=True, fill='x', padx=(8, 0))

        resumo_titulo = ctk.CTkLabel(

            main_frame,

            text='Relatórios e Indicadores Financeiros',

            font=self.fonts['section'],

            text_color=BRAND_COLORS['text_primary'],

        )

        resumo_titulo.pack(anchor='w', padx=12, pady=(0, 8))

        cards_container = ctk.CTkFrame(main_frame, fg_color='transparent')

        cards_container.pack(fill='x', padx=4, pady=(0, 10))

        cards_container.grid_columnconfigure(0, weight=1)

        cards_container.grid_columnconfigure(1, weight=1)

        self.total_card_value = self._criar_card_resumo(

            cards_container,

            'Valor total registrado',

            'R$ 0,00',

            0,

        )

        self.quantidade_card_value = self._criar_card_resumo(

            cards_container,

            'Quantidade de registros',

            '0 lançamentos',

            1,

        )

        botoes_relatorios = ctk.CTkFrame(main_frame, fg_color='transparent')

        botoes_relatorios.pack(fill='x', padx=12, pady=(4, 18))

        self._criar_botao(

            botoes_relatorios,

            'Filtro',

            self.abrir_modal_filtro_resumo,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#2C2C2C',

        ).pack(side='left', expand=True, fill='x', padx=(0, 8))

        self._criar_botao(

            botoes_relatorios,

            'Histórico detalhado',

            self.mostrar_relatorio,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#2C2C2C',

        ).pack(side='left', expand=True, fill='x', padx=8)

        self._criar_botao(

            botoes_relatorios,

            'Exportar relatório em PDF',

            self.exportar_relatorio_pdf,

        ).pack(side='left', expand=True, fill='x', padx=(8, 0))

        ctk.CTkLabel(

            main_frame,

            text='Desenvolvido pelo Departamento de Tecnologia — GRUPO 14D • 2025',

            font=ctk.CTkFont(family=FONT_FAMILY, size=11),

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(pady=(8, 0))

        self.atualizar_stats()

    def abrir_modal_filtro_resumo(self):

        self._abrir_modal_filtros(

            "Filtro do Resumo Financeiro",

            self.resumo_filtros,

            self._aplicar_filtros_resumo,

            allow_clear=True,

        )

    def _aplicar_filtros_resumo(self, filtros: dict[str, str] | None):

        self.resumo_filtros = filtros

        self.atualizar_stats()

    def abrir_modal_filtro_relatorio(self):

        if not self.relatorio_window or not self.relatorio_window.winfo_exists():

            messagebox.showinfo("Info", "Abra o relatório completo antes de aplicar filtros.")

            return

        self._abrir_modal_filtros(

            "Filtros do Relatório Completo",

            self.relatorio_filtros,

            self._aplicar_filtros_relatorio,

            allow_clear=True,

            parent=self.relatorio_window,

        )

    def _aplicar_filtros_relatorio(self, filtros: dict[str, str] | None):

        self.relatorio_filtros = filtros

        self._renderizar_relatorio_detalhado()

    def _renderizar_relatorio_detalhado(self):

        if not self.relatorio_scroll_frame or not self.relatorio_scroll_frame.winfo_exists():

            return

        for child in self.relatorio_scroll_frame.winfo_children():

            child.destroy()

        registros = self._filtrar_registros(self.gastos, self.relatorio_filtros)

        def _parse_data(g: dict[str, Any]) -> datetime:

            try:

                return datetime.strptime(g.get("data", "01/01/1970"), "%d/%m/%Y")

            except (ValueError, TypeError):

                return datetime(1970, 1, 1)

        registros_ordenados = sorted(registros, key=_parse_data, reverse=True)

        self.relatorio_dados_visiveis = registros_ordenados

        frame = self.relatorio_scroll_frame

        frame.grid_columnconfigure(0, weight=2)

        frame.grid_columnconfigure(1, weight=4)

        frame.grid_columnconfigure(2, weight=3)

        frame.grid_columnconfigure(3, weight=2)

        if not registros_ordenados:

            ctk.CTkLabel(

                frame,

                text="Nenhum registro encontrado para os filtros selecionados.",

                font=self.fonts["label"],

                text_color=BRAND_COLORS["text_secondary"],

            ).pack(pady=20)

            return

        header_font = self.fonts["subtitle"]

        headers = ["Data", "Tipo de despesa", "Forma de pagamento", "Valor"]

        for col, header_text in enumerate(headers):

            sticky = "e" if col == 3 else "w"

            ctk.CTkLabel(

                frame,

                text=header_text,

                font=header_font,

                text_color=BRAND_COLORS["text_secondary"],

            ).grid(row=0, column=col, padx=10, pady=(5, 6), sticky=sticky)

        separator = ctk.CTkFrame(frame, height=2, fg_color=BRAND_COLORS["neutral"])

        separator.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=(0, 8))

        row_font = self.fonts["label"]

        for i, gasto in enumerate(registros_ordenados, start=2):

            data_label = ctk.CTkLabel(frame, text=gasto.get("data", "--"), font=row_font)

            tipo_label = ctk.CTkLabel(frame, text=gasto.get("tipo", "--"), font=row_font)

            forma_label = ctk.CTkLabel(frame, text=gasto.get("forma_pagamento", "--"), font=row_font)

            valor_label = ctk.CTkLabel(

                frame,

                text=format_brl(gasto.get("valor", 0.0)),

                font=row_font,

                text_color=BRAND_COLORS["text_primary"],

            )

            data_label.grid(row=i, column=0, padx=10, pady=6, sticky="w")

            tipo_label.grid(row=i, column=1, padx=10, pady=6, sticky="w")

            forma_label.grid(row=i, column=2, padx=10, pady=6, sticky="w")

            valor_label.grid(row=i, column=3, padx=10, pady=6, sticky="e")

            row_separator = ctk.CTkFrame(frame, height=1, fg_color=BRAND_COLORS["neutral"])

            row_separator.grid(row=i + 1, column=0, columnspan=4, sticky="ew", padx=10)

    def _exportar_pdf_relatorio_filtrado(self):

        registros = self.relatorio_dados_visiveis or self._filtrar_registros(self.gastos, self.relatorio_filtros)

        self.exportar_relatorio_pdf(registros)

    def _fechar_relatorio_window(self):

        if self.relatorio_window and self.relatorio_window.winfo_exists():

            self.relatorio_window.destroy()

        self.relatorio_window = None

        self.relatorio_scroll_frame = None

    def _reiniciar_aplicacao(self):

        from app.ui.empresa_selector import selecionar_empresa

        resposta = messagebox.askyesno(

            "Mudar de empresa",

            "Deseja voltar à seleção de empresas? Todos os dados visíveis serão recarregados.",

        )

        if not resposta:

            return

        info = selecionar_empresa()

        if not info:

            return

        novo_app = ControleGastosApp(

            arquivo_dados=info.get("arquivo"),

            empresa_nome=info.get("empresa_nome"),

            empresa_id=info.get("empresa_id"),

        )

        self.destroy()

        novo_app.mainloop()

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

        registros = []

        if isinstance(self.gastos, list):

            registros = self._filtrar_registros(self.gastos, self.resumo_filtros)

        total = sum((g.get("valor", 0.0) if isinstance(g, dict) else 0.0) for g in registros)

        quantidade = len(registros)

        if self.total_card_value:

            self.total_card_value.configure(text=format_brl(total))

        if self.quantidade_card_value:

            sufixo = "lançamento" if quantidade == 1 else "lançamentos"

            self.quantidade_card_value.configure(text=f"{quantidade} {sufixo}")

    # ------- Gestão com múltiplos filtros simples -------

    def abrir_gestao_gastos(self):

        if not self.gastos:

            messagebox.showinfo('Info', 'Nenhuma despesa registrada ainda.')

            return

        if self.janela_gestao and self.janela_gestao.winfo_exists():

            self.janela_gestao.focus_force()

            self.renderizar_lista_gastos()

            return

        self.janela_gestao = ctk.CTkToplevel(self)

        self.janela_gestao.title('Captação de Despesas-14D — Gestão de Despesas')

        self.janela_gestao.geometry('940x620')

        self.janela_gestao.resizable(True, True)

        self.janela_gestao.minsize(760, 520)

        self.janela_gestao.configure(fg_color=BRAND_COLORS['surface'])

        self._priorizar_janela(self.janela_gestao)

        ctk.CTkLabel(

            self.janela_gestao,

            text='Gestão de Despesas Operacionais',

            font=self.fonts['section'],

            text_color=BRAND_COLORS['text_primary'],

        ).pack(pady=20)

        filtros_frame = ctk.CTkFrame(

            self.janela_gestao,

            corner_radius=16,

            fg_color=BRAND_COLORS['panel'],

            border_color=BRAND_COLORS['neutral'],

            border_width=1,

        )

        filtros_frame.pack(fill='x', padx=20, pady=(0, 15))

        for coluna in range(4):

            filtros_frame.grid_columnconfigure(coluna, weight=1)

        ctk.CTkLabel(

            filtros_frame,

            text='Data Início (DD/MM/AAAA)',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=0, column=0, sticky='w', padx=12, pady=(12, 2))

        ctk.CTkLabel(

            filtros_frame,

            text='Data Fim (DD/MM/AAAA)',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=0, column=1, sticky='w', padx=12, pady=(12, 2))

        ctk.CTkLabel(

            filtros_frame,

            text='Tipo de despesa',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=0, column=2, sticky='w', padx=12, pady=(12, 2))

        ctk.CTkLabel(

            filtros_frame,

            text='Forma de pagamento',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=0, column=3, sticky='w', padx=12, pady=(12, 2))

        self.filtro_data_inicio_entry = ctk.CTkEntry(filtros_frame, height=36, font=self.fonts['label'])

        self.filtro_data_inicio_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky='ew')

        self.filtro_data_fim_entry = ctk.CTkEntry(filtros_frame, height=36, font=self.fonts['label'])

        self.filtro_data_fim_entry.grid(row=1, column=1, padx=12, pady=(0, 10), sticky='ew')

        tipos_filtro = ['Todos'] + sorted(self.tipos_despesa)

        self.filtro_tipo_combo = ReadOnlyComboBox(

            filtros_frame, values=tipos_filtro, height=36, font=self.fonts['label'], dropdown_font=self.fonts['dropdown']

        )

        self.filtro_tipo_combo.set('Todos')

        self.filtro_tipo_combo.grid(row=1, column=2, padx=12, pady=(0, 10), sticky='ew')

        formas_filtro = ['Todos'] + sorted(self.formas_pagamento)

        self.filtro_forma_combo = ReadOnlyComboBox(

            filtros_frame, values=formas_filtro, height=36, font=self.fonts['label'], dropdown_font=self.fonts['dropdown']

        )

        self.filtro_forma_combo.set('Todos')

        self.filtro_forma_combo.grid(row=1, column=3, padx=12, pady=(0, 10), sticky='ew')

        ctk.CTkLabel(

            filtros_frame,

            text='Valor',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=2, column=0, columnspan=4, sticky='w', padx=12, pady=(6, 2))

        self.filtro_valor_combo = ReadOnlyComboBox(

            filtros_frame,

            values=['Todos', 'Até 100', '100 a 500', '500 a 1000', 'Acima de 1000'],

            height=36,

            font=self.fonts['label'],

            dropdown_font=self.fonts['dropdown'],

        )

        self.filtro_valor_combo.set('Todos')

        self.filtro_valor_combo.grid(row=3, column=0, columnspan=4, padx=12, pady=(0, 10), sticky='ew')

        botoes_filtro = ctk.CTkFrame(filtros_frame, fg_color='transparent')

        botoes_filtro.grid(row=4, column=0, columnspan=4, pady=(0, 12), sticky='ew')

        self._criar_botao(

            botoes_filtro,

            'Aplicar filtros',

            self.renderizar_lista_gastos,

        ).pack(side='left', expand=True, fill='x', padx=(0, 6))

        self._criar_botao(

            botoes_filtro,

            'Limpar filtros',

            self.limpar_filtros_gestao,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#2C2C2C',

        ).pack(side='left', expand=True, fill='x', padx=(6, 0))

        self.lista_gastos_frame = ctk.CTkScrollableFrame(

            self.janela_gestao,

            width=880,

            height=420,

            fg_color=BRAND_COLORS['surface'],

        )

        self.lista_gastos_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self._criar_botao(

            self.janela_gestao,

            'Fechar painel',

            self.fechar_janela_gestao,

            fg_color=BRAND_COLORS['danger'],

            hover_color='#96281B',

        ).pack(pady=(0, 20), ipadx=10)

        self.janela_gestao.protocol('WM_DELETE_WINDOW', self.fechar_janela_gestao)

        self.renderizar_lista_gastos()

    def fechar_janela_gestao(self):

        if self.janela_gestao and self.janela_gestao.winfo_exists():

            self.janela_gestao.destroy()

        self.janela_gestao = None

        self.lista_gastos_frame = None

        self.filtro_data_inicio_entry = None

        self.filtro_data_fim_entry = None

        self.filtro_tipo_combo = None

        self.filtro_forma_combo = None

        self.filtro_valor_combo = None

    def limpar_filtros_gestao(self):

        if self.filtro_data_inicio_entry:

            self.filtro_data_inicio_entry.delete(0, "end")

        if self.filtro_data_fim_entry:

            self.filtro_data_fim_entry.delete(0, "end")

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

            ctk.CTkLabel(

                self.lista_gastos_frame,

                text="Nenhuma despesa correspondente aos filtros.",

                font=self.fonts["label"],

                text_color=BRAND_COLORS["text_secondary"],

            ).pack(pady=20)

            return

        for indice, gasto in gastos_filtrados:

            card = ctk.CTkFrame(

                self.lista_gastos_frame,

                corner_radius=16,

                fg_color=BRAND_COLORS["panel"],

                border_color=BRAND_COLORS["neutral"],

                border_width=1,

            )

            card.pack(fill="x", padx=14, pady=8)

            topo = ctk.CTkFrame(card, fg_color="transparent")

            topo.pack(fill="x", padx=16, pady=(12, 4))

            topo.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(

                topo,

                text=gasto.get("data", "--"),

                font=self.fonts["subtitle"],

                text_color=BRAND_COLORS["text_primary"],

            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(

                topo,

                text=format_brl(gasto.get("valor", 0.0)),

                font=self.fonts["section"],

                text_color=BRAND_COLORS["success"],

            ).grid(row=0, column=1, sticky="e")

            detalhes = ctk.CTkFrame(card, fg_color="transparent")

            detalhes.pack(fill="x", padx=16, pady=(0, 8))

            ctk.CTkLabel(

                detalhes,

                text=f"{gasto.get('tipo', '--')}  |  Forma: {gasto.get('forma_pagamento', '--')}",

                font=self.fonts["label"],

                text_color=BRAND_COLORS["text_primary"],

            ).grid(row=0, column=0, sticky="w")

            timestamp = gasto.get("timestamp")

            exibicao = timestamp.replace("T", " ")[:16] if timestamp else "Sem registro de horário"

            ctk.CTkLabel(

                detalhes,

                text=f"Registrado em {exibicao}",

                font=self.fonts["subtitle"],

                text_color=BRAND_COLORS["text_muted"],

            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

            botoes_frame = ctk.CTkFrame(card, fg_color="transparent")

            botoes_frame.pack(fill="x", padx=16, pady=(4, 12))

            self._criar_botao(

                botoes_frame,

                "Editar despesa",

                lambda idx=indice: self.abrir_editor_gasto(idx),

                height=38,

            ).pack(side="left", expand=True, fill="x", padx=(0, 6))

            self._criar_botao(

                botoes_frame,

                "Excluir",

                lambda idx=indice: self.excluir_gasto(idx),

                fg_color=BRAND_COLORS["danger"],

                hover_color="#96281B",

                height=38,

            ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def filtrar_gastos(self, gastos_ordenados):

        filtros_basicos: dict[str, str] = {}

        inicio = self.filtro_data_inicio_entry.get().strip() if self.filtro_data_inicio_entry else ""

        fim = self.filtro_data_fim_entry.get().strip() if self.filtro_data_fim_entry else ""

        if inicio:

            filtros_basicos["data_inicio"] = inicio

        if fim:

            filtros_basicos["data_fim"] = fim

        tipo_filtro = self.filtro_tipo_combo.get() if self.filtro_tipo_combo else "Todos"

        if tipo_filtro and tipo_filtro != "Todos":

            filtros_basicos["tipo"] = tipo_filtro

        forma_filtro = self.filtro_forma_combo.get() if self.filtro_forma_combo else "Todos"

        if forma_filtro and forma_filtro != "Todos":

            filtros_basicos["forma"] = forma_filtro

        valor_filtro = self.filtro_valor_combo.get() if self.filtro_valor_combo else "Todos"

        filtros_norm = self._normalizar_filtros(filtros_basicos)

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

            if filtros_norm and not self._registro_atende_filtros(gasto, filtros_norm):

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

        editor.title("Atualizar Registro Financeiro")

        editor.geometry("520x620")

        editor.resizable(True, True)

        editor.minsize(420, 520)

        editor.configure(fg_color=BRAND_COLORS["surface"])

        editor.transient(self)

        editor.grab_set()

        self._priorizar_janela(editor)

        ctk.CTkLabel(

            editor,

            text="Atualizar despesa operacional",

            font=self.fonts["section"],

            text_color=BRAND_COLORS["text_primary"],

        ).pack(pady=(18, 10))

        destaque = ctk.CTkFrame(

            editor,

            corner_radius=16,

            fg_color=BRAND_COLORS["panel"],

            border_color=BRAND_COLORS["neutral"],

            border_width=1,

        )

        destaque.pack(fill="x", padx=24, pady=(0, 12))

        ctk.CTkLabel(

            destaque,

            text=gasto.get("tipo", "--"),

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_primary"],

        ).pack(pady=(12, 2))

        ctk.CTkLabel(

            destaque,

            text=f"Valor atual: {format_brl(gasto.get('valor', 0))}",

            font=self.fonts["label"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(pady=(0, 14))

        form_frame = ctk.CTkFrame(editor, fg_color="transparent")

        form_frame.pack(fill="x", padx=24, pady=(0, 6))

        def criar_campo(rotulo, widget_factory):

            bloco = ctk.CTkFrame(form_frame, fg_color="transparent")

            bloco.pack(fill="x", pady=8)

            ctk.CTkLabel(

                bloco,

                text=rotulo,

                font=self.fonts["subtitle"],

                text_color=BRAND_COLORS["text_secondary"],

            ).pack(anchor="w")

            widget = widget_factory(bloco)

            widget.pack(fill="x", pady=(6, 0))

            return widget

        entry_data = criar_campo(

            "Data (DD/MM/AAAA)",

            lambda parent: ctk.CTkEntry(parent, height=40, font=self.fonts["label"]),

        )

        entry_data.insert(0, gasto.get("data", ""))

        tipos = self.tipos_despesa.copy()

        if gasto.get("tipo") and gasto["tipo"] not in tipos:

            tipos.append(gasto["tipo"])

        combo_tipo = criar_campo(

            "Tipo de despesa",

            lambda parent: ReadOnlyComboBox(

                parent,

                values=tipos,

                height=40,

                font=self.fonts["label"],

                dropdown_font=self.fonts["dropdown"],

            ),

        )

        combo_tipo.set(gasto.get("tipo", "Selecione o tipo"))

        formas = self.formas_pagamento.copy()

        if gasto.get("forma_pagamento") and gasto["forma_pagamento"] not in formas:

            formas.append(gasto["forma_pagamento"])

        combo_pagamento = criar_campo(

            "Forma de pagamento",

            lambda parent: ReadOnlyComboBox(

                parent,

                values=formas,

                height=40,

                font=self.fonts["label"],

                dropdown_font=self.fonts["dropdown"],

            ),

        )

        combo_pagamento.set(gasto.get("forma_pagamento", "Selecione a forma"))

        entry_valor = criar_campo(

            "Valor (R$)",

            lambda parent: ctk.CTkEntry(parent, height=40, font=self.fonts["label"]),

        )

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

            gasto.update(

                {

                    "data": nova_data,

                    "tipo": novo_tipo,

                    "forma_pagamento": novo_pagamento,

                    "valor": novo_valor,

                }

            )

            save_ok = save_data(self.arquivo_dados, self.gastos)

            self.atualizar_stats()

            self.renderizar_lista_gastos()

            if not save_ok:

                messagebox.showerror("Erro", "Não foi possível salvar os dados em disco.")

            else:

                messagebox.showinfo("Sucesso", "Despesa atualizada com sucesso!")

            editor.destroy()

        botoes_modal = ctk.CTkFrame(editor, fg_color="transparent")

        botoes_modal.pack(fill="x", padx=24, pady=(12, 10))

        self._criar_botao(botoes_modal, "Salvar alterações", salvar_edicao, height=42).pack(

            side="left", expand=True, fill="x", padx=(0, 8)

        )

        self._criar_botao(

            botoes_modal,

            "Cancelar",

            editor.destroy,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#2C2C2C",

            height=42,

        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

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

        if self.relatorio_window and self.relatorio_window.winfo_exists():

            self.relatorio_window.focus_force()

            self._renderizar_relatorio_detalhado()

            return

        self.relatorio_window = ctk.CTkToplevel(self)

        self.relatorio_window.title("Relatórios e Indicadores Financeiros — Grupo 14D")

        self.relatorio_window.geometry("1050x720")

        self.relatorio_window.resizable(True, True)

        self.relatorio_window.minsize(780, 560)

        self.relatorio_window.configure(fg_color=BRAND_COLORS["surface"])

        self.relatorio_window.transient(self)

        self.relatorio_window.grab_set()

        self._priorizar_janela(self.relatorio_window)

        ctk.CTkLabel(

            self.relatorio_window,

            text="Histórico corporativo de despesas",

            font=self.fonts["section"],

            text_color=BRAND_COLORS["text_primary"],

        ).pack(pady=20)

        acoes_frame = ctk.CTkFrame(self.relatorio_window, fg_color="transparent")

        acoes_frame.pack(fill="x", padx=24, pady=(0, 10))

        self._criar_botao(

            acoes_frame,

            "Filtro",

            self.abrir_modal_filtro_relatorio,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#2C2C2C",

            height=38,

        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(

            acoes_frame,

            "Limpar filtros",

            lambda: self._aplicar_filtros_relatorio(None),

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#2C2C2C",

            height=38,

        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.relatorio_scroll_frame = ctk.CTkScrollableFrame(self.relatorio_window, fg_color=BRAND_COLORS["surface"])

        self.relatorio_scroll_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        botoes_frame = ctk.CTkFrame(self.relatorio_window, fg_color="transparent")

        botoes_frame.pack(pady=(0, 20))

        self._criar_botao(

            botoes_frame,

            "Exportar PDF",

            self._exportar_pdf_relatorio_filtrado,

            height=40,

        ).pack(side="left", padx=(0, 8))

        self._criar_botao(

            botoes_frame,

            "Fechar",

            self._fechar_relatorio_window,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#2C2C2C",

            height=40,

        ).pack(side="left", padx=(8, 0))

        self.relatorio_window.protocol("WM_DELETE_WINDOW", self._fechar_relatorio_window)

        self._renderizar_relatorio_detalhado()


    def exportar_relatorio_pdf(self, registros: Iterable[dict[str, Any]] | None = None):

        registros_validos: list[dict[str, Any]] = []

        if registros is not None:

            registros_validos = list(registros)

        elif isinstance(self.gastos, list):

            registros_validos = list(self.gastos)

        if not registros_validos:

            messagebox.showinfo("Info", "Nenhuma despesa registrada para exportar.")

            return

        destino = Path("relatorios")

        destino.mkdir(parents=True, exist_ok=True)

        nome_arquivo = f"relatorio_{self.empresa_slug}.pdf"

        caminho_destino = destino / nome_arquivo

        try:

            logo_param = str(self.logo_path) if self.logo_path.exists() else None

            company_label = f"{self.empresa_nome} — Captação de Despesas-14D"

            caminho = generate_pdf_report(

                registros_validos,

                str(caminho_destino),

                company_name=company_label,

                logo_path=logo_param,

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

    ctk.set_default_color_theme("dark-blue")

    from app.ui.empresa_selector import selecionar_empresa

    empresa_info = selecionar_empresa()

    if not empresa_info:

        return

    app = ControleGastosApp(

        arquivo_dados=empresa_info.get("arquivo"),

        empresa_nome=empresa_info.get("empresa_nome"),

        empresa_id=empresa_info.get("empresa_id"),

    )

    app.mainloop()

