import json

with open('base_conocimiento_udec.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

reglamentos = [d['texto'] for d in datos if "Reglamento" in d['fuente']]

total = len(reglamentos)
terminan_bien = 0
malos = []

for r in reglamentos:
    r_limpio = r.strip()
    # Un buen párrafo suele terminar en punto, dos puntos, punto y coma, o número (ej. títulos)
    if r_limpio.endswith('.') or r_limpio.endswith(':') or r_limpio.endswith(';') or r_limpio.endswith('"') or r_limpio[-1].isdigit():
        terminan_bien += 1
    else:
        malos.append(r_limpio)

print(f"Total de chunks de reglamento evaluados: {total}")
print(f"Chunks que terminan con puntuación correcta: {terminan_bien}")
print(f"Chunks 'sospechosos' (sin punto final): {len(malos)}")
print(f"Porcentaje de éxito estructural: {(terminan_bien/total)*100:.1f}%")

if malos:
    print("\nRevisando los sospechosos:")
    for m in malos[:3]:
        print(f"- {m[-50:]}")
