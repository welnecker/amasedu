from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import urllib.request
from io import BytesIO
from datetime import datetime
import unicodedata

app = FastAPI()

class PDFRequest(BaseModel):
    escola: str
    professor: str
    data: str
    atividades: List[str]
    disciplina: str

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode().upper()

@app.post("/gerar-pdf")
async def gerar_pdf(req: PDFRequest):
    try:
        pdf = fitz.open("modelo.pdf")
        pagina = pdf[0]

        # Cabeçalho
        y = 100
        pagina.insert_text(fitz.Point(72, y),
                           f"Escola: {req.escola}    Data: {datetime.strptime(req.data, '%Y-%m-%d').strftime('%d/%m/%Y')}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        y += 20
        pagina.insert_text(fitz.Point(72, y),
                           "Estudante: _________________________________    Turma: ____________",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        y += 20
        pagina.insert_text(fitz.Point(72, y),
                           f"Professor(a): {req.professor}",
                           fontsize=12, fontname="helv", color=(0, 0, 0))
        y += 40

        # Título e subpasta baseados na disciplina
        disciplina_normalizada = normalizar(req.disciplina)
        subpasta = "matematica" if "MATEMATICA" in disciplina_normalizada else "portugues"
        titulo_texto = f"ATIVIDADE DE {'MATEMÁTICA' if subpasta == 'matematica' else 'LÍNGUA PORTUGUESA'}"

        largura_titulo = fitz.get_text_length(titulo_texto, fontname="helv", fontsize=14)
        pagina_largura = pagina.rect.width
        posicao_x = (pagina_largura - largura_titulo) / 2
        pagina.insert_text(fitz.Point(posicao_x, y),
                           titulo_texto, fontsize=14, fontname="helv", color=(0, 0, 0))
        y += 25

        print(f"📘 Disciplina: {req.disciplina} → subpasta: {subpasta}")
        print(f"🖼️ Título gerado: {titulo_texto}")

        # Colagem das atividades
        for i, nome in enumerate(req.atividades, start=1):
            url_img = f"https://questoesama.pages.dev/{subpasta}/{nome}.jpg"
            print(f"🔗 Carregando imagem: {url_img}")
            try:
                req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_img) as resp:
                    img = Image.open(BytesIO(resp.read())).convert("RGB")
                    largura_original, altura_original = img.size

                    nova_largura = 448
                    fator_escala = nova_largura / largura_original
                    nova_altura = altura_original * fator_escala

                    # Verifica se cabe na página atual
                    if y + nova_altura + 40 > 792:  # margem de segurança
                        pagina = pdf.new_page()
                        y = 50

                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')

                    pagina.insert_text(fitz.Point(72, y), f"Questão {i}",
                                       fontsize=12, fontname="helv", color=(0, 0, 0))
                    y += 22

                    pagina.insert_image(
                        fitz.Rect(72, y, 72 + nova_largura, y + nova_altura),
                        stream=buffer.getvalue()
                    )
                    y += nova_altura + 10

            except Exception as img_error:
                print(f"❌ Erro ao baixar imagem {nome}: {img_error}")
                continue

        # Gabarito com altura proporcional
        try:
            url_gabarito = "https://raw.githubusercontent.com/welnecker/questoesama/main/img/gabarito-preencher.jpg"
            req_img = urllib.request.Request(url_gabarito, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img) as resp:
                img = Image.open(BytesIO(resp.read())).convert("RGB")
                largura_original, altura_original = img.size

                nova_largura = 448
                fator_escala = nova_largura / largura_original
                nova_altura = altura_original * fator_escala

                buffer = BytesIO()
                img.save(buffer, format='JPEG')

                pagina = pdf.new_page()
                pagina.insert_text(fitz.Point(72, 40), "GABARITO",
                                   fontsize=12, fontname="helv", color=(0, 0, 0))
                pagina.insert_image(
                    fitz.Rect(72, 70, 72 + nova_largura, 70 + nova_altura),
                    stream=buffer.getvalue()
                )
                print(f"✅ Gabarito incluído com altura proporcional: {nova_altura:.1f}")
        except Exception as e:
            print(f"❌ Erro ao adicionar gabarito: {e}")

        # Finaliza PDF
        pdf_bytes = pdf.write()
        pdf_stream = BytesIO(pdf_bytes)
        nome_arquivo = f"{req.professor}_{req.data}.pdf"

        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={nome_arquivo}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
