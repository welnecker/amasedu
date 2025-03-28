# Proxy


import streamlit as st
st.set_page_config(page_title="Configurar Proxy", layout="centered")

st.title("⚙️ Configuração de Proxy (desativado)")

st.info("""
Atualmente, o uso de proxy está **desativado** no sistema.
Você pode limpar configurações antigas ou reativá-lo manualmente no código, se necessário.
""")

# Exibe configurações existentes (se houver)
if "proxy_usuario" in st.session_state or "proxy_senha" in st.session_state or "proxy_servidor" in st.session_state:
    st.warning("Configurações de proxy ativas detectadas:")
    st.code({
        "proxy_usuario": st.session_state.get("proxy_usuario"),
        "proxy_senha": st.session_state.get("proxy_senha"),
        "proxy_servidor": st.session_state.get("proxy_servidor")
    })

    if st.button("🧹 Limpar configurações de proxy"):
        for key in ["proxy_usuario", "proxy_senha", "proxy_servidor"]:
            st.session_state.pop(key, None)
        st.success("Proxy removido com sucesso. Você pode voltar à seleção de atividades.")
else:
    st.success("Nenhuma configuração de proxy ativa.")

if st.button("⬅ Voltar para atividades"):
    st.switch_page("../QuestoesAMA")
