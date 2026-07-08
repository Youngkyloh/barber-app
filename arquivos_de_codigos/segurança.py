import os
import hashlib
import streamlit as st

# A senha "adson2026" criptografada (Ninguém consegue ler isso olhando o código)
SENHA_MESTRA_HASH = "81c0c1b48b11fbfe84d0ab02cd7bc84b55eaf17bcfb9292cbe341be9cb3e1c68"

def verificar_senha(senha_digitada):
    hash_digitado = hashlib.sha256(senha_digitada.encode()).hexdigest()
    return hash_digitado == SENHA_MESTRA_HASH

def checar_licenca():
    if not os.path.exists("licenca.txt"):
        with open("licenca.txt", "w") as f:
            f.write("ativo") 
    with open("licenca.txt", "r") as f:
        return f.read().strip()

def mudar_licenca(novo_status):
    with open("licenca.txt", "w") as f:
        f.write(novo_status)

def painel_agencia():
    status_atual = checar_licenca()
    
    if status_atual == "bloqueado":
        st.error("⚠️ Sistema temporariamente suspenso.")
        st.warning("Por favor, entre em contato com a Agência para regularizar o software.")
        
    with st.sidebar.expander("⚙️ Admin Agência"):
        senha_god = st.text_input("Senha Mestra", type="password", key="god_pass")
        
        if senha_god:
            if verificar_senha(senha_god):
                st.success("Acesso Divindade Liberado!")
                status_selecionado = st.selectbox(
                    "Status do Sistema", 
                    ["ativo", "bloqueado"], 
                    index=["ativo", "bloqueado"].index(status_atual)
                )
                if st.button("Atualizar Licença"):
                    mudar_licenca(status_selecionado)
                    st.rerun()
            else:
                st.error("Senha incorreta.")
                
    if status_atual == "bloqueado":
        st.stop() # Trava o resto do sistema