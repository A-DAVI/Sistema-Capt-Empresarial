# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import shutil
import subprocess
from pathlib import Path

import requests

from app.config import PROJECT_ROOT

GITHUB_REPO = "A-DAVI/Sistema-Capt-Empresarial"
CURRENT_VERSION = "1.0.0"
FILENAME = "CaptacaoEmpresarial14D.exe"
UPDATE_DIR = PROJECT_ROOT / "update"


def get_latest():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return None
    return resp.json()


def check_update():
    data = get_latest()
    if not data:
        return None
    latest_version = data["tag_name"].replace("v", "")
    if latest_version == CURRENT_VERSION:
        return None
    for asset in data.get("assets", []):
        if asset["name"] == FILENAME:
            return asset["browser_download_url"], latest_version
    return None


def download(url: str) -> Path:
    UPDATE_DIR.mkdir(exist_ok=True, parents=True)
    exe_path = UPDATE_DIR / FILENAME
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(exe_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return exe_path


def install_and_restart(new_exe: Path) -> None:
    current_exe = Path(sys.argv[0])
    backup = current_exe.with_suffix(".old.exe")
    if backup.exists():
        backup.unlink()
    current_exe.rename(backup)
    shutil.copy(new_exe, current_exe)
    subprocess.Popen([str(current_exe)])
    sys.exit()


def auto_update():
    result = check_update()
    if not result:
        return
    url, _version = result
    new_exe = download(url)
    install_and_restart(new_exe)
