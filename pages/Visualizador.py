import streamlit as st
import pandas as pd
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Visualizador de Imagens", page_icon="🖼️")
st.title("🖼️ Visualizador de Imagens das Atividades")

# --- Função para carregar dados da aba MATEMATICA ---
@st.cache_data(show_spinner=False)
def carregar_dados_mat():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range="MATEMATICA!A1:Z"
    ).execute()

    values = result.get("values", [])
    if not values or len(values) < 2:
        return pd.DataFrame()

    header = [col.strip().upper() for col in values[0]]
    rows = [linha + [None] * (len(header) - len(linha)) for linha in values[1:]]
    df = pd.DataFrame(rows, columns=header)
    df = df.dropna(subset=["ATIVIDADE"])
    return df

df = carregar_dados_mat()

if df.empty:
    st.warning("⚠️ Nenhuma atividade encontrada na aba MATEMATICA.")
    st.stop()

# Normalizar e ordenar
df["SERIE"] = df["SERIE"].str.strip()
df["HABILIDADE"] = df["HABILIDADE"].str.strip()
df["DESCRITOR"] = df["DESCRITOR"].str.strip()
df["NIVEL"] = df["NIVEL"].str.strip()
df["ATIVIDADE"] = df["ATIVIDADE"].str.strip()

# --- Menu de seleção hierárquico ---
serie_opcao = st.selectbox("Selecione a Série:", sorted(df["SERIE"].dropna().unique()))
df_filtrado_serie = df[df["SERIE"] == serie_opcao]

habilidade_opcao = st.selectbox("Selecione a Habilidade:", sorted(df_filtrado_serie["HABILIDADE"].dropna().unique()))
df_filtrado_hab = df_filtrado_serie[df_filtrado_serie["HABILIDADE"] == habilidade_opcao]

descritor_opcao = st.selectbox("Selecione o Descritor:", sorted(df_filtrado_hab["DESCRITOR"].dropna().unique()))
df_filtrado_desc = df_filtrado_hab[df_filtrado_hab["DESCRITOR"] == descritor_opcao]

nivel_opcao = st.selectbox("Selecione o Nível:", sorted(df_filtrado_desc["NIVEL"].dropna().unique()))
df_final = df_filtrado_desc[df_filtrado_desc["NIVEL"] == nivel_opcao]

# --- Exibir imagens ---
st.markdown("---")
st.markdown(f"### Imagens para o descritor `{descritor_opcao}` - Nível `{nivel_opcao}`")

col1, col2 = st.columns(2)
for i, atividade in enumerate(df_final["ATIVIDADE"].dropna().unique()):
    url = f"https://raw.githubusercontent.com/welnecker/questoesama/main/{atividade}.jpg"
    with col1 if i % 2 == 0 else col2:
        st.image(url, caption=atividade, use_container_width=True)
        with st.expander("🔍 Ampliar"):
            st.image(url, use_container_width=True)

if df_final.empty:
    st.info("Nenhuma imagem encontrada para os filtros selecionados.")