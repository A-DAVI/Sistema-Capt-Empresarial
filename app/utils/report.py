from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from app.utils.formatting import format_brl

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph
except Exception:  # pragma: no cover
    colors = None  # type: ignore[assignment]
    A4 = None  # type: ignore[assignment]
    ParagraphStyle = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    mm = 1  # type: ignore[assignment]
    canvas = None  # type: ignore[assignment]
    Paragraph = None  # type: ignore[assignment]


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
    output.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output), pagesize=A4)
    largura, altura = A4

    topo = altura - 30 * mm
    margem_x = 25 * mm

    # Logo (opcional)
    if logo_path:
        logo_file = Path(logo_path)
        if logo_file.exists():
            try:
                c.drawImage(
                    str(logo_file),
                    margem_x,
                    topo,
                    width=30 * mm,
                    height=20 * mm,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                # Se der erro na imagem, apenas segue sem logo
                pass

    # Cabeçalho textual
    c.setFont("Helvetica-Bold", 16)

    c.drawString(margem_x, topo - 8 * mm, company_name)
    c.setFont("Helvetica", 10)
    c.drawString(
        margem_x,
        topo - 14 * mm,
        f"Relatório de Despesas Empresariais",
    )
    c.drawString(
        margem_x,
        topo - 19 * mm,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    )

    # Linha separadora
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(0.5)
    c.line(margem_x, topo - 22 * mm, largura - margem_x, topo - 22 * mm)

    # Resumo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_x, topo - 30 * mm, "Resumo Geral")

    c.setFont("Helvetica", 11)
    c.drawString(
        margem_x,
        topo - 36 * mm,
        f"Total de despesas: {format_brl(total)}",
    )
    c.drawString(
        margem_x,
        topo - 42 * mm,
        f"Quantidade de lançamentos: {quantidade}",
    )

    # Espaço antes da lista
    y = topo - 52 * mm

    # Título da seção de detalhes
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_x, y, "Detalhamento das Despesas")
    y -= 8 * mm

    # Cabeçalho das colunas
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_x, y, "Data")
    c.drawString(margem_x + 30 * mm, y, "Tipo")
    c.drawString(margem_x + 100 * mm, y, "Forma")
    c.drawRightString(largura - margem_x, y, "Valor (R$)")
    y -= 4 * mm
    c.line(margem_x, y, largura - margem_x, y)
    y -= 6 * mm

    c.setFont("Helvetica", 9)

    # Ordena por data desc se possível
    def _parse_data(g: dict[str, Any]) -> datetime:
        try:
            return datetime.strptime(g.get("data", "01/01/1970"), "%d/%m/%Y")
        except Exception:
            return datetime(1970, 1, 1)

    gastos_ordenados = sorted(gastos_list, key=_parse_data, reverse=True)

    for gasto in gastos_ordenados:
        if y < 40 * mm:
            c.showPage()
            y = altura - 30 * mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margem_x, y, "Continuação - Detalhamento das Despesas")
            y -= 10 * mm
            c.setFont("Helvetica", 9)

        data = gasto.get("data", "")
        tipo = str(gasto.get("tipo", ""))[:40]
        forma = str(gasto.get("forma_pagamento", ""))[:25]
        valor = format_brl(float(gasto.get("valor", 0) or 0))

        c.drawString(margem_x, y, data)
        c.drawString(margem_x + 30 * mm, y, tipo)
        c.drawString(margem_x + 100 * mm, y, forma)
        c.drawRightString(largura - margem_x, y, valor)
        y -= 6 * mm

    c.showPage()
    c.save()

    return str(output)

