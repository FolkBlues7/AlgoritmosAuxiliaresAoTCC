import re
import pytesseract
from pdf2image import convert_from_path

def extrair_cabecalhos_pagina_ocr(texto_pagina: str, num_pagina: int) -> list:
    """
    Lê o texto extraído via OCR de uma página e busca os cabeçalhos.
    """
    linhas = [l.strip() for l in texto_pagina.splitlines() if l.strip()]
    cabecalhos_da_pagina = []
    i = 0
    
    while i < len(linhas):
        linha = linhas[i]
        
        # Regex para capturar a Linha 1: "1 Q4279852 Banco de Dados > Banco de Dados Relacionais, SQL"
        match_l1 = re.search(r'^(\d+)\s+(Q\d+)\s+(.*?)\s*>\s*(.*)$', linha)
        
        if match_l1:
            num_questao = int(match_l1.group(1))
            codigo_q = match_l1.group(2)
            disciplina = match_l1.group(3).strip()
            assuntos_raw = match_l1.group(4).strip()
            
            # Separa múltiplos assuntos por vírgula
            assuntos = [a.strip() for a in assuntos_raw.split(",") if a.strip()]
            
            ano, banca, orgao = "", "", ""
            
            # Procura a Linha 2 ("Ano: 2026 Banca: FGV Órgão: TCE-PE") nas próximas 4 linhas
            for j in range(i + 1, min(i + 5, len(linhas))):
                match_l2 = re.search(r'Ano:\s*(\d{4})\s+Banca:\s*(.*?)\s+Órgão:\s*(.*)', linhas[j])
                if match_l2:
                    ano = match_l2.group(1).strip()
                    banca = match_l2.group(2).strip()
                    orgao = match_l2.group(3).strip()
                    break
            
            cabecalho_info = {
                "pagina": num_pagina,
                "numero": num_questao,
                "codigo_q": codigo_q,
                "disciplina": disciplina,
                "assuntos": assuntos,
                "ano": ano,
                "banca": banca,
                "orgao": orgao
            }
            
            cabecalhos_da_pagina.append(cabecalho_info)
        
        i += 1
        
    return cabecalhos_da_pagina

def extrair_todos_cabecalhos_pdf(caminho_pdf: str) -> list:
    """
    Converte o PDF em imagens, aplica OCR e extrai os cabeçalhos.
    """
    print("Convertendo PDF em imagens para OCR... (Isso pode levar alguns segundos)")
    imagens = convert_from_path(caminho_pdf)
    todos_cabecalhos = []
    
    for index_pag, imagem in enumerate(imagens):
        num_pagina = index_pag + 1
        print(f"Processando página {num_pagina}/{len(imagens)} via OCR...")
        
        # Aplica o OCR na imagem usando o idioma português (por)
        texto_ocr = pytesseract.image_to_string(imagem, lang='por')
        
        # Extrai os cabeçalhos do texto gerado
        cabecalhos = extrair_cabecalhos_pagina_ocr(texto_ocr, num_pagina)
        
        if cabecalhos:
            todos_cabecalhos.extend(cabecalhos)
            
    return todos_cabecalhos