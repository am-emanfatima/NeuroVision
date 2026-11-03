"""Structured, explicitly non-diagnostic MRI research reports.

Only actual Prediction objects are used by the application's export path.
Demonstration data may be printed *only* with sample=True, which visibly
watermarks the output. These reports do not impersonate a radiologist.
"""
from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from xml.sax.saxutils import escape

from backend import APP_VERSION, Prediction, RESEARCH_NOTICE


@dataclass(frozen=True)
class PatientDetails:
    """User-entered, unverified context; blank values are supported."""

    name: str = ""
    patient_id: str = ""
    age: str = ""
    sex: str = ""
    study_date: str = ""
    referring_clinician: str = ""
    institution: str = ""
    clinical_indication: str = ""
    sequence: str = ""


def fields(result: Prediction) -> list[tuple[str, str]]:
    items = [
        ("Application", "NeuroVision AI"),
        ("Version", APP_VERSION),
        ("Analysis UTC", result.time_utc),
        ("Image file", result.image.filename),
        ("Input format", result.image.format),
        ("Image dimensions", f"{result.image.width} x {result.image.height}"),
        ("Highest output", result.output_names[result.primary_index]),
        ("Highest output score", f"{result.top_score:.2f}%"),
        ("Top-two difference", f"{result.margin:.2f} percentage points"),
    ]
    for i, score in enumerate(result.scores):
        items.append((result.output_names[i], f"{score * 100:.2f}%"))
    items += [
        ("Class order verified", "Yes" if result.labels_verified else "No - displayed names use provisional mapping"),
        ("Model checksum", result.model_sha256),
        ("Limitation", RESEARCH_NOTICE),
    ]
    return items


def safe_spreadsheet_text(value: str) -> str:
    if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def export_csv(result: Prediction) -> bytes:
    """The raw CSV intentionally excludes optional identifying patient details."""
    handle = io.StringIO(newline="")
    writer = csv.writer(handle)
    writer.writerow(("Field", "Value"))
    writer.writerows((key, safe_spreadsheet_text(val)) for key, val in fields(result))
    return handle.getvalue().encode('utf-8-sig')


def _clean(value: object, *, limit: int = 160) -> str:
    # ReportLab Paragraph treats XML markup specially, so escape ALL user text.
    # Also prevent control characters and unbounded patient-entered content.
    raw = str(value or "")
    raw = " ".join("".join(ch if ch.isprintable() else " " for ch in raw).split())
    return escape(raw[:limit]) if raw else "Not provided"


def export_pdf(
    result: Prediction,
    patient: PatientDetails | None = None,
    *,
    image_bytes: bytes | None = None,
    sample: bool = False,
) -> bytes:
    """Generate a polished radiology-style *research* report.

    The report always distinguishes algorithmic scores from clinical findings.
    No radiological interpretation, physician name, or signature is invented.
    Images can be embedded only on explicit user opt-in.
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (
        KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
        TableStyle, Image as RLImage,
    )

    patient = patient or PatientDetails()
    navy = colors.HexColor("#172E49")
    dark = colors.HexColor("#20384F")
    blue = colors.HexColor("#267E91")
    teal = colors.HexColor("#167C84")
    subtle = colors.HexColor("#65758A")
    pale = colors.HexColor("#EFF5F8")
    line = colors.HexColor("#DCE6EC")
    warning = colors.HexColor("#A55521")
    amber_pale = colors.HexColor("#FFF6E8")
    white = colors.white

    buf = io.BytesIO()
    page_width, page_height = A4
    margin_x = 43
    usable = page_width - 2 * margin_x
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=margin_x, rightMargin=margin_x,
        topMargin=100, bottomMargin=54,
        title="NeuroVision AI | MRI Research Analysis | Not for clinical use",
        author="NeuroVision AI - automated research software",
        subject="Research classification with patient metadata; unsigned and non-diagnostic",
    )

    def pstyle(name, **kwargs):
        options = dict(fontName="Helvetica", leading=13, fontSize=9,
                       textColor=dark, spaceAfter=0)
        options.update(kwargs)
        return ParagraphStyle(name, **options)

    small = pstyle("small", fontSize=8, leading=11, textColor=subtle)
    content = pstyle("content", fontSize=9, leading=13.5)
    meta_label = pstyle("meta_label", fontName="Helvetica-Bold", fontSize=7.4, leading=11, textColor=subtle)
    meta_value = pstyle("meta_value", fontName="Helvetica-Bold", fontSize=9, leading=12)
    section = pstyle("section", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=navy)
    headline = pstyle("headline", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=navy)
    scorestyle = pstyle("score", fontName="Helvetica-Bold", fontSize=17, leading=22, textColor=teal)
    flagstyle = pstyle("flag", fontName="Helvetica-Bold", fontSize=8.2, leading=12, textColor=warning)
    row_text = pstyle("row_text", fontSize=8.4, leading=12)

    analysis_ref = hashlib.sha256(
        (result.time_utc + result.image.filename + result.model_sha256).encode("utf-8")
    ).hexdigest()[:12].upper()
    try:
        analysis_dt = datetime.fromisoformat(result.time_utc.replace("Z", "+00:00"))
        report_date = analysis_dt.strftime("%d %b %Y  %H:%M UTC")
    except (ValueError, TypeError):
        report_date = str(result.time_utc)

    def draw_page(canvas, document):
        canvas.saveState()
        # Established visual rhythm: navy brand banner, fine cyan rule, page footer.
        canvas.setFillColor(navy)
        canvas.rect(0, page_height - 81, page_width, 81, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#40D1CE"))
        canvas.rect(0, page_height - 85, page_width, 4, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 19)
        canvas.setFillColor(white)
        canvas.drawString(margin_x, page_height - 36, "NeuroVision AI")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#C5E7E9"))
        canvas.drawString(margin_x, page_height - 54, "BRAIN MRI IMAGE ANALYSIS  /  RESEARCH REPORT")
        canvas.setFont("Helvetica-Bold", 7.6)
        canvas.setFillColor(colors.HexColor("#FFE9BA"))
        canvas.drawRightString(page_width - margin_x, page_height - 31, "UNSIGNED  |  NON-DIAGNOSTIC")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#D1E6EF"))
        canvas.drawRightString(page_width - margin_x, page_height - 49, f"Report ref: {analysis_ref}")
        if sample:
            canvas.saveState()
            canvas.translate(page_width / 2, page_height / 2)
            canvas.rotate(37)
            canvas.setFillColor(colors.Color(0.67, 0.24, 0.15, alpha=.11))
            canvas.setFont("Helvetica-Bold", 31)
            canvas.drawCentredString(0, 0, "DEMONSTRATION ONLY")
            canvas.restoreState()
        canvas.setStrokeColor(line)
        canvas.line(margin_x, 53, page_width - margin_x, 53)
        canvas.setFont("Helvetica-Bold", 7.4)
        canvas.setFillColor(warning)
        canvas.drawString(margin_x, 39, "RESEARCH USE ONLY - NOT A RADIOLOGIST'S REPORT")
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(subtle)
        canvas.drawRightString(page_width - margin_x, 39, f"Page {document.page}")

    def heading(text: str):
        # Self-contained section heading + hairline
        row = Table([[Paragraph(text, section)]], colWidths=[usable])
        row.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.7, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return row

    def detail_cell(label: str, value: object):
        return [Paragraph(escape(label.upper()), meta_label), Paragraph(_clean(value), meta_value)]

    def detail_grid(rows):
        ncol = 3
        col = usable / ncol
        table = Table(
            [[detail_cell(label, val) for label, val in row] for row in rows],
            colWidths=[col] * ncol,
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), pale),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -2), .5, white),
            ("LINEAFTER", (0, 0), (-2, -1), .7, white),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    def note_block(text: str, bg=amber_pale, fg=warning):
        msg = Paragraph(text, ParagraphStyle(
            "panel_" + str(len(text)), parent=content, fontSize=8.6,
            leading=12.7, textColor=fg,
        ))
        t = Table([[msg]], colWidths=[usable])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), .5, line),
            ("LINEBEFORE", (0, 0), (0, 0), 3, warning if fg == warning else teal),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        return t

    story = []
    if sample:
        story += [note_block("<b>DEMONSTRATION DOCUMENT:</b> Invented patient details and model scores are used solely to preview the report layout. No MRI was analyzed for this sample."), Spacer(1, 8)]

    story.extend([
        Paragraph("Patient &amp; examination details", headline), Spacer(1, 5),
        detail_grid([
            [("Patient name", patient.name), ("Patient ID / code", patient.patient_id), ("Age", f"{patient.age} years" if patient.age else "")],
            [("Sex / gender (recorded)", patient.sex), ("MRI study date", patient.study_date), ("Referral / requested by", patient.referring_clinician)],
            [("Organization", patient.institution), ("Analysis generated", report_date), ("Report status", "Research / unsigned")],
        ]),
        Spacer(1, 7),
        heading("01  EXAMINATION & CLINICAL INFORMATION"), Spacer(1, 5),
        Paragraph("<b>Examination:</b> Brain MRI image - single uploaded " + _clean(result.image.format) + " image; not a complete MRI study.", content),
        Spacer(1, 4),
        Paragraph("<b>Sequence / view (user-entered):</b> " + _clean(patient.sequence), content),
        Spacer(1, 4),
        Paragraph("<b>Clinical indication (user-entered):</b> " + _clean(patient.clinical_indication, limit=500), content),
        Spacer(1, 6),
        heading("02  AUTOMATED IMAGE CLASSIFICATION"), Spacer(1, 5),
    ])

    high_output = _clean(result.output_names[result.primary_index], limit=90)
    title_box = Table([
        [Paragraph("HIGHEST-SCORING CONFIGURED CLASS", meta_label), Paragraph("MODEL SCORE", meta_label)],
        [Paragraph(high_output, headline), Paragraph(f"{result.top_score:.2f}%", scorestyle)],
    ], colWidths=[usable * .73, usable * .27])
    title_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E9F4F4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 1),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 11),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story += [title_box, Spacer(1, 4), Paragraph(
        "Scores are algorithmic output values, <b>not</b> validated diagnostic probabilities, confidence levels, or a clinical interpretation.", small), Spacer(1, 5)]

    score_rows = [[Paragraph("RANK", meta_label), Paragraph("CONFIGURED CLASS", meta_label),
                   Paragraph("SCORE DISTRIBUTION", meta_label), Paragraph("VALUE", meta_label)]]
    from reportlab.graphics.shapes import Drawing, Rect
    class_colors = {
        "Glioma": colors.HexColor("#328AC9"),
        "Meningioma": colors.HexColor("#9572C8"),
        "No tumor": colors.HexColor("#25B99B"),
        "Pituitary": colors.HexColor("#D35D89"),
    }
    ranked_indices = sorted(range(len(result.scores)), key=lambda i: result.scores[i], reverse=True)
    for rank, i in enumerate(ranked_indices, start=1):
        name, score = result.output_names[i], result.scores[i]
        width = usable * .31
        bar = Drawing(width, 14)
        bar.add(Rect(0, 3, width, 8, fillColor=colors.HexColor("#E3EDF1"), strokeColor=None, rx=3, ry=3))
        bar.add(Rect(0, 3, max(.01, width * max(0, min(1, score))), 8,
                     fillColor=class_colors.get(name, teal), strokeColor=None, rx=3, ry=3))
        score_rows.append([
            Paragraph(str(rank), row_text), Paragraph(_clean(name, limit=70), row_text), bar,
            Paragraph(f"{score * 100:.2f}%", row_text),
        ])
    score_table = Table(score_rows, colWidths=[usable * .09, usable * .30, usable * .45, usable * .16], repeatRows=1)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pale),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, colors.HexColor("#FAFCFE")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), .4, line),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story += [score_table, Spacer(1, 3)]
    if not result.labels_verified:
        story += [Paragraph(
            "<b>Provisional class labels:</b> The displayed names (Glioma, Meningioma, No tumor and Pituitary) "
            "come from the application's configured mapping, <b>not</b> verified training class-index records. "
            "Names may be assigned to incorrect outputs; they must not be treated as a finding.", small),
            Spacer(1, 5)]

    story += [
        heading("03  RADIOLOGICAL FINDINGS & IMPRESSION"), Spacer(1, 5),
        Paragraph("<b>Findings:</b> Not assessed. The application classifies one exported image; it does not review the full MRI examination, anatomical structures, contrast series or clinical records.", content),
        Spacer(1, 5),
        Paragraph("<b>Impression:</b> No radiological diagnosis or exclusion of disease is provided. The model's highest score is a research output only. Interpretation of the complete study requires a qualified radiologist.", content),
        Spacer(1, 5),
        note_block("<b>Clinical sign-off:</b> Not performed. This is an <b>unsigned automated research report</b>, not an MRI report issued by a doctor. Do not use it for diagnosis, screening, triage or treatment."),
        Spacer(1, 6),
        heading("04  TECHNICAL DETAILS & LIMITATIONS"), Spacer(1, 5),
        Paragraph("Input: " + _clean(result.image.filename, limit=125) + "  |  " +
                  f"{result.image.width} x {result.image.height} pixels  |  " + _clean(result.image.format) +
                  ". Image resized to 224 x 224 RGB pixels for EfficientNetB0 classification. ", small),
        Spacer(1, 4),
        Paragraph("Model SHA-256: " + _clean(result.model_sha256), small),
    ]
    if image_bytes:
        from PIL import Image as PILImage, ImageOps
        story.append(PageBreak())
        story += [
            heading("APPENDIX  |  UPLOADED REFERENCE IMAGE"), Spacer(1, 9),
            note_block("This is an illustrative copy of the uploaded JPEG/PNG. It is <b>not</b> diagnostic-quality imaging or a substitute for full DICOM review."),
            Spacer(1, 13),
        ]
        try:
            with PILImage.open(io.BytesIO(image_bytes)) as original:
                original.load()
                img = ImageOps.exif_transpose(original).convert("RGB")
                img.thumbnail((1100, 900))
                picture_buf = io.BytesIO()
                img.save(picture_buf, format="JPEG", quality=84)
            picture_buf.seek(0)
            rl_img = RLImage(picture_buf)
            scale = min((usable - 20) / rl_img.imageWidth, 510 / rl_img.imageHeight, 1)
            rl_img.drawWidth = rl_img.imageWidth * scale
            rl_img.drawHeight = rl_img.imageHeight * scale
            rl_img.hAlign = "CENTER"
            story.append(rl_img)
            story += [Spacer(1, 9), Paragraph("Reference image attached by the report exporter at the user's request.", small)]
        except (OSError, ValueError):
            story.append(Paragraph("Reference image could not be rendered; classification data remain unaffected.", small))

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return buf.getvalue()
