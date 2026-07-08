# ✂️ BarberApp - Plataforma de Agendamento, Vendas e Gestão Multi-Admin

Um ecossistema completo de software desenvolvido para modernizar o fluxo de agendamentos, o controlo de stock de produtos, a gestão de assinaturas mensais e a análise financeira de barbearias e salões de beleza. Construído com uma arquitetura modular em Python, focada em segurança estrita, persistência de dados relacional e isolamento completo de privilégios.

---

## 👥 Níveis de Acesso e Permissões (RBAC)

O sistema implementa um controlo de acesso baseado em funções (Role-Based Access Control) para garantir a segurança da operação e blindar o modelo de negócios da agência desenvolvedora:

1. **Admin Deus (Desenvolvedor/Agência):**
 
   * **Permissões:** Acesso total a todas as operações comerciais, financeiras e de equipa, além do controlo exclusivo do painel de licenciamento (*Kill Switch*), permitindo suspender ou ativar o sistema remotamente.
2. **Admin Dono (Proprietário do Estabelecimento):**
 
   * **Permissões:** Acesso completo aos painéis financeiros de faturação, gestão total do catálogo de preços e stock, e controlo da equipa (adicionar e remover barbeiros). Não possui visibilidade nem permissão sobre o estado da licença do software.
3. **Equipe (Barbeiros):**
  
   * **Permissões:** Acesso exclusivo à sua própria fila de atendimento para o dia atual. Permite dar baixa nos serviços (marcar como Concluído, Cancelado ou Falta).
4. **Clientes:**
   * **Credenciais:** Número de WhatsApp.
   * **Permissões:** Visualização do catálogo de serviços, escolha de profissionais e agendamento de horários livres, com bloqueio automático de retroativos (passados).

---

## 🚀 Funcionalidades e Regras de Negócio

### 🛒 Loja & Catálogo Dinâmico
* **Flexibilidade Operacional:** O preço de qualquer item deixou de ser estático no código. Agora, o proprietário pode alterar valores e cadastrar novos itens diretamente pela interface.
* **Diversificação de Receita:** Suporte integrado para três categorias distintas:
  * **Serviços:** Exigem escolha de profissional, data e horário livre.
  * **Produtos:** Vendas físicas diretas no balcão (pomadas, óleos, etc.) com atribuição de comissão ao barbeiro atendente.
  * **Assinaturas:** Planos de recorrência mensal para fidelização de clientes.

### 📊 Painel de Faturamento Real & Auditoria
* **Dinheiro no Caixa:** O gráfico de faturação calcula estritamente os valores dos agendamentos marcados como "Concluído", refletindo o fluxo de caixa real.
* **Prejuízo por Faltas:** Contabilidade isolada de valores perdidos devido a clientes que faltaram (*No-show*), permitindo ao gestor tomar decisões estratégicas para reduzir a ociosidade.

---

## 🛡️ Arquitetura de Ficheiros do Projeto

O projeto adota o padrão de separação de responsabilidades para simplificar manutenções futuras:

* **`barbearia.py`**: Interface gráfica (Front-end) desenvolvida em Streamlit. Orquestra a navegação e exibe os ecrãs de acordo com o perfil autenticado.
* **`database.py`**: Camada de persistência de dados (Back-end) utilizando **SQLite3**. Todas as operações de leitura e escrita utilizam *Queries Parametrizadas* (`?`) para neutralizar por completo vulnerabilidades de *SQL Injection*.
* **`security.py`**: Módulo central de criptografia e validação do ficheiro de licença local.

---

## ⚙️ Como Executar e Implantar

1. Garanta que todas as dependências estão listadas no ficheiro raiz:
   ```text
   streamlit
   pandas
Instale localmente:

Bash
pip install -r requirements.txt
Execute a aplicação:

Bash
streamlit run barbearia.py
Desenvolvido por Adson - Soluções Tecnológicas e Gestão Estratégica.


---

### 2. Comandos Finais no Terminal para Concluir o Projeto

Com o ficheiro `README.md` guardado com as novas informações, feche o VS Code e envie esta última atualização de documentação para o GitHub. Corra estes três comandos no terminal:

```bash
git add README.md
git commit -m "Documentação final do ecossistema atualizada com sucesso"
git push origin main