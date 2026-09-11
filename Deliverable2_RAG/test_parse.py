import fitz
import re

# Test Reglamento
doc = fitz.open('../Deliverables/Reglamento/Reglamento_de_Docencia_de_Pregrado-FI.pdf')
text = doc[1].get_text()
print("--- FI REG ---")
print(text[:500])

# Test Calendario
doc2 = fitz.open('../Deliverables/Reglamento/Calendario-Academico-Pregrado-2026.pdf')
text2 = doc2[0].get_text()
print("--- CALENDARIO ---")
print(text2[:500])
