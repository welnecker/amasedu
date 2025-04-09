from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import urllib.request
from io import BytesIO
from datetime import datetime

app = FastAPI()

class PDFRequest(BaseModel):
    escola: str
    professor: str
    data: str  # formato: "YYYY-MM-DD"
    atividades: List[str]
    titulo: str = "ATIVIDADE"  # título opcional

@app.post("/gerar-pdf")
async def gerar_pdf(req: PDFRequest):
    try:
        pdf = fitz.open("modelo.pdf")
        pagina = pdf[0]

        # Cabeçalho
        texto = (
            f"Escola: {req.escola}    Data: {datetime.strptime(req.data, '%Y-%m-%d').strftime('%d/%m/%Y')}\n"
            f"Estudante: _________________________________    Turma: ____________\n"
            f"Professor(a): {req.professor}"
        )
        pagina.insert_text(fitz.Point(72, 100), texto, fontsize=12, fontname="helv", color=(0, 0, 0))

        # Título da atividade
        pagina.insert_text(fitz.Point(72, 170), req.titulo.upper(), fontsize=14, fontname="helv", color=(0, 0, 0))
        y = 210  # margem inicial para imagens

        for nome in req.atividades:
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            try:
                req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_img) as resp:
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
                continue

        pdf_bytes = pdf.write()
        pdf_stream = BytesIO(pdf_bytes)
        nome_arquivo = f"{req.professor}_{req.data}.pdf"

        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={nome_arquivo}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

