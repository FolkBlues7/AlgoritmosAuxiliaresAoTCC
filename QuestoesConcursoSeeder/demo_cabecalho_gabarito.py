import json
import pymupdf
import pytesseract
from pdf2image import convert_from_path

# Importações dos extratores
from extratores.extrair_cabecalhos import extrair_cabecalhos_pagina_ocr
from extratores.extrair_gabarito import extrair_gabarito

def demonstracao_cabecalho_e_gabarito(caminho_pdf: str, pagina_alvo_cabecalho: int = 1):
    """
    Script para demonstrar o passo a passo da captura de metadados (cabeçalho) 
    via OCR e do gabarito na última página.
    """
    print(f"\n{'='*65}\n DEMONSTRAÇÃO: EXTRAÇÃO DE CABEÇALHO (OCR) E GABARITO\n{'='*65}")

    # =========================================================================
    # PARTE 1: PROCESSAMENTO DO CABEÇALHO / METADADOS VIA OCR
    # =========================================================================
    print(f"\n[PARTE 1] Renderizando Imagem e Aplicando OCR na Página {pagina_alvo_cabecalho}...")

    # 1. Converte a página do PDF em imagem para o Tesseract
    imagens = convert_from_path(caminho_pdf, first_page=pagina_alvo_cabecalho, last_page=pagina_alvo_cabecalho)
    
    # 2. Executa o OCR
    texto_ocr_bruto = pytesseract.image_to_string(imagens[0], lang='por')
    
    print("\n--- TEXTO BRUTO OBTIDO PELO OCR ---")
    print(texto_ocr_bruto)

    # 3. Aplica o algoritmo de parsing via RegEx
    print("\n-> Extraindo disciplina, assuntos, banca, ano e órgão via RegEx...")
    metadados_extraidos = extrair_cabecalhos_pagina_ocr(texto_ocr_bruto, pagina_alvo_cabecalho)

    print("\n--- METADADOS ESTRUTURADOS (JSON) ---")
    print(json.dumps(metadados_extraidos, ensure_ascii=False, indent=4))

    # =========================================================================
    # PARTE 2: EXTRAÇÃO DO GABARITO (PÁGINA FINAL)
    # =========================================================================
    print(f"\n{'='*65}")
    print("\n[PARTE 2] Extraindo Gabarito da Última Página...")

    doc = pymupdf.open(caminho_pdf)
    num_ultima_pagina = len(doc)
    print(f"-> Acessando última página (Página {num_ultima_pagina})...")

    # Obtém o texto bruto da última página
    texto_ultima_pagina = doc[-1].get_text("text")
    
    print("\n--- TEXTO BRUTO DA ÚLTIMA PÁGINA ---")
    print(texto_ultima_pagina)

    # Aplica o mapeador de gabarito
    print("\n-> Mapeando respostas e aplicando correções de OCR (ex: 'I' -> '1')...")
    gabarito_mapeado = extrair_gabarito(doc, num_pagina=-1)

    print("\n--- GABARITO MAPEADO (JSON) ---")
    print(json.dumps(gabarito_mapeado, ensure_ascii=False, indent=4))

    print(f"\n{'='*65}\n DEMONSTRAÇÃO CONCLUÍDA\n{'='*65}")

if __name__ == "__main__":
    caminho = "/home/viniciusdesktop/Documentos/Projetos/QuestoesConcursoSeeder/pdfquestoes.pdf"
    # pagina_alvo_cabecalho = 1 representa a primeira página
    demonstracao_cabecalho_e_gabarito(caminho, pagina_alvo_cabecalho=1)