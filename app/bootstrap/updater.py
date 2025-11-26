# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import requests

import os

from app.utils.paths import ensure_workspace_dir
from app.version import __version__ as CURRENT_VERSION

GITHUB_REPO = "A-DAVI/Sistema-Capt-Empresarial"
ZIP_ASSET = "CaptacaoEmpresarial14D.zip"


def get_latest() -> dict | None:
    """Obtém informações da última release do GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def check_update() -> tuple[str, str] | None:
    """Verifica se existe uma versão mais recente publicada."""
    # Evita rodar em builds dev ou quando o usuário desabilita via env.
    if os.getenv("SKIP_AUTO_UPDATE"):
        return None
    if CURRENT_VERSION.startswith("0.0.0"):
        return None

    data = get_latest()
    if not data:
        return None
    latest_version = data.get("tag_name", "").replace("v", "")
    if latest_version == CURRENT_VERSION:
        return None
    for asset in data.get("assets", []):
        if asset.get("name") == ZIP_ASSET:
            return asset["browser_download_url"], latest_version
    return None


def download_zip(url: str) -> Path:
    """Baixa o pacote .zip do onedir para a pasta update."""
    update_dir = ensure_workspace_dir("update")
    zip_path = update_dir / ZIP_ASSET
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, "wb") as target:
            shutil.copyfileobj(response.raw, target)
    return zip_path


def _extract_zip(zip_path: Path) -> Path:
    """Extrai o zip baixado para uma pasta temporária."""
    extract_dir = ensure_workspace_dir("update", "extracted")
    if extract_dir.exists():
        shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    return extract_dir


def install_and_restart(zip_path: Path) -> None:
    """
    Copia o conteúdo do onedir extraído sobre a instalação atual e reinicia o app.
    Usa um script .bat para evitar problemas de arquivo em uso.
    """
    current_exe = Path(sys.argv[0]).resolve()
    current_dir = current_exe.parent
    extracted_dir = _extract_zip(zip_path)
    update_bat = current_dir / "update.bat"

    bat_script = f"""
@echo off
echo Atualizando aplicativo...
ping 127.0.0.1 -n 2 >nul
xcopy "{extracted_dir}\\*" "{current_dir}\\" /E /I /Y /Q
start "" "{current_exe}"
del "%~f0"
"""
    update_bat.write_text(bat_script.strip(), encoding="utf-8")
    subprocess.Popen(["cmd.exe", "/c", str(update_bat)])
    sys.exit()


def auto_update() -> None:
    """Executa o fluxo completo de atualização via pacote zip onedir."""
    result = check_update()
    if not result:
        return
    url, _version = result
    zip_path = download_zip(url)
    install_and_restart(zip_path)
