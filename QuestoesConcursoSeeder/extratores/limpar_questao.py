from bs4 import BeautifulSoup

def limpar_html_questao(q_html: str) -> dict:
    """
    Recebe o HTML bruto da questão, extrai a imagem (se existir),
    remove links/textos do Qconcursos e retorna o HTML limpo e a imagem separada.
    """
    soup = BeautifulSoup(q_html, "html.parser")
    
    # 1. Extrair a foto (se houver)
    img_tag = soup.find("img")
    imagem_b64 = img_tag["src"] if img_tag and "src" in img_tag.attrs else None
    
    if img_tag:
        img_tag.decompose() # Remove a imagem do HTML do enunciado
        
    # 2. Varre todos os textos procurando lixos de cabeçalho/rodapé
    for elemento_texto in soup.find_all(string=True):
        texto = elemento_texto.get_text(strip=True).lower()
        
        # Se encontrar a URL ou o título padrão do Qconcursos, deleta a tag
        if "qconcursos.com" in texto or "questões de concurso público" in texto:
            if elemento_texto.parent:
                elemento_texto.parent.decompose()
                
    # 3. Limpeza das tags completamente vazias para o JSON não ficar pesado
    for tag in soup.find_all(['span', 'p', 'div']):
        # Se a tag não tem texto e não tem outras tags essenciais (como table ou br), é excluída
        if not tag.get_text(strip=True) and not tag.find(['table', 'br']):
            tag.decompose()
            
    # Retorna um dicionário com o HTML limpo e a imagem separada
    return {
        "html_content": str(soup).strip(),
        "imagem_base64": imagem_b64
    }