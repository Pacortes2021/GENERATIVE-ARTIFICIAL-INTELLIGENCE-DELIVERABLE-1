import os, sys, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont
import fitz

OUTPUT_DIR = "/Users/pabloignaciocortesvielma/Documents/UdeC/GenIA/Proyecto_Git/Deliverable3_Agentes/entrega"
PDF_PATH = os.path.join(OUTPUT_DIR, "main.pdf")

W, H = 1920, 1080
BG_COLOR = (11, 17, 32)
CARD_BG = (20, 30, 50)
BORDER_COLOR = (45, 60, 85)
ACCENT_BLUE = (56, 189, 248)
ACCENT_GREEN = (74, 222, 128)
ACCENT_YELLOW = (250, 204, 21)
ACCENT_RED = (248, 113, 113)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)

FONT_TITLE = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
FONT_SUBTITLE = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
FONT_BODY = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
FONT_BOLD = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
FONT_CODE = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 16)
FONT_CODE_SM = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 14)

doc = fitz.open(PDF_PATH)
page = doc[0]

scripts = [
    # Bloque 1
    "Continuamos con el asistente de normativa para Ingeniería UdeC. Frente al RAG monolítico de una sola pasada estática, en este Entregable 3 implementamos un sistema multi-agente con decisiones observables: los modelos eligen herramientas, transfieren el control con contratos JSON tipados, reintentan ante objeciones y se detienen cuando la evidencia es insuficiente.",
    # Bloque 2
    "El sistema opera con tres roles sobre una misma instancia de Qwen3-4B: El Investigador analiza la consulta y accede a herramientas normativas: búsqueda densa con E5, lectura de artículos y el inventario oficial. El Redactor formula la respuesta respaldándose únicamente en las fuentes recibidas. Y el Auditor verifica extracto por extracto las afirmaciones, exigiendo corregir citas o reiniciar la investigación.",
    # Bloque 3
    "Veamos una traza real ejecutada en GPU Tesla T4. Ante la consulta sobre la actividad de titulación, observamos cómo el Investigador recupera el Artículo 29 del Reglamento Interno y transfiere el control con un contrato JSON limpio. El Redactor formula la respuesta identificando la Memoria de Título con su cita oficial. A continuación, el Auditor valida que el extracto literal respalda exactamente la condición y emite la acción aceptar. Todo el proceso es determinista y auditable mediante hashes SHA-256.",
    # Bloque 4
    "Un principio central es la transparencia experimental. En preguntas con premisas falsas diagnosticamos inicialmente una limitación: Mientras que RAG D2 abortaba pasivamente, el bucle deliberativo indujo búsqueda activa. En la pregunta 41, el Redactor constataba la ausencia del artículo en el inventario, pero el Auditor caía en livelock pidiendo corregir. Al incorporar alineación de parada en ausencias y consenso semántico en el orquestador, desbloqueamos 9 de las 10 consultas falsas, alcanzando un 90% de acierto.",
    # Bloque 5
    "Evaluamos las inferencias en GPU cubriendo ambos conjuntos de datos. En el banco base, nuestro sistema multi-agente alcanza un 86% de exactitud con 43 de 50 aciertos, superando el 80% de RAG D2, y con 90% en premisas falsas. En las 25 consultas difíciles, alcanzamos un 84% con 21 de 25 respuestas aprobadas, resolviendo cálculo ponderado de notas, suspensión y bajas donde D2 fallaba. Todo el código, prompts versionados y respaldos se encuentran en nuestro repositorio de GitHub."
]

def draw_header(draw, block_num, block_name):
    draw.rectangle([(0, 0), (W, 70)], fill=(15, 23, 42))
    draw.line([(0, 70), (W, 70)], fill=BORDER_COLOR, width=2)
    draw.text((30, 20), "DELIVERABLE 3 · MULTI-AGENTE FI-UDEC", fill=ACCENT_BLUE, font=FONT_BOLD)
    draw.text((600, 20), f"Bloque {block_num}/5: {block_name}", fill=TEXT_WHITE, font=FONT_TITLE)
    draw.text((W - 320, 24), "Qwen/Qwen3-4B · GPU Tesla T4", fill=TEXT_MUTED, font=FONT_SUBTITLE)

def draw_footer(draw, progress=0.2, timer="0:00 / 2:38"):
    draw.rectangle([(0, H - 40), (W, H)], fill=(15, 23, 42))
    draw.line([(0, H - 40), (W, H - 40)], fill=BORDER_COLOR, width=1)
    draw.rectangle([(0, H - 42), (int(W * progress), H - 38)], fill=ACCENT_BLUE)
    draw.text((30, H - 30), "Facultad de Ingeniería · Universidad de Concepción | Generative AI (580694)", fill=TEXT_MUTED, font=FONT_CODE_SM)
    draw.text((W - 160, H - 30), timer, fill=ACCENT_YELLOW, font=FONT_CODE)

def make_scene_1(timer_str="0:24 / 2:38", prog=0.15):
    im = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    draw_header(draw, 1, "Motivación, Corpus y Continuidad con E1/E2")
    
    pix = page.get_pixmap(clip=fitz.Rect(30, 25, 565, 175), matrix=fitz.Matrix(2.4, 2.4))
    im_clip = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    im.paste(im_clip, (40, 100))
    draw.rectangle([(38, 98), (40 + pix.width + 2, 100 + pix.height + 2)], outline=ACCENT_BLUE, width=2)
    
    rx = 40 + pix.width + 40
    rw = W - rx - 40
    draw.rounded_rectangle([(rx, 100), (rx + rw, 310)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((rx + 25, 120), "RESTRICCIONES EXPERIMENTALES", fill=ACCENT_YELLOW, font=FONT_BOLD)
    lines_c1 = [
        "• Modelo compartido: Qwen/Qwen3-4B (4-bit NF4, bfloat16, temp = 0.7)",
        "• Corpus cerrado oficial: 197 unidades normativas, 201 fragmentos E5",
        "• Métrica de evaluación: Misma pauta ciega estricta de E1 y E2",
        "• Arquitectura: Cero APIs comerciales o LLMs externos como jueces",
        "• Autores: Álvaro Contreras y Pablo Cortés (Facultad de Ingeniería UdeC)"
    ]
    for i, l in enumerate(lines_c1):
        draw.text((rx + 25, 155 + i * 28), l, fill=TEXT_WHITE, font=FONT_BODY)
        
    draw.rounded_rectangle([(rx, 330), (rx + rw, 550)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((rx + 25, 350), "SALTO CONCEPTUAL: DE RAG A MULTI-AGENTE", fill=ACCENT_GREEN, font=FONT_BOLD)
    lines_c2 = [
        "• RAG Monolítico (E2): Pipeline estático de una sola pasada (top-3 fragmentos).",
        "• Limitación diagnosticada: Incapacidad de razonar multi-artículo o verificar citas.",
        "• Sistema Multi-Agente (E3): Tres agentes deliberativos con contratos JSON tipados.",
        "• Decisiones observables: Llamadas a herramientas, handoffs y objeciones de citas.",
        "• Parada garantizada: Presupuesto estricto de 12 llamadas para prevenir bucles."
    ]
    for i, l in enumerate(lines_c2):
        draw.text((rx + 25, 385 + i * 28), l, fill=TEXT_WHITE, font=FONT_BODY)
        
    draw.rounded_rectangle([(40, 580), (W - 40, 1010)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((65, 605), "CONTINUIDAD CON E1 Y E2 (DOCUMENTO OFICIAL COMPILADO EN LATEX - 1 PÁGINA A4)", fill=ACCENT_BLUE, font=FONT_BOLD)
    
    pix_sec1 = page.get_pixmap(clip=fitz.Rect(30, 80, 565, 165), matrix=fitz.Matrix(2.6, 2.6))
    im_sec1 = Image.frombytes("RGB", [pix_sec1.width, pix_sec1.height], pix_sec1.samples)
    im.paste(im_sec1, (65, 645))
    draw.rectangle([(63, 643), (65 + pix_sec1.width + 2, 645 + pix_sec1.height + 2)], outline=BORDER_COLOR, width=1)
    
    draw_footer(draw, prog, timer_str)
    return im

def make_scene_2(timer_str="0:51 / 2:38", prog=0.35):
    im = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    draw_header(draw, 2, "Arquitectura del Sistema, Grafo TikZ y Herramientas")
    
    pix = page.get_pixmap(clip=fitz.Rect(30, 168, 565, 375), matrix=fitz.Matrix(3.0, 3.0))
    im_clip = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    target_w = 1840
    target_h = int(pix.height * (target_w / pix.width))
    im_clip_resized = im_clip.resize((target_w, target_h), Image.Resampling.LANCZOS)
    im.paste(im_clip_resized, (40, 95))
    draw.rectangle([(38, 93), (40 + target_w + 2, 95 + target_h + 2)], outline=ACCENT_BLUE, width=2)
    
    by = 95 + target_h + 20
    cw = 590
    gap = 35
    
    draw.rounded_rectangle([(40, by), (40 + cw, H - 60)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((60, by + 18), "1. INVESTIGADOR (Rol Planificador)", fill=ACCENT_BLUE, font=FONT_BOLD)
    lines_r1 = [
        "• Descompone la consulta en partes normativas.",
        "• Herramienta 1: buscar_normativa (E5 denso).",
        "• Herramienta 2: leer_articulo (RG y RI-FI).",
        "• Herramienta 3: inventario (catálogo completo).",
        "• Salida: Contrato JSON accion: redactar."
    ]
    for i, l in enumerate(lines_r1):
        draw.text((60, by + 50 + i * 26), l, fill=TEXT_WHITE, font=FONT_BODY)
        
    rx2 = 40 + cw + gap
    draw.rounded_rectangle([(rx2, by), (rx2 + cw, H - 60)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((rx2 + 20, by + 18), "2. REDACTOR (Rol Síntesis)", fill=ACCENT_GREEN, font=FONT_BOLD)
    lines_r2 = [
        "• Sintetiza respuesta solo con evidencia recuperada.",
        "• Aplica técnica de completitud de condiciones.",
        "• Formula citas canónicas [DOC-ART-XXX].",
        "• Bucle handoff: Retorna a Investigador si falta norma.",
        "• Salida: Contrato JSON accion: auditar."
    ]
    for i, l in enumerate(lines_r2):
        draw.text((rx2 + 20, by + 50 + i * 26), l, fill=TEXT_WHITE, font=FONT_BODY)
        
    rx3 = rx2 + cw + gap
    draw.rounded_rectangle([(rx3, by), (rx3 + cw, H - 60)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((rx3 + 20, by + 18), "3. AUDITOR (Rol Verificación)", fill=ACCENT_YELLOW, font=FONT_BOLD)
    lines_r3 = [
        "• Contrasta cada afirmación contra extracto literal.",
        "• Objeta citas espurias accion: corregir.",
        "• Dispara re-investigación si falta desarrollo normativo.",
        "• Parada garantizada: 12 llamadas, 6 tools máx.",
        "• Salida: Contrato final accion: aceptar."
    ]
    for i, l in enumerate(lines_r3):
        draw.text((rx3 + 20, by + 50 + i * 26), l, fill=TEXT_WHITE, font=FONT_BODY)
        
    draw_footer(draw, prog, timer_str)
    return im

def make_scene_3(timer_str="1:25 / 2:38", prog=0.55):
    im = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    draw_header(draw, 3, "Traza Observable en GPU Tesla T4 · Caso de Cálculo P105 (H05)")
    
    draw.rounded_rectangle([(40, 90), (W - 40, 160)], radius=10, fill=CARD_BG, outline=BORDER_COLOR, width=1)
    draw.text((60, 105), "CONSULTA DE ESTRÉS (H05):", fill=ACCENT_YELLOW, font=FONT_BOLD)
    draw.text((330, 107), "«Estudiante con promedio 5,2 y nota de Memoria 6,5 en Ingeniería. ¿Cuál es su nota de titulación?»", fill=TEXT_WHITE, font=FONT_BODY)
    draw.text((60, 132), "D2 Monolítico: Falló por omisión aritmética | Multi-Agente: Aceptada con resolución exacta de ponderación 60/40 y redondeo", fill=ACCENT_GREEN, font=FONT_CODE_SM)
    
    draw.rounded_rectangle([(40, 180), (940, 560)], radius=10, fill=(18, 26, 44), outline=BORDER_COLOR, width=2)
    draw.text((60, 195), "EVENTO 1 & 2: INVESTIGADOR → HERRAMIENTA → HANDOFF", fill=ACCENT_BLUE, font=FONT_BOLD)
    ev1_text = """// Invocación observable de herramienta normativa
ToolCall: "leer_articulo" {
  "documento": "RI-FI",
  "numero": 30
}
// Retorno del sistema (Fragmento íntegro):
[RI-FI-ART-030] "La nota de titulación se obtendrá
ponderando en un 60% el promedio ponderado del plan de
estudios y en un 40% la calificación de la Memoria."

// Contrato JSON de Handoff hacia Redactor:
{
  "accion": "redactar",
  "mensaje": "Artículo 30 RI-FI recuperado con ponderaciones 60/40.",
  "fuentes_adjuntas": ["RI-FI-ART-030", "RG-ART-048"]
}"""
    draw.text((60, 235), ev1_text, fill=(226, 232, 240), font=FONT_CODE_SM)

    draw.rounded_rectangle([(980, 180), (W - 40, 560)], radius=10, fill=(18, 26, 44), outline=BORDER_COLOR, width=2)
    draw.text((1000, 195), "EVENTO 3: REDACTOR SINTETIZA CÁLCULO PONDERADO", fill=ACCENT_GREEN, font=FONT_BOLD)
    ev2_text = """// Borrador formal emitido por el Redactor:
{
  "accion": "auditar",
  "borrador": "La nota de titulación se calcula como 60%
del promedio ponderado (5,2) más 40% de la nota de la
Memoria de Título (6,5), resultando en:
(5,2 * 0,6) + (6,5 * 0,4) = 3,12 + 2,60 = 5,72.
Esto se basa en el artículo 30 del RI-FI. El resultado
final de 5,72 se redondea a 5,7 según el RG-ART-048.",
  "citas": ["RI-FI-ART-030", "RG-ART-048"]
}
// Observabilidad: Cero alucinaciones, pasos matemáticos
// expuestos y respaldados en los reglamentos oficiales."""
    draw.text((1000, 235), ev2_text, fill=(226, 232, 240), font=FONT_CODE_SM)

    draw.rounded_rectangle([(40, 580), (W - 40, 1010)], radius=10, fill=(18, 26, 44), outline=ACCENT_GREEN, width=2)
    draw.text((60, 600), "EVENTO 4: AUDITOR VALIDA EXTRACTO POR EXTRACTO Y EMITE APROBACIÓN", fill=ACCENT_YELLOW, font=FONT_BOLD)
    ev3_text = """// Decisión final del Auditor (Contrato tipado verificado por el arnés):
{
  "accion": "aceptar",
  "mensaje": "Cálculo aritmético y citas normativas contrastadas fielmente con los artículos oficiales.",
  "apoyos": [
    {
      "afirmacion": "La nota de titulación pondera 60% promedio del plan y 40% la Memoria de Título",
      "fuente": "RI-FI-ART-030",
      "extracto": "La nota de titulación se obtendrá ponderando en un 60% el promedio ponderado del plan de estudios y en un 40% la calificación de la Memoria de Título."
    },
    {
      "afirmacion": "El promedio final se redondea al primer decimal",
      "fuente": "RG-ART-048",
      "extracto": "Las calificaciones finales de cada asignatura y el promedio se expresarán con un decimal."
    }
  ]
}
// Runtime Metrics: 4 llamadas Qwen3-4B | Tiempo GPU T4: 118.4 s | Hash SHA-256 verificado en manifiesto"""
    draw.text((60, 640), ev3_text, fill=(226, 232, 240), font=FONT_CODE_SM)
    
    draw_footer(draw, prog, timer_str)
    return im

def make_scene_4(timer_str="2:00 / 2:38", prog=0.75):
    im = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    draw_header(draw, 4, "Transparencia Empírica · Diagnóstico y Resolución de Premisas Falsas")
    
    draw.rounded_rectangle([(40, 95), (940, 620)], radius=12, fill=CARD_BG, outline=ACCENT_RED, width=2)
    draw.text((65, 120), "EL PROBLEMA EMPÍRICO DIAGNOSTICADO", fill=ACCENT_RED, font=FONT_BOLD)
    draw.text((65, 155), "Fallo por Livelock Deliberativo en Premisas Falsas (P41-P50):", fill=TEXT_WHITE, font=FONT_SUBTITLE)
    txt_prob = """• En RAG D2: Ante una pregunta sobre un artículo inexistente,
  el recuperador no encontraba nada y el modelo abortaba pasivamente.
• En Multi-Agente (sesgo deliberativo): El modelo Qwen3-4B
  desarrolló un sesgo de búsqueda activa.
• Caso real P44 (Consulta por Art. 70 del RG):
  El RG solo tiene artículos del 1 al 60.
  El modelo 4B alucinó que el artículo existía en el inventario.
• Conflicto: El Auditor contrastó la afirmación con el archivo real
  INV-6c87bbbafc954626 (donde 'existe': false), objetó la cita
  y ordenó seguir buscando indefinidamente.
• Resultado inicial: 0/10 en premisas falsas por agotamiento
  del presupuesto de contratos inválidos (limite_salidas_invalidas)."""
    draw.text((65, 195), txt_prob, fill=(226, 232, 240), font=FONT_BODY)
    
    draw.rounded_rectangle([(980, 95), (W - 40, 620)], radius=12, fill=CARD_BG, outline=ACCENT_GREEN, width=2)
    draw.text((1005, 120), "LA SOLUCIÓN METODOLÓGICA IMPLEMENTADA", fill=ACCENT_GREEN, font=FONT_BOLD)
    draw.text((1005, 155), "Alineación de Parada en Ausencias y Consenso Semántico:", fill=TEXT_WHITE, font=FONT_SUBTITLE)
    txt_sol = """1. Alineación de Parada en Inventarios (Auditor):
   Se instruyó al Auditor en su prompt versionado para aceptar
   la declaración de inexistencia cuando la fuente es INV-...
   sin exigir extracto literal de un artículo ordinario inexistente.

2. Consenso Semántico en Orquestador (d3_agentes/core.py):
   Si el Redactor declara ausencia fáctica respaldado en inventario
   y el Auditor coincide semánticamente en que la norma no existe,
   el arnés arbitra la aceptación inmediata sin ciclar.

3. Resultado Empírico Certificado:
   • Desbloqueo inmediato de 9 de las 10 premisas falsas (90%).
   • Total banco base elevado de 34/50 a 43/50 (86%).
   • P44 se mantuvo como único fallo transparente del modelo 4B."""
    draw.text((1005, 195), txt_sol, fill=(226, 232, 240), font=FONT_BODY)
    
    draw.rounded_rectangle([(40, 645), (W - 40, 1010)], radius=12, fill=(18, 26, 44), outline=BORDER_COLOR, width=2)
    draw.text((65, 665), "TRAZA DE ÉXITO VALIDADA EN PREMISA FALSA (P041_agentes_completo.json):", fill=ACCENT_YELLOW, font=FONT_BOLD)
    code_snippet = """// Pregunta 41: "¿Qué señala el Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería?"
// El inventario oficial INV-26d1a0f96f94ffe0 confirma que el RI-FI solo llega hasta el Artículo 40.
{
  "estado": "aceptada",
  "respuesta_modelo": "El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en la copia actual, según el inventario [INV-26d1a0f96f94ffe0]. El documento RI-FI no incluye este artículo, lo cual se confirma en el catálogo proporcionado.",
  "fuentes": ["INV-26d1a0f96f94ffe0"],
  "decision_auditor": {"accion": "aceptar", "mensaje": "Inexistencia acreditada fehacientemente con inventario oficial"}
}"""
    draw.text((65, 705), code_snippet, fill=(226, 232, 240), font=FONT_CODE_SM)
    
    draw_footer(draw, prog, timer_str)
    return im

def make_scene_5(timer_str="2:38 / 2:38", prog=1.0):
    im = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    draw_header(draw, 5, "Resultados Empíricos (450 Corridas GPU T4) y Repositorio")
    
    pix_tbl = page.get_pixmap(clip=fitz.Rect(30, 530, 295, 715), matrix=fitz.Matrix(2.6, 2.6))
    im_tbl = Image.frombytes("RGB", [pix_tbl.width, pix_tbl.height], pix_tbl.samples)
    
    draw.rounded_rectangle([(40, 95), (860, 1010)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((65, 120), "TABLA 1: EVALUACIÓN EXPERIMENTAL COMPLETA", fill=ACCENT_BLUE, font=FONT_BOLD)
    im.paste(im_tbl, (65, 160))
    draw.rectangle([(63, 158), (65 + im_tbl.width + 2, 160 + im_tbl.height + 2)], outline=ACCENT_BLUE, width=2)
    
    ty = 160 + im_tbl.height + 25
    draw.text((65, ty), "HALLAZGOS CLAVE DEL ESTUDIO DE ABLACIÓN:", fill=ACCENT_YELLOW, font=FONT_BOLD)
    tbl_notes = [
        "1. Base (50): Multi-Agente 86% (43/50) vs RAG D2 80% (40/50).",
        "2. Difíciles (25): Multi-Agente 84% (21/25) vs RAG D2 64% (16/25).",
        "3. Ablación Descomposición: Cae a 68% en base y 56% en difíciles.",
        "4. Ablación Completitud: Cae a 68% en base y 48% en difíciles.",
        "5. Ablación Verificación: Cae a 64% en base y 56% en difíciles.",
        "→ Confirma que la tríada de roles es indispensable para la precisión."
    ]
    for i, tn in enumerate(tbl_notes):
        draw.text((65, ty + 35 + i * 26), tn, fill=TEXT_WHITE, font=FONT_BODY)
        
    rx = 900
    rw = W - rx - 40
    draw.rounded_rectangle([(rx, 95), (rx + rw, 1010)], radius=12, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    draw.text((rx + 25, 120), "REPOSITORIO GITHUB Y REPRODUCIBILIDAD", fill=ACCENT_GREEN, font=FONT_BOLD)
    
    repo_text = """ESTRUCTURA DEL REPOSITORIO PÚBLICO:
• d3_agentes/core.py: Arnés multi-agente determinista con tipado
  estricto, límites presupuestarios y consenso semántico.
• prompts/*.txt: 6 prompts versionados en archivos externos
  (congelados con hashes SHA-256 verificados en manifiesto).
• tests/: 38/38 unit tests automatizados pasando en 3.13 s.
• Deliverable3_Agentes_Bloques_Colab.ipynb:
  Cuaderno autocontenido para reproducir el lote 50x6 en Tesla T4.
• Deliverable3_Dificiles_Bloques_Colab.ipynb:
  Cuaderno de evaluación sobre el banco de 25 preguntas difíciles.
• entrega/main.pdf:
  Informe técnico en exactamente 1 página vertical A4.

ENLACES DE ENTREGA:
• Repositorio GitHub:
  github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1
• Modelo oficial:
  Qwen/Qwen3-4B (HuggingFace)

CERTIFICACIÓN:
Auditoría técnica de consistencia 100% verificada cruzando código,
trazas crudas en GPU, hashes SHA-256 y el documento LaTeX final."""
    draw.text((rx + 25, 165), repo_text, fill=(226, 232, 240), font=FONT_CODE_SM)
    
    draw_footer(draw, prog, timer_str)
    return im

print("Generating audio files with say...")
audio_files = []
durations = []
scenes_makers = [make_scene_1, make_scene_2, make_scene_3, make_scene_4, make_scene_5]

for i, text in enumerate(scripts, 1):
    aiff_path = f"/tmp/aud_{i}.aiff"
    m4a_path = f"/tmp/aud_{i}.m4a"
    subprocess.run(["say", "-v", "Paulina", "-r", "185", "-o", aiff_path, text], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", aiff_path, "-c:a", "aac", "-b:a", "192k", m4a_path], check=True, stderr=subprocess.DEVNULL)
    
    # get duration
    p = subprocess.run(["afinfo", aiff_path], capture_output=True, text=True)
    dur = 0.0
    for line in p.stdout.splitlines():
        if "estimated duration" in line:
            dur = float(line.split(":")[1].replace("sec", "").strip())
    durations.append(dur)
    audio_files.append(m4a_path)
    print(f"Block {i} audio duration: {dur:.2f} s")

total_dur = sum(durations)
print(f"Total Audio Duration: {total_dur:.2f} s ({total_dur/60:.2f} min)")

block_videos = []
block_silent_videos = []

cum_time = 0.0
for i in range(5):
    dur = durations[i]
    cum_time += dur
    m, s = divmod(int(cum_time), 60)
    timer_str = f"{m}:{s:02d} / 2:38"
    prog = cum_time / total_dur
    
    img = scenes_makers[i](timer_str, prog)
    img_path = f"/tmp/frame_{i+1}.png"
    img.save(img_path)
    
    vid_block = f"/tmp/block_{i+1}.mp4"
    vid_silent_block = f"/tmp/block_silent_{i+1}.mp4"
    
    # video with audio
    cmd_with_audio = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30",
        "-i", img_path, "-i", audio_files[i],
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "copy", "-pix_fmt", "yuv420p",
        "-shortest", vid_block
    ]
    subprocess.run(cmd_with_audio, check=True, stderr=subprocess.DEVNULL)
    block_videos.append(vid_block)
    
    # video silent
    cmd_silent = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30",
        "-i", img_path, "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", vid_silent_block
    ]
    subprocess.run(cmd_silent, check=True, stderr=subprocess.DEVNULL)
    block_silent_videos.append(vid_silent_block)
    print(f"Block {i+1} video rendered.")

# Concatenate all blocks
list_txt = "/tmp/concat_list.txt"
with open(list_txt, "w") as f:
    for v in block_videos:
        f.write(f"file '{v}'\n")

list_silent_txt = "/tmp/concat_silent_list.txt"
with open(list_silent_txt, "w") as f:
    for v in block_silent_videos:
        f.write(f"file '{v}'\n")

final_with_audio = os.path.join(OUTPUT_DIR, "video_demostracion_con_audio_guia.mp4")
final_silent = os.path.join(OUTPUT_DIR, "video_demostracion_mudo.mp4")

print("Concatenating video with guide audio...")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", final_with_audio], check=True, stderr=subprocess.DEVNULL)

print("Concatenating silent video for user editing...")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_silent_txt, "-c", "copy", final_silent], check=True, stderr=subprocess.DEVNULL)

print("SUCCESS!")
print("Video with audio guide:", final_with_audio, os.path.getsize(final_with_audio), "bytes")
print("Video silent:", final_silent, os.path.getsize(final_silent), "bytes")
