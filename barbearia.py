import streamlit as st
from datetime import datetime
import urllib.parse
import database as db
import security as sec

st.set_page_config(page_title="BarberApp", page_icon="✂️", layout="centered")
db.inicializar_banco()

# ==========================================
# GESTÃO DE SESSÃO
# ==========================================
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'perfil': None, 'dados': {}})

status_licenca = sec.checar_licenca()

# Bloqueio do sistema (Apenas o perfil 'deus' consegue ver a trava interna)
if status_licenca == "bloqueado" and st.session_state['perfil'] != 'deus':
    st.error("⚠️ Sistema temporariamente indisponível. Retorne mais tarde.")
    with st.expander("⚙️ Acesso Restrito"):
        senha_god = st.text_input("Senha Mestra:", type="password")
        if senha_god == "adson2026":
            if st.button("Desbloquear"):
                sec.mudar_licenca("ativo")
                st.rerun()
    st.stop()

# ==========================================
# TELA DE LOGIN
# ==========================================
if not st.session_state['logado']:
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=800", use_container_width=True)
    st.title("Bem-vindo ao BarberApp ✂️")
    
    tab_cliente, tab_equipe = st.tabs(["👥 Sou Cliente", "💈 Sou da Equipe / Admin"])
    
    with tab_cliente:
        telefone = st.text_input("Seu WhatsApp (Ex: 43999999999):", max_chars=11)
        if len(telefone) >= 10:
            nome_cadastrado = db.get_cliente(telefone)
            if not nome_cadastrado:
                novo_nome = st.text_input("Primeira vez? Qual o seu nome?")
                if st.button("Entrar"):
                    db.add_cliente(telefone, novo_nome)
                    st.session_state.update({'logado': True, 'perfil': 'cliente', 'dados': {'telefone': telefone, 'nome': novo_nome}})
                    st.rerun()
            else:
                if st.button(f"Entrar como {nome_cadastrado}"):
                    st.session_state.update({'logado': True, 'perfil': 'cliente', 'dados': {'telefone': telefone, 'nome': nome_cadastrado}})
                    st.rerun()
                    
    with tab_equipe:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if usuario == "deus" and senha == "adson2026":
                st.session_state.update({'logado': True, 'perfil': 'deus'})
                st.rerun()
            elif usuario == "dono" and senha == "dono123":
                st.session_state.update({'logado': True, 'perfil': 'dono'})
                st.rerun()
            elif db.verificar_login_barbeiro(usuario, senha):
                st.session_state.update({'logado': True, 'perfil': 'barbeiro', 'dados': {'nome': usuario}})
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    st.stop()

# ==========================================
# NAVEGAÇÃO POR PERFIL
# ==========================================
perfil = st.session_state['perfil']
st.sidebar.title("✂️ BarberApp")

# Mapeamento estrito de quem pode ver o que
telas = {
    "cliente": ["Loja & Agendamento"],
    "barbeiro": ["Painel do Barbeiro"],
    "dono": ["Loja & Agendamento", "Painel do Barbeiro", "Gestão (Dono)"],
    "deus": ["Loja & Agendamento", "Painel do Barbeiro", "Gestão (Dono)"]
}
menu = st.sidebar.radio("Navegação", telas[perfil])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair (Logout)"):
    st.session_state.update({'logado': False, 'perfil': None, 'dados': {}})
    st.rerun()

# EXCLUSIVO ADMIN DEUS: O Dono da loja não vê este bloco de licença
if perfil == 'deus':
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ Admin Agência (DEUS)"):
        status_selecionado = st.selectbox("Status da Licença", ["ativo", "bloqueado"], index=["ativo", "bloqueado"].index(status_licenca))
        if st.button("Atualizar Licença"):
            sec.mudar_licenca(status_selecionado)
            st.rerun()

lista_barbeiros = db.get_barbeiros()
df_catalogo = db.get_catalogo()

# ==========================================
# TELA 1: ÁREA DO CLIENTE / LOJA
# ==========================================
if menu == "Loja & Agendamento":
    st.title("Atendimento & Loja")
    nome_cliente = st.session_state['dados'].get('nome', 'Cliente')
    telefone = st.session_state['dados'].get('telefone', '')
    
    item_selecionado = st.selectbox("O que você deseja hoje?", df_catalogo['item'].tolist())
    detalhes_item = df_catalogo[df_catalogo['item'] == item_selecionado].iloc[0]
    
    st.info(f"**{detalhes_item['tipo']}** | Valor: R$ {detalhes_item['preco']:.2f}")
    
    if detalhes_item['tipo'] == 'Serviço':
        col1, col2 = st.columns(2)
        with col1:
            barbeiro = st.selectbox("Profissional", lista_barbeiros)
        with col2:
            data_escolhida = st.date_input("Data", min_value=datetime.today())
            
        horarios_comerciais = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        ocupados = db.get_horarios_ocupados(barbeiro, str(data_escolhida))
        disponiveis = [h for h in horarios_comerciais if not (data_escolhida == datetime.now().date() and int(h.split(":")[0]) <= datetime.now().hour) and h not in ocupados]
        
        if not disponiveis:
            st.error("Agenda lotada para hoje.")
        else:
            hora = st.selectbox("Horário", disponiveis)
            if st.button("Confirmar Agendamento", type="primary"):
                db.add_agendamento(telefone, nome_cliente, barbeiro, item_selecionado, str(data_escolhida), hora, detalhes_item['preco'])
                st.success("Registrado!")
                msg = f"🔔 *NOVO AGENDAMENTO*\n{nome_cliente} marcou {item_selecionado} com {barbeiro} dia {data_escolhida.strftime('%d/%m')} às {hora}."
                st.markdown(f"### [📲 Enviar Confirmação via WhatsApp](https://wa.me/5571981205061?text={urllib.parse.quote(msg)})")
    else:
        barbeiro = st.selectbox("Quem está te atendendo? (Para comissão)", lista_barbeiros)
        if st.button(f"Confirmar Compra de {detalhes_item['tipo']}", type="primary"):
            db.add_agendamento(telefone, nome_cliente, barbeiro, item_selecionado, str(datetime.today().date()), "N/A", detalhes_item['preco'])
            st.success("Compra registrada na conta do salão!")

# ==========================================
# TELA 2: PAINEL DO BARBEIRO
# ==========================================
elif menu == "Painel do Barbeiro":
    st.title("Sua Fila de Atendimento")
    barbeiro_selecionado = st.session_state['dados']['nome'] if perfil == 'barbeiro' else st.selectbox("Visualizar agenda de:", lista_barbeiros)
    
    df_todos = db.get_todos_agendamentos()
    if not df_todos.empty:
        agenda = df_todos[(df_todos['barbeiro'] == barbeiro_selecionado) & (df_todos['status'] == 'Pendente')]
        
        if agenda.empty:
            st.success("Nenhum atendimento pendente na sua fila.")
        else:
            st.write("### Pendentes")
            st.dataframe(agenda[['id', 'nome', 'item', 'data', 'hora']], hide_index=True)
            
            st.markdown("---")
            st.write("### Dar baixa no atendimento")
            col_id, col_status, col_btn = st.columns([2,2,1])
            with col_id:
                agendamento_id = st.selectbox("ID do Cliente", agenda['id'].tolist())
            with col_status:
                novo_status = st.selectbox("Ação", ["Concluído", "Falta (Não Compareceu)", "Cancelado"])
            with col_btn:
                st.write("") 
                if st.button("Atualizar"):
                    db.atualizar_status(agendamento_id, novo_status)
                    st.success("Baixa realizada!")
                    st.rerun()

# ==========================================
# TELA 3: GESTÃO DO DONO / DEUS (Acesso Completo às Operações)
# ==========================================
elif menu == "Gestão (Dono)":
    st.title("Painel Administrativo")
    tab1, tab2, tab3 = st.tabs(["📊 Faturamento Real", "🛒 Catálogo (Preços)", "👥 Equipe"])
    
    df_todos = db.get_todos_agendamentos()
    
    with tab1:
        st.subheader("Indicadores de Caixa")
        if df_todos.empty:
            st.info("Nenhum registro no banco de dados.")
        else:
            concluidos = df_todos[df_todos['status'] == 'Concluído']
            faltas = df_todos[df_todos['status'] == 'Falta (Não Compareceu)']
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Dinheiro no Caixa", f"R$ {concluidos['valor'].sum():,.2f}")
            col2.metric("Atendimentos Feitos", len(concluidos))
            col3.metric("Prejuízo por Faltas", f"R$ {faltas['valor'].sum():,.2f}")
            
    with tab2:
        st.subheader("Gerenciar Catálogo")
        st.dataframe(df_catalogo, hide_index=True, use_container_width=True)
        
        col_cad, col_exc = st.columns(2)
        
        with col_cad:
            with st.form("form_catalogo"):
                st.write("### Adicionar ou Alterar")
                nome_item = st.text_input("Nome do Item")
                tipo_item = st.selectbox("Categoria", ["Serviço", "Produto", "Assinatura"])
                preco_item = st.number_input("Preço (R$)", min_value=0.0, step=5.0)
                if st.form_submit_button("Salvar no Catálogo"):
                    if nome_item:
                        db.add_item_catalogo(nome_item, tipo_item, preco_item)
                        st.success("Item atualizado!")
                        st.rerun()
                        
        with col_exc:
            st.write("### Remover do Catálogo")
            item_remover = st.selectbox("Selecione o item para deletar:", df_catalogo['item'].tolist(), key="del_item")
            if st.button("❌ Excluir Item permanentemente", type="secondary"):
                db.delete_item_catalogo(item_remover)
                st.success("Item removido do catálogo.")
                st.rerun()
                
    with tab3:
        st.subheader("Gerenciar Equipe")
        st.write(f"Profissionais Ativos: `{', '.join(lista_barbeiros)}`")
        
        col_cad_b, col_exc_b = st.columns(2)
        
        with col_cad_b:
            with st.form("form_equipe"):
                st.write("### Novo Profissional")
                novo_barbeiro = st.text_input("Nome do Barbeiro:")
                senha_barbeiro = st.text_input("Senha de acesso:", type="password")
                if st.form_submit_button("Cadastrar Profissional"):
                    if novo_barbeiro and senha_barbeiro:
                        db.add_barbeiro(novo_barbeiro, senha_barbeiro)
                        st.success("Cadastrado com sucesso!")
                        st.rerun()
                        
        with col_exc_b:
            st.write("### Remover da Equipe")
            barbeiro_remover = st.selectbox("Selecione o barbeiro para desligar:", lista_barbeiros, key="del_barber")
            if st.button("❌ Remover Profissional do Sistema", type="secondary"):
                db.delete_barbeiro(barbeiro_remover)
                st.success("Profissional removido da equipe.")
                st.rerun()