import json
import pymupdf

# Importações dos extratores do projeto
from extratores.extrair_cabecalhos import extrair_todos_cabecalhos_pdf
from extratores.extrair_gabarito import extrair_gabarito
from extratores.reordenar_html_pdf import reordenar_e_juntar_alternativas
from extratores.isolar_questoes_html import isolar_questoes_html
from extratores.limpar_questao import limpar_html_questao

def demonstracao_passo_a_passo(caminho_pdf: str, pagina_alvo: int = 0):
    """
    Script de demonstração modular para apresentação em vídeo.
    Exibe a evolução completa do HTML em cada etapa da pipeline em uma única página.
    """
    print(f"\n{'='*60}\n INICIANDO DEMONSTRAÇÃO - PÁGINA {pagina_alvo + 1}\n{'='*60}")

    # =========================================================================
    # ETAPA 1: EXTRAÇÃO DO HTML BRUTO VIA PYMUPDF
    # =========================================================================
    print("\n[ETAPA 1] Extraindo HTML nativo do PDF...")
    doc = pymupdf.open(caminho_pdf)
    html_bruto_pagina = doc[pagina_alvo].get_text("html")
    
    print("-> HTML Bruto Completo:")
    print(html_bruto_pagina)
    
    # =========================================================================
    # ETAPA 2: REORDENAÇÃO INTELIGENTE (EIXOS Y E X)
    # =========================================================================
    print("\n[ETAPA 2] Aplicando reordenação espacial (Eixos Y/X)...")
    html_ordenado = reordenar_e_juntar_alternativas(html_bruto_pagina)
    
    print("-> HTML Reordenado Completo:")
    print(html_ordenado)

    # =========================================================================
    # ETAPA 3: ISOLAMENTO DAS QUESTÕES
    # =========================================================================
    print("\n[ETAPA 3] Particionando o HTML em questões isoladas...")
    questoes_isoladas = isolar_questoes_html(html_ordenado)
    print(f"-> Total de questões encontradas nesta página: {len(questoes_isoladas)}")
    
    if questoes_isoladas:
        print("-> HTML da Questão 1 (sem limpeza) Completo:")
        print(questoes_isoladas[0])

    # =========================================================================
    # ETAPA 4: LIMPEZA E ISOLAMENTO DE IMAGEM BASE64
    # =========================================================================
    print("\n[ETAPA 4] Limpando lixos do Qconcursos e extraindo imagem Base64...")
    if questoes_isoladas:
        dados_limpos = limpar_html_questao(questoes_isoladas[0])
        print("-> HTML Final Limpo Completo:")
        print(dados_limpos["html_content"])
        print(f"-> Imagem em Base64 extraída? {'SIM' if dados_limpos['imagem_base64'] else 'NÃO'}")

    # =========================================================================
    # ETAPA 5: METADADOS VIA OCR E MONTAGEM DO JSON FINAL
    # =========================================================================
    print("\n[ETAPA 5] Associando Metadados (OCR) e Gabarito ao JSON Final...")
    gabarito_map = extrair_gabarito(doc, num_pagina=-1)
    
    questao_demo = {
        "numero": 1,
        "codigo_q": "Q4279852",
        "disciplina": "Banco de Dados",
        "assuntos": ["Banco de Dados Relacionais", "SQL"],
        "ano": "2026",
        "banca": "FGV",
        "orgao": "TCE-PE",
        "gabarito": gabarito_map.get(1, None),
        "html_content": dados_limpos["html_content"] if questoes_isoladas else "",
        "imagem_base64": dados_limpos["imagem_base64"] if questoes_isoladas else None
    }
    
    print("\n-> ESTRUTURA FINAL DA QUESTÃO EM JSON:")
    print(json.dumps(questao_demo, ensure_ascii=False, indent=4))
    print(f"\n{'='*60}\n DEMONSTRAÇÃO CONCLUÍDA\n{'='*60}")

if __name__ == "__main__":
    caminho = "/home/viniciusdesktop/Documentos/Projetos/QuestoesConcursoSeeder/pdfquestoes.pdf"
    demonstracao_passo_a_passo(caminho, pagina_alvo=0)