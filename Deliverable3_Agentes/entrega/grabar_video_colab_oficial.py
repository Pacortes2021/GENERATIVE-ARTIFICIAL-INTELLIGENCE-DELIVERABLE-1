#!/usr/bin/env python3
"""
Generador del Video Oficial de Google Colab en Modo Oscuro (Entregable 3).
Navega en tiempo real sobre Google Colab usando Playwright y captura la pantalla a 1080p,
sincronizado con los 5 bloques del guion humano (exactamente 170 segundos / 2m50s).
"""
import os
import sys
import time
import subprocess
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_DIR = Path("/Users/pabloignaciocortesvielma/Documents/UdeC/GenIA/Proyecto_Git")
OUTPUT_DIR = REPO_DIR / "Deliverable3_Agentes/entrega"
TEMP_DIR = Path("/tmp/colab_record_work")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

COLAB_URL = "https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable3_Agentes/Deliverable3_Demo_Video.ipynb"

FINAL_VIDEO_MUDO = OUTPUT_DIR / "video_demostracion_colab_mudo.mp4"
FINAL_VIDEO_AUDIO = OUTPUT_DIR / "video_demostracion_colab_con_audio_guia.mp4"

# Timeline choreography (total 170 seconds = 2m50s)
# Each keyframe: (timestamp_seconds, target_scroll_top, mouse_x, mouse_y)
KEYFRAMES = [
    # Bloque 1 (0:00 - 0:30): Introducción, Autores y Setup
    (0.0,    0,    500, 300),   # Title & authors Álvaro y Pablo
    (5.0,    0,    750, 320),   # Highlight authors
    (10.0,   0,    600, 420),   # Context description
    (14.0, 1350,   450, 400),   # Scroll down to Setup cell
    (20.0, 1350,   700, 450),   # Hover on GPU Tesla T4 & Qwen3-4B
    (25.0, 1350,   850, 520),   # Hover on 6/6 SHA-256 prompt hashes
    
    # Bloque 2 (0:30 - 1:00): Arquitectura y Grafo
    (30.0,  520,   600, 250),   # Scroll up to Architecture TikZ Graph
    (36.0,  520,   450, 480),   # Hover on Investigador node
    (43.0,  520,   890, 480),   # Hover on Redactor node
    (50.0,  520,  1330, 480),   # Hover on Auditor node & verification loop
    (56.0,  520,   600, 750),   # Hover on Normative Tools box
    
    # Bloque 3 (1:00 - 1:45): Consulta de Titulación P105 (45 s)
    (60.0, 2150,   500, 350),   # Scroll to Titulación Case H05/P105
    (68.0, 2150,   700, 420),   # Stress Question: promedio 5,2 y memoria 6,5
    (76.0, 2150,   650, 620),   # Event 1: Investigador calling leer_articulo(RI-FI, 30)
    (84.0, 2400,   650, 350),   # Event 2: Handoff JSON to Redactor
    (93.0, 2500,   750, 450),   # Event 3: Redactor calculation 5,2*0,6 + 6,5*0,4 = 5,72 -> 5,7
    (100.0, 2500,  850, 680),   # Event 4: Auditor veredicto "aceptar" with citas
    
    # Bloque 4 (1:45 - 2:20): Premisas Falsas P41 / P44 (35 s)
    (105.0, 3250,  500, 320),   # Scroll to False Premise Case P41
    (112.0, 3250,  650, 450),   # P41 question: Artículo 90
    (120.0, 3250,  700, 600),   # ToolCall inventario showing non-existence [INV-]
    (128.0, 3250,  800, 780),   # Consenso Semántico green card
    (135.0, 3250,  750, 880),   # Balance 9/10 (90%) and P44 livelock diagnosis
    
    # Bloque 5 (2:20 - 2:50): Auditoría Global, Tabla 1 y Ablaciones (30 s)
    (140.0, 3900,  500, 300),   # Scroll to Table 1 & Reproducible Audit
    (147.0, 3900,  750, 420),   # Multi-Agente E3 row (86% Base, 84% Difíciles, 4.5 llamadas)
    (155.0, 3900,  750, 520),   # Ablation rows: sin descomp., sin complet., sin verific.
    (163.0, 3900,  600, 680),   # Conclusión del estudio de ablación
    (170.0, 3900,  600, 680),   # Final hold
]

def main():
    print("=== Grabador Automatizado de Google Colab (Modo Oscuro) ===")
    print(f"URL destino: {COLAB_URL}")
    print(f"Duración objetivo: 170.0 segundos (2m 50s)")
    
    # Limpiar carpeta temporal de videos
    for f in TEMP_DIR.glob("*.webm"):
        f.unlink()
        
    with sync_playwright() as p:
        print("Lanzando Google Chrome en modo headless con emulación oscura...")
        browser = p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=True
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            color_scheme="dark",
            record_video_dir=str(TEMP_DIR),
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        print("Navegando a Google Colab...")
        page.goto(COLAB_URL, wait_until="networkidle", timeout=45000)
        time.sleep(4)
        
        # Inyectar cursor visual simulado para screencast profesional
        page.evaluate('''() => {
            const cursor = document.createElement('div');
            cursor.id = 'fake-cursor';
            cursor.style.cssText = 'position:fixed; width:16px; height:16px; border-radius:50%; background:rgba(56, 189, 248, 0.85); border:2px solid #ffffff; box-shadow:0 0 10px rgba(0,0,0,0.7); pointer-events:none; z-index:99999999; transform:translate(-50%, -50%); transition:left 0.4s ease-out, top 0.4s ease-out;';
            document.body.appendChild(cursor);
            window.addEventListener('mousemove', (e) => {
                cursor.style.left = e.clientX + 'px';
                cursor.style.top = e.clientY + 'px';
            });
        }''')
        
        print("Iniciando coreografía y navegación sincronizada de 170 segundos...")
        start_time = time.time()
        
        # Bucle de animación suave
        total_duration = 170.0
        fps = 10  # 10 actualizaciones de posición por segundo
        total_steps = int(total_duration * fps)
        
        for step in range(total_steps):
            current_t = step / fps
            
            # Encontrar los dos keyframes entre los que nos encontramos
            kf_prev = KEYFRAMES[0]
            kf_next = KEYFRAMES[-1]
            for i in range(len(KEYFRAMES) - 1):
                if KEYFRAMES[i][0] <= current_t <= KEYFRAMES[i+1][0]:
                    kf_prev = KEYFRAMES[i]
                    kf_next = KEYFRAMES[i+1]
                    break
                    
            t0, scroll0, mx0, my0 = kf_prev
            t1, scroll1, mx1, my1 = kf_next
            
            # Interpolación cúbica suave (ease-in-out)
            span = max(t1 - t0, 0.001)
            alpha = (current_t - t0) / span
            alpha_smooth = alpha * alpha * (3 - 2 * alpha)
            
            current_scroll = int(scroll0 + (scroll1 - scroll0) * alpha_smooth)
            current_mx = int(mx0 + (mx1 - mx0) * alpha_smooth)
            current_my = int(my0 + (my1 - my0) * alpha_smooth)
            
            # Aplicar scroll a .notebook-container
            page.evaluate(f'''() => {{
                const el = document.querySelector('.notebook-container');
                if (el) el.scrollTop = {current_scroll};
            }}''')
            
            # Mover mouse
            page.mouse.move(current_mx, current_my)
            
            # Mantener el ritmo de tiempo exacto
            elapsed = time.time() - start_time
            sleep_time = (current_t + 1.0/fps) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
            if step % (fps * 15) == 0:
                print(f"  Progreso: {int(current_t)}s / 170s | Scroll: {current_scroll}px | Mouse: ({current_mx}, {current_my})")
                
        print("Grabación de sesión completada.")
        context.close()
        browser.close()
        
    # Obtener el archivo .webm grabado por Playwright
    webm_files = list(TEMP_DIR.glob("*.webm"))
    if not webm_files:
        raise RuntimeError("Playwright no generó ningún archivo de video.")
    raw_video = webm_files[0]
    print(f"Video crudo generado por Playwright: {raw_video} ({raw_video.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # 1. Convertir a MP4 mudo oficial de alta compatibilidad (1080p, H.264, 30 fps)
    print(f"Exportando video mudo a: {FINAL_VIDEO_MUDO}")
    cmd_mudo = [
        "ffmpeg", "-y", "-i", str(raw_video),
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-crf", "20", str(FINAL_VIDEO_MUDO)
    ]
    subprocess.run(cmd_mudo, check=True)
    
    # 2. Generar audio guía con 'say' de macOS para sincronización opcional
    print("Sintetizando audio guía con el guion humano de 342 palabras...")
    spoken_blocks = [
        # B1 (0:00 - 0:30)
        "Hola, somos Álvaro Contreras y Pablo Cortés. Presentamos nuestro sistema multi-agente para normativas de la Facultad de Ingeniería de la Universidad de Concepción. Mientras en el entregable dos usamos un RAG de una sola pasada, aquí implementamos tres agentes deliberativos con Qwen3-4B cuantizado en NF4 sobre GPU Tesla T4, operando sobre un corpus de 197 unidades normativas.",
        # B2 (0:30 - 1:00)
        "Dividimos el trabajo en tres agentes coordinados por contratos JSON. El Investigador descompone consultas y consulta herramientas normativas: embeddings E5, lectura de artículos e inventario reglamentario. El Redactor sintetiza la respuesta con citas oficiales. Y el Auditor verifica extracto por extracto el respaldo documental y los cálculos; si detecta inconsistencias o alucinaciones, rechaza el borrador y abre un bucle de corrección supervisado.",
        # B3 (1:00 - 1:45)
        "Revisamos la traza real registrada en GPU T4 para la consulta P105: un estudiante con promedio 5,2 y nota 6,5 en su memoria de título. En los eventos observamos el flujo observable en JSON. El Investigador recupera el artículo 30 del RI-FI. Con esa evidencia, el Redactor aplica la ponderación de sesenta por ciento de asignaturas y cuarenta de memoria, calculando 5,72 que aproxima a 5,7. El Auditor valida el cálculo aritmético y emite la aprobación final.",
        # B4 (1:45 - 2:20)
        "En premisas falsas y normas inexistentes, evaluamos la capacidad de abstención del sistema. En la pregunta P41 sobre un supuesto artículo 90, el Investigador constata con el inventario que el reglamento solo posee 35 artículos. El Auditor valida formalmente esa ausencia, evitando el bloqueo o livelock observado en pruebas preliminares. Con esta alineación y el consenso semántico en el orquestador, el sistema resolvió exitosamente nueve de las diez premisas falsas.",
        # B5 (2:20 - 2:50)
        "Para reproducibilidad, la celda calcula dinámicamente los hashes SHA-256 de los seis prompts en disco. La tabla final registra un desempeño de ochenta y seis por ciento en el conjunto Base y ochenta y cuatro por ciento en las veinticinco consultas Difíciles, con cuatro coma cinco llamadas de inferencia de modelo por consulta. El estudio de ablación confirma la contribución del bucle de auditoría y la descomposición ante razonamientos complejos."
    ]
    
    # Crear audios individuales con ritmo pausado
    audio_parts = []
    block_durations = [30.0, 30.0, 45.0, 35.0, 30.0]
    for idx, (text, target_d) in enumerate(zip(spoken_blocks, block_durations)):
        part_aiff = TEMP_DIR / f"part_{idx}.aiff"
        part_wav = TEMP_DIR / f"part_{idx}.wav"
        subprocess.run(["say", "-v", "Paulina", "-r", "150", "-o", str(part_aiff), text], check=True)
        # Convertir a wav y rellenar con silencio hasta target_d
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(part_aiff)], capture_output=True, text=True)
        cur_d = float(probe.stdout.strip())
        pad_silence = max(target_d - cur_d, 0.5)
        subprocess.run([
            "ffmpeg", "-y", "-i", str(part_aiff),
            "-af", f"apad=pad_dur={pad_silence}",
            "-t", str(target_d), str(part_wav)
        ], check=True)
        audio_parts.append(part_wav)
        
    # Concatenar audios
    concat_list = TEMP_DIR / "concat_audio.txt"
    with open(concat_list, "w") as f:
        for p in audio_parts:
            f.write(f"file '{p.resolve()}'\n")
            
    full_audio = TEMP_DIR / "guia_full.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(full_audio)], check=True)
    
    # 3. Exportar versión con audio guía incorporado
    print(f"Exportando video con audio guía a: {FINAL_VIDEO_AUDIO}")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(FINAL_VIDEO_MUDO), "-i", str(full_audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(FINAL_VIDEO_AUDIO)
    ], check=True)
    
    print("\n✅ ¡VIDEOS GENERADOS EXITOSAMENTE!")
    print(f"1. Video Mudo (para tu voz final): {FINAL_VIDEO_MUDO}")
    print(f"2. Video con Audio Guía (para practicar/revisar): {FINAL_VIDEO_AUDIO}")

if __name__ == "__main__":
    main()
