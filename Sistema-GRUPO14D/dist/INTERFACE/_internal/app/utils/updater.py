import sys
import requests
import shutil
import subprocess
from pathlib import Path

from app.utils.paths import ensure_workspace_dir

# CONFIGURAÇÕES
GITHUB_REPO = "A-DAVI/Sistema-Capt-Empresarial"
CURRENT_VERSION = "1.0.0"
FILENAME = "CaptacaoEmpresarial14D.exe"


def get_latest():
    """Obtém informações da última release do GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return None
    return resp.json()


def check_update():
    """Verifica se existe uma versão mais recente na release do GitHub."""
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


def download(url):
    """Baixa o novo executável para a pasta workspace/update."""
    update_path = ensure_workspace_dir("update")
    exe_path = update_path / FILENAME

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(exe_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return exe_path


def install_and_restart(new_exe):
    """
    Realiza a atualização criando um script .BAT externo para substituir o executável.
    Isso evita o erro WinError 32 (arquivo em uso).
    """
    current_exe = Path(sys.argv[0]).resolve()
    backup_exe = current_exe.with_suffix(".old.exe")
    update_bat = current_exe.parent / "update.bat"

    # Script .bat 100% compatível com acentos, espaços e caminhos UNC
    bat_script = f'''
@echo off
echo Atualizando aplicacao...

REM Aguarda o programa fechar
ping 127.0.0.1 -n 2 >nul

REM Remove backup antigo se existir
if exist "{backup_exe}" del "{backup_exe}"

REM Renomeia o executável atual
ren "{current_exe}" "{backup_exe.name}"

REM Copia o novo executável baixado
copy "{new_exe}" "{current_exe}" /Y

REM Inicia o executável atualizado
start "" "{current_exe}"

REM Apaga o próprio script
del "%~f0"
'''

    update_bat.write_text(bat_script, encoding="utf-8")

    # FORÇA o Windows CMD a executar o .bat (PowerShell não serve)
    subprocess.Popen(["cmd.exe", "/c", str(update_bat)])

    # Fecha o programa atual
    sys.exit()


def auto_update():
    """Executa o processo completo de update."""
    result = check_update()
    if not result:
        return

    url, version = result
    new_exe = download(url)
    install_and_restart(new_exe)
