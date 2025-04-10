import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata
from datetime import datetime
import random
import string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

# **Botão "Recomeçar tudo" fixo na parte superior da página**
if st.button("Recomeçar tudo"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()  # limpa o cache de dados da planilha
    st.rerun()

# Lógica do restante da página
if st.session_state.get("reiniciar_pedido"):
    st.session_state.clear()
    st.rerun()

# --- BLOQUEIO POR SENHA ---
if "relatorio_autenticado" not in st.session_state:
    st.session_state.relatorio_autenticado = False

if not st.session_state.relatorio_autenticado:
    st.markdown("### 🔐 Acesso restrito aos professores")
    email = st.text_input("Digite seu e-mail institucional:")
    if email.endswith("@educador.edu.es.gov.br"):
        st.session_state.relatorio_autenticado = True
        st.success("✅ Acesso autorizado!")
        st.rerun()
    elif email:
        st.error("❌ E-mail inválido. Use seu e-mail institucional.")
    st.stop()

st.markdown("### ✅ Versão atual: 01/04/2025 - 13h12")

# --- ESTILO VISUAL ---
st.markdown("""
<style>
.stApp {
    background-image: url("https://questoesama.pages.dev/img/fundo.png");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center top;
    background-attachment: fixed;
}
.main > div {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 15px;
    margin-top: 100px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
}
div.block-container {
    padding: 0.5rem 1rem;
}
.element-container {
    margin-bottom: 0.25rem !important;
}
hr {
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
st.title("ATIVIDADE AMA 2025")

# --- ESCOLHA DA DISCIPLINA ---
st.markdown("### Escolha a disciplina:")
col1, col2 = st.columns(2)

if "disciplina" not in st.session_state:
    st.session_state.disciplina = None

botao_matematica = col1.button("📘 MATEMÁTICA", disabled=st.session_state.disciplina is not None)
botao_portugues = col2.button("📗 LÍNGUA PORTUGUESA", disabled=st.session_state.disciplina is not None)

if botao_matematica:
    st.session_state.disciplina = "MATEMATICA"
    st.rerun()

if botao_portugues:
    st.session_state.disciplina = "PORTUGUES"
    st.rerun()

if not st.session_state.disciplina:
    st.warning("Selecione uma disciplina para continuar.")
    st.stop()

# Mensagem de confirmação com destaque visual
st.markdown(
    f"<div style='padding:10px; background-color:#dff0d8; border-radius:10px;'><b>✅ Disciplina selecionada:</b> {st.session_state.disciplina}</div>",
    unsafe_allow_html=True
)

# O restante do código segue normalmente...
