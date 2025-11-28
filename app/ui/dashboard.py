"""Dashboard executivo de despesas (CustomTkinter + Matplotlib).

API pública:
    abrir_dashboard(parent, empresa_path: Path)
"""

from __future__ import annotations

import json
from collections import defaultdict, OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Paleta expandida para garantir cores distintas nas categorias
PIE_PALETTE = [
    "#7B61FF",
    "#4C7DFF",
    "#7DD3FC",
    "#F59E0B",
    "#EF4444",
    "#10B981",
    "#6366F1",
    "#EC4899",
    "#22D3EE",
    "#F97316",
    "#8B5CF6",
    "#14B8A6",
    "#FBBF24",
    "#A855F7",
    "#3B82F6",
    "#0EA5E9",
    "#D946EF",
    "#0EA5E9",
]

# Paletas para acompanhar o tema atual (dark/light)
DARK_COLORS = {
    "background": "#0B0B0B",
    "surface": "#121212",
    "panel": "#1A1A1A",
    "card": "#1E1E1E",
    "accent": "#4C7DFF",
    "accent_muted": "#7FA2FF",
    "accent_alt": "#7B61FF",
    "bar": "#2D6DFF",
    "line": "#6FA6FF",
    "pie": PIE_PALETTE,
    "text_primary": "#FFFFFF",
    "text_secondary": "#C7CCD4",
    "divider": "#2C2F36",
    "success": "#22C55E",
    "danger": "#F87171",
}
LIGHT_COLORS = {
    "background": "#F5F7FA",
    "surface": "#FFFFFF",
    "panel": "#F1F3F7",
    "card": "#FFFFFF",
    "accent": "#3B7BFF",
    "accent_muted": "#6FA0FF",
    "accent_alt": "#7B61FF",
    "bar": "#2D6DFF",
    "line": "#5B8DEF",
    "pie": PIE_PALETTE,
    "text_primary": "#0F172A",
    "text_secondary": "#4B5563",
    "divider": "#E5E7EB",
    "success": "#16A34A",
    "danger": "#DC2626",
}


def _palette() -> dict[str, str]:
    modo = ctk.get_appearance_mode().lower()
    return DARK_COLORS if modo == "dark" else LIGHT_COLORS


# ---------------------- Dados e KPIs ---------------------- #
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
    return OrderedDict(sorted(soma.items()))


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


def _total_por_fornecedor(despesas: Iterable[dict]) -> dict[str, float]:
    """Soma valores por fornecedor (normalizado)."""
    tot = defaultdict(float)
    try:
        if not despesas:
            return {}
        for reg in despesas:
            if not isinstance(reg, dict):
                continue
            nome = str(reg.get("fornecedor") or "").strip().upper()
            if not nome:
                continue
            try:
                tot[nome] += float(reg.get("valor", 0) or 0)
            except Exception:
                continue
    except Exception:
        return {}
    return dict(sorted(tot.items(), key=lambda x: x[1], reverse=True))


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


# ---------------------- UI helpers ---------------------- #
FONT_TITLE = ("Segoe UI Semibold", 22)
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_KPI_TITLE = ("Segoe UI Semibold", 13)
FONT_KPI_VALUE = ("Segoe UI Semibold", 16)
FONT_KPI_LABEL = ("Segoe UI", 9)


def _center(win: ctk.CTkToplevel | ctk.CTk, w: int = 1150, h: int = 760) -> None:
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
    colors = _palette()
    card = ctk.CTkFrame(
        parent,
        fg_color=colors["card"],
        corner_radius=8,
        border_width=1,
        border_color=colors["divider"],
        height=96,
    )
    card.grid_propagate(False)
    card.pack_propagate(False)
    lbl_titulo = ctk.CTkLabel(
        card,
        text=titulo,
        font=FONT_KPI_LABEL,
        text_color=colors["text_secondary"],
        anchor="w",
    )
    lbl_titulo.pack(fill="x", padx=10, pady=(2, 1))
    lbl_valor = ctk.CTkLabel(
        card,
        text=valor,
        font=FONT_KPI_VALUE,
        text_color=cor_valor or colors["text_primary"],
        anchor="w",
    )
    lbl_valor.pack(fill="x", padx=10, pady=(0, 1))
    if subtitulo:
        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=FONT_KPI_LABEL,
            text_color=colors["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=10, pady=(0, 4))
    card.lbl_titulo = lbl_titulo  # type: ignore[attr-defined]
    card.lbl_valor = lbl_valor  # type: ignore[attr-defined]
    return card


# ---------------------- Gráficos ---------------------- #
def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _estilizar_axes(ax, colors: dict[str, str]):
    ax.set_facecolor(colors["panel"])
    ax.tick_params(colors=colors["text_secondary"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(colors["divider"])


def _plot_barras(ax, dados: OrderedDict[str, float], colors: dict[str, str]):
    if not dados:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color=colors["text_secondary"])
        ax.axis("off")
        return
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b/%y") for k in dados.keys()]
    valores = list(dados.values())
    bars = ax.bar(labels, valores, color=colors["bar"], edgecolor=colors["divider"], linewidth=0.6, width=0.6)
    ax.bar_label(
        bars,
        labels=[f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in valores],
        fontsize=8,
        padding=2,
        color=colors["text_secondary"],
        rotation=90,
    )
    ax.set_title("Gastos por mês", color=colors["text_primary"], pad=12, fontsize=12, fontweight="bold")
    _estilizar_axes(ax, colors)


def _plot_pizza(ax, categorias: dict[str, float], colors: dict[str, str], color_map: dict[str, str] | None = None):
    if not categorias:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color=colors["text_secondary"])
        ax.axis("off")
        return []
    labels = list(categorias.keys())
    valores = list(categorias.values())
    total = sum(valores) or 1.0
    # Explode zero para não destacar fatias pequenas
    explode = [0.0 for _ in valores]
    palette = colors.get("pie")
    if not palette:
        palette = [
            "#7B61FF", "#4C7DFF", "#7DD3FC", "#F59E0B", "#EF4444",
            "#10B981", "#6366F1", "#EC4899", "#22D3EE", "#F97316",
        ]
    if color_map:
        palette = [color_map.get(lbl, palette[idx % len(palette)]) for idx, lbl in enumerate(labels)]
    pie_result = ax.pie(
        valores,
        labels=None,
        autopct=None,
        pctdistance=0.7,
        startangle=90,
        explode=explode,
        colors=palette[: len(valores)],
        textprops={"color": colors["text_primary"], "fontsize": 9},
        wedgeprops={"width": 0.35, "edgecolor": colors["surface"], "linewidth": 1},
    )
    wedges = pie_result[0]
    legend_items = []
    effective_colors = palette[: len(valores)]
    for lbl, val, cor in zip(labels, valores, effective_colors):
        pct = (val / total) * 100 if total else 0
        legend_items.append((lbl, val, pct, cor))

    # hover: exibe tooltip com valor e %
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=9,
        color=colors["text_primary"],
        bbox=dict(boxstyle="round,pad=0.35", fc=colors["panel"], ec=colors["divider"], lw=1),
    )
    annot.set_visible(False)

    def _hover(event):
        vis = annot.get_visible()
        if event.inaxes != ax:
            if vis:
                annot.set_visible(False)
                ax.figure.canvas.draw_idle()
            return
        for wedge, lbl, val in zip(wedges, labels, valores):
            contains, _ = wedge.contains(event)
            if contains:
                pct = (val / total) * 100 if total else 0
                annot.xy = (event.xdata, event.ydata)
                annot.set_text(f"{lbl}\n{_fmt_brl(val)} ({pct:.1f}%)")
                annot.get_bbox_patch().set_facecolor(colors["panel"])
                annot.get_bbox_patch().set_edgecolor(colors["divider"])
                annot.set_visible(True)
                ax.figure.canvas.draw_idle()
                return
        if vis:
            annot.set_visible(False)
            ax.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("motion_notify_event", _hover)

    ax.text(0, 0, f"{_fmt_brl(total)}\nTotal", ha="center", va="center", color=colors["text_primary"], fontsize=11, fontweight="bold")
    ax.set_title("Distribuição por categoria", color=colors["text_primary"], pad=10, fontsize=12, fontweight="bold")
    _estilizar_axes(ax, colors)
    return legend_items


def _plot_top_fornecedores(ax, dados: dict[str, float], colors: dict[str, str], limite: int = 7):
    """Exibe barras horizontais dos maiores fornecedores por valor."""
    if not dados:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color=colors["text_secondary"])
        ax.axis("off")
        return
    items = sorted(dados.items(), key=lambda x: x[1], reverse=True)[:limite]
    labels = [k for k, _ in items][::-1]
    valores = [v for _, v in items][::-1]
    bars = ax.barh(range(len(labels)), valores, color=colors["bar"], edgecolor=colors["divider"], height=0.6)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, color=colors["text_secondary"], fontsize=9)
    for bar, val in zip(bars, valores, strict=False):
        ax.text(
            bar.get_width() + max(valores) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            _fmt_brl(val),
            va="center",
            color=colors["text_primary"],
            fontsize=9,
        )
    ax.invert_yaxis()
    ax.set_title("Top fornecedores por valor", color=colors["text_primary"], pad=10, fontsize=12, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.3, color=colors["divider"])
    ax.set_facecolor(colors["panel"])
    ax.tick_params(colors=colors["text_secondary"], labelsize=9)
    return []


def _plot_linha(ax, dados: OrderedDict[str, float], colors: dict[str, str]):
    if not dados:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", color=colors["text_secondary"])
        ax.axis("off")
        return
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b/%y") for k in dados.keys()]
    valores = list(dados.values())
    acumulado = []
    soma = 0.0
    for v in valores:
        soma += v
        acumulado.append(soma)
    ax.plot(labels, acumulado, marker="o", color=colors["line"], linewidth=2.2, markersize=6)
    ax.fill_between(range(len(acumulado)), acumulado, color=colors["accent_muted"], alpha=0.18)
    ax.set_title("Evolução acumulada", color=colors["text_primary"], pad=12, fontsize=12, fontweight="bold")
    _estilizar_axes(ax, colors)


def _criar_figuras(frame_plots, dados_mes, categorias_mes, linha_total, colors):
    # Mantido por compatibilidade, embora não seja chamado atualmente
    fig = Figure(figsize=(8, 4), dpi=100, facecolor=colors["surface"])
    ax = fig.add_subplot(1, 1, 1, facecolor=colors["panel"])
    _plot_pizza(ax, categorias_mes, colors)
    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas


# ---------------------- Dashboard ---------------------- #
def abrir_dashboard(parent, empresa_path: Path):
    """Abre o dashboard executivo para a empresa indicada."""
    despesas = _ler_despesas(empresa_path) or []
    colors = _palette()

    janela = ctk.CTkToplevel(parent)
    janela.title("Central de Controle - Dashboard")
    janela.configure(fg_color=colors["background"])
    try:
        janela.state("zoomed")  # Windows
    except Exception:
        try:
            janela.attributes("-zoomed", True)  # *nix
        except Exception:
            _center(janela)
    janela.grab_set()
    janela.transient(parent)

    # Cabeçalho
    header = ctk.CTkFrame(janela, fg_color="transparent")
    header.pack(fill="x", padx=16, pady=(16, 12))
    ctk.CTkLabel(
        header,
        text=f"Centro de controle de gastos — {Path(empresa_path).stem}",
        font=FONT_TITLE,
        text_color=colors["text_primary"],
    ).pack(anchor="w")
    ctk.CTkLabel(
        header,
        text="Visão consolidada das suas despesas.",
        font=FONT_SUBTITLE,
        text_color=colors["text_secondary"],
    ).pack(anchor="w", pady=(2, 0))

    # Scroll container para caber gráfico inteiro
    scroll = ctk.CTkScrollableFrame(janela, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=0, pady=0)

    # meses disponíveis e estado atual
    meses_disponiveis = list(_agrupa_por_mes(despesas).keys())
    if not meses_disponiveis:
        meses_disponiveis = []
    current_idx = len(meses_disponiveis) - 1 if meses_disponiveis else 0

    # mapa de cores para todas as categorias do dataset
    todas_categorias = sorted({str(reg.get("tipo") or reg.get("categoria") or "Sem categoria") for reg in despesas})
    palette_base = colors["pie"]
    color_map_global = {nome: palette_base[i % len(palette_base)] for i, nome in enumerate(todas_categorias)}

    agrupado = _agrupa_por_mes(despesas)

    def calcular_kpi_idx(idx: int) -> dict[str, str | bool]:
        if not meses_disponiveis:
            return {
                "mes_atual_label": "—",
                "mes_anterior_label": "—",
                "total_mes_atual": _fmt_brl(0.0),
                "total_mes_anterior": _fmt_brl(0.0),
                "variacao": "+0.0%",
                "variacao_up": True,
                "maior_categoria": "—",
            }
        atual_key = meses_disponiveis[idx]
        prev_key = meses_disponiveis[idx - 1] if idx - 1 >= 0 else None
        atual_total = agrupado.get(atual_key, 0.0)
        prev_total = agrupado.get(prev_key, 0.0) if prev_key else 0.0
        variacao = 0.0
        if prev_total:
            variacao = ((atual_total - prev_total) / prev_total) * 100
        cats_mes = _total_por_categoria(despesas, atual_key)
        maior_cat = max(cats_mes.items(), key=lambda x: x[1])[0] if cats_mes else "N/A"

        def fmt_mes(chave: str | None) -> str:
            if not chave:
                return "—"
            dt = datetime.strptime(chave, "%Y-%m")
            return dt.strftime("%b/%Y")

        return {
            "mes_atual_label": fmt_mes(atual_key),
            "mes_anterior_label": fmt_mes(prev_key),
            "total_mes_atual": _fmt_brl(atual_total),
            "total_mes_anterior": _fmt_brl(prev_total),
            "variacao": f"{variacao:+.1f}%",
            "variacao_up": variacao >= 0,
            "maior_categoria": maior_cat,
        }

    if meses_disponiveis:
        mes_atual = meses_disponiveis[current_idx]
        categorias_orig: dict[str, float] = _total_por_categoria(despesas, mes_atual)
        if not categorias_orig:
            categorias_orig = _total_por_categoria(despesas, None)
    else:
        categorias_orig = _total_por_categoria(despesas, None)
    color_map: dict[str, str] = {nome: color_map_global.get(nome, palette_base[i % len(palette_base)]) for i, nome in enumerate(categorias_orig.keys())}

    # KPIs (grid 4 col)
    kpi_data = calcular_kpi_idx(current_idx)
    kpi_wrap = ctk.CTkFrame(scroll, fg_color="transparent")
    kpi_wrap.pack(fill="x", padx=12, pady=(0, 8))

    for i in range(4):
        kpi_wrap.grid_columnconfigure(i, weight=1)

    card1 = _criar_kpi(
        kpi_wrap,
        f"Total do mês — {kpi_data['mes_atual_label']}",
        kpi_data["total_mes_atual"],
    )
    card1.grid(row=0, column=0, sticky="nsew", padx=4, pady=2, ipady=0)

    card2 = _criar_kpi(
        kpi_wrap,
        f"Total do mês anterior — {kpi_data['mes_anterior_label']}",
        kpi_data["total_mes_anterior"],
    )
    card2.grid(row=0, column=1, sticky="nsew", padx=4, pady=2, ipady=0)

    card3 = _criar_kpi(
        kpi_wrap,
        "Variação frente ao mês anterior",
        kpi_data["variacao"],
        cor_valor=colors["success"] if kpi_data["variacao_up"] else colors["danger"],
    )
    card3.grid(row=0, column=2, sticky="nsew", padx=4, pady=2, ipady=0)

    card4 = _criar_kpi(
        kpi_wrap,
        "Despesa com maior impacto no mês",
        kpi_data["maior_categoria"],
    )
    card4.grid(row=0, column=3, sticky="nsew", padx=4, pady=2, ipady=0)

    def atualizar_kpis(idx: int) -> None:
        kpi = calcular_kpi_idx(idx)
        card1.lbl_titulo.configure(text=f"Total do mês — {kpi['mes_atual_label']}")
        card1.lbl_valor.configure(text=kpi["total_mes_atual"])
        card2.lbl_titulo.configure(text=f"Total do mês anterior — {kpi['mes_anterior_label']}")
        card2.lbl_valor.configure(text=kpi["total_mes_anterior"])
        card3.lbl_valor.configure(
            text=kpi["variacao"],
            text_color=colors["success"] if kpi.get("variacao_up") else colors["danger"],
        )
        card4.lbl_valor.configure(text=kpi["maior_categoria"])
    atualizar_kpis(current_idx)

    # Plots (somente pizza com legenda)
    plots_frame = ctk.CTkFrame(scroll, fg_color=colors["surface"], corner_radius=18)
    plots_frame.pack(fill="both", expand=True, padx=14, pady=12)

    def mes_label(idx: int) -> str:
        if not meses_disponiveis:
            return "Sem dados"
        dt = datetime.strptime(meses_disponiveis[idx], "%Y-%m")
        return dt.strftime("%b/%Y")

    agrupado = _agrupa_por_mes(despesas)

    def calcular_kpi_idx(idx: int) -> dict[str, str | bool]:
        if not meses_disponiveis:
            return {
                "mes_atual_label": "—",
                "mes_anterior_label": "—",
                "total_mes_atual": _fmt_brl(0.0),
                "total_mes_anterior": _fmt_brl(0.0),
                "variacao": "+0.0%",
                "variacao_up": True,
                "maior_categoria": "—",
            }
        atual_key = meses_disponiveis[idx]
        prev_key = meses_disponiveis[idx - 1] if idx - 1 >= 0 else None
        atual_total = agrupado.get(atual_key, 0.0)
        prev_total = agrupado.get(prev_key, 0.0) if prev_key else 0.0
        variacao = 0.0
        if prev_total:
            variacao = ((atual_total - prev_total) / prev_total) * 100
        cats_mes = _total_por_categoria(despesas, atual_key)
        maior_cat = max(cats_mes.items(), key=lambda x: x[1])[0] if cats_mes else "N/A"
        def fmt_mes(chave: str | None) -> str:
            if not chave:
                return "—"
            dt = datetime.strptime(chave, "%Y-%m")
            return dt.strftime("%b/%Y")
        return {
            "mes_atual_label": fmt_mes(atual_key),
            "mes_anterior_label": fmt_mes(prev_key),
            "total_mes_atual": _fmt_brl(atual_total),
            "total_mes_anterior": _fmt_brl(prev_total),
            "variacao": f"{variacao:+.1f}%",
            "variacao_up": variacao >= 0,
            "maior_categoria": maior_cat,
        }

    # estado do filtro
    selected_categories: set[str] = set(categorias_orig.keys())

    # header de filtros dentro do frame de gráficos
    toolbar = ctk.CTkFrame(plots_frame, fg_color="transparent")
    toolbar.pack(fill="x", padx=10, pady=(8, 0))

    # Controles de navegação de mês
    month_nav = ctk.CTkFrame(toolbar, fg_color="transparent")
    month_nav.pack(side="left", padx=(0, 8))

    lbl_mes = ctk.CTkLabel(
        month_nav,
        text=mes_label(current_idx),
        font=FONT_KPI_TITLE,
        text_color=colors["text_primary"],
    )

    def mudar_mes(delta: int):
        nonlocal current_idx, categorias_orig, selected_categories
        if not meses_disponiveis:
            return
        new_idx = max(0, min(len(meses_disponiveis) - 1, current_idx + delta))
        if new_idx == current_idx:
            return
        current_idx = new_idx
        lbl_mes.configure(text=mes_label(current_idx))
        mes_atual = meses_disponiveis[current_idx]
        categorias_orig = _total_por_categoria(despesas, mes_atual)
        selected_categories = set(categorias_orig.keys())
        atualizar_colors(categorias_orig)
        render_pie(categorias_orig)
        atualizar_kpis(current_idx)

    btn_prev = ctk.CTkButton(
        month_nav,
        text="<",
        width=32,
        command=lambda: mudar_mes(-1),
        fg_color=colors.get("neutral", colors["panel"]),
        hover_color=colors["divider"],
        text_color=colors["text_primary"],
        corner_radius=10,
    )
    btn_prev.pack(side="left", padx=(0, 6))

    lbl_mes.pack(side="left")

    btn_next = ctk.CTkButton(
        month_nav,
        text=">",
        width=32,
        command=lambda: mudar_mes(1),
        fg_color=colors.get("neutral", colors["panel"]),
        hover_color=colors["divider"],
        text_color=colors["text_primary"],
        corner_radius=10,
    )
    btn_next.pack(side="left", padx=(6, 0))

    ctk.CTkLabel(
        toolbar,
        text="Visão por categoria",
        font=FONT_KPI_TITLE,
        text_color=colors["text_primary"],
    ).pack(side="left", padx=6)

    def render_pie(cats: dict[str, float]):
        # destrói canvas anterior, se existir
        nonlocal canvas_pie
        if canvas_pie:
            try:
                canvas_pie.get_tk_widget().destroy()
            except Exception:
                pass
        fig = Figure(figsize=(6.5, 5.2), dpi=100, facecolor=colors["surface"])
        ax_pie = fig.add_subplot(1, 1, 1, facecolor=colors["panel"])
        _plot_pizza(ax_pie, cats, colors, color_map)
        fig.tight_layout(pad=1.2)
        canvas_pie = FigureCanvasTkAgg(fig, master=plots_frame)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=30, pady=(10, 12))

    def abrir_filtro_categorias():
        modal = ctk.CTkToplevel(janela)
        modal.title("Ajustar categorias")
        modal.configure(fg_color=colors["surface"])
        modal.resizable(False, False)
        modal.grab_set()
        modal.transient(janela)
        _center(modal, 420, 420)

        ctk.CTkLabel(
            modal,
            text="Escolha quais categorias deseja visualizar",
            font=FONT_KPI_TITLE,
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=16, pady=(14, 8))

        body = ctk.CTkFrame(modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # lista em ordem decrescente de valor
        items = sorted(categorias_orig.items(), key=lambda x: x[1], reverse=True)
        checks = []
        for nome, _ in items:
            var = ctk.BooleanVar(value=nome in selected_categories)
            chk = ctk.CTkCheckBox(
                body,
                text=nome,
                variable=var,
                onvalue=True,
                offvalue=False,
                text_color=colors["text_primary"],
            )
            chk.pack(anchor="w", padx=8, pady=2)
            checks.append((nome, var))

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", padx=12, pady=(4, 12))

        def aplicar():
            nonlocal selected_categories
            selecionadas = {nome for nome, var in checks if var.get()}
            if not selecionadas:
                selecionadas = set(categorias_orig.keys())
            selected_categories = selecionadas
            filtradas = {k: v for k, v in categorias_orig.items() if k in selected_categories}
            render_pie(filtradas)
            modal.destroy()

        def limpar():
            for _, var in checks:
                var.set(True)

        ctk.CTkButton(
            btns,
            text="Aplicar",
            command=aplicar,
            fg_color=colors["accent"],
            hover_color=colors["accent_muted"],
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btns,
            text="Selecionar todas",
            command=limpar,
            fg_color=colors["neutral"] if "neutral" in colors else colors["card"],
            hover_color=colors["divider"],
            text_color=colors["text_primary"],
        ).pack(side="left", expand=True, fill="x", padx=6)

        ctk.CTkButton(
            btns,
            text="Cancelar",
            command=modal.destroy,
            fg_color=colors["panel"],
            hover_color=colors["divider"],
            text_color=colors["text_secondary"],
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    ctk.CTkButton(
        toolbar,
        text="Filtro",
        command=abrir_filtro_categorias,
        fg_color=colors["neutral"] if "neutral" in colors else colors["panel"],
        hover_color=colors["divider"],
        text_color=colors["text_primary"],
        height=32,
        corner_radius=10,
    ).pack(side="right")

    # corpo do gráfico + legenda em duas colunas
    body = ctk.CTkFrame(plots_frame, fg_color=colors["surface"])
    body.pack(fill="both", expand=True, padx=8, pady=(6, 10))
    body.grid_columnconfigure(0, weight=2)
    body.grid_columnconfigure(1, weight=1)

    chart_holder = ctk.CTkFrame(body, fg_color="transparent")
    chart_holder.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=6)

    legend_frame = ctk.CTkFrame(body, fg_color=colors["panel"], corner_radius=12, border_width=1, border_color=colors["divider"])
    legend_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 10), pady=6)
    legend_frame.pack_propagate(True)

    canvas_pie: FigureCanvasTkAgg | None = None

    def atualizar_legenda(items: list[tuple[str, float, float, str]] | None):
        items = items or []
        for child in legend_frame.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        ctk.CTkLabel(
            legend_frame,
            text="Categorias",
            font=("Segoe UI Semibold", 13),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=12, pady=(10, 8))
        for nome, val, pct, cor in sorted(items, key=lambda x: x[1], reverse=True):
            row = ctk.CTkFrame(legend_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=16), text_color=cor).pack(side="left", padx=(0, 8))
            text_container = ctk.CTkFrame(row, fg_color="transparent")
            text_container.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(
                text_container,
                text=f"{nome if len(nome)<=28 else nome[:25]+'...'}",
                font=("Segoe UI Semibold", 12),
                text_color=colors["text_primary"],
                anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                text_container,
                text=f"{_fmt_brl(val)}",
                font=("Segoe UI", 11),
                text_color=colors["text_secondary"],
                anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                row,
                text=f"{pct:.1f}%",
                font=("Segoe UI", 11),
                text_color=colors["text_secondary"],
            ).pack(side="right", padx=(6, 0))

    def atualizar_colors(cats_ref: dict[str, float]):
        nonlocal color_map
        # recalcula color_map baseado no global para consistência
        color_map = {nome: color_map_global.get(nome, palette_base[i % len(palette_base)]) for i, nome in enumerate(cats_ref.keys())}

    def render_pie(cats: dict[str, float]):
        nonlocal canvas_pie
        if canvas_pie:
            try:
                canvas_pie.get_tk_widget().destroy()
            except Exception:
                pass
        fig = Figure(figsize=(6.2, 4.8), dpi=100, facecolor=colors["surface"])
        ax_pie = fig.add_subplot(1, 1, 1, facecolor=colors["panel"])
        legend_items = _plot_pizza(ax_pie, cats, colors, color_map) or []
        fig.tight_layout(pad=1.0)
        canvas_pie = FigureCanvasTkAgg(fig, master=chart_holder)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=30, pady=(10, 12))
        atualizar_legenda(legend_items)

    render_pie(categorias_orig)

    return janela


if __name__ == "__main__":
    # Execução isolada para depuração manual
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    arquivo = Path.cwd() / "gastos_empresa.json"
    abrir_dashboard(root, arquivo)
    root.mainloop()
