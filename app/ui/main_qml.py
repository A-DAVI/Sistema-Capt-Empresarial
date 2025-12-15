# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main():
    # FORÇA UM ESTILO QUE SUPORTA placeholderText
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    qml_path = Path(__file__).resolve().parent / "qml" / "main.qml"
    engine.load(qml_path.as_posix())

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
