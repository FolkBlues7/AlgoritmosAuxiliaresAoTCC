#!/usr/bin/env python3
"""Gera um cartão-resposta OMR vetorial em A4 e um mapa JSON das coordenadas.

Exemplo:
  python3 gerador_gabarito_omr.py --questions 60 --options ABCDE
  python3 gerador_gabarito_omr.py --questions 80 --options ABCDE --output prova.pdf
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

PAGE_W_PT, PAGE_H_PT = A4
PAGE_W_MM, PAGE_H_MM = PAGE_W_PT / mm, PAGE_H_PT / mm
SAFE_X = 16.0
CONTENT_W = PAGE_W_MM - 2 * SAFE_X
COLUMNS = 3
QUESTIONS_PER_PAGE = 60
ROWS_PER_COLUMN = 20
ROW_STEP_MM = 7.1
FIRST_ROW_CENTER_TOP_MM = 130.0
BUBBLE_DIAMETER_MM = 4.6
FIDUCIAL_SIZE_MM = 7.0


def y_pt(top_mm: float) -> float:
    """Translate a top-origin millimetre coordinate to PDF's bottom-origin points."""
    return PAGE_H_PT - top_mm * mm


def draw_text(c: canvas.Canvas, x_mm: float, top_baseline_mm: float, text: str,
              font: str = "Helvetica", size: float = 8.0,
              color: colors.Color = colors.black) -> None:
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x_mm * mm, y_pt(top_baseline_mm), text)


def draw_centered(c: canvas.Canvas, x_mm: float, top_baseline_mm: float, text: str,
                  font: str = "Helvetica", size: float = 8.0,
                  color: colors.Color = colors.black) -> None:
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(x_mm * mm, y_pt(top_baseline_mm), text)


def draw_top_rect(c: canvas.Canvas, x_mm: float, top_mm: float,
                  w_mm: float, h_mm: float, *, fill: bool = False,
                  stroke: bool = True, line_width: float = 0.5,
                  fill_color: colors.Color = colors.white,
                  stroke_color: colors.Color = colors.black) -> None:
    c.setLineWidth(line_width)
    c.setStrokeColor(stroke_color)
    c.setFillColor(fill_color)
    c.rect(x_mm * mm, PAGE_H_PT - (top_mm + h_mm) * mm,
           w_mm * mm, h_mm * mm, stroke=int(stroke), fill=int(fill))


def wrap_text(text: str, font: str, size: float, width_mm: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and stringWidth(candidate, font, size) > width_mm * mm:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def draw_fiducials(c: canvas.Canvas) -> list[dict[str, Any]]:
    # Solid, square registration marks set inside normal printer margins.
    offset = 8.5
    size = FIDUCIAL_SIZE_MM
    rects = [
        (offset, offset, "top_left"),
        (PAGE_W_MM - offset - size, offset, "top_right"),
        (offset, PAGE_H_MM - offset - size, "bottom_left"),
        (PAGE_W_MM - offset - size, PAGE_H_MM - offset - size, "bottom_right"),
    ]
    result = []
    for x, top, name in rects:
        draw_top_rect(c, x, top, size, size, fill=True, stroke=False, fill_color=colors.black)
        result.append({
            "name": name,
            "xMm": round(x, 3),
            "topMm": round(top, 3),
            "sizeMm": size,
            "centerMmTopOrigin": [round(x + size / 2, 3), round(top + size / 2, 3)],
        })
    return result


def draw_name_cells(c: canvas.Canvas, max_chars: int) -> list[dict[str, Any]]:
    rows = math.ceil(max_chars / 20)
    cell_w = 8.35
    cell_h = 7.2
    gap = 1.0
    start_x = (PAGE_W_MM - 20 * cell_w - 19 * gap) / 2
    top_start = 44.0
    boxes = []
    for i in range(max_chars):
        row, col = divmod(i, 20)
        x = start_x + col * (cell_w + gap)
        top = top_start + row * (cell_h + 1.1)
        draw_top_rect(c, x, top, cell_w, cell_h, line_width=0.45)
        boxes.append({"index": i + 1, "xMm": round(x, 3), "topMm": round(top, 3),
                      "widthMm": cell_w, "heightMm": cell_h})
    return boxes


def draw_candidate_fields(c: canvas.Canvas, max_name_chars: int) -> dict[str, Any]:
    name_rows = math.ceil(max_name_chars / 20)
    draw_text(c, SAFE_X, 40.5, f"NOME COMPLETO - UMA LETRA POR QUADRÍCULA (ATÉ {max_name_chars} CARACTERES)",
              "Helvetica-Bold", 7.4)
    name_boxes = draw_name_cells(c, max_name_chars)

    draw_text(c, SAFE_X, 67.2, "INSCRIÇÃO / MATRÍCULA:", "Helvetica-Bold", 7.4)
    id_x = SAFE_X + 34.0
    draw_top_rect(c, id_x, 61.0, 43.0, 8.0, line_width=0.45)
    draw_text(c, 113.0, 67.2, "TURMA / SALA:", "Helvetica-Bold", 7.4)
    draw_top_rect(c, 137.0, 61.0, 57.0, 8.0, line_width=0.45)

    draw_text(c, SAFE_X, 78.5, "ASSINATURA DO(A) CANDIDATO(A):", "Helvetica-Bold", 7.4)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.55)
    c.line(SAFE_X * mm, y_pt(84.0), (PAGE_W_MM - SAFE_X) * mm, y_pt(84.0))
    return {
        "nameBoxes": name_boxes,
        "studentIdBox": {"xMm": round(id_x, 3), "topMm": 61.0, "widthMm": 43.0, "heightMm": 8.0},
        "classBox": {"xMm": 137.0, "topMm": 61.0, "widthMm": 57.0, "heightMm": 8.0},
        "signatureLine": {"x1Mm": SAFE_X, "x2Mm": PAGE_W_MM - SAFE_X, "yMmTopOrigin": 84.0},
        "nameRows": name_rows,
    }


def draw_instructions(c: canvas.Canvas) -> None:
    top, height = 88.5, 20.0
    draw_top_rect(c, SAFE_X, top, CONTENT_W, height, line_width=0.45,
                  fill=True, fill_color=colors.HexColor("#F5F5F5"))
    draw_text(c, SAFE_X + 2.5, top + 4.5, "INSTRUÇÕES", "Helvetica-Bold", 7.2)
    instructions = [
        "Use exclusivamente caneta esferográfica preta; não use lápis. Preencha totalmente um único círculo por questão.",
        "Não marque com X, traço ou círculo externo. Para corrigir, apague por completo; não faça rasuras.",
        "Não dobre, amasse ou escreva sobre as marcas pretas de referência e as trilhas laterais.",
    ]
    y = top + 8.5
    for line in instructions:
        draw_text(c, SAFE_X + 2.5, y, "•  " + line, "Helvetica", 6.8)
        y += 3.6


def draw_bubble(c: canvas.Canvas, x_mm: float, top_center_mm: float) -> None:
    c.setLineWidth(0.65)
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.circle(x_mm * mm, y_pt(top_center_mm), (BUBBLE_DIAMETER_MM / 2) * mm,
             stroke=1, fill=1)


def chunk_questions(n_questions: int, per_page: int = QUESTIONS_PER_PAGE) -> list[list[int]]:
    return [list(range(start, min(start + per_page, n_questions + 1)))
            for start in range(1, n_questions + 1, per_page)]


def draw_answer_grid(c: canvas.Canvas, qnums: list[int], options: str,
                     page_num: int, page_count: int) -> dict[str, Any]:
    columns = COLUMNS
    rows_per_col = max(1, math.ceil(len(qnums) / columns))
    col_gap = 3.0
    col_w = (CONTENT_W - (columns - 1) * col_gap) / columns
    grid_x = SAFE_X
    panel_top = 117.0
    row_top_first = FIRST_ROW_CENTER_TOP_MM
    pitch = ROW_STEP_MM
    panel_bottom = row_top_first + (rows_per_col - 1) * pitch + 5.2
    panel_height = panel_bottom - panel_top

    draw_text(c, SAFE_X, 113.0,
              "RESPOSTAS - MARQUE COMPLETAMENTE UMA ÚNICA ALTERNATIVA POR QUESTÃO",
              "Helvetica-Bold", 8.0)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(colors.black)
    c.drawRightString((PAGE_W_MM - SAFE_X) * mm, y_pt(113.0), f"FOLHA {page_num}/{page_count}")

    # Per-column outlines and synchronism ticks provide fixed row landmarks.
    grid_layout: dict[str, Any] = {"page": page_num, "columns": [], "questions": []}
    columns_q = [qnums[i * rows_per_col:(i + 1) * rows_per_col] for i in range(columns)]
    for col_idx in range(columns):
        x = grid_x + col_idx * (col_w + col_gap)
        draw_top_rect(c, x, panel_top, col_w, panel_height, line_width=0.45)
        if col_idx:
            c.setStrokeColor(colors.HexColor("#9A9A9A"))
            c.setLineWidth(0.3)
            c.line(x * mm, y_pt(panel_top), x * mm, y_pt(panel_bottom))
        # Label and option headers.
        draw_centered(c, x + 11.4, 125.2, "Nº", "Helvetica-Bold", 6.8)
        region_left = x + 18.5
        region_right = x + col_w - 5.0
        if len(options) == 1:
            centers = [(region_left + region_right) / 2]
        else:
            option_pitch = min(8.0, (region_right - region_left) / (len(options) - 1))
            total = (len(options) - 1) * option_pitch
            start_center = (region_left + region_right - total) / 2
            centers = [start_center + i * option_pitch for i in range(len(options))]
        for letter, center_x in zip(options, centers):
            draw_centered(c, center_x, 125.2, letter, "Helvetica-Bold", 6.8)

        col_questions = columns_q[col_idx]
        col_entry = {"column": col_idx + 1, "xMm": round(x, 3), "widthMm": round(col_w, 3),
                     "timingTrackXmm": round(x + 1.2, 3), "questionNumbers": col_questions}
        grid_layout["columns"].append(col_entry)
        for row_idx, qnum in enumerate(col_questions):
            row_top = row_top_first + row_idx * pitch
            center_y_pt = y_pt(row_top)
            # Synchronism bar: one dark tick on each answer row.
            draw_top_rect(c, x + 1.1, row_top - 1.55, 1.4, 3.1,
                          fill=True, stroke=False, fill_color=colors.black)
            draw_text(c, x + 4.3, row_top + 1.05, f"{qnum:02d}", "Helvetica-Bold", 7.1)
            bubble_info = []
            for letter, center_x in zip(options, centers):
                draw_bubble(c, center_x, row_top)
                bubble_info.append({
                    "option": letter,
                    "centerMmTopOrigin": [round(center_x, 3), round(row_top, 3)],
                    "diameterMm": BUBBLE_DIAMETER_MM,
                })
            grid_layout["questions"].append({
                "question": qnum,
                "page": page_num,
                "column": col_idx + 1,
                "row": row_idx + 1,
                "rowCenterMmTopOrigin": round(row_top, 3),
                "timingMarkerCenterMmTopOrigin": [round(x + 1.8, 3), round(row_top, 3)],
                "bubbles": bubble_info,
            })
    return {
        "grid": grid_layout,
        "geometry": {
            "topMm": panel_top,
            "bottomMm": round(panel_bottom, 3),
            "xMm": SAFE_X,
            "widthMm": round(CONTENT_W, 3),
            "heightMm": round(panel_height, 3),
            "rowPitchMm": pitch,
            "bubbleDiameterMm": BUBBLE_DIAMETER_MM,
        },
    }


def make_pdf(args: argparse.Namespace) -> tuple[Path, Path]:
    options = args.options.upper().strip()
    if not 2 <= len(options) <= 5:
        raise ValueError("Use entre 2 e 5 alternativas, por exemplo ABCD ou ABCDE.")
    if len(set(options)) != len(options) or not options.isalnum():
        raise ValueError("As alternativas devem ser caracteres alfanuméricos únicos.")
    if args.questions < 1:
        raise ValueError("A quantidade de questões deve ser maior que zero.")
    if not 20 <= args.name_characters <= 40 or args.name_characters % 20 != 0:
        raise ValueError("--name-characters deve ser 20 ou 40.")

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    layout_path = output.with_suffix(".layout.json")
    pages = chunk_questions(args.questions)
    doc = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    doc.setTitle("Cartão-resposta OMR A4")
    doc.setAuthor("Gerador de cartão-resposta programático")
    doc.setSubject(f"{args.questions} questões; alternativas {options}; layout OMR com marcas fiduciárias")

    layout: dict[str, Any] = {
        "schemaVersion": "1.0",
        "formId": args.form_id,
        "pageSizeMm": [round(PAGE_W_MM, 3), round(PAGE_H_MM, 3)],
        "coordinateOrigin": "canto superior esquerdo; x cresce para a direita e y cresce para baixo",
        "questions": args.questions,
        "options": list(options),
        "columnsPerPage": COLUMNS,
        "questionsPerPage": QUESTIONS_PER_PAGE,
        "printScale": "100%; desativar ajustar à página",
        "fiducialSizeMm": FIDUCIAL_SIZE_MM,
        "bubbleDiameterMm": BUBBLE_DIAMETER_MM,
        "pages": [],
    }

    for page_idx, qnums in enumerate(pages, start=1):
        c = doc
        fiducials = draw_fiducials(c)
        draw_centered(c, PAGE_W_MM / 2, 14.0, "FOLHA DE RESPOSTAS - QUESTÕES OBJETIVAS",
                      "Helvetica-Bold", 12.0)
        draw_centered(c, PAGE_W_MM / 2, 20.0, args.organization.upper(),
                      "Helvetica-Bold", 7.1, colors.HexColor("#333333"))
        total_on_page = len(qnums)
        draw_centered(c, PAGE_W_MM / 2, 26.0,
                      f"FORMULÁRIO {args.form_id}  |  {args.questions} QUESTÕES  |  OPÇÕES {options}  |  FOLHA {page_idx}/{len(pages)}",
                      "Helvetica", 6.6, colors.HexColor("#333333"))
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.75)
        c.line(SAFE_X * mm, y_pt(30.0), (PAGE_W_MM - SAFE_X) * mm, y_pt(30.0))

        field_layout = draw_candidate_fields(c, args.name_characters)
        draw_instructions(c)
        grid = draw_answer_grid(c, qnums, options, page_idx, len(pages))

        # Printer note kept in the safe bottom area, well away from OMR marks.
        draw_centered(c, PAGE_W_MM / 2, PAGE_H_MM - 7.5,
                      "IMPRIMIR EM A4, ESCALA 100% - NÃO REDIMENSIONAR NEM MARCAR FORA DOS CAMPOS",
                      "Helvetica", 6.2, colors.HexColor("#444444"))
        layout["pages"].append({
            "page": page_idx,
            "questionRange": [qnums[0], qnums[-1]],
            "fiducials": fiducials,
            "candidateFields": field_layout,
            "answerGrid": grid["grid"],
            "gridGeometry": grid["geometry"],
        })
        c.showPage()

    doc.save()
    layout_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output, layout_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerar cartão-resposta OMR vetorial em A4.")
    parser.add_argument("--questions", type=int, default=60, help="quantidade total de questões (padrão: 60)")
    parser.add_argument("--options", default="ABCDE", help="alternativas únicas de A a E, por exemplo ABCDE (padrão)")
    parser.add_argument("--name-characters", type=int, default=40, help="quadrículas de nome: 20 ou 40 (padrão: 40)")
    parser.add_argument("--organization", default="INSTITUIÇÃO / PROCESSO SELETIVO", help="identificação impressa no cabeçalho")
    parser.add_argument("--form-id", default="OMR-A4-v1", help="identificador curto do formulário")
    parser.add_argument("--output", default="gabarito_A4_60q_ABCDE.pdf", help="caminho do PDF de saída")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    pdf_path, json_path = make_pdf(args)
    print(f"PDF: {pdf_path}")
    print(f"Mapa OMR: {json_path}")
