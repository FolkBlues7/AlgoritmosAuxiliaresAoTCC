import json
import pymupdf

# Importações anteriores
from extratores.extrair_cabecalhos import extrair_todos_cabecalhos_pdf
from extratores.extrair_gabarito import extrair_gabarito
from extratores.reordenar_html_pdf import reordenar_e_juntar_alternativas
from extratores.isolar_questoes_html import isolar_questoes_html
from extratores.limpar_questao import limpar_html_questao

def pipeline_principal(caminho_pdf: str):
    print("[1/5] Extraindo metadados (cabeçalhos) via OCR...")
    cabecalhos = extrair_todos_cabecalhos_pdf(caminho_pdf)
    mapa_cabecalhos = {c["numero"]: c for c in cabecalhos}

    print("[2/5] Abrindo PDF via PyMuPDF e extraindo gabarito...")
    doc = pymupdf.open(caminho_pdf)
    gabarito = extrair_gabarito(doc, num_pagina=-1)

    print("[3/5] Extraindo e reordenando HTML nativo...")
    html_bruto = ""
    for page in doc:
        html_bruto += page.get_text("html")
        
    html_ordenado = reordenar_e_juntar_alternativas(html_bruto)

    print("[4/5] Isolando blocos de questões no HTML...")
    questoes_isoladas_html = isolar_questoes_html(html_ordenado)

    print("[5/5] Mesclando todos os dados...")
    questoes_finais = []
    
    for i, html_q in enumerate(questoes_isoladas_html, start=1):
        meta = mapa_cabecalhos.get(i, {
            "codigo_q": "", "disciplina": "", "assuntos": [], 
            "ano": "", "banca": "", "orgao": ""
        })
        
        resposta_correta = gabarito.get(i, None)
        
        # --- NOVO: Recebe o dicionário com HTML e Imagem ---
        dados_limpos = limpar_html_questao(html_q)
        
        questao_completa = {
            "numero": i,
            "codigo_q": meta.get("codigo_q", ""),
            "disciplina": meta.get("disciplina", ""),
            "assuntos": meta.get("assuntos", []),
            "ano": meta.get("ano", ""),
            "banca": meta.get("banca", ""),
            "orgao": meta.get("orgao", ""),
            "gabarito": resposta_correta,
            "html_content": dados_limpos["html_content"],
            "imagem_base64": dados_limpos["imagem_base64"]
        }
        questoes_finais.append(questao_completa)

    nome_arquivo_saida = "banco_de_questoes_final.json"
    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(questoes_finais, f, ensure_ascii=False, indent=4)
        
    print(f"\n[-] Sucesso absoluto! {len(questoes_finais)} questões estruturadas e salvas em '{nome_arquivo_saida}'.")

if __name__ == "__main__":
    caminho_do_pdf = "/home/viniciusdesktop/Documentos/Projetos/QuestoesConcursoSeeder/pdfquestoes.pdf"
    pipeline_principal(caminho_do_pdf)