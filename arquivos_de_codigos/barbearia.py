import streamlit as st
from datetime import datetime
import urllib.parse
import database as db
import security as sec

# Inicializa banco de dados
db.inicializar_banco()

st.set_page_config(page_title="BarberApp", page_icon="✂️", layout="centered")

# Validação de Segurança (Kill Switch)
sec.painel_agencia()

# Variáveis Globais
tabela_precos = {"Corte": 40.0, "Barba": 30.0, "Corte + Barba": 65.0, "Platinado": 120.0}
horarios_comerciais = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
lista_barbeiros = db.get_barbeiros()

# ==========================================
# MENU LATERAL
# ==========================================
st.sidebar.title("✂️ BarberApp")
st.sidebar.image("https://images.unsplash.com/photo-1585747860715-2ba37e788b70?q=80&w=500", use_container_width=True)
menu = st.sidebar.radio("Navegação", ["Área do Cliente", "Painel do Barbeiro", "Gestão (Dono)"])

# ==========================================
# TELA 1: ÁREA DO CLIENTE
# ==========================================
if menu == "Área do Cliente":
    st.title("Agende seu Horário")
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=800", use_container_width=True)
    
    telefone = st.text_input("Seu WhatsApp (Ex: 43999999999):", max_chars=11)
    
    if len(telefone) >= 10:
        nome_cliente = db.get_cliente(telefone)
        
        if not nome_cliente:
            st.info("Primeira vez aqui? Como podemos te chamar?")
            novo_nome = st.text_input("Seu Nome:")
            if st.button("Criar Cadastro"):
                db.add_cliente(telefone, novo_nome)
                st.rerun()
        else:
            st.success(f"Bem-vindo de volta, {nome_cliente}!")
            col1, col2 = st.columns(2)
            with col1:
                barbeiro = st.selectbox("Barbeiro", lista_barbeiros)
            with col2:
                data_escolhida = st.date_input("Data", min_value=datetime.today())
            
            # Lógica: Filtra horários ocupados e horários no passado
            horarios_ocupados = db.get_horarios_ocupados(barbeiro, str(data_escolhida))
            horarios_disponiveis = []
            
            agora = datetime.now()
            
            for h in horarios_comerciais:
                # Se for hoje, bloqueia horários que já passaram
                if data_escolhida == agora.date():
                    hora_int = int(h.split(":")[0])
                    if hora_int <= agora.hour:
                        continue 
                # Se não estiver ocupado, adiciona na lista
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
                    
                    # Link WhatsApp 
                    tel_teste = "5571981205061"
                    msg = f"🔔 *NOVO AGENDAMENTO*\nCliente: {nome_cliente}\nServiço: {servico} com {barbeiro}\nData: {data_escolhida.strftime('%d/%m')} às {hora}\nStatus: PENDENTE."
                    link_wpp = f"https://wa.me/{tel_teste}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"### [📲 Enviar Confirmação via WhatsApp]({link_wpp})")

# ==========================================
# TELA 2: PAINEL DO BARBEIRO
# ==========================================
elif menu == "Painel do Barbeiro":
    st.title("Sua Agenda")
    barbeiro_selecionado = st.selectbox("Selecione seu perfil:", lista_barbeiros)
    
    df_todos = db.get_todos_agendamentos()
    if not df_todos.empty:
        agenda = df_todos[(df_todos['barbeiro'] == barbeiro_selecionado) & (df_todos['status'] != 'Cancelado')]
        if agenda.empty:
            st.warning("Sem clientes agendados.")
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
            # Faturamento APENAS de serviços concluídos ou pendentes (ignora cancelados)
            df_valido = df_todos[df_todos['status'] != 'Cancelado']
            faturamento = df_valido['valor'].sum()
            col1, col2 = st.columns(2)
            col1.metric("Faturamento Esperado/Realizado", f"R$ {faturamento:,.2f}")
            col2.metric("Serviços Ativos", len(df_valido))
            
    with tab2:
        st.subheader("Atualizar Status de Serviço")
        if not df_todos.empty:
            agendamento_id = st.selectbox("Selecione o ID do agendamento", df_todos['id'].tolist())
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
                st.success("Cadastrado!")
                st.rerun()
            else:
                st.error("Erro ou já cadastrado.")