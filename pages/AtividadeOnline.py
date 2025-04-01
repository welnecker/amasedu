# AtividadeOnline.py (Geração de formulário interativo com imagens)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from PIL import Image
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- CAMPOS DO CABEÇALHO ---
st.subheader("Identificação do Aluno")
aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
serie = st.text_input("Série:")

# --- PLANILHA COM QUESTÕES ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"

@st.cache_data
def carregar_dados():
    try:
        response = requests.get(URL_PLANILHA, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

dados = carregar_dados()
if dados is None:
    st.error("❌ Erro ao carregar os dados da planilha.")
    st.stop()

# --- ATIVIDADES SELECIONADAS ---
st.subheader("Atividades")

if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade foi selecionada pelo professor.")
    st.stop()

respostas = {}

for i, idx in enumerate(st.session_state.atividades_exibidas):
    nome = dados.loc[idx, "ATIVIDADE"]
    url_img = f"https://questoesama.pages.dev/{nome}.jpg"

    st.image(url_img, caption=f"Atividade {i+1}", use_container_width=True)
    resposta = st.radio(
        f"Resposta para a atividade {i+1}", ["A", "B", "C", "D", "E"], key=f"resp_{i}"
    )
    respostas[f"Atividade_{i+1}"] = resposta

# --- ENVIO PARA GOOGLE SHEETS ---
def registrar_respostas_google_sheets(secrets, spreadsheet_id, aba):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)

    linha = [
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        aluno,
        escola,
        serie,
    ] + list(respostas.values())

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{aba}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [linha]}
    ).execute()

if st.button("📤 Enviar Respostas"):
    if not aluno or not escola or not serie:
        st.warning("Por favor, preencha todos os campos de identificação.")
        st.stop()

    try:
        registrar_respostas_google_sheets(
            st.secrets["gcp_service_account"],
            "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
            "ATIVIDADES_GERADAS"
        )
        st.success("Respostas enviadas com sucesso! Obrigado por participar.")

        st.write("### Resumo das respostas:")
        st.write(f"**Aluno:** {aluno}")
        st.write(f"**Escola:** {escola}")
        st.write(f"**Série:** {serie}")
        for k, v in respostas.items():
            st.write(f"{k}: {v}")

    except Exception as e:
        st.error(f"Erro ao registrar respostas: {e}")

if st.button("🔁 Voltar ao início"):
    st.session_state.clear()
    st.switch_page("app.py")
