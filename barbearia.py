import streamlit as st
from datetime import datetime
import urllib.parse
import database as db
import security as sec

# Configuração da página e inicialização
st.set_page_config(page_title="BarberApp", page_icon="✂️", layout="centered")
db.inicializar_banco()

# ==========================================
# GESTÃO DE SESSÃO (LOGIN)
# ==========================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['perfil'] = None
    st.session_state['dados'] = {}

# ==========================================
# VERIFICAÇÃO DE LICENÇA (KILL SWITCH)
# ==========================================
# Proteção invisível: O cliente só vê um aviso genérico se você bloquear o sistema.
status_licenca = sec.checar_licenca()
if status_licenca == "bloqueado" and st.session_state['perfil'] != 'dono':
    st.error("⚠️ Sistema temporariamente indisponível. Retorne mais tarde.")
    
    # Campo escondido para você (dono da agência) conseguir destravar mesmo bloqueado
    with st.expander("⚙️ Acesso Restrito"):
        senha_god = st.text_input("Senha Mestra:", type="password")
        if senha_god == "adson2026":
            novo_status = st.selectbox("Status", ["ativo", "bloqueado"])
            if st.button("Salvar Status"):
                sec.mudar_licenca(novo_status)
                st.rerun()
    st.stop() # Interrompe o código aqui. Ninguém acessa nada.

# ==========================================
# TELA DE LOGIN 
# ==========================================
if not st.session_state['logado']:
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=800", use_container_width=True)
    st.title("Bem-vindo ao BarberApp ✂️")
    
    tab_cliente, tab_equipe = st.tabs(["👥 Sou Cliente", "💈 Sou da Equipe / Admin"])
    
    with tab_cliente:
        st.write("Identifique-se para agendar seu horário.")
        telefone = st.text_input("Seu WhatsApp (Ex: 43999999999):", max_chars=11)
        if len(telefone) >= 10:
            nome_cadastrado = db.get_cliente(telefone)
            if not nome_cadastrado:
                st.info("Primeira vez aqui? Qual o seu nome?")
                novo_nome = st.text_input("Nome:")
                if st.button("Criar Cadastro e Entrar"):
                    db.add_cliente(telefone, novo_nome)
                    st.session_state['logado'] = True
                    st.session_state['perfil'] = 'cliente'
                    st.session_state['dados'] = {'telefone': telefone, 'nome': novo_nome}
                    st.rerun()
            else:
                if st.button(f"Entrar como {nome_cadastrado}"):
                    st.session_state['logado'] = True
                    st.session_state['perfil'] = 'cliente'
                    st.session_state['dados'] = {'telefone': telefone, 'nome': nome_cadastrado}
                    st.rerun()
                    
    with tab_equipe:
        st.write("Acesso restrito para profissionais e gestão.")
        usuario = st.text_input("Usuário (Nome do Barbeiro ou 'admin')")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Acessar"):
            if usuario == "admin" and senha == "adson2026":
                st.session_state['logado'] = True
                st.session_state['perfil'] = 'dono'
                st.rerun()
            elif usuario in db.get_barbeiros() and senha == "1234":
                st.session_state['logado'] = True
                st.session_state['perfil'] = 'barbeiro'
                st.session_state['dados'] = {'nome': usuario}
                st.rerun()
            else:
                st.error("Credenciais inválidas. (Dica: A senha padrão de barbeiro é 1234)")
                
    st.stop() # Se não estiver logado, a tela para por aqui.

# ==========================================
# SISTEMA LOGADO (Navegação Isolada)
# ==========================================
perfil = st.session_state['perfil']

st.sidebar.title("✂️ BarberApp")
st.sidebar.image("https://images.unsplash.com/photo-1585747860715-2ba37e788b70?q=80&w=500", use_container_width=True)

# Define estritamente quais telas o perfil pode ver no menu lateral
telas_permitidas = []
if perfil == 'cliente':
    telas_permitidas = ["Área do Cliente"]
elif perfil == 'barbeiro':
    telas_permitidas = ["Painel do Barbeiro"]
elif perfil == 'dono':
    telas_permitidas = ["Área do Cliente", "Painel do Barbeiro", "Gestão (Dono)"]

menu = st.sidebar.radio("Navegação", telas_permitidas)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair (Logout)"):
    st.session_state['logado'] = False
    st.session_state['perfil'] = None
    st.session_state['dados'] = {}
    st.rerun()

# Acesso Divindade renderiza apenas se o perfil for o Dono (Agência/Admin)
if perfil == 'dono':
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ Admin Agência"):
        status_selecionado = st.selectbox(
            "Status da Licença", 
            ["ativo", "bloqueado"], 
            index=["ativo", "bloqueado"].index(status_licenca)
        )
        if st.button("Atualizar Licença"):
            sec.mudar_licenca(status_selecionado)
            st.rerun()

# Variáveis globais carregadas para as telas
tabela_precos = {"Corte": 40.0, "Barba": 30.0, "Corte + Barba": 65.0, "Platinado": 120.0}
horarios_comerciais = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
lista_barbeiros = db.get_barbeiros()

# ==========================================
# TELA 1: ÁREA DO CLIENTE
# ==========================================
if menu == "Área do Cliente":
    st.title("Agende seu Horário")
    nome_cliente = st.session_state['dados'].get('nome', 'Cliente')
    telefone = st.session_state['dados'].get('telefone', '')
    
    st.success(f"Olá, {nome_cliente}! Escolha os detalhes do seu atendimento.")
    
    col1, col2 = st.columns(2)
    with col1:
        barbeiro = st.selectbox("Profissional", lista_barbeiros)
    with col2:
        data_escolhida = st.date_input("Data", min_value=datetime.today())
    
    horarios_ocupados = db.get_horarios_ocupados(barbeiro, str(data_escolhida))
    horarios_disponiveis = []
    agora = datetime.now()
    
    for h in horarios_comerciais:
        if data_escolhida == agora.date():
            hora_int = int(h.split(":")[0])
            if hora_int <= agora.hour:
                continue 
        if h not in horarios_ocupados:
            horarios_disponiveis.append(h)
    
    if not horarios_disponiveis:
        st.error("Agenda lotada ou horários indisponíveis para hoje. Escolha outra data.")
    else:
        col3, col4 = st.columns(2)
        with col3:
            servico = st.selectbox("Serviço", list(tabela_precos.keys()))
        with col4:
            hora = st.selectbox("Horário", horarios_disponiveis)
        
        valor = tabela_precos[servico]
        st.info(f"**Valor total:** R$ {valor:.2f}")
        
        if st.button("Confirmar Agendamento", type="primary"):
            db.add_agendamento(telefone, nome_cliente, barbeiro, servico, str(data_escolhida), hora, valor)
            st.success("Agendamento registrado!")
            
            tel_teste = "5571981205061"
            msg = f"🔔 *NOVO AGENDAMENTO*\nCliente: {nome_cliente}\nServiço: {servico} com {barbeiro}\nData: {data_escolhida.strftime('%d/%m')} às {hora}\nStatus: PENDENTE."
            link_wpp = f"https://wa.me/{tel_teste}?text={urllib.parse.quote(msg)}"
            st.markdown(f"### [📲 Enviar Confirmação via WhatsApp]({link_wpp})")

# ==========================================
# TELA 2: PAINEL DO BARBEIRO
# ==========================================
elif menu == "Painel do Barbeiro":
    st.title("Sua Agenda")
    
    # Trava a visualização: Barbeiro só vê a própria agenda; Dono pode visualizar qualquer um.
    if perfil == 'barbeiro':
        barbeiro_selecionado = st.session_state['dados']['nome']
        st.subheader(f"Profissional: {barbeiro_selecionado}")
    else:
        barbeiro_selecionado = st.selectbox("Visualizar agenda de:", lista_barbeiros)
    
    df_todos = db.get_todos_agendamentos()
    if not df_todos.empty:
        agenda = df_todos[(df_todos['barbeiro'] == barbeiro_selecionado) & (df_todos['status'] != 'Cancelado')]
        if agenda.empty:
            st.warning("Nenhum cliente agendado para você ainda.")
        else:
            agenda = agenda.sort_values(by=['data', 'hora'])
            st.dataframe(agenda[['nome', 'telefone', 'servico', 'data', 'hora', 'status']], hide_index=True)

# ==========================================
# TELA 3: GESTÃO DO DONO
# ==========================================
elif menu == "Gestão (Dono)":
    st.title("Painel Administrativo")
    tab1, tab2, tab3 = st.tabs(["📊 Faturamento", "⚙️ Status", "👥 Equipe"])
    
    df_todos = db.get_todos_agendamentos()
    
    with tab1:
        st.subheader("Visão Estratégica")
        if df_todos.empty:
            st.info("Nenhum dado.")
        else:
            df_valido = df_todos[df_todos['status'] != 'Cancelado']
            faturamento = df_valido['valor'].sum()
            col1, col2 = st.columns(2)
            col1.metric("Faturamento Esperado/Realizado", f"R$ {faturamento:,.2f}")
            col2.metric("Serviços Ativos", len(df_valido))
            
    with tab2:
        st.subheader("Atualizar Status de Serviço")
        if not df_todos.empty:
            agendamento_id = st.selectbox("ID do Agendamento", df_todos['id'].tolist())
            novo_status = st.radio("Status", ["Pendente", "Concluído", "Cancelado"], horizontal=True)
            if st.button("Salvar Status"):
                db.atualizar_status(agendamento_id, novo_status)
                st.success("Status atualizado!")
                st.rerun()
                
    with tab3:
        st.subheader("Equipe")
        st.write(f"Ativos: {', '.join(lista_barbeiros)}")
        novo_barbeiro = st.text_input("Novo profissional:")
        if st.button("Cadastrar"):
            if db.add_barbeiro(novo_barbeiro):
                st.success("Cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ou profissional já cadastrado.")