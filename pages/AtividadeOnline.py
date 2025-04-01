# AtividadeOnline.py (Geração de link com QR Code para formulário único)
import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

st.subheader("Acesse a atividade gerada pelo professor")

# URL do Google Forms padrão (único para todos os alunos)
URL_GOOGLE_FORMS = "https://docs.google.com/forms/d/e/1FAIpQLSdxICVdcS9nEgH_vwetgvJHZRQEYPDJXCOywaTaNVC4F6XLRQ/viewform"

# Gerar QR Code
qr = qrcode.make(URL_GOOGLE_FORMS)
buffer = BytesIO()
qr.save(buffer, format="PNG")
buffer.seek(0)

# Exibir QR Code e link
st.image(buffer, caption="Escaneie o QR Code para responder à atividade", use_container_width=True)
st.markdown(f"Ou acesse diretamente: [Clique aqui para abrir o formulário]({URL_GOOGLE_FORMS})")

# Botão para copiar o link para a área de transferência
st.markdown("---")
st.code(URL_GOOGLE_FORMS, language="text")
st.markdown("Copie o link acima para enviar aos alunos (via WhatsApp, e-mail, etc).")
