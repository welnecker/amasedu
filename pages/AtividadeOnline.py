# AtividadeOnline.py (Geração de QR Code e Google Forms com base na atividade gerada)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import qrcode
from PIL import Image
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import tempfile
import base64

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- PARÂMETROS DA PLANILHA ---
SPREADSHEET_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
SHEET_NAME = "ATIVIDADES_GERADAS"

# --- FORMULÁRIO DO GOOGLE FORMS ---
FORM_BASE = "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform"

# --- FUNÇÃO: GERAR QR CODE ---
def gerar_qrcode(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    return img

# --- FORMULÁRIO DE ACESSO COM CÓDIGO FIXO ---
codigo = "ama25"

# Monta o link com código como parâmetro se necessário
form_url = FORM_BASE + f"?usp=pp_url&entry.1000000={codigo}"

# Gera e exibe o QR Code e o link
st.subheader("📲 Compartilhe com seus alunos")
img_qr = gerar_qrcode(form_url)
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
img_qr.save(temp_file.name)

with open(temp_file.name, "rb") as f:
    img_bytes = f.read()
    b64_img = base64.b64encode(img_bytes).decode()
    st.image(img_bytes, caption="Escaneie com a câmera do celular", use_column_width=True)

st.markdown(f"👉 Ou clique para acessar o formulário: [Abrir formulário]({form_url})")
st.info("Os alunos devem preencher este formulário com suas respostas.")

if st.button("🔁 Voltar ao início"):
    st.session_state.clear()
    st.switch_page("app.py")
