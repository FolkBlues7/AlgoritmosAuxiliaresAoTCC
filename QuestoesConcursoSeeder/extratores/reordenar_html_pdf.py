import re
from bs4 import BeautifulSoup

def reordenar_e_juntar_alternativas(html_str: str, tol_linha: float = 4.0, fundir_mesma_linha: bool = True) -> str:
    soup = BeautifulSoup(html_str, "html.parser")
    
    for page_div in soup.find_all("div"):
        children = [c for c in page_div.find_all(recursive=False) if c.get("style")]
        
        items = []
        for child in children:
            style = child.get("style", "")
            top_m = re.search(r"top:\s*([\d.]+)pt", style)
            left_m = re.search(r"left:\s*([\d.]+)pt", style)
            
            top = float(top_m.group(1)) if top_m else 0.0
            left = float(left_m.group(1)) if left_m else 0.0
            texto = child.get_text(strip=True)
            
            items.append({
                "top": top, 
                "left": left, 
                "elem": child,
                "texto": texto
            })
            
        # --- PASSO NOVO: Alinhamento inteligente de rótulos de alternativa ---
        for item in items:
            if item["texto"] in ["A", "B", "C", "D", "E"] and len(item["texto"]) == 1:
                vizinhos_direita = [
                    outro for outro in items 
                    if outro != item 
                    and outro["left"] > item["left"]
                    and abs(outro["top"] - item["top"]) <= 15.0
                ]
                
                if vizinhos_direita:
                    primeira_linha = min(vizinhos_direita, key=lambda x: x["top"])
                    item["top"] = primeira_linha["top"]

        # 1. Ordena todos os elementos pelo top
        items.sort(key=lambda x: x["top"])
        
        # 2. Agrupa dinamicamente em linhas (Clusters)
        linhas = []
        for item in items:
            if not linhas:
                linhas.append([item])
            else:
                ultima_linha = linhas[-1]
                media_top = sum(x["top"] for x in ultima_linha) / len(ultima_linha)
                
                if abs(item["top"] - media_top) <= tol_linha:
                    ultima_linha.append(item)
                else:
                    linhas.append([item])
                    
        # 3. Processa cada linha e reconstrói o container
        page_div.clear()
        
        for linha in linhas:
            linha.sort(key=lambda x: x["left"])
            
            # PROTEÇÃO PARA IMAGENS: Verifica se há alguma tag <img> ou filho <img> nesta linha
            tem_imagem = any(item["elem"].name == "img" or item["elem"].find("img") for item in linha)
            
            # Só funde o texto se não houver imagens envolvidas no meio
            if fundir_mesma_linha and len(linha) > 1 and not tem_imagem:
                primeiro_elem = linha[0]["elem"]
                textos = [item["elem"].get_text(strip=True) for item in linha]
                
                span = primeiro_elem.find("span")
                if span:
                    span.string = " ".join(textos)
                else:
                    primeiro_elem.string = " ".join(textos)
                    
                page_div.append(primeiro_elem)
            else:
                # Se for linha única, ou se contiver uma imagem, apenas insere na ordem correta
                for item in linha:
                    page_div.append(item["elem"])
                    
    return str(soup)