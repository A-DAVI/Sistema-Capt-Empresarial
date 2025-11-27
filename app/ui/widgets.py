# -*- coding: utf-8 -*-
from __future__ import annotations

import customtkinter as ctk


class ReadOnlyComboBox(ctk.CTkComboBox):
    """CTkComboBox travada para impedir edição de texto (somente seleção)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.configure(state="readonly")
        except Exception:
            pass

        def _block(_evt=None):
            return "break"

        for seq in (
            "<Key>",
            "<BackSpace>",
            "<Delete>",
            "<Control-v>",
            "<Control-V>",
            "<Control-x>",
            "<Control-X>",
        ):
            try:
                self.bind(seq, _block)
            except Exception:
                pass

