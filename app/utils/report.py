# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from app.utils.formatting import format_brl
from app.utils.paths import runtime_path, workspace_path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph
except Exception:  # pragma: no cover
    colors = None  # type: ignore[assignment]
    A4 = None  # type: ignore[assignment]
    ParagraphStyle = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    cm = mm = 1  # type: ignore[assignment]
    canvas = None  # type: ignore[assignment]
    Paragraph = None  # type: ignore[assignment]


if canvas is not None:
    class NumberedCanvas(canvas.Canvas):
        """Canvas que salva o estado das páginas para inserir rodapé e numeração."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states: list[dict[str, Any]] = []

        def showPage(self):  # pragma: no cover - manipulação do reportlab
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()  # type: ignore[attr-defined]

        def save(self):  # pragma: no cover - manipulação do reportlab
            self._saved_page_states.append(dict(self.__dict__))
            total_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_footer(total_pages)
                super().showPage()
            super().save()

        def _draw_footer(self, total_pages: int):
            width, _ = self._pagesize  # type: ignore[attr-defined]
            footer_y = 1.5 * cm
            tagline = "Emitido automaticamente pelo Sistema CAPT Empresarial - Grupo 14D"
            self.setFont("Helvetica-Oblique", 9)
            self.drawCentredString(width / 2, footer_y, tagline)
            self.setFont("Helvetica", 9)
            self.drawCentredString(

                width / 2,

                footer_y - 0.45 * cm,

                f"{self._pageNumber}/{total_pages}",  # type: ignore[attr-defined]

            )


else:  # pragma: no cover
    NumberedCanvas = None  # type: ignore[assignment]


def generate_pdf_report(
    gastos: Iterable[dict[str, Any]],
    output_path: str,
    company_name: str = "Sua Empresa",
    logo_path: str | None = None,
) -> str:
    """
    Gera um relatório PDF minimalista de despesas.

    - Logo opcional no topo (se logo_path existir).
    - Cabeçalho com nome da empresa e data/hora de geração.
    - Resumo com total e quantidade de lançamentos.
    - Lista de despesas (data, tipo, forma, valor).
    """
    if canvas is None or A4 is None:
        raise RuntimeError(
            "Biblioteca 'reportlab' não encontrada. "
            "Instale com: pip install reportlab"
        )

    gastos_list = list(gastos)
    total = sum(float(g.get("valor", 0) or 0) for g in gastos_list)
    quantidade = len(gastos_list)

    output = Path(output_path)
    if not output.is_absolute():
        output = workspace_path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    canvas_class = NumberedCanvas or canvas.Canvas
    c = canvas_class(str(output), pagesize=A4)

    width, height = A4
    top_margin = height - 2.5 * cm
    x_margin = 2.5 * cm

    # Logo (opcional)
    if logo_path:
        logo_candidate = Path(logo_path)
        if not logo_candidate.is_absolute():
            workspace_logo = workspace_path(logo_candidate)
            runtime_logo = runtime_path(logo_candidate)
            if workspace_logo.exists():
                logo_candidate = workspace_logo
            elif runtime_logo.exists():
                logo_candidate = runtime_logo
        if logo_candidate.exists():
            try:
                c.drawImage(
                    str(logo_candidate),
                    x_margin,
                    top_margin,
                    width=30 * mm,
                    height=20 * mm,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:  # pragma: no cover
                pass

    # Cabeçalho textual
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, top_margin - 0.3 * cm, company_name)

    c.setFont("Helvetica", 10)
    c.drawString(
        x_margin,
        top_margin - 0.9 * cm,
        "Relatórios e Indicadores Financeiros",
    )
    c.drawString(
        x_margin,
        top_margin - 1.4 * cm,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    )

    # Linha separadora
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(0.5)
    c.line(x_margin, top_margin - 1.7 * cm, width - x_margin, top_margin - 1.7 * cm)

    # Resumo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, top_margin - 2.5 * cm, "Resumo Geral")

    c.setFont("Helvetica", 11)
    c.drawString(
        x_margin,
        top_margin - 3.1 * cm,
        f"Total de despesas: {format_brl(total)}",
    )
    c.drawString(
        x_margin,
        top_margin - 3.7 * cm,
        f"Quantidade de lançamentos: {quantidade}",
    )

    def desenhar_cabecalho_tabela(y_pos: float, titulo: str) -> float:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, y_pos, titulo)
        y_pos -= 8 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_margin, y_pos, "Data")
        c.drawString(x_margin + 3 * cm, y_pos, "Tipo")
        c.drawString(x_margin + 10 * cm, y_pos, "Forma")
        c.drawRightString(width - x_margin, y_pos, "Valor (R$)")
        y_pos -= 4 * mm
        c.line(x_margin, y_pos, width - x_margin, y_pos)
        y_pos -= 6 * mm
        c.setFont("Helvetica", 9)
        return y_pos

    y = desenhar_cabecalho_tabela(top_margin - 4.7 * cm, "Detalhamento das Despesas")

    # Ordena por data desc se possível
    def _parse_data(g: dict[str, Any]) -> datetime:
        try:
            return datetime.strptime(g.get("data", "01/01/1970"), "%d/%m/%Y")
        except (ValueError, TypeError):
            return datetime(1970, 1, 1)

    gastos_ordenados = sorted(gastos_list, key=_parse_data, reverse=True)

    for gasto in gastos_ordenados:
        if y < 4 * cm:  # mantém margem inferior confortável
            c.showPage()
            y = desenhar_cabecalho_tabela(height - 3 * cm, "Continuação - Detalhamento das Despesas")

        data = gasto.get("data", "")
        tipo = str(gasto.get("tipo", ""))[:40]
        forma = str(gasto.get("forma_pagamento", ""))[:25]
        valor = format_brl(float(gasto.get("valor", 0) or 0))

        c.drawString(x_margin, y, data)
        c.drawString(x_margin + 3 * cm, y, tipo)
        c.drawString(x_margin + 10 * cm, y, forma)
        c.drawRightString(width - x_margin, y, valor)
        y -= 6 * mm

    c.save()
    return str(output)
