import re
from bs4 import BeautifulSoup

def isolar_questoes_html(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    questoes = []
    questao_atual_html = []
    
    # Regex para identificar o início da alternativa E (ex: "E uma procedure...")
    regex_alternativa_e = re.compile(r'^E\s+')
    
    # Itera sobre todas as páginas geradas pelo PyMuPDF (as tags <div id="pageX">)
    for page_div in soup.find_all("div"):
        
        # Pega TODOS os elementos diretos da página (textos, imagens, etc.) na ordem exata
        for elemento in page_div.find_all(recursive=False):
            texto = elemento.get_text(strip=True)
            
            # 1. Filtro de Ruído: Ignora cabeçalhos e rodapés da página
            if "Questões de Concurso" in texto or re.search(r'\d+\s+of\s+\d+', texto) or re.search(r'\d{2}/\d{2}/\d{4}', texto):
                continue
                
            # 2. Adiciona o elemento atual ao bloco da questão (seja ele <p> de texto ou <img> base64)
            questao_atual_html.append(str(elemento))
            
            # 3. Ponto de Corte: Se o texto do elemento bater com a alternativa E, fechamos a questão
            if regex_alternativa_e.match(texto):
                html_da_questao = "".join(questao_atual_html)
                questoes.append(html_da_questao)
                
                # Limpa o acumulador para iniciar a coleta da próxima questão
                questao_atual_html = []
                
    # 4. Tratamento de "Sobra": Caso a última página acabe cortando uma questão 
    # antes da alternativa E, salvamos o fragmento restante.
    if questao_atual_html:
        questoes.append("".join(questao_atual_html))
            
    return questoes

# --- Exemplo de Uso ---
# html_ordenado = """<div id="page0">...</div>""" 

# questoes_isoladas = isolar_questoes_html(html_ordenado)
# for i, q_html in enumerate(questoes_isoladas, 1):
#     print(f"--- Questão {i} ---")
#     print(q_html)
#     print("\n")