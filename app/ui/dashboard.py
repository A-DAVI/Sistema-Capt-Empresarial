"""Dashboard executivo de despesas com gráficos e KPIs.

Este módulo abre um CTkToplevel com três KPIs e três gráficos
usando Matplotlib embutido no Tkinter.

API pública:
    abrir_dashboard(parent, empresa_path: Path)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict, OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Paleta simples alinhada ao restante do app
BRAND_COLORS = {
    "background": "#0B0B0B",
    "surface": "#1A1A1A",
    "panel": "#111111",
    "accent": "#0D6EFD",
    "accent_muted": "#1F6FEB",
    "text_primary": "#FFFFFF",
    "text_secondary": "#C7CCD4",
    "divider": "#2C2F36",
    "success": "#22C55E",
    "danger": "#F87171",
}


def _ler_despesas(empresa_path: Path) -> list[dict]:
    try:
        raw = Path(empresa_path).read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []


def _parse_data(reg: dict) -> datetime | None:
    valor = reg.get("data") or ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, fmt)
        except Exception:
            continue
    return None


def _agrupa_por_mes(despesas: Iterable[dict]) -> OrderedDict[str, float]:
    soma = defaultdict(float)
    for reg in despesas:
        dt = _parse_data(reg)
        if not dt:
            continue
        chave = dt.strftime("%Y-%m")
        try:
            soma[chave] += float(reg.get("valor", 0) or 0)
        except Exception:
            continue
    # ordenar cronologicamente
    ordenado = OrderedDict(sorted(soma.items()))
    return ordenado


def _ultimos_meses(dados: OrderedDict[str, float], limite: int = 6) -> OrderedDict[str, float]:
    if len(dados) <= limite:
        return dados
    items = list(dados.items())[-limite:]
    return OrderedDict(items)


def _total_por_categoria(despesas: Iterable[dict], mes_ano: str | None = None) -> dict[str, float]:
    tot = defaultdict(float)
    for reg in despesas:
        dt = _parse_data(reg)
        if not dt:
            continue
        if mes_ano and dt.strftime("%Y-%m") != mes_ano:
            continue
        cat = str(reg.get("tipo") or reg.get("categoria") or "Sem categoria")
        try:
            tot[cat] += float(reg.get("valor", 0) or 0)
        except Exception:
            continue
    return dict(tot)


def _kpis(despesas: list[dict]) -> dict[str, str]:
    agrupado = _agrupa_por_mes(despesas)
    meses = list(agrupado.keys())
    atual_chave = meses[-1] if meses else None
    anterior_chave = meses[-2] if len(meses) > 1 else None

    atual_total = agrupado.get(atual_chave, 0.0)
    anterior_total = agrupado.get(anterior_chave, 0.0)
    variacao = 0.0
    if anterior_total:
        variacao = ((atual_total - anterior_total) / anterior_total) * 100

    cat_mes = _total_por_categoria(despesas, atual_chave) if atual_chave else {}
    maior_categoria = max(cat_mes.items(), key=lambda x: x[1])[0] if cat_mes else "N/A"

    def fmt_moeda(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_mes(chave: str | None) -> str:
        if not chave:
            return "—"
        dt = datetime.strptime(chave, "%Y-%m")
        return dt.strftime("%b/%Y")

    return {
        "mes_atual_label": fmt_mes(atual_chave),
        "mes_anterior_label": fmt_mes(anterior_chave),
        "total_mes_atual": fmt_moeda(atual_total),
        "total_mes_anterior": fmt_moeda(anterior_total),
        "variacao": f"{variacao:+.1f}%",
        "variacao_up": variacao >= 0,
        "maior_categoria": maior_categoria,
    }


def _center(win: ctk.CTkToplevel | ctk.CTk, w: int = 1100, h: int = 720) -> None:
    try:
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = max(0, int((sw - w) / 2))
        y = max(0, int((sh - h) / 2))
        win.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass


def _criar_kpi(parent, titulo: str, valor: str, subtitulo: str | None = None, *, cor_valor: str | None = None):
    frame = ctk.CTkFrame(
        parent,
        fg_color=BRAND_COLORS["panel"],
        corner_radius=14,
        border_color=BRAND_COLORS["divider"],
        border_width=1,
    )
    frame.pack(side="left", expand=True, fill="both", padx=6, pady=6)
    ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_COLORS["text_secondary"]).pack(
        anchor="w", padx=12, pady=(10, 4)
    )
    ctk.CTkLabel(
        frame,
        text=valor,
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=cor_valor or BRAND_COLORS["text_primary"],
    ).pack(anchor="w", padx=12)
    if subtitulo:
        ctk.CTkLabel(
            frame,
            text=subtitulo,
            font=ctk.CTkFont(size=12),
            text_color=BRAND_COLORS["text_secondary"],
        ).pack(anchor="w", padx=12, pady=(0, 10))
    return frame


def _plot_barras(ax, dados: OrderedDict[str, float]):
    if not dados:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color="gray")
        ax.axis("off")
        return
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b/%y") for k in dados.keys()]
    valores = list(dados.values())
    ax.bar(labels, valores, color=BRAND_COLORS["accent"])
    ax.set_title("Gastos por mês", color="white")
    ax.tick_params(axis="x", rotation=20, colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.spines[:].set_color("#444444")


def _plot_pizza(ax, categorias: dict[str, float]):
    if not categorias:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color="gray")
        ax.axis("off")
        return
    labels = list(categorias.keys())
    valores = list(categorias.values())
    ax.pie(valores, labels=labels, autopct="%1.1f%%", textprops={"color": "white"})
    ax.set_title("Distribuição por categoria", color="white")


def _plot_linha(ax, dados: OrderedDict[str, float]):
    if not dados:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color="gray")
        ax.axis("off")
        return
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b/%y") for k in dados.keys()]
    valores = list(dados.values())
    acumulado = []
    soma = 0.0
    for v in valores:
        soma += v
        acumulado.append(soma)
    ax.plot(labels, acumulado, marker="o", color=BRAND_COLORS["accent_muted"], linewidth=2)
    ax.fill_between(range(len(acumulado)), acumulado, color=BRAND_COLORS["accent"], alpha=0.2)
    ax.set_title("Evolução acumulada", color="white")
    ax.tick_params(axis="x", rotation=20, colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.spines[:].set_color("#444444")


def _criar_figuras(frame_plots, dados_mes, categorias_mes, linha_total):
    fig = Figure(figsize=(11, 5), dpi=100, facecolor=BRAND_COLORS["surface"])
    ax1 = fig.add_subplot(1, 3, 1, facecolor=BRAND_COLORS["panel"])
    ax2 = fig.add_subplot(1, 3, 2, facecolor=BRAND_COLORS["panel"])
    ax3 = fig.add_subplot(1, 3, 3, facecolor=BRAND_COLORS["panel"])

    _plot_barras(ax1, dados_mes)
    _plot_pizza(ax2, categorias_mes)
    _plot_linha(ax3, linha_total)

    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(fill="both", expand=True)
    return canvas


def abrir_dashboard(parent, empresa_path: Path):
    """Abre o dashboard executivo para a empresa indicada."""
    despesas = _ler_despesas(empresa_path)

    janela = ctk.CTkToplevel(parent)
    janela.title("Dashboard Executivo")
    janela.configure(fg_color=BRAND_COLORS["background"])
    _center(janela)
    janela.grab_set()
    janela.transient(parent)

    # Cabeçalho
    header = ctk.CTkFrame(janela, fg_color="transparent")
    header.pack(fill="x", padx=16, pady=(12, 8))
    ctk.CTkLabel(
        header,
        text=f"Dashboard Executivo - {Path(empresa_path).stem}",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=BRAND_COLORS["text_primary"],
    ).pack(anchor="w")
    ctk.CTkLabel(
        header,
        text="Visão dos últimos meses com KPIs e gráficos consolidados.",
        font=ctk.CTkFont(size=13),
        text_color=BRAND_COLORS["text_secondary"],
    ).pack(anchor="w", pady=(2, 0))

    # KPIs
    kpi_data = _kpis(despesas)
    kpi_wrap = ctk.CTkFrame(janela, fg_color="transparent")
    kpi_wrap.pack(fill="x", padx=12)

    _criar_kpi(
        kpi_wrap,
        f"Total {kpi_data['mes_atual_label']}",
        kpi_data["total_mes_atual"],
    )
    _criar_kpi(
        kpi_wrap,
        f"Total {kpi_data['mes_anterior_label']}",
        kpi_data["total_mes_anterior"],
    )
    _criar_kpi(
        kpi_wrap,
        "Variação vs mês anterior",
        kpi_data["variacao"],
        cor_valor=BRAND_COLORS["success"] if kpi_data["variacao_up"] else BRAND_COLORS["danger"],
    )
    _criar_kpi(
        kpi_wrap,
        "Maior categoria (mês atual)",
        kpi_data["maior_categoria"],
    )

    # Plots
    plots_frame = ctk.CTkFrame(janela, fg_color=BRAND_COLORS["surface"], corner_radius=18)
    plots_frame.pack(fill="both", expand=True, padx=12, pady=12)

    dados_mes = _ultimos_meses(_agrupa_por_mes(despesas), limite=6)
    categorias_mes_atual = {}
    if dados_mes:
        ultimo_mes = list(dados_mes.keys())[-1]
        categorias_mes_atual = _total_por_categoria(despesas, ultimo_mes)

    _criar_figuras(plots_frame, dados_mes, categorias_mes_atual, _agrupa_por_mes(despesas))

    return janela


if __name__ == "__main__":
    # Execução isolada para depuração manual
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    arquivo = Path.cwd() / "gastos_empresa.json"
    abrir_dashboard(root, arquivo)
    root.mainloop()
