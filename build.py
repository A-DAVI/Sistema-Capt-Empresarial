"""Script de build com PyInstaller para o CAPT Empresarial."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
OUTPUT_NAME = "CaptacaoEmpresarial14D"


def _run_pyinstaller() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    BUILD_DIR.mkdir(exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "INTERFACE.py",
        "--noconsole",
        "--onefile",
        "--windowed",
        "--uac-admin",
        "--clean",
        "--name",
        OUTPUT_NAME,
        "--hidden-import",
        "customtkinter",
        f"--icon={PROJECT_ROOT / 'Logo.ico'}",
    ]
    subprocess.run(command, check=True)


def _hash_executable(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handler:
        while chunk := handler.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _save_build_info(executable: Path, file_hash: str) -> None:
    info_path = PROJECT_ROOT / "build_info.txt"
    content = (
        f"Arquivo: {executable.name}\n"
        f"Caminho: {executable}\n"
        f"SHA256: {file_hash}\n"
        f"Gerado em: {datetime.now().isoformat()}\n"
        f"Sistema: {os.name}\n"
    )
    info_path.write_text(content, encoding="utf-8")


def main() -> None:
    """Executa a compilação com PyInstaller e registra o hash do build."""
    _run_pyinstaller()
    executable = DIST_DIR / (OUTPUT_NAME + (".exe" if os.name == "nt" else ""))
    if not executable.exists():
        raise FileNotFoundError(f"Executável não encontrado em {executable}")
    digest = _hash_executable(executable)
    _save_build_info(executable, digest)
    print(f"Build finalizado. SHA256: {digest}")


if __name__ == "__main__":
    main()
