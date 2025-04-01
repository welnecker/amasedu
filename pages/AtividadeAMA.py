# AtividadeAMA.py (Streamlit integrado com FastAPI para gerar PDF + envio automático para Google Forms)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from urllib.parse import urlencode

st.set_page_config(page_title="ATIVIDADE AMA 2025", page_icon="📚")

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
professor = st.text_input("Nome do Professor(a):")

if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades.")
    st.stop()

st.success("Atividades selecionadas:")
col1, col2 = st.columns(2)
for i, idx in enumerate(st.session_state.atividades_exibidas):
    nome = dados.loc[idx, "ATIVIDADE"]
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"- **Atividade:** {nome}")

col_gerar, col_cancelar = st.columns([1, 1])

with col_gerar:
    if st.button("📄 GERAR ATIVIDADE"):
        if not escola or not professor:
            st.warning("Preencha todos os campos antes de gerar o PDF.")
            st.stop()

        with st.spinner("Gerando PDF e enviando log..."):
            try:
                url_api = "https://amasedu.onrender.com/gerar-pdf"
                atividades = [dados.loc[idx, "ATIVIDADE"] for idx in st.session_state.atividades_exibidas]
                payload = {
                    "escola": escola,
                    "professor": professor,
                    "data": data.strftime("%Y-%m-%d"),
                    "atividades": atividades
                }
                response = requests.post(url_api, json=payload)

                # Envio de log ao Google Forms
                dados_forms = {
                    "entry.1932539975": escola,  # Escola
                    "entry.1534567646": professor,  # Professor
                    "entry.272957323": st.session_state.get("serie", ""),
                    "entry.465063798": st.session_state.get("descritor", ""),
                    "entry.537108716": st.session_state.get("habilidade", ""),
                    "entry.633190190": str(len(st.session_state.atividades_exibidas)),
                }

                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform",
                    "User-Agent": "Mozilla/5.0"
                }

                form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/formResponse"
                try:
                    payload_encoded = urlencode(dados_forms)
                    requests.post(form_url, data=payload_encoded, headers=headers, timeout=5)
                except Exception as e:
                    st.warning(f"⚠️ Erro ao enviar log: {e}")

                if response.status_code == 200:
                    st.download_button(
                        label="📥 Baixar PDF",
                        data=response.content,
                        file_name=f"{professor}_{data.strftime('%Y-%m-%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF gerado com sucesso!")
                else:
                    st.error(f"Erro ao gerar PDF: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Erro de conexão com o gerador de PDF: {str(e)}")

with col_cancelar:
    if st.button("❌ CANCELAR E RECOMEÇAR"):
        st.session_state.clear()
        st.switch_page("QuestoesAMA.py")
