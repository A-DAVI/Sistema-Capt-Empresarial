![Banner](https://github.com/A-DAVI/Sistema-Capt-Empresarial/blob/master/logo_empresa.png)

# 💼 Sistema de Controle de Gastos Empresariais

Este sistema foi desenvolvido com o objetivo de facilitar o registro, visualização e gerenciamento de despesas empresariais, oferecendo uma interface moderna, organizada e compatível com ambientes corporativos.

---

## 📌 1. Objetivo

Fornecer uma ferramenta simples e eficiente para:

- Registrar despesas com data, tipo, forma de pagamento e valor.
- Gerenciar lançamentos existentes (edição e exclusão).
- Aplicar filtros rápidos por múltiplos critérios.
- Obter resumo financeiro consolidado.
- Gerar relatórios em PDF com layout profissional.

---

## 📌 2. Funcionalidades Principais

### **Registro**
- Inserção rápida de dados.
- Campos padronizados para manter consistência.
- Timestamp automático para auditoria.

### **Gestão**
- Listagem ordenada por data.
- Filtros por:
  - Data
  - Tipo
  - Forma de pagamento
  - Faixa de valor
- Edição com validação.
- Exclusão segura com confirmação.

### **Relatórios**
- Visualização completa dentro do sistema.
- Exportação em PDF contendo:
  - Cabeçalho institucional
  - Total e quantidade de despesas
  - Tabela organizada
  - Logo da empresa (opcional)

---

## 📌 3. Tecnologias Utilizadas

- **Python 3.10+**
- **CustomTkinter** — Interface moderna e responsiva.
- **ReportLab** — Geração de relatórios em PDF.
- **JSON** — Persistência de dados local.
- Arquitetura **modular** (UI / Data / Utils).

---

## 📌 4. Estrutura do Projeto

```
Sistema-Capt-Empresarial/
│
├── app/
│   ├── data/
│   │   ├── store.py               # Leitura/gravação + mock dev
│   │   └── ...
│   │
│   ├── ui/
│   │   ├── app.py                 # Interface principal
│   │   ├── widgets.py             # Componentes reutilizáveis
│   │   └── ...
│   │
│   ├── utils/
│   │   ├── formatting.py          # Formatação (BRL, datas, validações)
│   │   ├── report.py              # Geração de PDF
│   │   └── ...
│
├── relatorios/
│   └── relatorio_despesas.pdf     # PDF gerado automaticamente
│
├── INTERFACE.py                   # Entry point do sistema
└── README.md
```

---

## 📌 5. Como Executar

### 🧩 Instalar dependências
```bash
pip install -r requirements.txt
```

### ▶️ Executar o sistema
```bash
python INTERFACE.py
```

---

## 📌 6. Modo Desenvolvedor (Mock de Dados)

O projeto possui um modo especial que carrega dados fictícios para testes internos.

### Ativar
```bash
# Windows PowerShell
$Env:APP_ENV = "dev"

# Linux/Mac
export APP_ENV=dev

python INTERFACE.py
```

### Resultado
O sistema é carregado com uma lista de despesas simuladas — útil para testes de UI, relatório e fluxo geral.

---

## 📌 7. Relatório em PDF

O PDF é gerado automaticamente em:

```bash
relatorios/relatorio_despesas.pdf
```

### O documento inclui:
- Nome da empresa  
- Data/hora de geração  
- Resumo geral  
- Tabela das despesas  
- Logo institucional (se existir `logo_empresa.png`)

---

## 📌 8. Roadmap (Melhorias Futuras)
- [ ] Exportação para Excel/CSV  
- [ ] Dashboard com gráficos  
- [ ] Login e controle de usuários  
- [ ] Backup automático  
- [ ] Integração com sistemas contábeis  

---

## 📌 9. Autor

**Desenvolvido por:**  
**Davi Cassoli Lira**  
Departamento de Tecnologia — **Escritório Grupo 14D • 2025**

🔗 GitHub: [A-DAVI](https://github.com/A-DAVI)  
📧 Contato: tecnologiagrupo14d@gmail.com

---

<p align="center">
  <sub>© 2025 GRUPO 14D — Todos os direitos reservados.</sub>
</p>
