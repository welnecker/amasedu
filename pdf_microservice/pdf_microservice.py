from fastapi import FastAPI, HTTPException
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
    data: str
    atividades: List[str]
    titulo: str = "ATIVIDADE"
    gabarito: List[str] = []  # Lista como ["1-A", "2-C", ...]

@app.post("/gerar-pdf")
async def gerar_pdf(req: PDFRequest):
    try:
        pdf = fitz.open("modelo.pdf")
        pagina = pdf[0]

        # Cabeçalho
        y_base = 100
        pagina.insert_text(fitz.Point(72, y_base),
                           f"Escola: {req.escola}    Data: {datetime.strptime(req.data, '%Y-%m-%d').strftime('%d/%m/%Y')}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        pagina.insert_text(fitz.Point(72, y_base + 20),
                           "Estudante: _________________________________    Turma: ____________",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        pagina.insert_text(fitz.Point(72, y_base + 40),
                           f"Professor(a): {req.professor}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))

        # Título centralizado
        titulo_texto = req.titulo.upper()
        largura_titulo = fitz.get_text_length(titulo_texto, fontname="helv", fontsize=14)
        pagina_largura = pagina.rect.width
        posicao_x = (pagina_largura - largura_titulo) / 2
        pagina.insert_text(fitz.Point(posicao_x, 160),
                           titulo_texto, fontsize=14, fontname="helv", color=(0, 0, 0))

        # Imagens das questões
        y = 185
        for i, nome in enumerate(req.atividades, start=1):
            url_img = f"https://questoesama.pages.dev/{nome}.jpg"
            try:
                req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_img) as resp:
                    img = Image.open(BytesIO(resp.read())).convert("RGB")
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')

                    if y > 700:
                        pagina = pdf.new_page()
                        y = 50
                    else:
                        y += 12

                    pagina.insert_text(fitz.Point(72, y), f"Questão {i}", fontsize=12, fontname="helv", color=(0, 0, 0))
                    y += 22

                    pagina.insert_image(
                        fitz.Rect(72, y, 520, y + 240),  # imagem maior
                        stream=buffer.getvalue()
                    )
                    y += 245
            except:
                continue

        # Adiciona imagem do gabarito em branco
        try:
            url_gabarito = "https://questoesama.pages.dev/img/gabarito-preencher.jpg"
            req_img = urllib.request.Request(url_gabarito, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img) as resp:
                img = Image.open(BytesIO(resp.read())).convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format='JPEG')

                if y > 700:
                    pagina = pdf.new_page()
                    y = 50
                else:
                    y += 20

                pagina.insert_text(fitz.Point(72, y), "Gabarito a preencher:", fontsize=12, fontname="helv", color=(0, 0, 0))
                y += 22

                pagina.insert_image(fitz.Rect(72, y, 520, y + 240), stream=buffer.getvalue())
        except:
            pass

        # Nova página para gabarito preenchido
        pdf.new_page()
        y_gab = 50
        pagina = pdf[-1]
        pagina.insert_text(fitz.Point(72, y_gab), "Gabarito para correção:", fontsize=12, fontname="helv", color=(0, 0, 0))
        y_gab += 20
        for linha in req.gabarito:
            pagina.insert_text(fitz.Point(72, y_gab), linha, fontsize=12, fontname="helv", color=(0, 0, 0))
            y_gab += 18

        # Finaliza PDF
        pdf_bytes = pdf.write()
        pdf_stream = BytesIO(pdf_bytes)
        nome_arquivo = f"{req.professor}_{req.data}.pdf"

        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={nome_arquivo}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
