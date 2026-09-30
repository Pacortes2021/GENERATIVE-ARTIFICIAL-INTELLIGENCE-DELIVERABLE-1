import json

with open('base_conocimiento_udec.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

print("--- AUDITORÍA DE DATOS ---")
print(f"Total Chunks: {len(datos)}\n")

print("👉 EJEMPLOS DEL CALENDARIO:")
calendario = [d['texto'] for d in datos if "Calendario" in d['fuente']]
# Imprimir feriados
feriados = [c for c in calendario if "Feriado" in c]
for f in feriados[:5]:
    print(f)

print("\n👉 EJEMPLOS DEL REGLAMENTO:")
reglamento = [d['texto'] for d in datos if "Reglamento" in d['fuente']]
for r in reglamento[20:23]: # Tomar algunos del medio al azar
    print(r)
