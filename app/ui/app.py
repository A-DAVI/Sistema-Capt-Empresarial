# -*- coding: utf-8 -*-

from __future__ import annotations


import re
import os
from pathlib import Path
import shutil

import customtkinter as ctk
from PIL import Image
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Any, Iterable

from app.utils.formatting import format_brl, validar_data, validar_valor

from app.utils.report import generate_pdf_report
from app.ui.dashboard import abrir_dashboard

from app.data.store import load_data, save_data

from app.ui.widgets import ReadOnlyComboBox
from app.utils.paths import runtime_path, workspace_path

LIGHT_COLORS = {
    "background": "#F5F7FA",
    "surface": "#FFFFFF",
    "panel": "#F0F2F5",
    "accent": "#0D6EFD",
    "accent_hover": "#0B5ED7",
    "neutral": "#E5E7EB",
    "text_primary": "#111827",
    "text_secondary": "#4B5563",
    "text_muted": "#6B7280",
    "success": "#0F9D58",
    "danger": "#B91C1C",
}

BRAND_COLORS: dict[str, str] = {}

ctk.set_default_color_theme("blue")
FONT_FAMILY = "Segoe UI"

USE_EMOJI = False

def e(txt: str, emoji: str) -> str:

    return f"{emoji} {txt}" if USE_EMOJI and emoji else txt

class ControleGastosApp(ctk.CTk):

    def __init__(self, arquivo_dados: str | None = None, empresa_nome: str | None = None, empresa_id: str | None = None, empresa_razao: str | None = None, *, theme_mode: str = "light", config_path: str | None = None):

        super().__init__()

        # tema fixo (apenas claro)
        self.theme_mode = "light"
        self.config_path = config_path
        self._apply_theme(self.theme_mode)

        self.title("Central de Controle")

        self.geometry("860x1000")

        self.resizable(True, True)

        self.minsize(640, 720)

        self.configure(fg_color=BRAND_COLORS["background"])

        self._icon_photo: tk.PhotoImage | None = None

        dados_path = Path(arquivo_dados) if arquivo_dados else workspace_path("gastos_empresa.json")
        self.arquivo_dados = str(dados_path)

        self.empresa_nome = empresa_nome or "Empresa Corporativa"

        self.empresa_razao = empresa_razao or self.empresa_nome

        self.empresa_id = empresa_id or "empresa"

        self.empresa_slug = self._gerar_slug(self.empresa_razao or self.empresa_nome or self.empresa_id)

        self.gastos: list[dict[str, Any]] = load_data(self.arquivo_dados)
        self.fornecedores: list[str] = sorted({str(g.get("fornecedor") or "").strip() for g in self.gastos if (g.get("fornecedor") or "").strip()})

        # Estado janela de gestão (lista com filtros por campos simples)

        self.janela_gestao = None

        self.lista_gastos_frame = None

        self.filtro_data_inicio_entry = None

        self.filtro_data_fim_entry = None

        self.filtro_tipo_combo = None

        self.filtro_forma_combo = None

        self.filtro_fornecedor_combo = None

        self.filtro_valor_combo = None

        self.scroll_container: ctk.CTkScrollableFrame | None = None

        self.resumo_filtros: dict[str, str] | None = None

        self.relatorio_filtros: dict[str, str] | None = None

        self.relatorio_dados_visiveis: list[dict[str, Any]] = []

        self.relatorio_window: ctk.CTkToplevel | None = None

        self.relatorio_scroll_frame: ctk.CTkScrollableFrame | None = None

        self.logo_path = self._resolver_recurso("logo_empresa.png")

        self.logo_icon_path = self._encontrar_logo_icon()

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

        fornecedores_base = [
            "PMAN SERVICOS REPRESENTACOES COM E IND LTDA",
            "COLMEIA DISTRIBUIDORA LTDA",
            "SOLUCAO, INGREDIENTES INDUSTRIAIS LTDA",
            "KASSIA FLORES LTDA",
            "ETIQUETAS MARINGA LTDA",
            "SANTA ROSA COMERCIO DE EMBALAGENS LTDA-EPP",
            "COMERCIO DE CHAPAS DE MDF LAMINIL LTDA",
            "CLEVERSON GERALDO RODRIGUES - ME",
            "ALMEVAN DISTRIBUIDORA DE ALIMENTOS LTDA",
            "BEBIDAS WHITE RIVER LTDA",
            "USINA ALTO ALEGRE S.A - ACUCAR E ALCOOL",
            "PALUMA VARIEDADES LTDA",
            "SUNNYVALE COM E REPRES LTDA",
            "CELERITAS DISTRIBUICAO DE BEBIDAS EM GERAL LTDA",
            "IND. COM. BEBIDAS FUNADA LTDA",
            "L DUARTE ALVES LTDA",
            "DIFRIPAR LOGISTICA E DISTRIBUICAO LTDA",
            "COFERPAN - COM FERM E PROD PANIF LTDA",
            "ARILU DISTRIBUIDORA S/A",
            "OESA COMERCIO E REPRESENTACOES S/A",
            "DISTRIBUIDORA DE GEN ALIM COLUMBIA LTDA",
            "TRANS APUCARANA TRANSPORTES RODOVIARIOS LTDA",
            "RODOVIARIO AFONSO LTDA",
            "ATACADAO S.A.",
            "SUPERMERCADO GUGUY LTDA",
            "M.J. DISTRIBUIDORA",
            "BAKER FAF LTDA",
            "COAGRU COOPERATIVA AGROINDUSTRIAL UNIAO",
        ]
        base_fornecedores = sorted({nome.strip().upper() for nome in fornecedores_base if nome.strip()})
        if not self.fornecedores:
            self.fornecedores = base_fornecedores
        else:
            # mescla base + existentes sem duplicar
            atuais = {f.upper() for f in self.fornecedores}
            self.fornecedores = sorted(atuais.union(base_fornecedores))

        categorias_flags = [
            ("Água e esgoto", False),
            ("Energia Elétrica", False),
            ("Telefone", False),
            ("Correios e Malotes", False),
            ("FGTS", False),
            ("DARF INSS", False),
            ("ICMS", False),
            ("Impostos Fiscais (PIS, Cofins, IRP e CSLL)", False),
            ("Simples Nacional", False),
            ("Salários (Funcionários)", False),
            ("Férias (Funcionários)", False),
            ("Rescisão (Funcionários)", False),
            ("13º Salário (Funcionários)", False),
            ("Pro-labore (Sócios)", False),
            ("Aluguel", False),
            ("Tarifas bancarias", False),
            ("combustível lubrificante", True),
            ("serviços de terceiros", True),
            ("Internet", False),
            ("Fretes e transportes", True),
            ("materiais de consumo", True),
            ("comissão de venda", True),
            ("despesa de viagem", False),
            ("Fornecedores de matéria prima, embalagens e insumos", True),
            ("Honorários", False),
            ("Consultoria jurídica", True),
            ("manutenção de equipamentos", True),
            ("bens de pequeno valor", True),
            ("Imobilizado - Veiculo", True),
            ("Imobilizado - Maquina e equipamentos", True),
            ("Imobilizado - Computadores e Periféricos", True),
            ("Manutenção de veículos", True),
            ("Alvara e taxa de licença sanitária", False),
            ("IPVA e licenciamento", False),
            ("IPTU", False),
        ]
        categorias_flags = [(self._normalizar_categoria(nome), precisa) for nome, precisa in categorias_flags]
        self.categorias_requer_fornecedor = {nome for nome, precisa in categorias_flags if precisa}
        self.tipos_despesa = sorted({nome for nome, _ in categorias_flags})

        self.criar_widgets()

        self._aplicar_icone_janela()

    def _resolver_recurso(self, nome: str) -> Path | None:
        workspace_candidate = workspace_path(nome)
        if workspace_candidate.exists():
            return workspace_candidate
        runtime_candidate = runtime_path(nome)
        if runtime_candidate.exists():
            return runtime_candidate
        return None

    def _encontrar_logo_icon(self) -> Path | None:
        candidatos = ["logo_icon.ico", "logo_icon.png", "logo_icon.gif"]
        for nome in candidatos:
            caminho = self._resolver_recurso(nome)
            if caminho:
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

    def _carregar_logo(self, caminho: Path | None, max_size: tuple[int, int] = (260, 120)) -> ctk.CTkImage | None:

        if not caminho or not caminho.exists():

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

    def _criar_card_resumo(self, parent: ctk.CTkFrame, titulo: str, valor: str, column: int, extra_widget=None):

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

        valor_label.pack(anchor="w", padx=16, pady=(0, 8))

        if extra_widget:
            try:
                extra_widget(card).pack(anchor="e", padx=12, pady=(0, 12))
            except Exception:
                pass

        return valor_label

    def _criar_botao(self, parent, texto: str, comando, *, fg_color=None, hover_color=None, height: int = 46, width: int | None = None):

        kwargs = {
            "height": height,
            "corner_radius": 12,
            "fg_color": fg_color or BRAND_COLORS["accent"],
            "hover_color": hover_color or BRAND_COLORS["accent_hover"],
            "font": self.fonts["button"],
            "text_color": BRAND_COLORS["text_primary"],
        }
        if width is not None:
            kwargs["width"] = width

        return ctk.CTkButton(

            parent,

            text=texto,

            command=comando,

            **kwargs,

        )

    def _apply_theme(self, mode: str):

        BRAND_COLORS.clear()
        BRAND_COLORS.update(LIGHT_COLORS)
        ctk.set_appearance_mode("light")

        try:

            self.configure(fg_color=BRAND_COLORS["background"])

        except Exception:

            pass


    def _fechar_janelas_secundarias(self):

        try:

            self._fechar_relatorio_window()

        except Exception:

            pass

        if self.janela_gestao and self.janela_gestao.winfo_exists():

            try:

                self.janela_gestao.destroy()

            except Exception:

                pass

        self.janela_gestao = None
        self.relatorio_window = None
        self.relatorio_scroll_frame = None

    def _reset_ui(self):
        """Remove todos os filhos visuais para recriar a interface do zero."""
        for child in list(self.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        self.scroll_container = None

    def _centralizar_janela(self, win: ctk.CTkToplevel | ctk.CTk | None):
        if not win:
            return
        try:
            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = max(0, int((sw - w) / 2))
            y = max(0, int((sh - h) / 2))
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _persistir_tema(self):
        """Salva a preferência de tema no config.json para uso em próximas execuções."""
        if not self.config_path:
            target = workspace_path("config.json")
        else:
            target = Path(self.config_path)

        try:
            import json

            data = {}
            if target.exists():
                data = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
            data["tema"] = self.theme_mode
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _atualizar_listas_categorias(self):

        if hasattr(self, "tipos_despesa"):

            normalizadas = {self._normalizar_categoria(valor) for valor in self.tipos_despesa if valor}
            self.tipos_despesa = sorted(normalizadas)

        combo_principal = getattr(self, "combo_tipo", None)

        if combo_principal:

            combo_principal.configure(values=self.tipos_despesa)

        filtro_combo = getattr(self, "filtro_tipo_combo", None)

        if filtro_combo:

            valores = ["Todos"] + sorted(self.tipos_despesa, key=lambda valor: valor.lower())

            selecionado = filtro_combo.get()

            filtro_combo.configure(values=valores)

            if selecionado not in valores:

                filtro_combo.set("Todos")

    def abrir_modal_nova_categoria(self):

        if not hasattr(self, "tipos_despesa"):

            base = [
                "Tarifas bancarias",
                "Combustivel lubrificante",
                "Servicos de terceiros",
                "Internet",
                "Fretes e transportes",
                "Materiais de consumo",
                "Comissao de venda",
                "Despesa de viagem",
                "Fornecedores de materia prima, embalagens e insumos",
                "Honorarios",
                "Consultoria juridica",
                "Manutencao de equipamentos",
                "Bens de pequeno valor",
                "Imobilizado - Veiculo",
                "Imobilizado - Maquina e equipamentos",
                "Imobilizado - Computadores e Perifericos",
                "Manutencao de veiculos",
                "Alvara e taxa de licenca sanitaria",
                "IPVA e licenciamento",
                "IPTU",
                "Agua e esgoto",
                "Energia Eletrica",
                "Telefone",
                "Correios e Malotes",
                "FGTS",
                "DARF INSS",
                "ICMS",
                "Impostos Fiscais (PIS, Cofins, IRP e CSLL)",
                "Simples Nacional",
                "Salarios (Funcionarios)",
                "Ferias (Funcionarios)",
                "Rescisao (Funcionarios)",
                "13o Salario (Funcionarios)",
                "Pro-labore (Socios)",
                "Aluguel",
            ]
            self.tipos_despesa = sorted({self._normalizar_categoria(nome) for nome in base})

        modal = ctk.CTkToplevel(self)

        modal.title("Adicionar nova categoria")

        modal.geometry("420x220")

        modal.resizable(False, False)

        modal.configure(fg_color=BRAND_COLORS["surface"])

        modal.transient(self)

        modal.grab_set()

        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        corpo = ctk.CTkFrame(

            modal,

            corner_radius=16,

            fg_color=BRAND_COLORS["panel"],

            border_color=BRAND_COLORS["neutral"],

            border_width=1,

        )

        corpo.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(

            corpo,

            text="Informe o nome da nova categoria de despesa",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 6))

        entry_nome = ctk.CTkEntry(corpo, height=40, font=self.fonts["label"])

        entry_nome.pack(fill="x", padx=12)

        botoes = ctk.CTkFrame(corpo, fg_color="transparent")

        botoes.pack(fill="x", padx=12, pady=(18, 6))

        def adicionar():

            nome = self._normalizar_categoria(entry_nome.get())

            if not nome:
                messagebox.showerror("Erro", "Informe um nome para a categoria.")
                return

            if any(nome == self._normalizar_categoria(existente) for existente in self.tipos_despesa):

                messagebox.showinfo("Aviso", "Esta categoria já está cadastrada.")
                return

            self.tipos_despesa.append(nome)

            self._atualizar_listas_categorias()

            messagebox.showinfo("Sucesso", f'Categoria "{nome}" adicionada.')

            modal.destroy()

        self._criar_botao(

            botoes,

            "Adicionar categoria",

            adicionar,

            height=40,

        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(

            botoes,

            "Cancelar",

            modal.destroy,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

            height=40,

        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def abrir_central_cadastros(self):
        categorias = sorted(self.tipos_despesa, key=lambda v: v.lower())
        fornecedores = sorted(self.fornecedores, key=lambda v: v.lower())

        modal = ctk.CTkToplevel(self)
        modal.title("Central de cadastros")
        modal.geometry("620x360")
        modal.resizable(False, False)
        modal.configure(fg_color=BRAND_COLORS["surface"])
        modal.transient(self)
        modal.grab_set()
        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        container = ctk.CTkFrame(modal, fg_color=BRAND_COLORS["panel"], border_color=BRAND_COLORS["neutral"], border_width=1, corner_radius=12)
        container.pack(fill="both", expand=True, padx=16, pady=16)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Categorias
        cat_frame = ctk.CTkFrame(container, fg_color="transparent")
        cat_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=10)
        ctk.CTkLabel(cat_frame, text="Categorias", font=self.fonts["subtitle"], text_color=BRAND_COLORS["text_primary"]).pack(anchor="w")
        cat_combo = ReadOnlyComboBox(cat_frame, values=categorias, height=34, font=self.fonts["label"], dropdown_font=self.fonts["dropdown"])
        cat_combo.pack(fill="x", pady=(6, 4))
        cat_entry = ctk.CTkEntry(cat_frame, height=36, font=self.fonts["label"])
        cat_entry.pack(fill="x", pady=(0, 8))

        def refresh_categorias():
            cats = sorted(self.tipos_despesa, key=lambda v: v.lower())
            cat_combo.configure(values=cats)
            if cats:
                cat_combo.set(cats[0])

        def add_categoria():
            nome = cat_entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Informe o nome da categoria.")
                return
            if any(nome.lower() == c.lower() for c in self.tipos_despesa):
                messagebox.showinfo("Aviso", "Categoria já existe.")
                return
            self.tipos_despesa.append(nome)
            self._atualizar_listas_categorias()
            refresh_categorias()
            cat_entry.delete(0, tk.END)

        def renomear_categoria():
            atual = cat_combo.get().strip()
            novo = cat_entry.get().strip()
            if not atual:
                messagebox.showerror("Erro", "Selecione uma categoria.")
                return
            if not novo:
                messagebox.showerror("Erro", "Informe o novo nome.")
                return
            if any(novo.lower() == c.lower() for c in self.tipos_despesa if c.lower() != atual.lower()):
                messagebox.showerror("Erro", "Já existe uma categoria com esse nome.")
                return
            for i, c in enumerate(self.tipos_despesa):
                if c.lower() == atual.lower():
                    self.tipos_despesa[i] = novo
                    break
            self._atualizar_listas_categorias()
            refresh_categorias()
            cat_entry.delete(0, tk.END)

        def remover_categoria():
            atual = cat_combo.get().strip()
            if not atual:
                messagebox.showerror("Erro", "Selecione uma categoria.")
                return
            if not messagebox.askyesno("Confirmar", f"Remover categoria \"{atual}\"?"):
                return
            self.tipos_despesa = [c for c in self.tipos_despesa if c.lower() != atual.lower()]
            self._atualizar_listas_categorias()
            refresh_categorias()
            cat_entry.delete(0, tk.END)

        btns_cat = ctk.CTkFrame(cat_frame, fg_color="transparent")
        btns_cat.pack(fill="x", pady=(6, 0))
        self._criar_botao(btns_cat, "Adicionar", add_categoria, height=34).pack(fill="x", pady=2)
        self._criar_botao(btns_cat, "Renomear", renomear_categoria, height=34, fg_color=BRAND_COLORS["neutral"], hover_color="#3B3B3B").pack(fill="x", pady=2)
        self._criar_botao(btns_cat, "Remover", remover_categoria, height=34, fg_color=BRAND_COLORS["danger"], hover_color="#962d22").pack(fill="x", pady=2)
        refresh_categorias()

        # Fornecedores
        forn_frame = ctk.CTkFrame(container, fg_color="transparent")
        forn_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 10), pady=10)
        ctk.CTkLabel(forn_frame, text="Fornecedores", font=self.fonts["subtitle"], text_color=BRAND_COLORS["text_primary"]).pack(anchor="w")
        forn_combo = ReadOnlyComboBox(forn_frame, values=fornecedores, height=34, font=self.fonts["label"], dropdown_font=self.fonts["dropdown"])
        forn_combo.pack(fill="x", pady=(6, 4))
        forn_entry = ctk.CTkEntry(forn_frame, height=36, font=self.fonts["label"])
        forn_entry.pack(fill="x", pady=(0, 8))

        def refresh_fornecedores():
            lista = sorted(self.fornecedores, key=lambda v: v.lower())
            forn_combo.configure(values=lista)
            if lista:
                forn_combo.set(lista[0])

        def add_fornecedor():
            nome = forn_entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Informe o nome do fornecedor.")
                return
            if any(nome.lower() == f.lower() for f in self.fornecedores):
                messagebox.showinfo("Aviso", "Fornecedor já existe.")
                return
            self.fornecedores.append(nome)
            refresh_fornecedores()
            forn_entry.delete(0, tk.END)

        def renomear_fornecedor():
            atual = forn_combo.get().strip()
            novo = forn_entry.get().strip()
            if not atual:
                messagebox.showerror("Erro", "Selecione um fornecedor.")
                return
            if not novo:
                messagebox.showerror("Erro", "Informe o novo nome.")
                return
            if any(novo.lower() == f.lower() for f in self.fornecedores if f.lower() != atual.lower()):
                messagebox.showerror("Erro", "Já existe um fornecedor com esse nome.")
                return
            for i, f in enumerate(self.fornecedores):
                if f.lower() == atual.lower():
                    self.fornecedores[i] = novo
                    break
            refresh_fornecedores()
            forn_entry.delete(0, tk.END)

        def remover_fornecedor():
            atual = forn_combo.get().strip()
            if not atual:
                messagebox.showerror("Erro", "Selecione um fornecedor.")
                return
            if not messagebox.askyesno("Confirmar", f"Remover fornecedor \"{atual}\"?"):
                return
            self.fornecedores = [f for f in self.fornecedores if f.lower() != atual.lower()]
            refresh_fornecedores()
            forn_entry.delete(0, tk.END)

        btns_forn = ctk.CTkFrame(forn_frame, fg_color="transparent")
        btns_forn.pack(fill="x", pady=(6, 0))
        self._criar_botao(btns_forn, "Adicionar", add_fornecedor, height=34).pack(fill="x", pady=2)
        self._criar_botao(btns_forn, "Renomear", renomear_fornecedor, height=34, fg_color=BRAND_COLORS["neutral"], hover_color="#3B3B3B").pack(fill="x", pady=2)
        self._criar_botao(btns_forn, "Remover", remover_fornecedor, height=34, fg_color=BRAND_COLORS["danger"], hover_color="#962d22").pack(fill="x", pady=2)
        refresh_fornecedores()

    def abrir_modal_editar_categoria(self):

        if not getattr(self, "tipos_despesa", None):

            messagebox.showinfo("Aviso", "Nenhuma categoria cadastrada para editar.")

            return

        categorias_ordenadas = sorted(self.tipos_despesa, key=lambda valor: valor.lower())

        modal = ctk.CTkToplevel(self)

        modal.title("Editar categoria")

        modal.geometry("460x260")

        modal.resizable(False, False)

        modal.configure(fg_color=BRAND_COLORS["surface"])

        modal.transient(self)

        modal.grab_set()

        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        corpo = ctk.CTkFrame(

            modal,

            corner_radius=16,

            fg_color=BRAND_COLORS["panel"],

            border_color=BRAND_COLORS["neutral"],

            border_width=1,

        )

        corpo.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(

            corpo,

            text="Selecione a categoria e informe o novo nome",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        combo = ReadOnlyComboBox(

            corpo,

            values=categorias_ordenadas,

            height=38,

            font=self.fonts["label"],

            dropdown_font=self.fonts["dropdown"],

        )

        combo.pack(fill="x", padx=12)

        entry_nome = ctk.CTkEntry(corpo, height=40, font=self.fonts["label"])

        entry_nome.pack(fill="x", padx=12, pady=(12, 0))

        valor_inicial = categorias_ordenadas[0]

        combo.set(valor_inicial)

        entry_nome.insert(0, valor_inicial)

        def atualizar_entry(valor: str):

            entry_nome.delete(0, tk.END)

            entry_nome.insert(0, valor)

        combo.configure(command=atualizar_entry)

        botoes = ctk.CTkFrame(corpo, fg_color="transparent")

        botoes.pack(fill="x", padx=12, pady=(18, 6))

        def salvar():

            antigo = self._normalizar_categoria(combo.get())

            novo = self._normalizar_categoria(entry_nome.get())

            if not antigo:

                messagebox.showerror("Erro", "Selecione uma categoria.")

                return

            if not novo:

                messagebox.showerror("Erro", "Informe o novo nome da categoria.")

                return

            if novo != antigo and any(novo == self._normalizar_categoria(existente) for existente in self.tipos_despesa):

                messagebox.showerror("Erro", "Já existe uma categoria com este nome.")

                return

            for idx, valor in enumerate(self.tipos_despesa):

                if self._normalizar_categoria(valor) == antigo:

                    self.tipos_despesa[idx] = novo

                    break

            combo_principal = getattr(self, "combo_tipo", None)

            if combo_principal and self._normalizar_categoria(combo_principal.get()) == antigo:

                combo_principal.set(novo)

            combo_filtro = getattr(self, "filtro_tipo_combo", None)

            if combo_filtro and self._normalizar_categoria(combo_filtro.get()) == antigo:

                combo_filtro.set(novo)

            self._atualizar_listas_categorias()

            messagebox.showinfo("Sucesso", "Categoria atualizada com sucesso.")

            modal.destroy()

        self._criar_botao(

            botoes,

            "Salvar",

            salvar,

            height=40,

        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(

            botoes,

            "Cancelar",

            modal.destroy,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

            height=40,

        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

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

        tipo = self._normalizar_categoria(filtros.get("tipo"))

        if tipo and tipo != "TODOS":

            normalizados["tipo"] = tipo

        forma = (filtros.get("forma") or "").strip()

        if forma and forma != "Todos":

            normalizados["forma"] = forma

        fornecedor = self._normalizar_fornecedor(filtros.get("fornecedor"))

        if fornecedor and fornecedor != "TODOS":

            normalizados["fornecedor"] = fornecedor

        return normalizados

    def _normalizar_categoria(self, nome: str | None) -> str:
        """Normaliza o nome da categoria para comparação e exibição."""
        return (nome or "").strip().upper()

    def _normalizar_fornecedor(self, nome: str | None) -> str:
        """Normaliza o nome do fornecedor."""
        return (nome or "").strip().upper()

    def _toggle_fornecedor(self) -> None:
        """Exibe ou oculta o campo de fornecedor conforme a necessidade."""
        if not hasattr(self, "fornecedor_fields"):
            return
        ativo = bool(getattr(self, "fornecedor_ativo", tk.IntVar(value=0)).get())
        try:
            if ativo:
                self.fornecedor_fields.pack(fill="x", padx=12, pady=(0, 12))
            else:
                self.fornecedor_fields.pack_forget()
                self.combo_fornecedor.set("Selecione o fornecedor")
        except Exception:
            pass

    def _abrir_busca_fornecedor(self) -> None:
        """Abre uma janela simples para buscar fornecedor por texto."""
        modal = ctk.CTkToplevel(self)
        modal.title("Buscar fornecedor")
        modal.geometry("420x480")
        modal.configure(fg_color=BRAND_COLORS.get("surface", "#111111"))
        modal.transient(self)
        modal.grab_set()
        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        ctk.CTkLabel(
            modal,
            text="Digite para filtrar",
            font=self.fonts["subtitle"],
            text_color=BRAND_COLORS.get("text_secondary", "#CCCCCC"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry = ctk.CTkEntry(modal, height=36, font=self.fonts["label"])
        entry.pack(fill="x", padx=12, pady=(0, 8))

        lista = tk.Listbox(modal, height=15, font=("Segoe UI", 11))
        lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        fornecedores = self.fornecedores

        def atualizar_lista(filtro: str = "") -> None:
            lista.delete(0, tk.END)
            termo = filtro.strip().upper()
            for nome in fornecedores:
                if not termo or termo in nome:
                    lista.insert(tk.END, nome)

        def selecionar(event=None) -> None:  # noqa: ANN001
            if not lista.curselection():
                return
            valor = lista.get(lista.curselection()[0])
            if hasattr(self, "fornecedor_ativo"):
                self.fornecedor_ativo.set(1)
            self.combo_fornecedor.set(valor)
            self._toggle_fornecedor()
            modal.destroy()

        lista.bind("<Double-Button-1>", selecionar)
        entry.bind("<KeyRelease>", lambda event: atualizar_lista(entry.get()))
        atualizar_lista()

    def _abrir_busca_categoria(self) -> None:
        """Abre uma janela para buscar e selecionar categoria de despesa."""
        modal = ctk.CTkToplevel(self)
        modal.title("Buscar categoria")
        modal.geometry("420x480")
        modal.configure(fg_color=BRAND_COLORS.get("surface", "#111111"))
        modal.transient(self)
        modal.grab_set()
        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        ctk.CTkLabel(
            modal,
            text="Digite para filtrar",
            font=self.fonts["subtitle"],
            text_color=BRAND_COLORS.get("text_secondary", "#CCCCCC"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry = ctk.CTkEntry(modal, height=36, font=self.fonts["label"])
        entry.pack(fill="x", padx=12, pady=(0, 8))

        lista = tk.Listbox(modal, height=15, font=("Segoe UI", 11))
        lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        categorias = sorted(self.tipos_despesa)

        def atualizar_lista(filtro: str = "") -> None:
            lista.delete(0, tk.END)
            termo = filtro.strip().upper()
            for nome in categorias:
                if not termo or termo in nome:
                    lista.insert(tk.END, nome)

        def selecionar(event=None) -> None:  # noqa: ANN001
            if not lista.curselection():
                return
            valor = lista.get(lista.curselection()[0])
            self.combo_tipo.set(valor)
            self._on_tipo_change()
            modal.destroy()

        lista.bind("<Double-Button-1>", selecionar)
        entry.bind("<KeyRelease>", lambda event: atualizar_lista(entry.get()))
        atualizar_lista()

    def _on_tipo_change(self, *_args) -> None:
        """Ativa/desativa fornecedor automaticamente conforme a categoria."""
        tipo_atual = self._normalizar_categoria(self.combo_tipo.get())
        exige = tipo_atual in getattr(self, "categorias_requer_fornecedor", set())
        try:
            if exige:
                self.fornecedor_ativo.set(1)
            else:
                self.fornecedor_ativo.set(0)
                self.combo_fornecedor.set("Selecione o fornecedor")
            self._toggle_fornecedor()
        except Exception:
            pass

    def _formatar_valor_widget(self, widget: tk.Entry | ctk.CTkEntry | None) -> None:
        """Formata o campo de valor enquanto digita (##.###,##)."""
        if widget is None:
            return
        if getattr(self, "_formatando_valor", False):
            return
        try:
            self._formatando_valor = True
            texto = widget.get() or ""
            digits = "".join(ch for ch in texto if ch.isdigit())
            if not digits:
                widget.delete(0, "end")
                return
            valor_centavos = int(digits)
            valor_float = valor_centavos / 100
            formatado = (
                f"{valor_float:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
            cursor = len(formatado)
            widget.delete(0, "end")
            widget.insert(0, formatado)
            widget.icursor(cursor)
        except Exception:
            try:
                widget.icursor("end")
            except Exception:
                pass
        finally:
            self._formatando_valor = False

    def _formatar_data_widget(self, widget: tk.Entry | ctk.CTkEntry | None) -> None:
        """Formata o campo de data enquanto digita (DD/MM/AAAA)."""
        if widget is None:
            return
        if getattr(self, "_formatando_data", False):
            return
        try:
            self._formatando_data = True
            texto = widget.get() or ""
            digits = "".join(ch for ch in texto if ch.isdigit())[:8]
            partes = []
            if len(digits) >= 2:
                partes.append(digits[:2])
            else:
                partes.append(digits)
            if len(digits) >= 4:
                partes.append(digits[2:4])
            elif len(digits) > 2:
                partes.append(digits[2:])
            if len(digits) > 4:
                partes.append(digits[4:])
            formatado = "/".join(partes)
            cursor = len(formatado)
            widget.delete(0, "end")
            widget.insert(0, formatado)
            widget.icursor(cursor)
        except Exception:
            try:
                widget.icursor("end")
            except Exception:
                pass
        finally:
            self._formatando_data = False

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

        if tipo and self._normalizar_categoria(gasto.get("tipo")) != tipo:

            return False

        forma = filtros.get("forma")

        if forma and gasto.get("forma_pagamento") != forma:

            return False

        fornecedor = filtros.get("fornecedor")

        if fornecedor and self._normalizar_fornecedor(gasto.get("fornecedor")) != fornecedor:

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

        parent: ctk.CTk | ctk.CTkToplevel | None = None,

    ):

        alvo = parent or self

        modal = ctk.CTkToplevel(alvo)

        modal.title(titulo)

        modal.geometry("520x560")
        modal.minsize(480, 520)

        modal.resizable(False, False)

        modal.configure(fg_color=BRAND_COLORS["surface"])

        modal.transient(alvo)

        modal.grab_set()

        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

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
        entry_inicio.bind("<KeyRelease>", lambda event: self._formatar_data_widget(entry_inicio))

        ctk.CTkLabel(

            conteudo,

            text="Data Fim (DD/MM/AAAA)",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry_fim = ctk.CTkEntry(conteudo, height=38, font=self.fonts["label"])

        entry_fim.pack(fill="x", padx=12)

        entry_fim.insert(0, filtros.get("data_fim", ""))
        entry_fim.bind("<KeyRelease>", lambda event: self._formatar_data_widget(entry_fim))

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

        ctk.CTkLabel(

            conteudo,

            text="Fornecedor",

            font=self.fonts["subtitle"],

            text_color=BRAND_COLORS["text_secondary"],

        ).pack(anchor="w", padx=12, pady=(12, 4))

        fornecedores_opcoes = ["Todos"] + self.fornecedores

        combo_fornecedor = ReadOnlyComboBox(conteudo, values=fornecedores_opcoes, height=38, font=self.fonts["label"], dropdown_font=self.fonts["dropdown"])

        combo_fornecedor.pack(fill="x", padx=12)

        combo_fornecedor.set(filtros.get("fornecedor", "Todos") or "Todos")

        botoes = ctk.CTkFrame(conteudo, fg_color="transparent")

        botoes.pack(fill="x", padx=12, pady=(20, 12))

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

            fornecedor_valor = combo_fornecedor.get().strip().upper()

            if fornecedor_valor and fornecedor_valor != "TODOS":

                novos_filtros["fornecedor"] = fornecedor_valor

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

        ).pack(side="left", expand=True, fill="x", padx=(0, 6), pady=4)

        self._criar_botao(

            botoes,

            "Limpar filtros",

            limpar,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

            height=42,

        ).pack(side="left", expand=True, fill="x", padx=6, pady=4)

        self._criar_botao(

            botoes,

            "Fechar",

            modal.destroy,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

            height=42,

        ).pack(side="left", expand=True, fill="x", padx=(6, 0), pady=4)

    def criar_widgets(self):

        if self.scroll_container and self.scroll_container.winfo_exists():

            self.scroll_container.destroy()

        try:
            self.configure(fg_color=BRAND_COLORS['background'])
        except Exception:
            pass

        self.scroll_container = ctk.CTkScrollableFrame(

            self,

            corner_radius=0,

            fg_color=BRAND_COLORS['background'],

        )

        # ajusta cores internas do canvas/scrollbar para evitar faixas pretas
        try:
            canvas = self.scroll_container._parent_canvas  # type: ignore[attr-defined]
            canvas.configure(bg=BRAND_COLORS["background"], highlightthickness=0, bd=0)
            if hasattr(self.scroll_container, "_scrollbar"):
                sb = self.scroll_container._scrollbar  # type: ignore[attr-defined]
                sb.configure(
                    background=BRAND_COLORS["neutral"],
                    troughcolor=BRAND_COLORS["panel"],
                    borderwidth=0,
                    relief="flat",
                    fg_color=BRAND_COLORS["neutral"],
                )
        except Exception:
            pass

        self.scroll_container.pack(fill='both', expand=True, padx=12, pady=12)

        main_frame = ctk.CTkFrame(self.scroll_container, corner_radius=24, fg_color=BRAND_COLORS['surface'])

        # ancorar no topo para evitar área vazia
        main_frame.pack(fill='both', expand=False, padx=12, pady=12, anchor="n")

        header_frame = ctk.CTkFrame(main_frame, fg_color='transparent')

        header_frame.pack(fill='x', pady=(10, 6))

        top_actions = ctk.CTkFrame(header_frame, fg_color='transparent')

        top_actions.pack(fill='x', pady=(0, 12), padx=16)

        ctk.CTkLabel(

            top_actions,

            text=f"Área do cliente — {self.empresa_nome}",

            font=ctk.CTkFont(family=FONT_FAMILY, size=13),

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(side='left', padx=(0, 12))

        self._criar_botao(

            top_actions,

            "Mudar de empresa",

            self._reiniciar_aplicacao,

            fg_color=BRAND_COLORS['neutral'],

            hover_color="#3B3B3B",

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

    
            text='Meu Negócio — Central de Controle',

            font=self.fonts['title'],

            text_color=BRAND_COLORS['text_primary'],

        ).pack()

        ctk.CTkLabel(

            header_frame,

            text='Despesas, Dashboards e Relatórios',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(pady=(4, 8))

        ctk.CTkLabel(

            main_frame,

            text=' ',

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

        categorias_header = ctk.CTkFrame(formulario_frame, fg_color='transparent')

        categorias_header.pack(fill='x', padx=12, pady=(12, 0))

        ctk.CTkLabel(

            categorias_header,

            text='Adicione suas Despesas aqui: ',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(side='left')

        botoes_categoria = ctk.CTkFrame(categorias_header, fg_color='transparent')

        botoes_categoria.pack(side='right')

        self._criar_botao(
            botoes_categoria,
            'Central de cadastros',
            self.abrir_central_cadastros,
            height=36,
            fg_color=BRAND_COLORS['neutral'],
            hover_color="#3B3B3B",
        ).pack(side='right')

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
        self.entry_data.bind("<KeyRelease>", lambda event: self._formatar_data_widget(self.entry_data))

        if not getattr(self, "tipos_despesa", None):
            base = [
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
            self.tipos_despesa = sorted({self._normalizar_categoria(nome) for nome in base})

        def _build_combo_tipo(container: ctk.CTkFrame):
            linha = ctk.CTkFrame(container, fg_color="transparent")
            linha.pack(fill="x")
            combo = ReadOnlyComboBox(
                linha,
                values=self.tipos_despesa,
                height=40,
                font=self.fonts['label'],
                dropdown_font=self.fonts['dropdown'],
            )
            combo.pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                linha,
                text="🔍",
                width=42,
                fg_color=BRAND_COLORS["accent"],
                hover_color=BRAND_COLORS["accent_hover"],
                text_color="#FFFFFF",
                font=self.fonts["button"],
                command=self._abrir_busca_categoria,
            ).pack(side="left", padx=(8, 0))
            return combo

        self.combo_tipo = self._criar_input_group(

            formulario_frame,

            'Tipo de despesa',

            _build_combo_tipo,

        )
        self.combo_tipo.configure(command=self._on_tipo_change)

        self.combo_tipo.set('Selecione o tipo')

        self.formas_pagamento = [
            "E. G. FONSECA — Cresol 104687-0",
            "M X FONSECA CAPELLO — Sicoob 131.309-6",
            "R. G. FONSECA & CIA. LTDA — Cresol 115676-4",
            "R. G. FONSECA & CIA. LTDA — Sicoob 90.569-0",
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
        self.entry_valor.bind("<KeyRelease>", lambda event: self._formatar_valor_widget(self.entry_valor))

        # Controle interno para exibir fornecedor somente quando a categoria exige.
        self.fornecedor_ativo = tk.IntVar(value=0)

        # Seção de fornecedor (visível apenas quando a categoria exige).
        self.fornecedor_fields = ctk.CTkFrame(formulario_frame, fg_color="transparent")
        self.fornecedor_fields.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(
            self.fornecedor_fields,
            text="Fornecedor",
            font=self.fonts["subtitle"],
            text_color=BRAND_COLORS["text_secondary"],
        ).pack(anchor="w", pady=(6, 4))

        fornecedor_row = ctk.CTkFrame(self.fornecedor_fields, fg_color="transparent")
        fornecedor_row.pack(fill="x")

        self.combo_fornecedor = ReadOnlyComboBox(
            fornecedor_row,
            values=self.fornecedores,
            height=38,
            font=self.fonts["label"],
            dropdown_font=self.fonts["dropdown"],
        )
        self.combo_fornecedor.pack(side="left", fill="x", expand=True, pady=(0, 6))
        self.combo_fornecedor.set("Selecione o fornecedor")

        # Botão de busca do fornecedor (visível em ambos os temas).
        ctk.CTkButton(
            fornecedor_row,
            text="🔍",
            width=42,
            fg_color=BRAND_COLORS["accent"],
            hover_color=BRAND_COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=self.fonts["button"],
            command=self._abrir_busca_fornecedor,
        ).pack(side="left", padx=(8, 0), pady=(0, 6))

        self._toggle_fornecedor()

        botoes_frame = ctk.CTkFrame(main_frame, fg_color='transparent')

        botoes_frame.pack(fill='x', padx=12, pady=(0, 16))

        self._criar_botao(

            botoes_frame,

            'Registrar despesa',

            self.salvar_despesa,

            fg_color=BRAND_COLORS['success'],

            hover_color='#17A589',

        ).pack(side='left', expand=True, fill='x', padx=(0, 8))

        self._criar_botao(

            botoes_frame,

            'Limpar formulário',

            self.limpar_campos,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#3B3B3B',

        ).pack(side='left', expand=True, fill='x', padx=8)

        self._criar_botao(

            botoes_frame,

            'Gerenciar despesas',

            self.abrir_gestao_gastos,

        ).pack(side='left', expand=True, fill='x', padx=(8, 0))

        resumo_titulo = ctk.CTkLabel(

            main_frame,

            text='Central de Resumo e Relatórios',

            font=self.fonts['section'],

            text_color=BRAND_COLORS['text_primary'],

        )

        resumo_titulo.pack(anchor='w', padx=12, pady=(0, 8))

        cards_container = ctk.CTkFrame(main_frame, fg_color='transparent')

        cards_container.pack(fill='x', padx=4, pady=(0, 10))

        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_columnconfigure(2, weight=0)

        self.total_card_value = self._criar_card_resumo(

            cards_container,

            'Valor total registrado',

            'R$ 0,00',

            0,

        )

        self.quantidade_card_value = self._criar_card_resumo(
            cards_container,
            'Total de Despesas Lançadas',
            '0 registros',
            1,
            extra_widget=lambda parent: self._criar_botao(
                parent,
                'Filtro',
                self.abrir_modal_filtro_resumo,
                fg_color=BRAND_COLORS['neutral'],
                hover_color='#3B3B3B',
                height=28,
            ),
        )

        botoes_relatorios = ctk.CTkFrame(main_frame, fg_color='transparent')

        botoes_relatorios.pack(fill='x', padx=12, pady=(4, 18))

        self._criar_botao(

            botoes_relatorios,

            'Histórico completo de Depesas',

            self.mostrar_relatorio,

            fg_color=BRAND_COLORS['neutral'],

            hover_color='#4B4B4B',

        ).pack(side='left', expand=True, fill='x', padx=8)

        self._criar_botao(

            botoes_relatorios,

            'Dashboard',

            self.abrir_dashboard_executivo,

            fg_color=BRAND_COLORS['neutral'],

            hover_color="#4B4B4B",

        ).pack(side='left', expand=True, fill='x', padx=8)

        self._criar_botao(

            botoes_relatorios,

            'Exportar relatórios',

            self.abrir_modal_exportar_relatorio,

        ).pack(side='left', expand=True, fill='x', padx=(8, 0))


        ctk.CTkLabel(

            main_frame,

            text='Desenvolvido pelo Departamento de Tecnologia - GRUPO 14D - 2025',

            font=ctk.CTkFont(family=FONT_FAMILY, size=11),

            text_color=BRAND_COLORS['text_secondary'],

        ).pack(pady=(8, 0))

        # atualiza cards/resumo ao finalizar criacao

        self.atualizar_stats()

    def abrir_modal_filtro_resumo(self):

        self._abrir_modal_filtros(

            "Filtros do resumo executivo",

            self.resumo_filtros,

            self._aplicar_filtros_resumo,

        )

    def _aplicar_filtros_resumo(self, filtros: dict[str, str] | None):

        self.resumo_filtros = filtros

        self.atualizar_stats()

    def abrir_dashboard_executivo(self):
        try:
            abrir_dashboard(self, Path(self.arquivo_dados))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível exibir o painel:\n{exc}")

    def abrir_modal_filtro_relatorio(self):

        if not self.relatorio_window or not self.relatorio_window.winfo_exists():

            messagebox.showinfo("Informa??o", "Abra o relatorio completo antes de aplicar filtros.")

            return

        self._abrir_modal_filtros(

            "Filtros do relatorio completo",

            self.relatorio_filtros,

            self._aplicar_filtros_relatorio,

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

        frame.grid_columnconfigure(0, weight=0, minsize=90)
        frame.grid_columnconfigure(1, weight=2, minsize=220)
        frame.grid_columnconfigure(2, weight=1, minsize=140)
        frame.grid_columnconfigure(3, weight=0, minsize=90)
        frame.grid_columnconfigure(4, weight=2, minsize=220)

        if not registros_ordenados:

            ctk.CTkLabel(

                frame,

                text="Nenhum lançamento corresponde aos filtros selecionados.",

                font=self.fonts["label"],

                text_color=BRAND_COLORS["text_secondary"],

            ).pack(pady=20)

            return

        header_font = self.fonts["subtitle"]

        headers = ["Data", "Tipo de despesa", "Forma de pagamento", "Valor", "Fornecedor"]

        for col, header_text in enumerate(headers):

            sticky = "e" if col == 3 else "w"

            ctk.CTkLabel(

                frame,

                text=header_text,

                font=header_font,

                text_color=BRAND_COLORS["text_secondary"],

            ).grid(row=0, column=col, padx=10, pady=(5, 6), sticky=sticky)

        separator = ctk.CTkFrame(frame, height=2, fg_color=BRAND_COLORS["neutral"])

        separator.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5, pady=(0, 8))

        row_font = self.fonts["label"]

        for i, gasto in enumerate(registros_ordenados, start=2):

            data_label = ctk.CTkLabel(frame, text=gasto.get("data", "--"), font=row_font)

            tipo_label = ctk.CTkLabel(
                frame,
                text=gasto.get("tipo", "--"),
                font=row_font,
                anchor="w",
                justify="left",
                wraplength=300,
            )

            forma_label = ctk.CTkLabel(frame, text=gasto.get("forma_pagamento", "--"), font=row_font)

            valor_label = ctk.CTkLabel(

                frame,

                text=format_brl(gasto.get("valor", 0.0)),

                font=row_font,

                text_color=BRAND_COLORS["text_primary"],

            )
            fornecedor_label = ctk.CTkLabel(
                frame,
                text=gasto.get("fornecedor", "--") or "--",
                font=row_font,
                anchor="w",
                justify="left",
                wraplength=260,
            )

            data_label.grid(row=i, column=0, padx=10, pady=6, sticky="w")

            tipo_label.grid(row=i, column=1, padx=10, pady=6, sticky="w")

            forma_label.grid(row=i, column=2, padx=10, pady=6, sticky="w")

            valor_label.grid(row=i, column=3, padx=10, pady=6, sticky="e")
            fornecedor_label.grid(row=i, column=4, padx=10, pady=6, sticky="w")

            row_separator = ctk.CTkFrame(frame, height=1, fg_color=BRAND_COLORS["neutral"])

            row_separator.grid(row=i + 1, column=0, columnspan=5, sticky="ew", padx=10)

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

        empresa_atual = {
            "arquivo_dados": self.arquivo_dados,
            "empresa_nome": self.empresa_nome,
            "empresa_id": self.empresa_id,
            "empresa_razao": self.empresa_razao,
        }

        # encerra antes de abrir novo seletor para evitar múltiplas instâncias do Tk
        self.destroy()

        info = selecionar_empresa()

        if not info:
            retorno = ControleGastosApp(
                arquivo_dados=empresa_atual["arquivo_dados"],
                empresa_nome=empresa_atual["empresa_nome"],
                empresa_id=empresa_atual["empresa_id"],
                empresa_razao=empresa_atual["empresa_razao"],
            )
            retorno.mainloop()
            return

        novo_app = ControleGastosApp(

            arquivo_dados=info.get("arquivo"),

            empresa_nome=info.get("empresa_nome"),

            empresa_id=info.get("empresa_id"),

            empresa_razao=info.get("empresa_razao"),

        )

        novo_app.mainloop()
    def salvar_despesa(self):

        data = (self.entry_data.get() or "").strip()

        tipo_raw = (self.combo_tipo.get() or "").strip()
        tipo = self._normalizar_categoria(tipo_raw)

        pagamento = self.combo_pagamento.get()

        valor_str = (self.entry_valor.get() or "").strip()

        if not validar_data(data):

            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")

            return

        if not tipo_raw or tipo_raw == "Selecione o tipo":

            messagebox.showerror("Erro", "Selecione um tipo de despesa!")

            return

        if pagamento == "Selecione a forma":

            messagebox.showerror("Erro", "Selecione uma forma de pagamento!")

            return

        valor = validar_valor(valor_str)

        if valor is None:

            messagebox.showerror("Erro", "Valor inválido! Digite um número maior que zero.")

            return

        fornecedor = ""
        if getattr(self, "fornecedor_ativo", tk.IntVar(value=0)).get():
            fornecedor = self._normalizar_fornecedor(self.combo_fornecedor.get())

        registro = {
            "data": data,
            "tipo": tipo,
            "forma_pagamento": pagamento,
            "valor": valor,
            "fornecedor": fornecedor or None,
            "timestamp": datetime.now().isoformat(),
        }

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

        if getattr(self, "fornecedor_ativo", None) is not None:
            self.fornecedor_ativo.set(0)
            self.combo_fornecedor.set("Selecione o fornecedor")
            try:
                self._toggle_fornecedor()
            except Exception:
                pass

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

        self.janela_gestao.title('Captacao de Despesas-14D - Gestão de Despesas')

        self.janela_gestao.geometry('940x620')

        self.janela_gestao.resizable(True, True)

        self.janela_gestao.minsize(760, 520)

        self.janela_gestao.configure(fg_color=BRAND_COLORS['surface'])

        # Garantir que a janela fique em primeiro plano ao abrir
        try:
            self.janela_gestao.transient(self)
            self.janela_gestao.grab_set()
            self.janela_gestao.lift()
            self.janela_gestao.focus_force()
            self.janela_gestao.attributes("-topmost", True)
            self.janela_gestao.after(400, lambda: self.janela_gestao.attributes("-topmost", False))
        except Exception:
            pass

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

        for coluna in range(5):

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
        self.filtro_data_inicio_entry.bind("<KeyRelease>", lambda event: self._formatar_data_widget(self.filtro_data_inicio_entry))

        self.filtro_data_fim_entry = ctk.CTkEntry(filtros_frame, height=36, font=self.fonts['label'])

        self.filtro_data_fim_entry.grid(row=1, column=1, padx=12, pady=(0, 10), sticky='ew')
        self.filtro_data_fim_entry.bind("<KeyRelease>", lambda event: self._formatar_data_widget(self.filtro_data_fim_entry))

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

            text='Fornecedor',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=0, column=4, sticky='w', padx=12, pady=(12, 2))

        fornecedores_filtro = ['Todos'] + self.fornecedores

        self.filtro_fornecedor_combo = ReadOnlyComboBox(

            filtros_frame, values=fornecedores_filtro, height=36, font=self.fonts['label'], dropdown_font=self.fonts['dropdown']

        )

        self.filtro_fornecedor_combo.set('Todos')

        self.filtro_fornecedor_combo.grid(row=1, column=4, padx=12, pady=(0, 10), sticky='ew')

        ctk.CTkLabel(

            filtros_frame,

            text='Valor',

            font=self.fonts['subtitle'],

            text_color=BRAND_COLORS['text_secondary'],

        ).grid(row=2, column=0, columnspan=5, sticky='w', padx=12, pady=(6, 2))

        self.filtro_valor_combo = ReadOnlyComboBox(

            filtros_frame,

            values=['Todos', 'Até 100', '100 a 500', '500 a 1000', 'Acima de 1000'],

            height=36,

            font=self.fonts['label'],

            dropdown_font=self.fonts['dropdown'],

        )

        self.filtro_valor_combo.set('Todos')

        self.filtro_valor_combo.grid(row=3, column=0, columnspan=5, padx=12, pady=(0, 10), sticky='ew')

        botoes_filtro = ctk.CTkFrame(filtros_frame, fg_color='transparent')

        botoes_filtro.grid(row=4, column=0, columnspan=5, pady=(0, 12), sticky='ew')

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

            hover_color=BRAND_COLORS['accent_hover'],

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

            fornecedor_nome = gasto.get("fornecedor") or ""
            if fornecedor_nome:
                ctk.CTkLabel(
                    detalhes,
                    text=f"Fornecedor: {fornecedor_nome}",
                    font=self.fonts["subtitle"],
                    text_color=BRAND_COLORS["text_secondary"],
                ).grid(row=2, column=0, sticky="w", pady=(2, 0))

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

        fornecedor_filtro = self.filtro_fornecedor_combo.get() if getattr(self, "filtro_fornecedor_combo", None) else "Todos"

        if fornecedor_filtro and fornecedor_filtro != "Todos":

            filtros_basicos["fornecedor"] = fornecedor_filtro

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
        entry_data.bind("<KeyRelease>", lambda event, w=entry_data: self._formatar_data_widget(w))

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
        entry_valor.bind("<KeyRelease>", lambda event, w=entry_valor: self._formatar_valor_widget(w))
        self._formatar_valor_widget(entry_valor)

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

            hover_color="#3B3B3B",

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

            messagebox.showinfo("Informação", "Nenhum lançamento registrado ainda.")

            return

        if self.relatorio_window and self.relatorio_window.winfo_exists():

            self.relatorio_window.focus_force()

            self._renderizar_relatorio_detalhado()

            return

        self.relatorio_window = ctk.CTkToplevel(self)

        self.relatorio_window.title("Centro de relatórios - Grupo 14D")

        self.relatorio_window.geometry("1050x720")

        self.relatorio_window.resizable(True, True)

        self.relatorio_window.minsize(780, 560)

        self.relatorio_window.configure(fg_color=BRAND_COLORS["surface"])

        self.relatorio_window.transient(self)

        self.relatorio_window.grab_set()

        self._priorizar_janela(self.relatorio_window)

        ctk.CTkLabel(

            self.relatorio_window,

            text="Centro de relatórios",

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

            hover_color="#3B3B3B",

            height=38,

        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(

            acoes_frame,

            "Limpar filtros",

            lambda: self._aplicar_filtros_relatorio(None),

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

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

            "Voltar ao painel",

            self._fechar_relatorio_window,

            fg_color=BRAND_COLORS["neutral"],

            hover_color="#3B3B3B",

            height=40,

        ).pack(side="left", padx=(8, 0))

        self.relatorio_window.protocol("WM_DELETE_WINDOW", self._fechar_relatorio_window)

        self._renderizar_relatorio_detalhado()


    def exportar_relatorio_pdf(self, registros: Iterable[dict[str, Any]] | None = None):

        registros_validos = self._obter_registros_exportacao(registros)
        if registros_validos is None:
            return

        destino_dir = filedialog.askdirectory(title="Escolha a pasta para salvar o PDF")
        if not destino_dir:
            return
        destino_dir_path = Path(destino_dir)
        destino_dir_path.mkdir(parents=True, exist_ok=True)

        nome_arquivo = f"Relatorio_{self.empresa_slug}.pdf"
        caminho_destino = destino_dir_path / nome_arquivo

        try:
            logo_param = str(self.logo_path) if self.logo_path and self.logo_path.exists() else None
            company_label = f"{self.empresa_razao} - Captacao de Despesas-14D"
            caminho = generate_pdf_report(
                registros_validos,
                str(caminho_destino),
                company_name=company_label,
                logo_path=logo_param,
            )
        except RuntimeError as exc:
            messagebox.showerror(
                "Erro ao gerar PDF",
                f"{exc}\n\nInstale a dependencia e tente novamente.",
            )
            return
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro ao gerar PDF", f"Ocorreu um erro inesperado:\n{exc}")
            return

        messagebox.showinfo(
            "Relatório criado",
            f"Relatório em PDF criado em:\n{caminho}",
        )

    def _obter_registros_exportacao(self, registros: Iterable[dict[str, Any]] | None = None) -> list[dict[str, Any]] | None:
        registros_validos: list[dict[str, Any]] = []
        if registros is not None:
            registros_validos = list(registros)
        elif isinstance(self.gastos, list):
            registros_validos = list(self.gastos)
        if not registros_validos:
            messagebox.showinfo("Informação", "Nenhum lançamento disponível para exportação.")
            return None
        return registros_validos

    def exportar_relatorio_csv(self, registros: Iterable[dict[str, Any]] | None = None):
        registros_validos = self._obter_registros_exportacao(registros)
        if registros_validos is None:
            return
        destino_dir = filedialog.askdirectory(title="Escolha a pasta para salvar o CSV")
        if not destino_dir:
            return
        destino_dir_path = Path(destino_dir)
        destino_dir_path.mkdir(parents=True, exist_ok=True)
        nome_arquivo = f"CSV - GRUPO14D - {self.empresa_slug}.csv"
        caminho_destino = destino_dir_path / nome_arquivo
        try:
            import csv
            with open(caminho_destino, "w", encoding="utf-8", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter=";")
                writer.writerow(["Data", "Tipo", "Forma", "Valor", "Fornecedor"])
                for gasto in registros_validos:
                    fornecedor_bruto = gasto.get("fornecedor")
                    fornecedor_csv = (
                        fornecedor_bruto if isinstance(fornecedor_bruto, str) else ""
                    )
                    fornecedor_csv = fornecedor_csv.strip().upper() if fornecedor_csv else ""
                    writer.writerow([
                        gasto.get("data", ""),
                        gasto.get("tipo", ""),
                        gasto.get("forma_pagamento", ""),
                        f"{float(gasto.get('valor', 0) or 0):.2f}".replace(".", ","),
                        fornecedor_csv,
                    ])
            messagebox.showinfo("Relatório criado", f"Arquivo CSV criado em: {caminho_destino}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível gerar o arquivo CSV: {exc}")

    def abrir_modal_exportar_relatorio(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Exportar relatório")
        modal.geometry("520x380")
        modal.resizable(False, False)
        modal.configure(fg_color=BRAND_COLORS["surface"])
        modal.transient(self)
        modal.grab_set()
        self._priorizar_janela(modal)
        self._centralizar_janela(modal)

        frame = ctk.CTkFrame(modal, fg_color=BRAND_COLORS["panel"], corner_radius=14, border_color=BRAND_COLORS["neutral"], border_width=1)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            frame,
            text="Selecione período e formato para exportar",
            font=self.fonts["section"],
            text_color=BRAND_COLORS["text_primary"],
        ).pack(pady=(12, 6))

        ctk.CTkLabel(
            frame,
            text="O relatório respeita os filtros atuais e o período informado.",
            font=self.fonts["subtitle"],
            text_color=BRAND_COLORS["text_secondary"],
        ).pack(pady=(0, 12))

        # Pré-preenche intervalo com menor/maior data dos lançamentos atuais
        registros_base = self._obter_registros_exportacao(self.gastos)
        if registros_base is None:
            modal.destroy()
            return
        datas_validas = []
        for reg in registros_base:
            dt = self._parse_data_str(reg.get("data"))
            if dt:
                datas_validas.append(dt)
        data_min = min(datas_validas).strftime("%d/%m/%Y") if datas_validas else ""
        data_max = max(datas_validas).strftime("%d/%m/%Y") if datas_validas else ""

        ctk.CTkLabel(frame, text="Data Início (DD/MM/AAAA)", font=self.fonts["subtitle"], text_color=BRAND_COLORS["text_secondary"]).pack(anchor="w", padx=12, pady=(4, 2))
        entry_inicio = ctk.CTkEntry(frame, height=36, font=self.fonts["label"])
        entry_inicio.pack(fill="x", padx=12)
        entry_inicio.insert(0, data_min)
        entry_inicio.bind("<KeyRelease>", lambda event, w=entry_inicio: self._formatar_data_widget(w))

        ctk.CTkLabel(frame, text="Data Fim (DD/MM/AAAA)", font=self.fonts["subtitle"], text_color=BRAND_COLORS["text_secondary"]).pack(anchor="w", padx=12, pady=(8, 2))
        entry_fim = ctk.CTkEntry(frame, height=36, font=self.fonts["label"])
        entry_fim.pack(fill="x", padx=12)
        entry_fim.insert(0, data_max)
        entry_fim.bind("<KeyRelease>", lambda event, w=entry_fim: self._formatar_data_widget(w))

        ctk.CTkLabel(frame, text="Formato", font=self.fonts["subtitle"], text_color=BRAND_COLORS["text_secondary"]).pack(anchor="w", padx=12, pady=(10, 2))
        formato_var = tk.StringVar(value="pdf")
        formatos_frame = ctk.CTkFrame(frame, fg_color="transparent")
        formatos_frame.pack(fill="x", padx=12, pady=(0, 8))
        for label, val in (("PDF", "pdf"), ("CSV - GRUPO14D", "csv")):
            ctk.CTkRadioButton(formatos_frame, text=label, variable=formato_var, value=val, font=self.fonts["label"]).pack(side="left", padx=(0, 12))

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.pack(fill="x", padx=12, pady=(12, 8))

        def aplicar_exportacao():
            inicio_val = entry_inicio.get().strip()
            fim_val = entry_fim.get().strip()
            if not inicio_val or not fim_val:
                messagebox.showerror("Erro", "Informe data inicial e final para exportar.")
                return
            if not validar_data(inicio_val):
                messagebox.showerror("Erro", "Data inicial inválida. Use o formato DD/MM/AAAA.")
                return
            if not validar_data(fim_val):
                messagebox.showerror("Erro", "Data final inválida. Use o formato DD/MM/AAAA.")
                return
            dt_inicio = self._parse_data_str(inicio_val)
            dt_fim = self._parse_data_str(fim_val)
            if dt_inicio and dt_fim and dt_inicio > dt_fim:
                messagebox.showerror("Erro", "A data inicial não pode ser posterior à data final.")
                return

            filtros_periodo = {"data_inicio": inicio_val, "data_fim": fim_val}
            registros_periodo = self._filtrar_registros(self.gastos, filtros_periodo)
            if not registros_periodo:
                messagebox.showinfo("Aviso", "Nenhum registro no período informado.")
                return

            if formato_var.get() == "pdf":
                self.exportar_relatorio_pdf(registros_periodo)
            else:
                self.exportar_relatorio_csv(registros_periodo)
            modal.destroy()

        self._criar_botao(
            botoes,
            "Exportar",
            aplicar_exportacao,
            height=38,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._criar_botao(
            botoes,
            "Cancelar",
            modal.destroy,
            fg_color=BRAND_COLORS["neutral"],
            hover_color="#3B3B3B",
            height=38,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))


def main(theme_mode: str | None = None, config_path: str | None = None):
    """Ponto de entrada da UI: abre seletor e instancia a aplicação."""
    from app.ui.empresa_selector import selecionar_empresa

    empresa_info = selecionar_empresa()
    if not empresa_info:
        return

    app = ControleGastosApp(
        arquivo_dados=empresa_info.get("arquivo"),
        empresa_nome=empresa_info.get("empresa_nome"),
        empresa_id=empresa_info.get("empresa_id"),
        empresa_razao=empresa_info.get("empresa_razao"),
        theme_mode=theme_mode or "dark",
        config_path=config_path,
    )
    app.mainloop()








