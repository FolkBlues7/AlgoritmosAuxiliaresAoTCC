import io
import re
import pymupdf
import pytesseract
from PIL import Image

def extrair_gabarito(doc, num_pagina: int = -1) -> dict:
    """
    Lê a última página do PDF, extrai o texto (via PyMuPDF ou Tesseract OCR)
    e retorna um dicionário no formato: {1: 'D', 2: 'B', ..., 20: 'A'}
    """
    page = doc[num_pagina]
    
    texto = page.get_text()
    
    if "Respostas" not in texto and not re.search(r'\d+\s*:\s*[A-E]', texto):
        # Renderiza a página em alta definição (300 DPI) para o OCR
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        texto = pytesseract.image_to_string(img, lang="por")
    
    padrao_respostas = re.findall(r'(\d+|[Il|])\s*[:;.,-]\s*([A-E])', texto)
        
    gabarito_map = {}
    for num_str, resposta in padrao_respostas:
        if num_str in ['I', 'l', '|']:
            num_str = '1'
            
        gabarito_map[int(num_str)] = resposta
            
    return gabarito_map