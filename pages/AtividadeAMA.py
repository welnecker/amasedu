import streamlit as st
import pandas as pd
from datetime import datetime
import unicodedata
import requests
import random
import string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

# ==========================================================
# 📟 FORMULÁRIO DE CABEÇALHO
# ==========================================================
st.subheader("Preencha o cabeçalho da atividade:")

escola = st.text_input("Escola:", value=st.session_state.get("selecionado_escola", ""))
data = st.date_input("Data:", value=datetime.today())
professor = st.text_input("Nome do Professor(a):")
serie = st.session_state.get("serie", "")
habilidade = st.session_state.get("habilidade", "")
descritor = st.session_state.get("descritor", "")
sre = st.session_state.get("selecionado_sre", "")
turma = st.session_state.get("selecionado_turma", "")

if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
    st.stop()

# ==========================================================
# 📋 LISTA DAS ATIVIDADES ESCOLHIDAS
# ==========================================================
st.success("Atividades selecionadas:")
col1, col2 = st.columns(2)
for i, nome in enumerate(st.session_state.atividades_exibidas):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"- **Atividade:** {nome}")

# ==========================================================
# 🚀 GERAÇÃO DE PDF E SALVAMENTO
# ==========================================================
def gerar_codigo_aleatorio(tamanho=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=tamanho))

def registrar_log_google_sheets(secrets, spreadsheet_id, dados_log):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)

    linha = [[
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        dados_log["Escola"],
        dados_log["Professor"],
        dados_log["Série"],
        dados_log["Habilidades"],
        dados_log["Descritor"],
        dados_log["TotalQuestoes"]
    ]]

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="LOG!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": linha}
    ).execute()

    st.cache_data.clear()

col_gerar, col_cancelar = st.columns([1, 1])

with col_gerar:
    if st.button("📄 GERAR ATIVIDADE"):
        if not escola or not professor:
            st.warning("Preencha todos os campos antes de gerar o PDF.")
            st.stop()

        with st.spinner("Gerando PDF, salvando código e registrando log..."):
            try:
                atividades = st.session_state.atividades_exibidas
                codigo_atividade = gerar_codigo_aleatorio()
                st.session_state.codigo_atividade = codigo_atividade
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                linha_unica = [codigo_atividade, timestamp, sre, escola, turma] + atividades

                creds = Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=["https://www.googleapis.com/auth/spreadsheets"]
                )
                service = build("sheets", "v4", credentials=creds)

                service.spreadsheets().values().append(
                    spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                    range="ATIVIDADES_GERADAS!A1",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [linha_unica]}
                ).execute()

                dados_log = {
                    "Escola": escola,
                    "Professor": professor,
                    "Série": serie,
                    "Habilidades": habilidade,
                    "Descritor": descritor,
                    "TotalQuestoes": len(atividades)
                }
                registrar_log_google_sheets(
                    st.secrets["gcp_service_account"],
                    "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                    dados_log
                )

                url_api = "https://amasedu.onrender.com/gerar-pdf"
                payload = {
                    "escola": escola,
                    "professor": professor,
                    "data": data.strftime("%Y-%m-%d"),
                    "atividades": atividades
                }
                response = requests.post(url_api, json=payload)

                if response.status_code == 200:
                    st.session_state.pdf_bytes = response.content
                else:
                    st.error(f"Erro ao gerar PDF: {response.status_code} - {response.text}")

                st.cache_data.clear()

            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF ou salvar dados: {e}")

if "codigo_atividade" in st.session_state and "pdf_bytes" in st.session_state:
    st.success("✅ PDF gerado com sucesso!")
    st.markdown("### 📟 Código da atividade para os alunos:")
    st.code(st.session_state.codigo_atividade, language="markdown")
    st.download_button(
        label="📅 Baixar PDF",
        data=st.session_state.pdf_bytes,
        file_name=f"{professor}_{data.strftime('%Y-%m-%d')}.pdf",
        mime="application/pdf"
    )

with col_cancelar:
    if st.button("❌ CANCELAR E RECOMEÇAR"):
        st.session_state.clear()
        st.switch_page("pages/Acesso_Professores.py")
