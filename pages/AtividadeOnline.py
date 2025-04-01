# AtividadeAMA.py (Streamlit integrado com FastAPI para gerar PDF + envio automático para Google Sheets)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

st.markdown("### ✅ Versão atual: 01/04/2025 - 13h12")

# --- ESTILO VISUAL ---
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)

# --- CARREGAMENTO DA PLANILHA ---
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
    st.error("❌ Erro ao carregar os dados da planilha do Google Sheets.")
    if st.button("🔄 Tentar novamente"):
        st.rerun()
    st.stop()

# --- CAMPOS DO CABEÇALHO ---
st.subheader("Preencha o cabeçalho da atividade:")
escola = st.text_input("Escola:")
data = st.date_input("Data:", value=datetime.today())
aluno = st.text_input("Nome do Aluno:")
serie = st.session_state.get("serie", "")
habilidade = st.session_state.get("habilidade", "")
descritor = st.session_state.get("descritor", "")

if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
    st.stop()

st.success("Atividades selecionadas:")
col1, col2 = st.columns(2)
for i, idx in enumerate(st.session_state.atividades_exibidas):
    nome = dados.loc[idx, "ATIVIDADE"]
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"- **Atividade:** {nome}")

# --- Função para registrar log diretamente no Google Sheets ---
def registrar_log_google_sheets(secrets, spreadsheet_id, dados_log):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)

    linha = [[
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),  # Coluna A: data/hora
        dados_log["Escola"],                            # Coluna B
        dados_log["Aluno"],                             # Coluna C
        dados_log["Série"],                             # Coluna D
        dados_log["Habilidades"],                       # Coluna E
        dados_log["Descritor"],                         # Coluna F
        dados_log["TotalQuestoes"]                      # Coluna G
    ]]

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="LOG!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": linha}
    ).execute()

col_gerar, col_cancelar = st.columns([1, 1])

with col_gerar:
    if st.button("📄 GERAR ATIVIDADE"):
        if not escola or not aluno:
            st.warning("Preencha todos os campos antes de gerar o PDF.")
            st.stop()

        with st.spinner("Gerando PDF e registrando log..."):
            try:
                url_api = "https://amasedu.onrender.com/gerar-pdf"
                atividades = [dados.loc[idx, "ATIVIDADE"] for idx in st.session_state.atividades_exibidas]
                payload = {
                    "escola": escola,
                    "professor": aluno,
                    "data": data.strftime("%Y-%m-%d"),
                    "atividades": atividades
                }
                response = requests.post(url_api, json=payload)

                dados_log = {
                    "Escola": escola,
                    "Aluno": aluno,
                    "Série": serie,
                    "Habilidades": habilidade,
                    "Descritor": descritor,
                    "TotalQuestoes": len(st.session_state.atividades_exibidas)
                }

                registrar_log_google_sheets(
                    st.secrets["gcp_service_account"],
                    "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                    dados_log
                )

                if response.status_code == 200:
                    st.download_button(
                        label="📥 Baixar PDF",
                        data=response.content,
                        file_name=f"{aluno}_{data.strftime('%Y-%m-%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF gerado com sucesso!")
                else:
                    st.error(f"Erro ao gerar PDF: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Erro de conexão ou registro de log: {str(e)}")

with col_cancelar:
    if st.button("❌ CANCELAR E RECOMEÇAR"):
        st.session_state.clear()
        st.switch_page("QuestoesAMA.py")
