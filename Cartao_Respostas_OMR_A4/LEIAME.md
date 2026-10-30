# Cartão-resposta OMR — A4

O gerador produz um formulário vetorial em PDF, otimizado para impressão em **A4 retrato**, com campos de identificação, nome letra por letra, assinatura, instruções e grade de respostas. O padrão acompanha o protótipo do TCC: **60 questões e cinco alternativas (A–E)** distribuídas em três colunas em uma única folha.

## Arquivos

- `gerador_gabarito_omr.py`: código-fonte Python parametrizável.
- `gabarito_A4_60q_ABCDE.pdf`: cartão padrão pronto para impressão.
- `gabarito_A4_60q_ABCDE.layout.json`: centros das bolhas, trilhas, marcas fiduciais e demais coordenadas para calibração no leitor OpenCV.
- `preview.png`: prévia rasterizada da página para inspeção rápida.

## Gerar outras quantidades

A biblioteca ReportLab é necessária (`python3 -m pip install reportlab`). Exemplos:

```bash
python3 gerador_gabarito_omr.py --questions 40 --options ABCDE --output gabarito_40.pdf
python3 gerador_gabarito_omr.py --questions 60 --options ABCDE --output gabarito_60.pdf
python3 gerador_gabarito_omr.py --questions 80 --options ABCD --output gabarito_80.pdf
```

As questões são distribuídas sequencialmente em três colunas. Até 60 itens cabem em uma folha; quantidades maiores são divididas automaticamente em páginas A4 adicionais, repetindo os campos de identificação em cada página. O número de quadrículas do nome pode ser 20 ou 40 (`--name-characters 20` ou `40`). As alternativas devem ser caracteres únicos; são aceitas de duas a cinco, com padrão A–E.

## Impressão e leitura óptica

Imprima em A4 retrato, em **escala 100%**, sem “ajustar à página”. Preferencialmente use impressão simples, papel branco e sem bordas adicionadas pela impressora. Oriente o candidato a preencher uma única bolha por questão, completamente, sem tocar nos marcadores laterais.

Os quatro quadrados pretos nos cantos são marcas de registro, 7 × 7 mm. Eles delimitam a folha e permitem estimar rotação e perspectiva. Cada linha de resposta também tem uma pequena barra preta de sincronismo. O JSON associado usa coordenadas em milímetros a partir do canto superior esquerdo e fornece a posição nominal de cada alternativa e cada marca; o algoritmo pode transformá-las para coordenadas da imagem depois de localizar os quatro fiduciais. A posição física real deve ser calibrada após digitalização de uma cópia impressa, pois impressoras e scanners podem introduzir pequenas variações.

O formulário é intencionalmente monocromático: texto, fiduciais, trilhas e contornos das bolhas são pretos, sem fundos coloridos que prejudiquem a segmentação. As bolhas permanecem vazias no PDF; o estudante deve preenchê-las.
