#!/usr/bin/env python3
"""Genera la propuesta de negocio de InmoVault en PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ── Paleta ──────────────────────────────────────────────────────────────────
VERDE     = HexColor("#0F3D2E")
VERDE_S   = HexColor("#1B5440")
DORADO    = HexColor("#C9A368")
DORADO_S  = HexColor("#E8D5B0")
CREMA     = HexColor("#FAF7F0")
GRAFITO   = HexColor("#1A1A1A")
GRIS      = HexColor("#5C5750")
LINEA     = HexColor("#E5DFD2")
ROJO      = HexColor("#B5443A")

PAGE_W, PAGE_H = A4

# ── Numeración de páginas ────────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page = self._pageNumber
        if page == 1:
            return
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(GRIS)
        txt = f"InmoVault — Propuesta de Negocio Confidencial   |   Pág. {page} de {page_count}"
        self.drawCentredString(PAGE_W / 2, 1.2 * cm, txt)
        self.restoreState()

# ── Flowable: banda de color ─────────────────────────────────────────────────
class ColorBand(Flowable):
    def __init__(self, color, height=0.5*cm, width=None):
        super().__init__()
        self.band_color = color
        self.band_height = height
        self.band_width = width

    def wrap(self, avail_w, avail_h):
        self.w = self.band_width or avail_w
        return self.w, self.band_height

    def draw(self):
        self.canv.setFillColor(self.band_color)
        self.canv.rect(0, 0, self.w, self.band_height, stroke=0, fill=1)

# ── Flowable: caja con fondo ─────────────────────────────────────────────────
class BoxedContent(Flowable):
    def __init__(self, paragraphs, bg_color, padding=0.4*cm, border_color=None):
        super().__init__()
        self.paragraphs = paragraphs
        self.bg_color = bg_color
        self.padding = padding
        self.border_color = border_color
        self._avail_w = 0

    def wrap(self, avail_w, avail_h):
        self._avail_w = avail_w
        inner_w = avail_w - 2 * self.padding
        total_h = self.padding
        for p in self.paragraphs:
            w, h = p.wrap(inner_w, avail_h)
            total_h += h + 4
        total_h += self.padding
        self._height = total_h
        return avail_w, total_h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg_color)
        if self.border_color:
            c.setStrokeColor(self.border_color)
            c.setLineWidth(1)
            c.roundRect(0, 0, self._avail_w, self._height, 6, stroke=1, fill=1)
        else:
            c.roundRect(0, 0, self._avail_w, self._height, 6, stroke=0, fill=1)
        c.restoreState()
        y = self._height - self.padding
        inner_w = self._avail_w - 2 * self.padding
        for p in self.paragraphs:
            w, h = p.wrap(inner_w, self._height)
            y -= h
            p.drawOn(c, self.padding, y)
            y -= 4

# ── Estilos ──────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_tag"] = ParagraphStyle("cover_tag",
        fontName="Helvetica", fontSize=9, textColor=DORADO,
        spaceAfter=8, letterSpacing=2, alignment=TA_LEFT)

    s["cover_title"] = ParagraphStyle("cover_title",
        fontName="Helvetica-Bold", fontSize=36, textColor=white,
        leading=42, spaceAfter=14, alignment=TA_LEFT)

    s["cover_subtitle"] = ParagraphStyle("cover_subtitle",
        fontName="Helvetica", fontSize=14, textColor=DORADO_S,
        leading=20, spaceAfter=28, alignment=TA_LEFT)

    s["cover_body"] = ParagraphStyle("cover_body",
        fontName="Helvetica", fontSize=11, textColor=HexColor("#D8DDD4"),
        leading=17, spaceAfter=6, alignment=TA_LEFT)

    s["section_label"] = ParagraphStyle("section_label",
        fontName="Helvetica-Bold", fontSize=8, textColor=DORADO,
        spaceAfter=6, letterSpacing=1.5, alignment=TA_LEFT)

    s["h1"] = ParagraphStyle("h1",
        fontName="Helvetica-Bold", fontSize=22, textColor=VERDE,
        leading=28, spaceAfter=10, spaceBefore=6, alignment=TA_LEFT)

    s["h2"] = ParagraphStyle("h2",
        fontName="Helvetica-Bold", fontSize=15, textColor=VERDE,
        leading=20, spaceAfter=8, spaceBefore=10, alignment=TA_LEFT)

    s["h3"] = ParagraphStyle("h3",
        fontName="Helvetica-Bold", fontSize=12, textColor=GRAFITO,
        leading=16, spaceAfter=4, spaceBefore=8, alignment=TA_LEFT)

    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=10.5, textColor=GRIS,
        leading=16, spaceAfter=8, alignment=TA_JUSTIFY)

    s["body_dark"] = ParagraphStyle("body_dark",
        fontName="Helvetica", fontSize=10.5, textColor=GRAFITO,
        leading=16, spaceAfter=8, alignment=TA_JUSTIFY)

    s["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=10.5, textColor=GRIS,
        leading=16, spaceAfter=5, leftIndent=14, alignment=TA_LEFT)

    s["bullet_bold"] = ParagraphStyle("bullet_bold",
        fontName="Helvetica-Bold", fontSize=10.5, textColor=GRAFITO,
        leading=16, spaceAfter=5, leftIndent=14, alignment=TA_LEFT)

    s["table_header"] = ParagraphStyle("table_header",
        fontName="Helvetica-Bold", fontSize=9.5, textColor=white,
        leading=14, alignment=TA_CENTER)

    s["table_cell"] = ParagraphStyle("table_cell",
        fontName="Helvetica", fontSize=9.5, textColor=GRAFITO,
        leading=13, alignment=TA_LEFT)

    s["table_cell_c"] = ParagraphStyle("table_cell_c",
        fontName="Helvetica", fontSize=9.5, textColor=GRAFITO,
        leading=13, alignment=TA_CENTER)

    s["highlight"] = ParagraphStyle("highlight",
        fontName="Helvetica-Bold", fontSize=10.5, textColor=VERDE,
        leading=16, spaceAfter=6, alignment=TA_LEFT)

    s["footer_note"] = ParagraphStyle("footer_note",
        fontName="Helvetica", fontSize=9, textColor=GRIS,
        leading=13, spaceAfter=4, alignment=TA_CENTER)

    s["big_number"] = ParagraphStyle("big_number",
        fontName="Helvetica-Bold", fontSize=28, textColor=VERDE,
        leading=32, spaceAfter=2, alignment=TA_CENTER)

    s["big_label"] = ParagraphStyle("big_label",
        fontName="Helvetica", fontSize=9, textColor=GRIS,
        leading=13, spaceAfter=0, alignment=TA_CENTER)

    s["quote"] = ParagraphStyle("quote",
        fontName="Helvetica-Oblique", fontSize=12, textColor=VERDE,
        leading=18, spaceAfter=6, leftIndent=10, alignment=TA_LEFT)

    return s

# ── Portada ──────────────────────────────────────────────────────────────────
def build_cover(c, styles):
    # Fondo verde
    c.setFillColor(VERDE)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Banda dorada izquierda
    c.setFillColor(DORADO)
    c.rect(0, 0, 0.5*cm, PAGE_H, stroke=0, fill=1)

    # Banda geométrica decorativa (esquina superior derecha)
    c.saveState()
    c.setFillColor(VERDE_S)
    c.setFillAlpha(0.5)
    c.roundRect(PAGE_W - 6*cm, PAGE_H - 6*cm, 8*cm, 8*cm, 60, stroke=0, fill=1)
    c.restoreState()

    # Logo mark
    c.setFillColor(DORADO)
    c.roundRect(2.2*cm, PAGE_H - 3.5*cm, 1*cm, 1*cm, 5, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(VERDE)
    c.drawCentredString(2.7*cm, PAGE_H - 3.1*cm, "V")

    # Nombre
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(white)
    c.drawString(3.5*cm, PAGE_H - 3.0*cm, "Inmo")
    c.setFillColor(DORADO)
    c.drawString(3.5*cm + c.stringWidth("Inmo", "Helvetica-Bold", 18),
                 PAGE_H - 3.0*cm, "Vault")

    # Fecha
    c.setFont("Helvetica", 9)
    c.setFillColor(DORADO_S)
    c.drawRightString(PAGE_W - 2*cm, PAGE_H - 3.0*cm, "Junio 2026 · Confidencial")

    # Título principal
    margin_l = 2.2*cm
    y = PAGE_H - 7.5*cm

    c.setFont("Helvetica", 9)
    c.setFillColor(DORADO)
    c.drawString(margin_l, y, "PROPUESTA DE NEGOCIO")

    y -= 1.0*cm
    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(white)
    c.drawString(margin_l, y, "InmoVault")

    y -= 1.2*cm
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DORADO_S)
    c.drawString(margin_l, y, "El catálogo digital verificado")
    y -= 0.7*cm
    c.drawString(margin_l, y, "para el mercado inmobiliario")
    y -= 0.7*cm
    c.drawString(margin_l, y, "venezolano y su diáspora.")

    # Separador
    y -= 0.8*cm
    c.setStrokeColor(DORADO)
    c.setLineWidth(1.5)
    c.line(margin_l, y, margin_l + 6*cm, y)

    # Resumen
    y -= 0.7*cm
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#D8DDD4"))
    lines = [
        "InmoVault digitaliza el inventario de inmobiliarias venezolanas",
        "y lo conecta con compradores locales y con los más de 7.7 millones",
        "de venezolanos en el exterior que buscan invertir en su país."
    ]
    for line in lines:
        c.drawString(margin_l, y, line)
        y -= 0.55*cm

    # Métricas clave — cajas
    y -= 0.9*cm
    metrics = [
        ("93,796", "propiedades\nactivas en portales VE"),
        ("+45%", "crecimiento usuarios\ndigitales (2 años)"),
        ("7.7M", "venezolanos en el\nexterior"),
    ]
    box_w = (PAGE_W - 4.4*cm - 2*0.4*cm) / 3
    x = margin_l
    for num, label in metrics:
        c.setFillColor(HexColor("#1B5440"))
        c.roundRect(x, y - 1.8*cm, box_w, 2*cm, 8, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(DORADO)
        c.drawCentredString(x + box_w/2, y - 0.6*cm, num)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(HexColor("#D8DDD4"))
        for i, ln in enumerate(label.split("\n")):
            c.drawCentredString(x + box_w/2, y - 1.2*cm - i*0.4*cm, ln)
        x += box_w + 0.4*cm

    # Pie de portada
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#8A9688"))
    c.drawString(margin_l, 1.5*cm,
                 "Documento confidencial preparado para presentación a inversores y socios estratégicos.")
    c.drawRightString(PAGE_W - 2*cm, 1.5*cm, "v1.0  ·  2026")

# ── Constructor del PDF ──────────────────────────────────────────────────────
def build_pdf(path):
    styles = make_styles()
    S = styles

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=2.2*cm,
        rightMargin=2.2*cm,
        topMargin=2.0*cm,
        bottomMargin=2.2*cm,
        title="InmoVault — Propuesta de Negocio",
        author="InmoVault",
        subject="Propuesta de Negocio Confidencial"
    )

    # ── Portada como primera página (se dibuja via onFirstPage) ──────────────
    story = []

    # Marcador de portada (página en blanco gestionada por el callback)
    story.append(PageBreak())

    # ── 1. Resumen Ejecutivo ─────────────────────────────────────────────────
    story += [
        Paragraph("RESUMEN EJECUTIVO", S["section_label"]),
        Paragraph("¿Qué es InmoVault?", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "InmoVault es una plataforma SaaS que convierte el catálogo de propiedades "
            "de las inmobiliarias venezolanas en una <b>experiencia digital confiable y verificada</b>, "
            "diseñada especialmente para dos audiencias: el comprador local que exige transparencia "
            "y el venezolano en el exterior que necesita invertir a distancia con seguridad.",
            S["body"]),
        Paragraph(
            "El producto combina un <b>catálogo digital white-label</b> (con la marca de cada inmobiliaria), "
            "herramientas de verificación documental, tours virtuales 360° y un CRM integrado, "
            "todo accesible desde web y móvil.",
            S["body"]),
        Spacer(1, 0.3*cm),
    ]

    # Pilares
    pillars = [
        ("📋", "Catálogo verificado", "Cada propiedad publicada pasa por validación de título, fotos y datos antes de aparecer en el portal."),
        ("🌎", "Mercado diáspora", "7.7 M de venezolanos en el exterior representan un segmento con alta capacidad de ahorro y deseo activo de invertir en Venezuela."),
        ("🏢", "White-label B2B", "La inmobiliaria opera su propia app y portal con su identidad; InmoVault es la tecnología invisible detrás."),
        ("📊", "CRM integrado", "Panel de leads, seguimiento de conversaciones y reportes de conversión incluidos en el plan."),
    ]

    for icon, title, desc in pillars:
        story.append(KeepTogether([
            BoxedContent(
                [
                    Paragraph(f"<b>{icon}  {title}</b>", S["highlight"]),
                    Paragraph(desc, S["body"]),
                ],
                bg_color=CREMA,
                border_color=LINEA,
                padding=0.35*cm
            ),
            Spacer(1, 0.25*cm),
        ]))

    story.append(PageBreak())

    # ── 2. El Problema ───────────────────────────────────────────────────────
    story += [
        Paragraph("EL PROBLEMA", S["section_label"]),
        Paragraph("El mercado inmobiliario venezolano opera en la desconfianza", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "Venezuela cuenta con más de 93,000 propiedades activas en portales digitales, "
            "pero el mercado sufre de problemas estructurales que frenan las transacciones:",
            S["body"]),
    ]

    problems = [
        ("Fotos desactualizadas o engañosas", "Los portales actuales no validan el estado real del inmueble; las fotos pueden tener años."),
        ("Títulos con problemas ocultos", "No existe un proceso estándar de verificación legal antes de publicar; el comprador descubre los problemas al final del proceso."),
        ("Brecha con la diáspora", "El venezolano en el exterior no tiene herramientas confiables para evaluar, negociar y cerrar una compra remotamente."),
        ("Gestión de leads manual", "Las inmobiliarias pierden clientes por falta de seguimiento; el 70% de los leads en portales actuales se responden con retraso mayor a 24h."),
        ("Identidad digital débil", "Las inmobiliarias dependen de portales genéricos y no construyen su propia marca digital ni base de clientes."),
    ]

    for i, (prob, detail) in enumerate(problems, 1):
        story.append(KeepTogether([
            BoxedContent(
                [
                    Paragraph(f"<b>Problema {i}: {prob}</b>", S["h3"]),
                    Paragraph(detail, S["body"]),
                ],
                bg_color=HexColor("#FDF5F4"),
                border_color=HexColor("#E8C0BC"),
                padding=0.35*cm
            ),
            Spacer(1, 0.2*cm),
        ]))

    story += [
        Spacer(1, 0.4*cm),
        BoxedContent(
            [Paragraph(
                '💬  "El comprador diáspora no necesita <i>confiar</i> — necesita <i>ver</i>. '
                'Sin herramientas de verificación, pierde la confianza antes de hacer la primera oferta."',
                S["quote"]
            )],
            bg_color=HexColor("#EDF4F0"),
            border_color=VERDE,
            padding=0.4*cm
        ),
    ]

    story.append(PageBreak())

    # ── 3. La Solución ───────────────────────────────────────────────────────
    story += [
        Paragraph("LA SOLUCIÓN", S["section_label"]),
        Paragraph("InmoVault: confianza como producto", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "InmoVault no es un portal de propiedades más. Es una <b>plataforma de gestión y publicación "
            "white-label</b> que la inmobiliaria adopta como su propio canal digital, con estándares "
            "de verificación que ningún portal genérico ofrece hoy en Venezuela.",
            S["body"]),
        Spacer(1, 0.3*cm),
    ]

    features = [
        ("01", "Catálogo digital verificado",
         "Cada propiedad pasa por un proceso de validación antes de publicarse: "
         "título revisado, fotos y video recientes, y estado legal confirmado. "
         "Un sello visible distingue las propiedades verificadas de las no verificadas."),
        ("02", "Tours virtuales 360°",
         "Integración con cámaras 360° y herramientas de recorrido virtual para que "
         "el comprador recorra cada espacio desde su teléfono, sin necesidad de viajar."),
        ("03", "App y portal white-label",
         "La inmobiliaria publica su catálogo bajo su propio nombre, colores y dominio. "
         "InmoVault es la tecnología invisible. El cliente nunca ve 'InmoVault'."),
        ("04", "CRM integrado + WhatsApp",
         "Panel de leads en tiempo real, histórico de conversaciones, etapas de negociación "
         "y alertas automáticas. Integración con WhatsApp Business para el seguimiento inmediato."),
        ("05", "Reporte legal express",
         "En alianza con estudios jurídicos locales, ofrecemos un resumen del estado del título "
         "y gravámenes en 48–72 horas, incluido en el plan Pro."),
        ("06", "Analytics para la inmobiliaria",
         "Dashboard con métricas de vistas, engagement por propiedad, fuentes de leads "
         "y tasas de conversión, para optimizar el inventario y el pricing."),
    ]

    for num, title, desc in features:
        story.append(KeepTogether([
            Table(
                [[
                    Paragraph(num, ParagraphStyle("fn2",
                        fontName="Helvetica-Bold", fontSize=13, textColor=DORADO,
                        alignment=TA_CENTER)),
                    [
                        Paragraph(title, S["h3"]),
                        Paragraph(desc, S["body"]),
                    ]
                ]],
                colWidths=[1.2*cm, None],
                style=TableStyle([
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("LEFTPADDING", (0,0), (-1,-1), 0),
                    ("RIGHTPADDING", (0,0), (-1,-1), 0),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ])
            ),
            HRFlowable(width="100%", thickness=0.5, color=LINEA, spaceAfter=8),
        ]))

    story.append(PageBreak())

    # ── 4. Mercado Objetivo ──────────────────────────────────────────────────
    story += [
        Paragraph("MERCADO OBJETIVO", S["section_label"]),
        Paragraph("Dos audiencias, una plataforma", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
    ]

    # Tabla de audiencias
    audience_data = [
        [
            Paragraph("SEGMENTO", S["table_header"]),
            Paragraph("PERFIL", S["table_header"]),
            Paragraph("DOLOR PRINCIPAL", S["table_header"]),
            Paragraph("TAMAÑO EST.", S["table_header"]),
        ],
        [
            Paragraph("Comprador local", S["table_cell"]),
            Paragraph("Clase media-alta caraqueña, 30–55 años, busca seguridad jurídica", S["table_cell"]),
            Paragraph("No confía en las fotos ni en la disponibilidad real del inmueble", S["table_cell"]),
            Paragraph("~80,000 transacciones/año", S["table_cell_c"]),
        ],
        [
            Paragraph("Diáspora venezolana", S["table_cell"]),
            Paragraph("Venezolano en Miami, Madrid, Bogotá, con ahorros en USD", S["table_cell"]),
            Paragraph("No puede evaluar ni cerrar una compra sin viajar; no confía en intermediarios anónimos", S["table_cell"]),
            Paragraph("7.7 M personas, mercado activo y creciente", S["table_cell_c"]),
        ],
        [
            Paragraph("Inmobiliaria (cliente B2B)", S["table_cell"]),
            Paragraph("Empresa con 1–200 agentes, sin app propia, usa portales genéricos", S["table_cell"]),
            Paragraph("Pierde leads, no tiene trazabilidad, depende de terceros para su presencia digital", S["table_cell"]),
            Paragraph("~3,500 inmobiliarias formales en Venezuela", S["table_cell_c"]),
        ],
    ]

    audience_table = Table(
        audience_data,
        colWidths=[3.0*cm, 4.5*cm, 5.0*cm, 3.5*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), VERDE),
            ("TEXTCOLOR", (0,0), (-1,0), white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, CREMA]),
            ("GRID", (0,0), (-1,-1), 0.5, LINEA),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9.5),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROUNDEDCORNERS", (0,0), (-1,-1), [6, 6, 6, 6]),
        ])
    )
    story.append(audience_table)
    story.append(Spacer(1, 0.5*cm))

    # Métricas de mercado
    story += [
        Paragraph("Dimensionamiento del mercado", S["h2"]),
        Paragraph(
            "Venezuela experimenta una recuperación gradual del sector inmobiliario desde 2021. "
            "El mercado opera casi exclusivamente en dólares, y la diáspora—con mayor acceso a liquidez "
            "en USD—se está convirtiendo en el comprador más activo y con mayor ticket promedio.",
            S["body"]),
    ]

    metrics_data = [
        [
            Paragraph("$1,200 M", S["big_number"]),
            Paragraph("$480 M", S["big_number"]),
            Paragraph("35%", S["big_number"]),
        ],
        [
            Paragraph("Mercado inmobiliario\nestimado VE (2025)", S["big_label"]),
            Paragraph("Segmento diáspora\ndirecto (estimado)", S["big_label"]),
            Paragraph("Crecimiento anual\ntransacciones digitales", S["big_label"]),
        ],
    ]

    metrics_table = Table(
        metrics_data,
        colWidths=[(PAGE_W - 4.4*cm) / 3] * 3,
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), CREMA),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING", (0,0), (-1,-1), 16),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LINEBEFORE", (1,0), (1,-1), 1, LINEA),
            ("LINEBEFORE", (2,0), (2,-1), 1, LINEA),
        ])
    )
    story.append(metrics_table)
    story.append(PageBreak())

    # ── 5. Modelo de Negocio ─────────────────────────────────────────────────
    story += [
        Paragraph("MODELO DE NEGOCIO", S["section_label"]),
        Paragraph("SaaS B2B con upsells de servicios de valor", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "InmoVault cobra a la inmobiliaria una suscripción mensual o anual según el plan. "
            "El cliente B2B (la inmobiliaria) es el pagador; el comprador final usa la plataforma de forma gratuita. "
            "Ingresos adicionales provienen de servicios complementarios.",
            S["body"]),
        Spacer(1, 0.3*cm),
    ]

    # Planes
    plans_data = [
        [
            Paragraph("", S["table_header"]),
            Paragraph("BÁSICO", S["table_header"]),
            Paragraph("PRO  ★", S["table_header"]),
            Paragraph("ENTERPRISE", S["table_header"]),
        ],
        [Paragraph("Precio/mes", S["table_cell"]),
         Paragraph("$149", S["table_cell_c"]),
         Paragraph("$399", S["table_cell_c"]),
         Paragraph("A medida", S["table_cell_c"])],
        [Paragraph("Propiedades", S["table_cell"]),
         Paragraph("Hasta 100", S["table_cell_c"]),
         Paragraph("Ilimitadas", S["table_cell_c"]),
         Paragraph("Ilimitadas", S["table_cell_c"])],
        [Paragraph("App white-label", S["table_cell"]),
         Paragraph("✓", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"]),
         Paragraph("Propia (stores)", S["table_cell_c"])],
        [Paragraph("CRM de leads", S["table_cell"]),
         Paragraph("Básico", S["table_cell_c"]),
         Paragraph("Completo + WA", S["table_cell_c"]),
         Paragraph("Completo + WA", S["table_cell_c"])],
        [Paragraph("Tours 360°", S["table_cell"]),
         Paragraph("—", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"])],
        [Paragraph("Reporte legal", S["table_cell"]),
         Paragraph("—", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"])],
        [Paragraph("Soporte", S["table_cell"]),
         Paragraph("Correo", S["table_cell_c"]),
         Paragraph("Prioritario", S["table_cell_c"]),
         Paragraph("Gerente dedicado", S["table_cell_c"])],
        [Paragraph("Multi-sucursal", S["table_cell"]),
         Paragraph("—", S["table_cell_c"]),
         Paragraph("—", S["table_cell_c"]),
         Paragraph("✓", S["table_cell_c"])],
    ]

    plans_table = Table(
        plans_data,
        colWidths=[4.0*cm, 3.0*cm, 3.5*cm, 3.5*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), VERDE),
            ("BACKGROUND", (2,0), (2,-1), HexColor("#EDF4F0")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,0), (-1,0), white),
            ("TEXTCOLOR", (2,0), (2,-1), VERDE),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (0,-1), [white, CREMA]),
            ("ROWBACKGROUNDS", (1,1), (1,-1), [white, CREMA]),
            ("ROWBACKGROUNDS", (3,1), (3,-1), [white, CREMA]),
            ("GRID", (0,0), (-1,-1), 0.5, LINEA),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ])
    )
    story.append(plans_table)
    story.append(Spacer(1, 0.5*cm))

    # Upsells
    story += [
        Paragraph("Fuentes de ingreso adicionales", S["h2"]),
    ]
    upsells = [
        ("Reporte legal avulso", "$60–120 por propiedad para inmobiliarias del plan Básico"),
        ("Tour 360° de producción", "$80–150 por propiedad, producción propia o con aliados"),
        ("Leads por referido (diáspora)", "Comisión del 1–1.5% sobre cierres verificados con compradores referidos por InmoVault"),
        ("Publicidad premium", "Posicionamiento destacado en el catálogo para propiedades de alto valor"),
    ]
    for name, desc in upsells:
        story.append(Paragraph(f"<b>▸ {name}:</b> {desc}", S["bullet_bold"]))

    story.append(PageBreak())

    # ── 6. Proyecciones Financieras ──────────────────────────────────────────
    story += [
        Paragraph("PROYECCIONES FINANCIERAS", S["section_label"]),
        Paragraph("Escenario base — 36 meses", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "Las proyecciones asumen captación gradual de inmobiliarias, starting con el mercado de Caracas "
            "y expandiéndose al interior del país en el segundo año. Se considera un churn mensual del 3%.",
            S["body"]),
        Spacer(1, 0.3*cm),
    ]

    fin_data = [
        [
            Paragraph("PERÍODO", S["table_header"]),
            Paragraph("CLIENTES ACTIVOS", S["table_header"]),
            Paragraph("INGRESO MRR", S["table_header"]),
            Paragraph("INGRESO ARR", S["table_header"]),
            Paragraph("MARGEN BRUTO EST.", S["table_header"]),
        ],
        [Paragraph("Mes 6", S["table_cell_c"]),   Paragraph("15",  S["table_cell_c"]), Paragraph("$4,500",  S["table_cell_c"]), Paragraph("$54,000",   S["table_cell_c"]), Paragraph("72%", S["table_cell_c"])],
        [Paragraph("Mes 12", S["table_cell_c"]),  Paragraph("45",  S["table_cell_c"]), Paragraph("$13,500", S["table_cell_c"]), Paragraph("$162,000",  S["table_cell_c"]), Paragraph("74%", S["table_cell_c"])],
        [Paragraph("Mes 18", S["table_cell_c"]),  Paragraph("90",  S["table_cell_c"]), Paragraph("$27,000", S["table_cell_c"]), Paragraph("$324,000",  S["table_cell_c"]), Paragraph("76%", S["table_cell_c"])],
        [Paragraph("Mes 24", S["table_cell_c"]),  Paragraph("160", S["table_cell_c"]), Paragraph("$52,000", S["table_cell_c"]), Paragraph("$624,000",  S["table_cell_c"]), Paragraph("78%", S["table_cell_c"])],
        [Paragraph("Mes 36 ★", S["table_cell_c"]), Paragraph("320", S["table_cell_c"]), Paragraph("$108,000",S["table_cell_c"]), Paragraph("$1,296,000",S["table_cell_c"]), Paragraph("80%", S["table_cell_c"])],
    ]

    fin_table = Table(
        fin_data,
        colWidths=[2.8*cm, 3.2*cm, 3.2*cm, 3.5*cm, 3.3*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), VERDE),
            ("TEXTCOLOR", (0,0), (-1,0), white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, CREMA]),
            ("BACKGROUND", (0,5), (-1,5), HexColor("#EDF4F0")),
            ("FONTNAME", (0,5), (-1,5), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,5), (-1,5), VERDE),
            ("GRID", (0,0), (-1,-1), 0.5, LINEA),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ])
    )
    story.append(fin_table)

    story += [
        Spacer(1, 0.5*cm),
        BoxedContent(
            [
                Paragraph("<b>Supuestos clave:</b>", S["highlight"]),
                Paragraph("• Ticket promedio: $300/mes (mezcla entre plan Básico y Pro)", S["bullet"]),
                Paragraph("• CAC estimado inicial: $120 por inmobiliaria (outbound + demos)", S["bullet"]),
                Paragraph("• LTV estimado (12 meses): $3,600 por cliente", S["bullet"]),
                Paragraph("• Ratio LTV/CAC: 30x — modelo altamente eficiente en captación", S["bullet"]),
                Paragraph("• Inversión requerida para Mes 1–12: USD 180,000 (equipo + infra + marketing)", S["bullet"]),
            ],
            bg_color=CREMA,
            border_color=LINEA,
            padding=0.4*cm
        ),
    ]

    story.append(PageBreak())

    # ── 7. Ventaja Competitiva ───────────────────────────────────────────────
    story += [
        Paragraph("VENTAJA COMPETITIVA", S["section_label"]),
        Paragraph("Por qué InmoVault gana", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
    ]

    comp_data = [
        [
            Paragraph("CARACTERÍSTICA", S["table_header"]),
            Paragraph("InmoVault", S["table_header"]),
            Paragraph("Portales genéricos\n(Inmuebles24, MercadoLibre)", S["table_header"]),
            Paragraph("Competidores\nregionales", S["table_header"]),
        ],
        [Paragraph("White-label por inmobiliaria", S["table_cell"]),   Paragraph("✓", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"]), Paragraph("Parcial", S["table_cell_c"])],
        [Paragraph("Verificación de título incluida", S["table_cell"]), Paragraph("✓", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"])],
        [Paragraph("Tours 360°", S["table_cell"]),                      Paragraph("✓", S["table_cell_c"]), Paragraph("Opcional", S["table_cell_c"]), Paragraph("Parcial", S["table_cell_c"])],
        [Paragraph("CRM integrado", S["table_cell"]),                   Paragraph("✓", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"])],
        [Paragraph("Foco diáspora venezolana", S["table_cell"]),        Paragraph("✓", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"]), Paragraph("✗", S["table_cell_c"])],
        [Paragraph("Precio accesible para VE", S["table_cell"]),        Paragraph("✓", S["table_cell_c"]), Paragraph("✗ (modelo comisión)", S["table_cell_c"]), Paragraph("Medio", S["table_cell_c"])],
    ]

    comp_table = Table(
        comp_data,
        colWidths=[4.5*cm, 3.0*cm, 4.0*cm, 3.5*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), VERDE),
            ("TEXTCOLOR", (0,0), (-1,0), white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("BACKGROUND", (1,1), (1,-1), HexColor("#EDF4F0")),
            ("TEXTCOLOR", (1,1), (1,-1), VERDE),
            ("FONTNAME", (1,1), (1,-1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (0,-1), [white, CREMA]),
            ("ROWBACKGROUNDS", (2,1), (2,-1), [white, CREMA]),
            ("ROWBACKGROUNDS", (3,1), (3,-1), [white, CREMA]),
            ("GRID", (0,0), (-1,-1), 0.5, LINEA),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ])
    )
    story.append(comp_table)

    story += [
        Spacer(1, 0.5*cm),
        Paragraph("Barreras de entrada", S["h2"]),
        Paragraph(
            "InmoVault construye una ventaja sostenible a través de:",
            S["body"]),
    ]
    barriers = [
        "Red de aliados legales locales que validan títulos — difícil de replicar sin relaciones en Venezuela",
        "Datos propietarios de leads y comportamiento de compradores de diáspora — aumenta con cada transacción",
        "Lock-in del CRM: una vez que la inmobiliaria migra su base de leads a InmoVault, el costo de cambio es alto",
        "Marca construida sobre la identidad de cada inmobiliaria — fidelización a nivel de agentes, no solo gerencia",
    ]
    for b in barriers:
        story.append(Paragraph(f"<b>▸</b>  {b}", S["bullet"]))

    story.append(PageBreak())

    # ── 8. Roadmap ───────────────────────────────────────────────────────────
    story += [
        Paragraph("HOJA DE RUTA", S["section_label"]),
        Paragraph("Plan de ejecución — 18 meses", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
    ]

    roadmap = [
        ("Q3 2026\n(Meses 1–3)", "MVP & Pilotos",
         ["Desarrollo MVP: catálogo, CRM básico, panel de agente",
          "5 inmobiliarias piloto en Caracas (plan gratuito 3 meses)",
          "Alianzas con 2 estudios jurídicos para verificación",
          "Landing page + outreach a diáspora en Miami y Madrid"]),
        ("Q4 2026\n(Meses 4–6)", "Go-to-Market Caracas",
         ["Lanzamiento comercial: planes Básico y Pro",
          "Objetivo: 20 clientes activos de pago",
          "Integración WhatsApp Business",
          "Primer webinar para captación de diáspora"]),
        ("Q1–Q2 2027\n(Meses 7–12)", "Expansión y Product",
         ["Expansión a Valencia, Maracaibo y Lechería",
          "Tours 360° propios con equipo de producción",
          "Plan Enterprise: primeras inmobiliarias multi-sucursal",
          "Objetivo: 60 clientes activos, MRR $18K+"]),
        ("Q3–Q4 2027\n(Meses 13–18)", "Escala Regional",
         ["Expansión piloto Colombia / Panamá (venezolanos emigrados)",
          "App mobile nativa (iOS + Android)",
          "Módulo de financiamiento en alianza con bancos locales",
          "Objetivo: 120+ clientes, MRR $38K+"]),
    ]

    for period, phase, items in roadmap:
        bullet_paras = [Paragraph(f"• {item}", S["bullet"]) for item in items]
        story.append(KeepTogether([
            Table(
                [[
                    Paragraph(f"<b>{period}</b>", ParagraphStyle("rp",
                        fontName="Helvetica-Bold", fontSize=10, textColor=DORADO,
                        alignment=TA_CENTER, leading=14)),
                    [
                        Paragraph(phase, S["h3"]),
                    ] + bullet_paras,
                ]],
                colWidths=[2.5*cm, None],
                style=TableStyle([
                    ("BACKGROUND", (0,0), (0,-1), VERDE),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("TOPPADDING", (0,0), (-1,-1), 10),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
                    ("LEFTPADDING", (0,0), (0,-1), 6),
                    ("RIGHTPADDING", (0,0), (0,-1), 6),
                    ("LEFTPADDING", (1,0), (1,-1), 12),
                    ("RIGHTPADDING", (1,0), (1,-1), 8),
                    ("LINEAFTER", (0,0), (0,-1), 3, DORADO),
                    ("ROWBACKGROUNDS", (1,0), (1,-1), [CREMA]),
                ])
            ),
            Spacer(1, 0.3*cm),
        ]))

    story.append(PageBreak())

    # ── 9. Equipo ────────────────────────────────────────────────────────────
    story += [
        Paragraph("EL EQUIPO", S["section_label"]),
        Paragraph("Quiénes están detrás", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=12),
        Paragraph(
            "InmoVault nace de la combinación de experiencia en tecnología, "
            "conocimiento profundo del mercado inmobiliario venezolano y conexión directa "
            "con la comunidad de la diáspora.",
            S["body"]),
        Spacer(1, 0.3*cm),
    ]

    team = [
        ("Ezequiel R.", "CEO & Co-fundador",
         "Desarrollador de producto con experiencia en startups B2B SaaS. "
         "Visión de producto orientada a mercados emergentes de América Latina."),
        ("Cargo por definir", "CTO & Co-fundador",
         "Perfil técnico senior (fullstack / mobile). Experiencia en arquitectura "
         "de plataformas SaaS escalables. Reclutamiento en proceso."),
        ("Cargo por definir", "Head of Sales & Partnerships",
         "Conocimiento del sector inmobiliario venezolano. Red de contactos con "
         "inmobiliarias en Caracas, Valencia y Maracaibo. Reclutamiento en proceso."),
        ("Cargo por definir", "Legal & Compliance Advisor",
         "Abogado especialista en derecho inmobiliario venezolano. "
         "Responsable de las alianzas para la verificación de títulos."),
    ]

    for name, role, bio in team:
        story.append(KeepTogether([
            BoxedContent(
                [
                    Paragraph(f"<b>{name}</b>  ·  {role}", S["highlight"]),
                    Paragraph(bio, S["body"]),
                ],
                bg_color=CREMA,
                border_color=LINEA,
                padding=0.35*cm
            ),
            Spacer(1, 0.2*cm),
        ]))

    story += [
        Spacer(1, 0.4*cm),
        BoxedContent(
            [
                Paragraph("<b>¿Buscamos?</b>", S["h3"]),
                Paragraph(
                    "• Inversor semilla: USD 150,000–250,000 para financiar el MVP y los primeros 12 meses de operación.",
                    S["bullet"]),
                Paragraph(
                    "• Socio estratégico: inmobiliaria o grupo del sector que quiera co-construir el producto como cliente ancla.",
                    S["bullet"]),
                Paragraph(
                    "• Advisors con red en el ecosistema proptech latinoamericano o en la diáspora venezolana.",
                    S["bullet"]),
            ],
            bg_color=HexColor("#EDF4F0"),
            border_color=VERDE,
            padding=0.4*cm
        ),
    ]

    story.append(PageBreak())

    # ── 10. Contacto y Cierre ────────────────────────────────────────────────
    story += [
        Paragraph("PRÓXIMOS PASOS", S["section_label"]),
        Paragraph("Hablemos", S["h1"]),
        HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=16),
        Paragraph(
            "Si estás interesado en conocer más, agendar una demo del prototipo o explorar "
            "una posible alianza, este es el momento de dar el primer paso.",
            S["body"]),
        Spacer(1, 0.5*cm),
        BoxedContent(
            [
                Paragraph("<b>Ezequiel Ramírez</b>", S["h2"]),
                Paragraph("CEO &amp; Co-fundador · InmoVault", S["body_dark"]),
                Spacer(1, 0.2*cm),
                Paragraph("📧  ezeram94@gmail.com", S["body_dark"]),
                Paragraph("🌐  inmovault.com  (en construcción)", S["body_dark"]),
            ],
            bg_color=CREMA,
            border_color=LINEA,
            padding=0.5*cm
        ),
        Spacer(1, 0.6*cm),
        Paragraph(
            "Este documento es confidencial y está destinado exclusivamente a los destinatarios "
            "autorizados. No debe reproducirse ni distribuirse sin el consentimiento expreso de InmoVault.",
            ParagraphStyle("disclaimer",
                fontName="Helvetica-Oblique", fontSize=9, textColor=GRIS,
                leading=14, alignment=TA_CENTER)
        ),
    ]

    # ── Build ────────────────────────────────────────────────────────────────
    def on_first_page(c, doc):
        build_cover(c, styles)

    def on_later_pages(c, doc):
        # Header line
        c.saveState()
        c.setFillColor(VERDE)
        c.rect(0, PAGE_H - 1.0*cm, PAGE_W, 0.4*cm, stroke=0, fill=1)
        c.setFillColor(DORADO)
        c.rect(0, PAGE_H - 1.0*cm, 0.5*cm, 0.4*cm, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(white)
        c.drawString(0.9*cm, PAGE_H - 0.75*cm, "InmoVault")
        c.setFont("Helvetica", 8)
        c.drawString(PAGE_W - 6*cm, PAGE_H - 0.75*cm, "Propuesta de Negocio — Confidencial")
        c.restoreState()

    doc.build(
        story,
        onFirstPage=on_first_page,
        onLaterPages=on_later_pages,
        canvasmaker=NumberedCanvas
    )
    print(f"PDF generado: {path}")

if __name__ == "__main__":
    build_pdf("/home/sharked/work/inmovault/propuesta-inmovault.pdf")
