# AtividadeAMA.py (gerador de PDF)
import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
import fitz  # PyMuPDF
from PIL import Image
import urllib.request
from datetime import datetime

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
        st.experimental_rerun()
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

        with st.spinner("Gerando PDF com as atividades..."):
            try:
                pdf = fitz.open("modelo.pdf")
                pagina = pdf[0]

                texto = (
                    f"Escola: {escola}                       Data: {data.strftime('%d/%m/%Y')}\n"
                    f"Estudante: _________________________________     Turma: ____________\n"
                    f"Professor(a): {professor}"
                )

                pagina.insert_text(
                    fitz.Point(72, 120), texto, fontsize=12, fontname="helv", color=(0, 0, 0)
                )

                y = 180
                for idx in st.session_state.atividades_exibidas:
                    nome = dados.loc[idx, "ATIVIDADE"]
                    url_img = f"https://questoesama.pages.dev/{nome}.jpg"
                    try:
                        req = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as resp:
                            img = Image.open(BytesIO(resp.read())).convert("RGB")

                        buffer = BytesIO()
                        img.save(buffer, format='JPEG')

                        if y > 700:
                            pagina = pdf.new_page()
                            y = 10

                        pagina.insert_image(
                            fitz.Rect(72, y, 520, y + 160), stream=buffer.getvalue()
                        )
                        y += 162
                    except:
                        st.warning(f"Erro ao baixar a imagem: {nome}")

                nome_arquivo = f"{professor}_{data.strftime('%Y-%m-%d')}.pdf"
                pdf_bytes = pdf.write()
                st.download_button("📥 Baixar PDF", pdf_bytes, nome_arquivo, "application/pdf")
                st.success("PDF criado com sucesso!")
            except Exception as e:
                st.error("Erro ao gerar o PDF. Tente novamente.")

with col_cancelar:
    if st.button("❌ CANCELAR E RECOMEÇAR"):
        st.session_state.clear()
        st.switch_page("QuestoesAMA.py")
