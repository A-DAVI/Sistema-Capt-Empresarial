import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import json
import os

# Aparência padrão
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def format_brl(valor: float) -> str:
    """Formata número em BRL: R$ 1.234,56"""
    try:
        return (
            f"R$ {valor:,.2f}"  # 1,234.56
            .replace(",", "X").replace(".", ",").replace("X", ".")  # 1.234,56
        )
    except Exception:
        return f"R$ {valor:.2f}".replace(".", ",")


class ControleGastosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("Controle de Gastos Empresariais")
        self.geometry("700x650")
        self.resizable(False, False)

        # Arquivo de dados
        self.arquivo_dados = "gastos_empresa.json"
        self.gastos = self.carregar_dados()

        # Criar interface
        self.criar_widgets()

    def criar_widgets(self):
        # Frame principal com padding
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = ctk.CTkLabel(
            main_frame,
            text="Registro de Despesas",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        titulo.pack(pady=(20, 30))

        # Frame de entrada de dados
        entrada_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        entrada_frame.pack(fill="x", padx=20, pady=(0, 20))

        # DATA
        data_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            data_frame,
            text="Data:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self.entry_data = ctk.CTkEntry(
            data_frame,
            placeholder_text="DD/MM/AAAA",
            height=35,
            font=ctk.CTkFont(size=13),
        )
        self.entry_data.pack(fill="x", pady=(5, 0))
        # Preencher com data atual
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # TIPO DE DESPESA
        tipo_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            tipo_frame,
            text="Tipo de Despesa:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        tipos_despesa = [
            "Salários e Encargos",
            "Aluguel",
            "Energia Elétrica",
            "Água",
            "Internet/Telefone",
            "Material de Escritório",
            "Manutenção",
            "Combustível",
            "Alimentação",
            "Marketing",
            "Impostos",
            "Consultoria",
            "Software/Licenças",
            "Equipamentos",
            "Outros",
        ]

        self.combo_tipo = ctk.CTkComboBox(
            tipo_frame,
            values=tipos_despesa,
            height=35,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.combo_tipo.pack(fill="x", pady=(5, 0))
        self.combo_tipo.set("Selecione o tipo")

        # FORMA DE PAGAMENTO
        pagamento_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        pagamento_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            pagamento_frame,
            text="Forma de Pagamento:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        formas_pagamento = [
            "Dinheiro",
            "Cartão de Crédito",
            "Cartão de Débito",
            "PIX",
            "Transferência Bancária",
            "Boleto",
            "Cheque",
        ]

        self.combo_pagamento = ctk.CTkComboBox(
            pagamento_frame,
            values=formas_pagamento,
            height=35,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.combo_pagamento.pack(fill="x", pady=(5, 0))
        self.combo_pagamento.set("Selecione a forma")

        # VALOR
        valor_frame = ctk.CTkFrame(entrada_frame, fg_color="transparent")
        valor_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            valor_frame,
            text="Valor (R$):",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self.entry_valor = ctk.CTkEntry(
            valor_frame,
            placeholder_text="0,00",
            height=35,
            font=ctk.CTkFont(size=13),
        )
        self.entry_valor.pack(fill="x", pady=(5, 0))

        # Frame de botões
        botoes_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            botoes_frame,
            text="Salvar Despesa",
            command=self.salvar_despesa,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
        )
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Botão Limpar
        self.btn_limpar = ctk.CTkButton(
            botoes_frame,
            text="Limpar Campos",
            command=self.limpar_campos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
        )
        self.btn_limpar.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Frame de estatísticas
        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            stats_frame,
            text="Resumo",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(15, 10))

        # Labels de estatísticas
        self.label_total = ctk.CTkLabel(
            stats_frame,
            text="Total de Despesas: R$ 0,00",
            font=ctk.CTkFont(size=13),
        )
        self.label_total.pack(pady=5)

        self.label_quantidade = ctk.CTkLabel(
            stats_frame,
            text="Quantidade de Registros: 0",
            font=ctk.CTkFont(size=13),
        )
        self.label_quantidade.pack(pady=(5, 15))

        # Botão Ver Relatório
        self.btn_relatorio = ctk.CTkButton(
            main_frame,
            text="Ver Relatório Completo",
            command=self.mostrar_relatorio,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
        )
        self.btn_relatorio.pack(fill="x", padx=20, pady=(0, 20))

        # Atualizar estatísticas
        self.atualizar_stats()

    def validar_data(self, data_str: str) -> bool:
        """Valida formato de data DD/MM/AAAA"""
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def validar_valor(self, valor_str: str):
        """Valida e converte valor monetário"""
        try:
            # Remove espaços e substitui vírgula por ponto
            valor_str = valor_str.strip().replace(",", ".")
            valor = float(valor_str)
            if valor <= 0:
                return None
            return valor
        except ValueError:
            return None

    def salvar_despesa(self):
        """Salva a despesa no arquivo JSON"""
        # Validar campos
        data = self.entry_data.get().strip()
        tipo = self.combo_tipo.get()
        pagamento = self.combo_pagamento.get()
        valor_str = self.entry_valor.get().strip()

        # Validações
        if not self.validar_data(data):
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA.")
            return

        if tipo == "Selecione o tipo":
            messagebox.showerror("Erro", "Selecione um tipo de despesa!")
            return

        if pagamento == "Selecione a forma":
            messagebox.showerror("Erro", "Selecione uma forma de pagamento!")
            return

        valor = self.validar_valor(valor_str)
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido! Digite um número maior que zero.")
            return

        # Criar registro
        registro = {
            "data": data,
            "tipo": tipo,
            "forma_pagamento": pagamento,
            "valor": valor,
            "timestamp": datetime.now().isoformat(),
        }

        # Adicionar aos gastos
        self.gastos.append(registro)

        # Salvar no arquivo
        self.salvar_dados()

        # Atualizar estatísticas
        self.atualizar_stats()

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso",
            f"Despesa de {format_brl(valor)} registrada com sucesso!",
        )

        # Limpar campos
        self.limpar_campos()

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.combo_tipo.set("Selecione o tipo")
        self.combo_pagamento.set("Selecione a forma")
        self.entry_valor.delete(0, "end")

    def atualizar_stats(self):
        """Atualiza as estatísticas na interface"""
        total = 0.0
        if isinstance(self.gastos, list):
            total = sum(
                (g.get("valor", 0.0) if isinstance(g, dict) else 0.0)
                for g in self.gastos
            )
            quantidade = len(self.gastos)
        else:
            quantidade = 0

        self.label_total.configure(text=f"Total de Despesas: {format_brl(total)}")
        self.label_quantidade.configure(text=f"Quantidade de Registros: {quantidade}")

    def mostrar_relatorio(self):
        """Mostra janela com relatório completo"""
        if not self.gastos:
            messagebox.showinfo("Info", "Nenhuma despesa registrada ainda.")
            return

        # Criar janela de relatório
        relatorio_window = ctk.CTkToplevel(self)
        relatorio_window.title("Relatório de Despesas")
        relatorio_window.geometry("800x600")

        # Título
        ctk.CTkLabel(
            relatorio_window,
            text="Relatório Completo de Despesas",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=20)

        # Frame com scrollbar
        scroll_frame = ctk.CTkScrollableFrame(
            relatorio_window,
            width=750,
            height=450,
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Ordenar por data (mais recente primeiro)
        try:
            gastos_ordenados = sorted(
                self.gastos,
                key=lambda x: datetime.strptime(x.get("data", "01/01/1970"), "%d/%m/%Y"),
                reverse=True,
            )
        except Exception:
            gastos_ordenados = list(self.gastos)

        # Mostrar cada gasto
        for i, gasto in enumerate(gastos_ordenados, 1):
            gasto_frame = ctk.CTkFrame(scroll_frame)
            gasto_frame.pack(fill="x", padx=10, pady=5)

            valor_fmt = format_brl(gasto.get("valor", 0.0))
            info_text = (
                f"{i}. Data: {gasto.get('data', '')}\n"
                f"   Tipo: {gasto.get('tipo', '')}\n"
                f"   Forma: {gasto.get('forma_pagamento', '')}\n"
                f"   Valor: {valor_fmt}"
            )

            ctk.CTkLabel(
                gasto_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                justify="left",
            ).pack(anchor="w", padx=15, pady=10)

        # Botão fechar
        ctk.CTkButton(
            relatorio_window,
            text="Fechar",
            command=relatorio_window.destroy,
            height=35,
        ).pack(pady=(0, 20))

    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                return dados if isinstance(dados, list) else []
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        try:
            with open(self.arquivo_dados, "w", encoding="utf-8") as f:
                json.dump(self.gastos, f, indent=2, ensure_ascii=False)
        except OSError:
            messagebox.showerror(
                "Erro",
                "Não foi possível salvar os dados em disco.",
            )


# Executar aplicação
if __name__ == "__main__":
    app = ControleGastosApp()
    app.mainloop()

