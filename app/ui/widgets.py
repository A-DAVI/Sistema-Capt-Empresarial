# -*- coding: utf-8 -*-
from __future__ import annotations

import customtkinter as ctk
import tkinter as tk


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


class ScrollableComboBox(ctk.CTkFrame):
    """
    Dropdown customizado com rolagem. Mantém aparência simples de botão
    e abre um Toplevel rolável para navegar por listas longas.
    """

    def __init__(
        self,
        master,
        values: list[str] | tuple[str, ...] | None = None,
        command=None,
        font=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent")
        self.values = list(values) if values else []
        self.command = command
        self._var = tk.StringVar(value="")

        self.button = ctk.CTkButton(
            self,
            text="Selecione",
            command=self._open_dropdown,
            height=kwargs.pop("height", 40),
            fg_color=kwargs.pop("fg_color", "#2d6cdf"),
            hover_color=kwargs.pop("hover_color", "#2253a8"),
            font=font or kwargs.get("font"),
            text_color=kwargs.get("text_color"),
        )
        self.button.pack(fill="x", expand=True)

    def _open_dropdown(self):
        if not self.values:
            return

        toplevel = ctk.CTkToplevel(self)
        toplevel.overrideredirect(True)
        toplevel.lift()

        # posiciona abaixo do botão
        bx = self.button.winfo_rootx()
        by = self.button.winfo_rooty() + self.button.winfo_height()
        toplevel.geometry(f"320x260+{bx}+{by}")
        toplevel.configure(fg_color="#1e1e1e")

        frame = ctk.CTkScrollableFrame(toplevel, fg_color=toplevel.cget("fg_color"))
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        def selecionar(valor: str):
            self.set(valor)
            toplevel.destroy()
            if callable(self.command):
                self.command()

        for val in self.values:
            ctk.CTkButton(
                frame,
                text=val,
                command=lambda v=val: selecionar(v),
                height=32,
                fg_color="#2d6cdf",
                hover_color="#2253a8",
                text_color="#ffffff",
            ).pack(fill="x", padx=6, pady=2)

        toplevel.after(50, lambda: toplevel.grab_set())
        toplevel.bind("<FocusOut>", lambda _e: toplevel.destroy())

    def set(self, value: str):
        self._var.set(value)
        try:
            self.button.configure(text=value or "Selecione")
        except Exception:
            pass

    def get(self) -> str:
        return self._var.get()

    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = list(kwargs.pop("values") or [])
        return super().configure(**kwargs)
