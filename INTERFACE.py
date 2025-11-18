# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.ui.app import main
from app.utils.updater import auto_update

auto_update()

if __name__ == "__main__":
    main()
