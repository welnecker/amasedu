# ==========================================================
# 📦 IMPORTAÇÕES
# ==========================================================
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import random
import string

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ==========================================================
# ⚙️ CONFIGURAÇÃO GERAL
# ==========================================================
st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

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
    </style>
""", unsafe_allow_html=True)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)

# ==========================================================
# 📊 CARREGAMENTO DOS DADOS
# ==========================================================
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=452645937&single=true&output=csv"


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
    if st.button("🔄 Tentar novamente"):
        st.rerun()
    st.stop()

# ==========================================================
# 🔧 FUNÇÕES AUXILIARES
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

# ==========================================================
# 🧾 FORMULÁRIO DE CABEÇALHO
# ==========================================================
st.subheader("Preencha o cabeçalho da atividade:")

escola = st.text_input("Escola:")
data = st.date_input("Data:", value=datetime.today())
professor = st.text_input("Nome do Professor(a):")
serie = st.session_state.get("serie", "")
habilidade = st.session_state.get("habilidade", "")
descritor = st.session_state.get("descritor", "")

if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
    st.stop()

# ==========================================================
# 📋 LISTA DAS ATIVIDADES ESCOLHIDAS
# ==========================================================
st.success("Atividades selecionadas:")
col1, col2 = st.columns(2)
for i, idx in enumerate(st.session_state.atividades_exibidas):
    nome = dados.loc[idx, "ATIVIDADE"]
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"- **Atividade:** {nome}")

# ==========================================================
# 🚀 GERAÇÃO DE PDF E SALVAMENTO
# ==========================================================
col_gerar, col_cancelar = st.columns([1, 1])

with col_gerar:
    if st.button("📄 GERAR ATIVIDADE"):
        if not escola or not professor:
            st.warning("Preencha todos os campos antes de gerar o PDF.")
            st.stop()

        with st.spinner("Gerando PDF, salvando código e registrando log..."):
            try:
                atividades = [dados.loc[idx, "ATIVIDADE"] for idx in st.session_state.atividades_exibidas]
                codigo_atividade = gerar_codigo_aleatorio()
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                # Salvar atividades com código
                linhas = [[codigo_atividade, atividade, timestamp] for atividade in atividades]
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
                    body={"values": linhas}
                ).execute()

                # Salvar log do cabeçalho
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

                # Gerar PDF
                url_api = "https://amasedu.onrender.com/gerar-pdf"
                payload = {
                    "escola": escola,
                    "professor": professor,
                    "data": data.strftime("%Y-%m-%d"),
                    "atividades": atividades
                }
                response = requests.post(url_api, json=payload)

                if response.status_code == 200:
                    st.download_button(
                        label="📥 Baixar PDF",
                        data=response.content,
                        file_name=f"{professor}_{data.strftime('%Y-%m-%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF gerado com sucesso!")
                    st.markdown("### 🧾 Código da atividade para os alunos:")
                    st.code(codigo_atividade, language="markdown")
                else:
                    st.error(f"Erro ao gerar PDF: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF ou salvar dados: {str(e)}")

with col_cancelar:
    if st.button("❌ CANCELAR E RECOMEÇAR"):
        st.session_state.clear()
        st.switch_page("QuestoesAMA.py")
