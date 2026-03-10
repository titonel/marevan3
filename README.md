# Linha de Cuidado de Anticoagulação (Marevan 3.0)

Este projeto é um sistema web desenvolvido para a gestão e monitoramento de pacientes em terapia de anticoagulação oral (uso de Marevan/Varfarina). Originalmente implementado no AME Caraguatatuba, o sistema foi migrado para **Django** para garantir maior robustez, rastreabilidade e segurança da informação através de Controle de Acesso Baseado em Perfis (RBAC).

## 🚀 Funcionalidades Principais

* **Gestão de Pacientes**: Cadastro completo de pacientes, incluindo dados demográficos, indicação clínica e metas terapêuticas (Alvo de INR).
* **Registro de Atendimentos (INR)**: Lançamento de resultados de exames de Tempo de Protrombina (INR) com registro automático do profissional responsável pela medição (rastreabilidade).
* **Painel de Monitoramento (Dashboard)**: Visão gerencial com KPIs de qualidade, estratificação de pacientes no tempo alvo terapêutico (TTR) e distribuição demográfica.
* **Controle de Acesso (RBAC)**:
  * **Administração/Coordenação**: Acesso total ao sistema, gestão de usuários e métricas globais.
  * **Equipe Assistencial (Médicos, Enfermeiros, Farmacêuticos)**: Permissão para realizar atendimentos, registrar INR e visualizar prontuários.
* **Segurança Reforçada**: Exigência de troca de senha no primeiro acesso e validação de senhas fortes.

## 🛠️ Tecnologias Utilizadas

* **Backend**: Python 3.x, Django 5.x
* **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript, Chart.js (Dashboard)
* **Banco de Dados**: SQLite (padrão para fácil implantação, podendo ser migrado para PostgreSQL/MySQL em produção).

---

## ⚙️ Implantação em Novas Unidades

O guia abaixo descreve os comandos essenciais para configurar o ambiente de desenvolvimento/produção local em qualquer unidade.

### 1. Preparando o Ambiente

Certifique-se de ter o [Python](https://www.python.org/downloads/) instalado na máquina (versão 3.14 ou superior recomendada). 

Abra o terminal na pasta onde deseja instalar o sistema e clone/baixe o repositório.

### 2. Criação do Ambiente Virtual (VENV)
É altamente recomendável isolar as dependências do projeto usando um ambiente virtual.

```bash
# Cria o ambiente virtual chamado 'venv'
python -m venv venv

# Ativa o ambiente virtual (Windows)
venv\Scripts\activate

# Ativa o ambiente virtual (Linux/Mac)
source venv/bin/activate