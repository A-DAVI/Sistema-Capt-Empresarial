# Sistema de Controle de Gastos Empresariais

Este projeto foi desenvolvido com o objetivo de fornecer uma solução interna para registro, gestão e análise de despesas empresariais.  
A aplicação permite centralizar lançamentos financeiros, gerar relatórios completos e exportar documentos em PDF com identificação da empresa.

---

## 1. Objetivo do Projeto

Criar uma ferramenta simples, eficiente e visualmente organizada para:

- Registrar despesas com informações detalhadas.
- Consultar e editar lançamentos já existentes.
- Aplicar filtros por data, tipo, forma de pagamento e faixa de valor.
- Gerar relatórios completos para análise administrativa.
- Exportar relatórios em formato PDF para fins de documentação e envio.

---

## 2. Principais Funcionalidades

### **Registro de Despesas**
- Data
- Tipo de despesa
- Forma de pagamento
- Valor
- Registro automático de horário (timestamp)

### **Gestão Completa**
- Listagem de todas as despesas em ordem cronológica
- Filtros simples e combinados
- Edição de lançamentos
- Exclusão de registros
- Resumo geral (total e quantidade)

### **Relatórios**
- Relatório completo exibido em nova janela
- Exportação em PDF com:
  - Identificação da empresa
  - Data de geração
  - Resumo geral
  - Tabela detalhada das despesas
  - Layout profissional (título, colunas, alinhamento e formatação em BRL)

---

## 3. Tecnologias Utilizadas

- **Python 3.10+**
- **CustomTkinter** (interface gráfica moderna)
- **ReportLab** (geração de PDF)
- **JSON** para persistência local dos dados
- Estrutura modular com diretórios:
  - `app/ui/`
  - `app/data/`
  - `app/utils/`

---

## 4. Estrutura do Projeto

Sistema-Capt-Empresarial/
│
├── app/
│ ├── data/ # Armazenamento e manipulação dos dados
│ ├── ui/ # Interface gráfica e telas do sistema
│ ├── utils/ # Funções auxiliares (formatação, relatórios)
│ └── ...
│
├── relatorios/ # PDF gerados pelo sistema
├── INTERFACE.py # Arquivo principal de inicialização
└── README.md

yaml
Copiar código

---

## 5. Como Executar

### Pré-requisitos
Certifique-se de ter o Python instalado.

### Instalar dependências
```bash
pip install -r requirements.txt
Executar o sistema
bash
Copiar código
python INTERFACE.py
Modo desenvolvedor (opcional)
Utiliza dados mockados em vez do arquivo real.

bash
Copiar código
export APP_ENV=dev  # Linux / Git Bash
python INTERFACE.py
6. Exportação de PDF
O relatório em PDF é gerado automaticamente em:

bash
Copiar código
/relatorios/relatorio_despesas.pdf
O documento contém:

Cabeçalho da empresa

Data de emissão

Resumo financeiro

Tabela completa dos lançamentos

Formatação profissional

7. Próximas Melhorias (Roadmap)
Exportação para CSV/Excel

Dashboard com gráficos e indicadores

Controle multiusuário (login)

Backup automático de dados

Integração direta com softwares contábeis

8. Autor
Desenvolvido internamente por
Davi Cassoli Lira
Departamento de Automação / Sistemas
2025
