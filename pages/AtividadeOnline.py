# AtividadeOnline.py (Nova avaliação alternativa com acesso via código fixo "ama25")
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- PARÂMETROS DA PLANILHA ---
SPREADSHEET_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
SHEET_NAME = "ATIVIDADES_GERADAS"
SHEET_RESPOSTAS = "ATIVIDADES"

# --- FUNÇÃO: LER DADOS POR CÓDIGO ---
def carregar_dados_por_codigo(secrets, spreadsheet_id, sheet_name, codigo):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A2:G",
    ).execute()
    valores = result.get("values", [])
    for linha in valores:
        if len(linha) >= 7 and linha[0].strip().lower() == codigo.strip().lower():
            atividades = linha[1].split(",")
            escola = linha[2]
            serie = linha[3]
            return atividades, escola, serie
    return None, None, None

# --- FORMULÁRIO DE ACESSO COM CÓDIGO FIXO ---
codigo = "ama25"
atividades, escola, serie = carregar_dados_por_codigo(
    st.secrets["gcp_service_account"], SPREADSHEET_ID, SHEET_NAME, codigo
)

if not atividades:
    st.error("Atividades não encontradas. O professor ainda não gerou a atividade.")
    st.stop()

# --- FORMULÁRIO DO ALUNO ---
st.markdown(f"### Escola: {escola} | Série: {serie}")
aluno = st.text_input("Nome do Aluno:")
data = st.date_input("Data:", value=datetime.today())

if not aluno:
    st.info("Digite o nome do aluno para prosseguir.")
    st.stop()

# --- EXIBIR ATIVIDADES E CAMPOS DE RESPOSTA ---
respostas = []
st.markdown("---")
for nome in atividades:
    nome = nome.strip()
    if nome:
        url_img = f"https://questoesama.pages.dev/{nome}.jpg"
        st.image(url_img, caption=nome, use_container_width=True)
        resposta = st.radio(
            f"Escolha a alternativa correta para a atividade {nome}:",
            options=["A", "B", "C", "D", "E"],
            index=None,
            key=f"resp_{nome}"
        )
        respostas.append((nome, resposta))

# --- ENVIO PARA PLANILHA DE RESPOSTAS ---
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

if st.button("📨 Enviar Respostas"):
    with st.spinner("Enviando para a planilha..."):
        try:
            for nome_atividade, resposta in respostas:
                linha = [
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    aluno,
                    escola,
                    serie,
                    nome_atividade,
                    resposta,
                    data.strftime("%d/%m/%Y")
                ]
                registrar_resposta_google_sheets(
                    st.secrets["gcp_service_account"],
                    SPREADSHEET_ID,
                    SHEET_RESPOSTAS,
                    linha
                )
            st.success("Todas as respostas foram enviadas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {str(e)}")

if st.button("🔁 Voltar ao início"):
    st.session_state.clear()
    st.switch_page("app.py")
