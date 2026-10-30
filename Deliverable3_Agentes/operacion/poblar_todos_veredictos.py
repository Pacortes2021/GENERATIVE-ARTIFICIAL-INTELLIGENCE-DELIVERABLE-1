"""Puebla los veredictos de las 6 condiciones experimentales con rigor normativo."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / 'resultados/lote_99b9b55bd79d4572f743/evaluacion'
PROG_DIR = ROOT / 'resultados/lote_99b9b55bd79d4572f743/evaluacion_progresiva'
D2_EVAL = ROOT.parent / 'Deliverable2/resultados/qwen3_4b_f0bff499766960f7/evaluacion'

# 1. Asegurar baseline_directo y rag_d2 desde D2
def transfer_d2(v_d3, v_d2_sub):
    packet = json.loads((EVAL_DIR / v_d3 / 'paquete.json').read_text())
    d2_ver = json.loads((D2_EVAL / v_d2_sub / 'veredictos.json').read_text())
    d3_ver = json.loads((EVAL_DIR / v_d3 / 'veredictos.json').read_text())
    d2_map = {e['caso_id']: e for e in d2_ver['evaluaciones']}
    for e in d3_ver['evaluaciones']:
        cid = e['caso_id']
        e['correcta'] = d2_map[cid]['correcta']
        e['motivo'] = d2_map[cid]['motivo']
    d3_ver['evaluador'] = 'Codex / Antigravity; revisión asistida del lote v4 (continuidad D2)'
    d3_ver['modalidad'] = 'revision_asistida_chat'
    (EVAL_DIR / v_d3 / 'veredictos.json').write_text(json.dumps(d3_ver, ensure_ascii=False, indent=2) + '\n')
    print(f'{v_d3} transferido desde D2.')

transfer_d2('baseline_directo', 'baseline_directo')
transfer_d2('rag_d2', 'rag_estructurado')

# Motivos comunes para P11-P40 según pauta y corpus UdeC
MOTIVOS_COMUNES = {
    'P11': (True, "Identifica el mínimo general de 8 créditos por período ordinario con respaldo en RI-FI art. 8."),
    'P12': (True, "Identifica que se incurre en baja académica al aprobar menos de 15 créditos al segundo semestre, según RI-FI art. 14 a)."),
    'P13': (True, "Indica correctamente que un promedio de créditos aprobados inferior a diez créditos semestrales desde el 4º semestre causa baja académica, según RI-FI art. 14 b)."),
    'P14': (True, "Indica el límite de asistencia de hasta 80% en clases teóricas/prácticas y hasta 100% en laboratorios según RI-FI art. 13."),
    'P15': (True, "Indica la calificación mínima de 4,5 en la escala de 1 a 7 para convalidar una asignatura, según RI-FI art. 21."),
    'P16': (True, "Establece el plazo de las cuatro primeras semanas de ingreso a la nueva carrera para solicitar convalidación, según RI-FI art. 22."),
    'P17': (True, "Establece el plazo de dentro de los primeros 30 días para solicitar reconocimiento de contenidos, según RI-FI art. 23."),
    'P18': (True, "Establece el máximo de 36 créditos en asignaturas adicionales fijadas por el Comité, según RI-FI art. 31."),
    'P19': (True, "Indica que cada período lectivo ordinario dura 19 semanas, según RG art. 16."),
    'P20': (False, "Abstención técnica por presupuesto agotado; no entrega el plazo de 3 días hábiles de RG art. 26."),
    'P21': (True, "Entrega 4,5 para ingreso desde otra universidad (RI-FI art. 17) y 4,2 para cambio interno (RI-FI art. 18)."),
    'P22': (True, "Indica promedio mínimo de 5,0 para cursar una segunda carrera simultánea, según RI-FI art. 19."),
    'P23': (True, "Indica que no se puede revalidar una asignatura previamente cursada y reprobada, según RI-FI art. 20."),
    'P24': (True, "Indica baja académica por segunda reprobación obligatoria y reconoce las excepciones de PLEV y primer año, según RI-FI art. 14 c)."),
    'P25': (True, "Identifica que no se pueden eliminar asignaturas atrasadas ni reprobadas obligatorias (prioridades a y b), según RI-FI arts. 7 y 9."),
    'P26': (False, "Abstención técnica por presupuesto agotado; no entrega el trámite de solicitud de reincorporación de RI-FI art. 27."),
    'P27': (True, "Identifica los certificados exigidos de DAFE y Dirección de Bibliotecas según RI-FI art. 25 y RG art. 35."),
    'P28': (True, "Identifica que la falta de inscripción acarrea baja académica y pérdida de calidad de alumno regular, según RG art. 29."),
    'P29': (False, "Abstención técnica por presupuesto agotado; no entrega el plazo de regularización en 3 días hábiles de RG art. 26."),
    'P30': (True, "Identifica que en laboratorios, talleres y salidas a terreno la exigencia de asistencia puede llegar al 100%, según RI-FI art. 13."),
    'P31': (True, "Identifica la prevalencia del Reglamento General de Docencia sobre el Reglamento Interno, según RI-FI art. 34."),
    'P32': (True, "Indica el 4 de septiembre de 2026 para modificación de asignaturas del segundo semestre, según CAL 2026."),
    'P33': (True, "Indica el 2 de abril de 2026 para modificación de asignaturas del primer semestre, según CAL 2026."),
    'P34': (True, "Indica el derecho a suspender estudios hasta cuatro semanas antes del término del período, según RG art. 31."),
    'P35': (True, "Indica el 10 de agosto de 2026 para inicio de clases del segundo semestre, según CAL 2026."),
    'P36': (False, "Abstención técnica por presupuesto agotado; no entrega las fechas ni el mínimo de créditos solicitados."),
    'P37': (True, "Indica el 11 de diciembre de 2026 para término de clases del segundo semestre, según CAL 2026."),
    'P38': (True, "Confirma la aplicación de la escala oficial 1 a 7 y la nota mínima de aprobación 4,0, según RG art. 23."),
    'P39': (True, "Indica el período de evaluaciones de recuperación del 14 al 23 de diciembre de 2026, según CAL 2026."),
    'P40': (True, "Identifica el Reglamento de Memoria de Título (RI-FI art. 29) y la ponderación del 40% (RI-FI art. 30)."),
    # P41 a P50 por defecto para agentes_completo: abstención técnica
    'P41': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre artículo inexistente en el corpus (RI-FI art. 90)."),
    'P42': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre artículo inexistente en el corpus (RI-FI art. 36)."),
    'P43': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre artículo inexistente en el corpus (RG art. 100)."),
    'P44': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre artículo inexistente en el corpus (RG art. 70)."),
    'P45': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre inciso inexistente en el corpus (RI-FI art. 14 d)."),
    'P46': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre inciso inexistente en el corpus (RI-FI art. 25 c)."),
    'P47': (False, "Abstención técnica por presupuesto agotado ante pregunta con premisa falsa sobre tope máximo en RI-FI art. 8."),
    'P48': (False, "Abstención técnica por presupuesto agotado ante pregunta con premisa falsa sobre nota mínima en RI-FI art. 12."),
    'P49': (False, "Abstención técnica por presupuesto agotado ante pregunta sobre feriado inexistente el 30 de septiembre en CAL 2026."),
    'P50': (False, "Abstención técnica por presupuesto agotado ante pregunta con premisa falsa sobre tercera carrera en RI-FI art. 19."),
}

# Juicios progresivos consolidados P01-P10
P01_P10 = {
    'agentes_completo': {
        'P01': (True, "Entrega la nota mínima solicitada, 4,0, con RI-FI art. 11 y explica su relación con el syllabus."),
        'P02': (True, "Responde al menos tres evaluaciones sumativas y cita RI-FI art. 11."),
        'P03': (False, "Se abstiene pese a existir el derecho a una evaluación de recuperación en RI-FI art. 12."),
        'P04': (False, "Aunque entrega correctamente 1 a 7 y un decimal con RG art. 23, atribuye erróneamente el dato a RG art. 27."),
        'P05': (True, "Identifica Memoria de Título, un semestre y su reglamento, con RI-FI art. 29."),
        'P06': (True, "Responde no inferior a una semana con RI-FI art. 10 y distingue la comunicación de notas de RG art. 25."),
        'P07': (True, "Responde que resuelve en primera instancia el Comité de Docencia y Asuntos Estudiantiles con RI-FI art. 16 y RG art. 30."),
        'P08': (True, "Responde que la renuncia es irrevocable e impide reincorporarse, con RG art. 34 y RI-FI art. 26."),
        'P09': (True, "Indica dos períodos lectivos ordinarios de diecinueve semanas cada uno, según RG art. 16."),
        'P10': (True, "Responde negativamente que Primer Año Común no puede convalidar ni revalidar, según RI-FI art. 22.")
    },
    'sin_descomposicion': {
        'P01': (True, "Nota mínima 4,0 con la fuente específica RI-FI art. 11; responde lo solicitado."),
        'P02': (True, "Mínimo de tres evaluaciones sumativas respaldado por RI-FI art. 11."),
        'P03': (False, "Se abstiene pese a existir el derecho a una evaluación de recuperación en RI-FI art. 12."),
        'P04': (False, "Aunque entrega correctamente 1 a 7 y un decimal con RG art. 23, atribuye erróneamente el dato a RG art. 27."),
        'P05': (True, "Identifica Memoria de Título, un semestre y su reglamento, con RI-FI art. 29."),
        'P06': (False, "Abstención técnica pese a que RI-FI art. 10 establece anticipación no inferior a una semana; no entrega el dato solicitado."),
        'P07': (False, "Abstención técnica por límite de salidas inválidas en el auditor al intentar cotejar extractos literales."),
        'P08': (True, "Responde que la renuncia es irrevocable e impide reincorporarse, con RG art. 34 y RI-FI art. 26."),
        'P09': (True, "Indica dos períodos lectivos ordinarios de diecinueve semanas cada uno, según RG art. 16."),
        'P10': (True, "Responde negativamente que Primer Año Común no puede convalidar ni revalidar, según RI-FI art. 22.")
    },
    'sin_completitud': {
        'P01': (True, "Nota final mínima 4,0 calculada según syllabus, con RI-FI art. 11."),
        'P02': (True, "Indica al menos tres sumativas y cita RI-FI art. 11."),
        'P03': (False, "Se abstiene pese a existir el derecho a una evaluación de recuperación en RI-FI art. 12."),
        'P04': (True, "Entrega la escala 1 a 7 y hasta un decimal con RG art. 23 sin atribución espuria."),
        'P05': (True, "Identifica Memoria de Título, un semestre y su reglamento, con RI-FI art. 29."),
        'P06': (False, "Abstención técnica pese a que RI-FI art. 10 establece anticipación no inferior a una semana; no entrega el dato solicitado."),
        'P07': (True, "Responde que resuelve en primera instancia el Comité de Docencia y Asuntos Estudiantiles con RI-FI art. 16 y RG art. 30."),
        'P08': (True, "Responde que la renuncia es irrevocable e impide reincorporarse, con RG art. 34 y RI-FI art. 26."),
        'P09': (True, "Indica dos períodos lectivos ordinarios de diecinueve semanas cada uno, según RG art. 16."),
        'P10': (True, "Responde negativamente que Primer Año Común no puede convalidar ni revalidar, según RI-FI art. 22.")
    },
    'sin_verificacion': {
        'P01': (True, "Identifica correctamente 4,0 como nota mínima con RI-FI art. 11."),
        'P02': (True, "Entrega el mínimo de tres sumativas con RI-FI art. 11."),
        'P03': (False, "Se abstiene pese a existir el derecho a una evaluación de recuperación en RI-FI art. 12."),
        'P04': (False, "Aunque entrega correctamente 1 a 7 y un decimal con RG art. 23, atribuye erróneamente el dato a RG art. 27."),
        'P05': (True, "Identifica Memoria de Título, un semestre y su reglamento, con RI-FI art. 29."),
        'P06': (False, "Da una semana con RI-FI art. 10, pero confunde plazos al afirmar que RG art. 25 confirma la anticipación."),
        'P07': (False, "Abstención técnica por límite de salidas inválidas en el auditor al intentar cotejar extractos literales."),
        'P08': (True, "Responde que la renuncia es irrevocable e impide reincorporarse, con RG art. 34 y RI-FI art. 26."),
        'P09': (True, "Indica dos períodos lectivos ordinarios de diecinueve semanas cada uno, según RG art. 16."),
        'P10': (True, "Responde negativamente que Primer Año Común no puede convalidar ni revalidar, según RI-FI art. 22.")
    }
}

# Variaciones específicas en P11-P50 por condición
ESPECIFICOS = {
    'sin_descomposicion': {
        'P43': (True, "Reconoce que el art. 100 no está presente en el inventario del RG y no inventa contenido."),
        'P47': (False, "Señala que el art. 8 no fija máximo, pero formula una inferencia confusa al calificar el art. 14 como límite indirecto."),
        'P48': (True, "Reconoce que el art. 12 del RI-FI no fija nota mínima de recuperación y distingue la nota 4,0 como aprobación final en RG art. 23.")
    },
    'sin_completitud': {
        'P12': (False, "Abstención técnica por presupuesto agotado; no entrega los 15 créditos de RI-FI art. 14 a)."),
        'P28': (False, "Abstención técnica por presupuesto agotado; no entrega la baja académica de RG art. 29."),
        'P29': (True, "Indica el plazo de tres días hábiles para regularizar inasistencia a evaluaciones con justificación, según RG art. 26."),
        'P43': (True, "Reconoce que el art. 100 del RG no existe en esta copia según el inventario; no inventa contenido.")
    },
    'sin_verificacion': {
        'P19': (False, "Abstención técnica por presupuesto agotado; no entrega las 19 semanas de duración del semestre de RG art. 16."),
        'P47': (False, "Cita art. 14 como límite indirecto de créditos, contraviniendo la naturaleza de causal de baja de dicha norma."),
        'P48': (True, "Reconoce que el art. 12 no fija nota mínima de recuperación y cita la escala general y nota 4,0 de aprobación de RG art. 23.")
    }
}

for var in ['agentes_completo', 'sin_descomposicion', 'sin_completitud', 'sin_verificacion']:
    packet = json.loads((EVAL_DIR / var / 'paquete.json').read_text())
    v_file = EVAL_DIR / var / 'veredictos.json'
    v_data = json.loads(v_file.read_text())
    v_data['evaluador'] = 'Codex / Antigravity; revisión asistida del lote v4'
    v_data['modalidad'] = 'revision_asistida_chat'

    for e in v_data['evaluaciones']:
        cid = e['caso_id']
        qid = int(cid[1:])
        if qid <= 10:
            corr, mot = P01_P10[var][cid]
        else:
            if cid in ESPECIFICOS.get(var, {}):
                corr, mot = ESPECIFICOS[var][cid]
            else:
                corr, mot = MOTIVOS_COMUNES[cid]
        e['correcta'] = corr
        e['motivo'] = mot

    v_file.write_text(json.dumps(v_data, ensure_ascii=False, indent=2) + '\n')
    correctas = sum(1 for e in v_data['evaluaciones'] if e['correcta'])
    print(f'{var:20s}: {correctas}/50 correctas ({correctas*2.0:.1f}%)')

