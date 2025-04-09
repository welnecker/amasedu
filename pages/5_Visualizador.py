import streamlit as st
import pandas as pd
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Visualizador de Imagens", page_icon="🖼️")
st.markdown("""
<h1 style='font-size:28px; white-space:nowrap;'>🖼️ Visualizador de Imagens das Atividades</h1>
""", unsafe_allow_html=True)

# --- Autenticação por e-mail institucional ---
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

# --- Escolha da disciplina ---
disciplina = st.radio("Escolha a disciplina:", ["MATEMATICA", "PORTUGUES"], horizontal=True)

# --- Função para carregar dados da aba correspondente ---
@st.cache_data(show_spinner=False)
def carregar_dados(disc):
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range=f"{disc}!A1:Z"
    ).execute()

    values = result.get("values", [])
    if not values or len(values) < 2:
        return pd.DataFrame()

    header = [col.strip().upper() for col in values[0]]
    rows = [linha + [None] * (len(header) - len(linha)) for linha in values[1:]]
    df = pd.DataFrame(rows, columns=header)
    df = df.dropna(subset=["ATIVIDADE"])
    return df

df = carregar_dados(disciplina)

if df.empty:
    st.warning(f"⚠️ Nenhuma atividade encontrada na aba {disciplina}.")
    st.stop()

# --- Normalização ---
for col in ["SERIE", "HABILIDADE", "DESCRITOR", "NIVEL", "ATIVIDADE"]:
    df[col] = df[col].str.strip()

# --- Filtros ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    serie_opcao = st.selectbox("Série", sorted(df["SERIE"].dropna().unique()))
df_filtrado_serie = df[df["SERIE"] == serie_opcao]

with col2:
    habilidade_opcao = st.selectbox("Habilidade", sorted(df_filtrado_serie["HABILIDADE"].dropna().unique()))
df_filtrado_hab = df_filtrado_serie[df_filtrado_serie["HABILIDADE"] == habilidade_opcao]

with col3:
    descritor_opcao = st.selectbox("Descritor", sorted(df_filtrado_hab["DESCRITOR"].dropna().unique()))
df_filtrado_desc = df_filtrado_hab[df_filtrado_hab["DESCRITOR"] == descritor_opcao]

with col4:
    nivel_opcao = st.selectbox("Nível", sorted(df_filtrado_desc["NIVEL"].dropna().unique()))
df_final = df_filtrado_desc[df_filtrado_desc["NIVEL"] == nivel_opcao]

# --- Exibição das imagens ---
st.markdown("---")
st.markdown(f"### Imagens para o descritor `{descritor_opcao}` - Nível `{nivel_opcao}`")

col1, col2 = st.columns(2)
for i, atividade in enumerate(df_final["ATIVIDADE"].dropna().unique()):
    url = f"https://raw.githubusercontent.com/welnecker/questoesama/main/{atividade}.jpg"
    with col1 if i % 2 == 0 else col2:
        with st.container():
            st.image(url, caption=atividade, use_container_width=True)
            st.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none; font-size:18px;">🔍</a>',
                unsafe_allow_html=True
            )

if df_final.empty:
    st.info("Nenhuma imagem encontrada para os filtros selecionados.")
