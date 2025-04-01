# AtividadeOnline.py (Nova avaliação alternativa com envio para planilha)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- CARREGAMENTO DAS IMAGENS SELECIONADAS ---
if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
    st.stop()

# --- CARREGAMENTO DOS DADOS DAS ATIVIDADES ---
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
    st.error("Erro ao carregar dados das atividades.")
    st.stop()

# --- CONFIG PLANILHA DE RESPOSTAS ---
SPREADSHEET_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
SHEET_NAME = "ATIVIDADES"

def registrar_resposta_google_sheets(secrets, spreadsheet_id, sheet_name, linha):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [linha]}
    ).execute()

# --- FORMULÁRIO ---
st.markdown("Preencha abaixo para responder às atividades online:")
aluno = st.text_input("Nome do Aluno:")
data = st.date_input("Data:", value=datetime.today())

if not aluno:
    st.info("Digite o nome do aluno para prosseguir.")
    st.stop()

# --- EXIBIR ATIVIDADES E CAMPOS DE RESPOSTA (COM MÚLTIPLA ESCOLHA) ---
st.markdown("---")
respostas = []
opcoes = ["A", "B", "C", "D", "E"]

for idx in st.session_state.atividades_exibidas:
    nome = dados.loc[idx, "ATIVIDADE"]
    url_img = f"https://questoesama.pages.dev/{nome}.jpg"
    st.image(url_img, caption=nome, use_container_width=True)
    resposta = st.radio(f"Escolha a resposta para a atividade {nome}:", opcoes, key=f"resposta_{idx}")
    respostas.append((nome, resposta))

if st.button("📨 Enviar Respostas"):
    with st.spinner("Enviando para a planilha..."):
        try:
            for nome_atividade, resposta in respostas:
                linha = [
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    aluno,
                    nome_atividade,
                    resposta,
                    data.strftime("%d/%m/%Y")
                ]
                registrar_resposta_google_sheets(
                    st.secrets["gcp_service_account"],
                    SPREADSHEET_ID,
                    SHEET_NAME,
                    linha
                )
            st.success("Todas as respostas foram enviadas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {str(e)}")

if st.button("🔁 Voltar ao início"):
    st.session_state.clear()
    st.switch_page("app.py")