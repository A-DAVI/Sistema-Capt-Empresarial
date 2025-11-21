# -*- coding: utf-8 -*-
"""
RPA simplificado para testar o fluxo da aplicação (seleciona empresa, cadastra despesas e gera PDFs).

Observação: Os cliques dependem de coordenadas de tela. Ajuste o dicionário COORDS abaixo
para sua resolução/posição. Se faltar coordenada ou pyautogui, o RPA é ignorado silenciosamente.
"""
from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass
from typing import Dict, Tuple

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore


# Coordenadas base (ajuste conforme sua tela). Ex.: (x, y) em pixels.
COORDS: Dict[str, Tuple[int, int] | None] = {
    "selector_dropdown": None,  # dropdown da seleção de empresa inicial
    "selector_enter": None,  # botão Entrar
    "mudar_empresa": None,  # botão "Mudar de empresa" na tela principal
    "campo_data": None,  # campo Data do formulário
    "campo_tipo": None,  # combo Tipo de despesa
    "campo_forma": None,  # combo Forma de pagamento
    "campo_valor": None,  # campo Valor
    "botao_salvar": None,  # botão Salvar despesa
}

EMPRESAS = [
    "MERCEARIA BELLA VISTA",
    "SUPERPAO",
    "SP FOODS",
]

TIPOS = [
    "Aluguel",
    "Energia Eletrica",
    "Agua e esgoto",
    "Salarios (Funcionarios)",
    "Marketing",
]

FORMAS = [
    "Banco",
    "Dinheiro",
]


@dataclass
class RPAOptions:
    despesas_por_empresa: int = 50
    atraso_inicial: float = 3.0
    atraso_entre_campos: float = 0.15
    atraso_entre_registros: float = 0.25


def _coords_ok() -> bool:
    return pyautogui is not None and all(isinstance(v, tuple) and len(v) == 2 for v in COORDS.values())


def _click(name: str, delay: float = 0.05):
    x, y = COORDS[name]  # type: ignore[index]
    pyautogui.click(x, y)
    time.sleep(delay)


def _digitar(texto: str, delay: float = 0.05):
    pyautogui.typewrite(texto, interval=delay)


def _selecionar_empresa(nome: str, opts: RPAOptions):
    _click("selector_dropdown", opts.atraso_entre_campos)
    _digitar(nome, opts.atraso_entre_campos)
    pyautogui.press("enter")
    time.sleep(0.3)
    _click("selector_enter", opts.atraso_entre_campos)
    time.sleep(1.2)


def _registrar_despesa(valor: float, tipo: str, forma: str, opts: RPAOptions):
    _click("campo_data", opts.atraso_entre_campos)
    _digitar(time.strftime("%d/%m/%Y"), opts.atraso_entre_campos)
    _click("campo_tipo", opts.atraso_entre_campos)
    _digitar(tipo, opts.atraso_entre_campos)
    pyautogui.press("enter")
    _click("campo_forma", opts.atraso_entre_campos)
    _digitar(forma, opts.atraso_entre_campos)
    pyautogui.press("enter")
    _click("campo_valor", opts.atraso_entre_campos)
    _digitar(f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), opts.atraso_entre_campos)
    _click("botao_salvar", opts.atraso_entre_campos)
    time.sleep(opts.atraso_entre_registros)


def _trocar_empresa(opts: RPAOptions):
    _click("mudar_empresa", 0.4)
    time.sleep(0.8)


def run_rpa(opts: RPAOptions | None = None):
    """Roda o fluxo completo (selector + 50 registros/empresa) se coords estiverem definidos."""
    if not _coords_ok():
        return
    if pyautogui:
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.05
    opts = opts or RPAOptions()
    time.sleep(opts.atraso_inicial)

    for idx, empresa in enumerate(EMPRESAS):
        if idx > 0:
            _trocar_empresa(opts)
        _selecionar_empresa(empresa, opts)
        for _ in range(opts.despesas_por_empresa):
            tipo = random.choice(TIPOS)
            forma = random.choice(FORMAS)
            valor = random.uniform(50, 5000)
            _registrar_despesa(valor, tipo, forma, opts)


def launch_rpa_in_background():
    """Inicia o RPA em thread se habilitado."""
    if not os.getenv("ENABLE_RPA_TESTS", "1") == "1":
        return
    if not _coords_ok():
        print("[RPA] Coordenadas não definidas ou pyautogui ausente. RPA ignorado.")
        return

    t = threading.Thread(target=run_rpa, name="RPA-AutoTests", daemon=True)
    t.start()
    print("[RPA] Automação iniciada em background.")


def calibrar_coordenadas(duracao: int = 15):
    """
    Modo de calibração: imprime a posição do mouse a cada 1s por `duracao` segundos.
    Use para mapear os pontos e preencher COORDS manualmente.
    Ative com a env var ENABLE_RPA_CALIBRATE=1.
    """
    if pyautogui is None:
        print("[RPA] pyautogui não disponível para calibração.")
        return
    print("[RPA] Calibração: mova o mouse para o alvo. Posicoes serão logadas:")
    for i in range(duracao):
        pos = pyautogui.position()
        print(f"[RPA] t={i:02d}s -> x={pos.x}, y={pos.y}")
        time.sleep(1)


def _maybe_calibrate():
    if os.getenv("ENABLE_RPA_CALIBRATE", "0") == "1":
        calibrar_coordenadas()


__all__ = ["launch_rpa_in_background", "run_rpa", "RPAOptions", "COORDS"]
