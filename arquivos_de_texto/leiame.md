# ✂️ BarberApp - Plataforma de Agendamento e Gestão

Um sistema completo desenvolvido para modernizar o fluxo de agendamentos e a gestão financeira de barbearias e salões de beleza. Arquitetura modular construída em Python com foco em segurança, persistência de dados e inteligência de negócios.

---

## 🚀 Funcionalidades e Regras de Negócio

### 1. Área do Cliente (Front-end)
* **Identificação Segura:** Login utilizando o número do WhatsApp com criação de perfil automático.
* **Agendamento Inteligente (Google Calendar-like):** * O sistema varre a agenda do profissional e oculta horários ocupados.
  * **Trava Temporal:** Bloqueio automático de agendamentos retroativos (impede marcar horários que já passaram no dia atual).
* **Integração WhatsApp:** Geração de *Deep Link* dinâmico que abre o aplicativo com o comprovante de agendamento pronto para envio.

### 2. Gestão Administrativa e BI (Back-office)
* **Visão Financeira (Business Intelligence):** Cálculo automático de Faturamento, Serviços Ativos e Desempenho por Barbeiro, isolando serviços cancelados.
* **Controle de Status:** Atualização de fluxo de caixa (Pendente, Concluído, Cancelado) alterando os indicadores em tempo real.
* **Gestão de Equipe:** Módulo dinâmico para cadastro de novos profissionais.

---

## 🛡️ Arquitetura, Banco de Dados e Segurança

O projeto foi refatorado utilizando o padrão de separação de responsabilidades (Modularização):

* **`app.py`**: Motor principal da aplicação e renderização de interface (Streamlit).
* **`database.py`**: Módulo exclusivo para comunicação com o banco de dados **SQLite3**. Implementa *Queries Parametrizadas* para bloqueio total contra ataques de *SQL Injection*.
* **`security.py`**: Módulo de criptografia (Hashed Passwords via `hashlib`) e **Role-Based Access Control (RBAC)** oculto para a Agência desenvolvedora. Possui um *Kill Switch* remoto para suspensão de licença por inadimplência.
* **`barbearia.db`**: Banco de dados relacional persistente contendo as tabelas: `clientes`, `barbeiros` e `agendamentos`.

Desenvolvido por Adson - Unindo engenharia de software e gestão estratégica.