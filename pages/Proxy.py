import streamlit as st
import json
import os

st.set_page_config(page_title="Configurar Proxy", layout="centered")
st.title("🔐 Configuração de Proxy")

st.markdown("Insira as credenciais de proxy, caso seja necessário para baixar as imagens.")

# Caminho do arquivo local
CONFIG_PATH = "proxy_config.json"

# Carregar configurações salvas do disco
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        st.session_state.proxy_usuario = config.get("proxy_usuario", "")
        st.session_state.proxy_servidor = config.get("proxy_servidor", "")
else:
    if "proxy_usuario" not in st.session_state:
        st.session_state.proxy_usuario = ""
    if "proxy_servidor" not in st.session_state:
        st.session_state.proxy_servidor = ""

# Campo de senha (não é salvo localmente por segurança)
if "proxy_senha" not in st.session_state:
    st.session_state.proxy_senha = ""

# Campos de entrada
proxy_usuario = st.text_input("Usuário do Proxy", value=st.session_state.proxy_usuario)
proxy_senha = st.text_input("Senha do Proxy", type="password")
proxy_servidor = st.text_input("Servidor do Proxy (ex: proxy.exemplo.com:3128)", value=st.session_state.proxy_servidor)

# Botão para salvar
if st.button("💾 Salvar e Continuar"):
    st.session_state.proxy_usuario = proxy_usuario
    st.session_state.proxy_senha = proxy_senha
    st.session_state.proxy_servidor = proxy_servidor

    with open(CONFIG_PATH, "w") as f:
        json.dump({
            "proxy_usuario": proxy_usuario,
            "proxy_servidor": proxy_servidor
        }, f)

    st.success("Credenciais salvas com sucesso! Você pode voltar manualmente à página de atividades.")

