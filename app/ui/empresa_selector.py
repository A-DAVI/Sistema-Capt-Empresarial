# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from pathlib import Path

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from app.ui.widgets import ReadOnlyComboBox
from app.utils.paths import runtime_path, workspace_path
import json


DARK_COLORS = {
    "background": "#0B0B0B",
    "surface": "#121212",
    "panel": "#1A1A1A",
    "accent": "#007BFF",
    "accent_hover": "#0056B3",
    "neutral": "#1F1F1F",
    "text_primary": "#FFFFFF",
    "text_secondary": "#CCCCCC",
}

LIGHT_COLORS = {
    "background": "#F5F7FA",
    "surface": "#FFFFFF",
    "panel": "#F0F2F5",
    "accent": "#0D6EFD",
    "accent_hover": "#0B5ED7",
    "neutral": "#E5E7EB",
    "text_primary": "#111827",
    "text_secondary": "#4B5563",
}
BRAND_COLORS = DARK_COLORS.copy()
FONT_FAMILY = "Segoe UI"

EMPRESAS_PRE_CONFIGURADAS = [
    {
        "id": "MERCEARIA BELLA VISTA",
        "razao_social": "E. G. FONSECA",
        "nome_fantasia": "MERCEARIA BELLA VISTA",
    },
    {
        "id": "SUPERPAO",
        "razao_social": "R. G. FONSECA & CIA. LTDA",
        "nome_fantasia": "SUPERPAO",
    },
    {
        "id": "SP FOODS",
        "razao_social": "M X FONSECA CAPELLO",
        "nome_fantasia": "SP FOODS",
    },
]

logger = logging.getLogger("app.empresa_selector")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class EmpresaSelector(ctk.CTk):
    """Tela inicial responsável por escolher a empresa ativa do sistema."""

    def __init__(self) -> None:
        super().__init__()

        self._aplicar_tema_preferido()
        self.title("Painel Financeiro - Selecione sua empresa")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(fg_color=BRAND_COLORS["background"])
        self._centralizar_janela(self)

        self.data_dir = workspace_path("app", "data")
        workspace_logo = workspace_path("logo_empresa.png")
        runtime_logo = runtime_path("logo_empresa.png")
        self.logo_path = workspace_logo if workspace_logo.exists() else runtime_logo

        self.logo_image = self._carregar_logo(self.logo_path)
        self.selected_info: dict[str, str] | None = None

        self.empresas = EMPRESAS_PRE_CONFIGURADAS.copy()
        self.empresas_map = {item["nome_fantasia"]: item for item in self.empresas}

        self._construir_layout()
        self._priorizar()
        self._centralizar_janela(self)

    def _aplicar_tema_preferido(self) -> None:
        tema = "dark"
        try:
            cfg_path = workspace_path("config.json")
            if cfg_path.exists():
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                tema = str(data.get("tema", "dark")).lower()
        except Exception:
            tema = "dark"

        if tema not in ("dark", "light"):
            tema = "dark"

        palette = DARK_COLORS if tema == "dark" else LIGHT_COLORS
        BRAND_COLORS.clear()
        BRAND_COLORS.update(palette)
        try:
            ctk.set_appearance_mode("dark" if tema == "dark" else "light")
        except Exception:
            pass

    def _priorizar(self) -> None:
        try:
            self.lift()
            self.focus_force()
            self.attributes("-topmost", True)
            self.after(250, lambda: self.attributes("-topmost", False))
        except Exception:
            pass
        self._centralizar_janela(self)

    def _centralizar_janela(self, win):
        """Centraliza a janela passada (root ou modal)."""
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

    def _construir_layout(self) -> None:
        container = ctk.CTkFrame(
            self,
            corner_radius=24,
            fg_color=BRAND_COLORS["surface"],
        )
        container.pack(fill="both", expand=True, padx=24, pady=24)

        if self.logo_image:
            logo_wrapper = ctk.CTkFrame(
                container,
                fg_color="#FFFFFF",
                corner_radius=18,
            )
            logo_wrapper.pack(pady=(10, 6))
            ctk.CTkLabel(logo_wrapper, image=self.logo_image, text="").pack(padx=20, pady=12)

        ctk.CTkLabel(
            container,
            text="Painel Financeiro — Grupo 14D",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=BRAND_COLORS["text_primary"],
        ).pack(pady=(6, 2))

        ctk.CTkLabel(
            container,
            text="Selecione sua empresa para acessar o painel",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=BRAND_COLORS["text_secondary"],
        ).pack(pady=(0, 18))

        self.combo_empresas = ReadOnlyComboBox(
            container,
            values=list(self.empresas_map.keys()),
            height=42,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        )
        self.combo_empresas.pack(fill="x", padx=40, pady=(0, 20))
        if self.empresas:
            self.combo_empresas.set(self.empresas[0]["nome_fantasia"])

        botoes = ctk.CTkFrame(container, fg_color="transparent")
        botoes.pack(fill="x", padx=40, pady=(10, 0))

        ctk.CTkButton(
            botoes,
            text="Acessar painel",
            command=self._entrar,
            height=44,
            corner_radius=12,
            fg_color=BRAND_COLORS["accent"],
            hover_color=BRAND_COLORS["accent_hover"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            botoes,
            text="Voltar",
            command=self._cancelar,
            height=40,
            corner_radius=12,
            fg_color="#E1E3E8",
            hover_color="#C5C9D0",
            text_color=BRAND_COLORS["text_primary"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
        ).pack(fill="x")

    def _carregar_logo(self, caminho: Path, max_size: tuple[int, int] = (220, 90)) -> ctk.CTkImage | None:
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
        return ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(nova_largura, nova_altura))

    def _entrar(self) -> None:
        nome_display = self.combo_empresas.get().strip()
        empresa_info = self.empresas_map.get(nome_display)
        if not empresa_info:
            messagebox.showerror("Seleção necessária", "Escolha uma de suas empresas para continuar.")
            return

        empresa_id = empresa_info['id']
        arquivo = self.data_dir / f'{empresa_id}.json'
        try:
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            if not arquivo.exists():
                arquivo.write_text("[]", encoding="utf-8")
                logger.info("Arquivo de empresa criado: %s", arquivo)
        except Exception as exc:
            logger.error("Falha ao preparar arquivo da empresa %s: %s", empresa_id, exc)
            messagebox.showerror("Erro", "Não foi possível preparar os dados da empresa selecionada.")
            return

        self.selected_info = {
            "arquivo": str(arquivo),
            "empresa_id": empresa_id,
            "empresa_nome": nome_display,
            "empresa_razao": empresa_info.get("razao_social", nome_display),
        }
        logger.info("Empresa selecionada: %s (%s)", nome_display, arquivo)
        self.destroy()

    def _cancelar(self) -> None:
        logger.info("Seleção de empresa cancelada pelo usuário.")
        self.selected_info = None
        self.destroy()


def selecionar_empresa() -> dict[str, str] | None:
    selector = EmpresaSelector()
    selector.mainloop()
    if selector.selected_info:
        return selector.selected_info
    return None
