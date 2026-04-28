import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def mostrar_splash():
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.attributes("-topmost", True)

    img = Image.open(resource_path("splash.png"))
    photo = ImageTk.PhotoImage(img)

    w, h = img.size
    x = (splash.winfo_screenwidth() // 2) - (w // 2)
    y = (splash.winfo_screenheight() // 2) - (h // 2)

    splash.geometry(f"{w}x{h}+{x}+{y}")

    label = tk.Label(splash, image=photo)
    label.image = photo
    label.pack()

    return splash


import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import numpy as np
import pyautogui
import time
import urllib.request
from collections import deque
from pystray import Icon, Menu, MenuItem
import threading
import win32gui, win32con, win32api

running = True

# ── Configuración ──────────────────────────────────────
DISTANCIA_MINIMA         = 0.10
COOLDOWN_SEGUNDOS        = 1.2
HISTORIAL_FRAMES         = 14
TIEMPO_PANTALLA_COMPLETA = 4.0
TIEMPO_RESTAURAR         = 4.0
TIEMPO_MINIMIZAR         = 4.0
TIEMPO_CERRAR            = 4.0

app_ready    = False
splash_pos_x = 0
splash_pos_y = 0

# ── Modelo ─────────────────────────────────────────────
def get_model_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "hand_landmarker.task")
    return "hand_landmarker.task"

MODEL_PATH = get_model_path()
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Descargando modelo (~25 MB), espera...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modelo descargado.")

# ── Landmarks ──────────────────────────────────────────
PUNTAS = [4, 8, 12, 16, 20]
BASES  = [3, 6, 10, 14, 18]

COLORES_DEDOS = [
    (80,  200, 255),
    (60,  220, 60),
    (255, 180, 0),
    (180, 60,  255),
    (0,   160, 255),
]
NOMBRES_DEDOS = ["PUL", "IND", "COR", "ANU", "MEN"]


# ── Helpers ────────────────────────────────────────────

def obtener_estado_ventana():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return "normal"
        if win32gui.IsIconic(hwnd):
            return "minimizado"
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMAXIMIZED:
            return "maximizado"
    except Exception:
        pass
    return "normal"


def dedos_extendidos(lm):
    ext = []
    for punta, base in zip(PUNTAS, BASES):
        if punta == 4:
            ext.append(abs(lm[4].x - lm[9].x) > abs(lm[2].x - lm[9].x) * 1.1)
        else:
            ext.append(lm[punta].y < lm[base].y - 0.02)
    return ext


def dibujar_mano(frame, lm, ext):
    h, w = frame.shape[:2]
    puntos = [(int(p.x * w), int(p.y * h)) for p in lm]

    grupos = [
        [(0,1),(1,2),(2,3),(3,4)],
        [(0,5),(5,6),(6,7),(7,8)],
        [(5,9),(9,10),(10,11),(11,12)],
        [(9,13),(13,14),(14,15),(15,16)],
        [(13,17),(17,18),(18,19),(19,20),(0,17)],
    ]
    for d, grupo in enumerate(grupos):
        color_linea = COLORES_DEDOS[d] if ext[d] else (80, 80, 90)
        for a, b in grupo:
            cv2.line(frame, puntos[a], puntos[b], color_linea, 2, cv2.LINE_AA)

    for i, p in enumerate(puntos):
        if i not in PUNTAS:
            cv2.circle(frame, p, 4, (130, 130, 145), -1, cv2.LINE_AA)

    for i, punta_idx in enumerate(PUNTAS):
        color = COLORES_DEDOS[i] if ext[i] else (60, 60, 70)
        p = puntos[punta_idx]
        cv2.circle(frame, p, 12, color, -1, cv2.LINE_AA)
        cv2.circle(frame, p, 13, (220, 220, 220), 1, cv2.LINE_AA)
        if ext[i]:
            cv2.putText(frame, NOMBRES_DEDOS[i], (p[0]-13, p[1]-16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (230, 230, 230), 1, cv2.LINE_AA)


def mover_derecha():
    pyautogui.hotkey('win', 'shift', 'right')
    print("Ventana movida a la derecha")


def mover_izquierda():
    pyautogui.hotkey('win', 'shift', 'left')
    print("Ventana movida a la izquierda")


def pantalla_completa():
    pyautogui.hotkey('win', 'up')
    print("Ventana maximizada / pantalla completa")


def restaurar_ventana():
    pyautogui.hotkey('win', 'down')
    print("Ventana restaurada")


def minimizar_ventana():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    print("Ventana minimizada")


def cerrar_ventana():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    print("Ventana cerrada")


def set_window_icon(nombre_ventana, ruta_ico):
    try:
        if not os.path.exists(ruta_ico):
            return
        import ctypes
        hwnd = win32gui.FindWindow(None, nombre_ventana)
        if hwnd:
            icon = ctypes.windll.user32.LoadImageW(
                0, ruta_ico,
                win32con.IMAGE_ICON,
                0, 0,
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )
            if icon:
                win32api.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG,   icon)
                win32api.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon)
    except Exception:
        pass


# ── MAIN ───────────────────────────────────────────────

def main():
    global running, app_ready

    opciones = mp_vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.65,
        min_tracking_confidence=0.55
    )

    print("Iniciando cámara...")

    cap = None

    
    for i in range(3):
        temp = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if temp.isOpened():
           
            temp.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            temp.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            temp.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            time.sleep(1)

            ret, frame = temp.read()

            if ret and frame is not None and frame.mean() > 10:
                cap = temp
                print(f" Cámara OK en índice {i}")
                break
            else:
                print(f" Cámara {i} negra")
                temp.release()

    if cap is None:
        print("No se pudo acceder a ninguna cámara")
        return

   
    app_ready = True

    historial_x         = deque(maxlen=HISTORIAL_FRAMES)
    ultimo_gesto        = 0
    flash_ok            = 0
    flash_dir           = ""
    ext                 = []
    icono_puesto        = False
    inicio_cinco_dedos  = 0
    inicio_puno         = 0
    inicio_cuatro_dedos = 0
    inicio_cruce        = 0
    progreso_5          = 0.0
    progreso_puno       = 0.0
    progreso_4          = 0.0
    progreso_cruce      = 0.0

    NOMBRE_VENTANA = "MoVen"
    cv2.namedWindow(NOMBRE_VENTANA, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(NOMBRE_VENTANA, 960, 540)
    cv2.moveWindow(NOMBRE_VENTANA, splash_pos_x, splash_pos_y)

    with mp_vision.HandLandmarker.create_from_options(opciones) as detector:
        while running:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                if cv2.getWindowProperty(NOMBRE_VENTANA, cv2.WND_PROP_VISIBLE) < 1:
                    running = False
                    break
            except cv2.error:
                running = False
                break

            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            
            timestamp_ms = int(time.time() * 1000)

            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect_for_video(mp_img, timestamp_ms)

            n_dedos      = 0
            ext          = []
            progreso_5   = 0.0
            progreso_puno  = 0.0
            progreso_4   = 0.0
            progreso_cruce = 0.0
            cruce_activo = False

            estado_ventana     = obtener_estado_ventana()
            permitir_maximizar = (estado_ventana != "maximizado")
            permitir_restaurar = (estado_ventana != "normal")
            permitir_minimizar = (estado_ventana != "minimizado")

            if result.hand_landmarks:
                lm      = result.hand_landmarks[0]
                ext     = dedos_extendidos(lm)
                n_dedos = sum(ext)

                dibujar_mano(frame, lm, ext)

                # ── 5 dedos → pantalla completa ──
                if n_dedos == 5 and permitir_maximizar:
                    if inicio_cinco_dedos == 0:
                        inicio_cinco_dedos = time.time()
                    progreso_5 = (time.time() - inicio_cinco_dedos) / TIEMPO_PANTALLA_COMPLETA
                    if progreso_5 >= 1.0 and time.time() - ultimo_gesto > COOLDOWN_SEGUNDOS:
                        pantalla_completa()
                        ultimo_gesto       = time.time()
                        flash_ok           = time.time()
                        flash_dir          = "[ ]"
                        inicio_cinco_dedos = 0
                        progreso_5         = 0.0
                else:
                    inicio_cinco_dedos = 0

                # ── Puño → restaurar ──
                if n_dedos == 0 and permitir_restaurar:
                    if inicio_puno == 0:
                        inicio_puno = time.time()
                    progreso_puno = (time.time() - inicio_puno) / TIEMPO_RESTAURAR
                    if progreso_puno >= 1.0 and time.time() - ultimo_gesto > COOLDOWN_SEGUNDOS:
                        restaurar_ventana()
                        ultimo_gesto  = time.time()
                        flash_ok      = time.time()
                        flash_dir     = "[ v ]"
                        inicio_puno   = 0
                        progreso_puno = 0.0
                else:
                    inicio_puno = 0

                # ── 4 dedos → minimizar ──
                if n_dedos == 4 and permitir_minimizar:
                    if inicio_cuatro_dedos == 0:
                        inicio_cuatro_dedos = time.time()
                    progreso_4 = (time.time() - inicio_cuatro_dedos) / TIEMPO_MINIMIZAR
                    if progreso_4 >= 1.0 and time.time() - ultimo_gesto > COOLDOWN_SEGUNDOS:
                        minimizar_ventana()
                        ultimo_gesto        = time.time()
                        flash_ok            = time.time()
                        flash_dir           = "[ _ ]"
                        inicio_cuatro_dedos = 0
                        progreso_4          = 0.0
                else:
                    inicio_cuatro_dedos = 0

                # ── 1 dedo (índice) → cerrar ──
                solo_indice  = (n_dedos == 1 and ext[1])
                cruce_activo = solo_indice
                if solo_indice:
                    if inicio_cruce == 0:
                        inicio_cruce = time.time()
                    progreso_cruce = (time.time() - inicio_cruce) / TIEMPO_CERRAR
                    if progreso_cruce >= 1.0 and time.time() - ultimo_gesto > COOLDOWN_SEGUNDOS:
                        cerrar_ventana()
                        ultimo_gesto   = time.time()
                        flash_ok       = time.time()
                        flash_dir      = "[ X ]"
                        inicio_cruce   = 0
                        progreso_cruce = 0.0
                else:
                    inicio_cruce = 0

                # ── 2 dedos → deslizar ──
                if n_dedos == 2:
                    xs = [lm[PUNTAS[i]].x for i in range(5) if ext[i]]
                    historial_x.append(float(np.mean(xs)))
                else:
                    historial_x.clear()

                if len(historial_x) == HISTORIAL_FRAMES:
                    desplazamiento = historial_x[-1] - historial_x[0]
                    ahora = time.time()
                    if ahora - ultimo_gesto > COOLDOWN_SEGUNDOS:
                        if desplazamiento > DISTANCIA_MINIMA:
                            mover_derecha()
                            ultimo_gesto = ahora
                            flash_ok     = ahora
                            flash_dir    = ">>>"
                            historial_x.clear()
                        elif desplazamiento < -DISTANCIA_MINIMA:
                            mover_izquierda()
                            ultimo_gesto = ahora
                            flash_ok     = ahora
                            flash_dir    = "<<<"
                            historial_x.clear()
            else:
                historial_x.clear()
                inicio_cinco_dedos  = 0
                inicio_puno         = 0
                inicio_cuatro_dedos = 0
                inicio_cruce        = 0
                progreso_5          = 0.0
                progreso_puno       = 0.0
                progreso_4          = 0.0
                progreso_cruce      = 0.0
                cruce_activo        = False

            # ── HUD ────────────────────────────────────
            t_flash = time.time() - flash_ok

            overlay = frame.copy()
            cv2.rectangle(overlay, (0, h-60), (w, h), (18, 18, 24), -1)
            cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

            if t_flash < 0.5:
                ov2 = frame.copy()
                cv2.rectangle(ov2, (0, 0), (w, h), (0, 150, 70), -1)
                cv2.addWeighted(ov2, 0.10, frame, 0.90, 0, frame)

            for i in range(5):
                cx = 22 + i * 50
                cy = h - 36
                color_c = COLORES_DEDOS[i] if (ext and ext[i]) else (50, 50, 60)
                cv2.circle(frame, (cx, cy), 11, color_c, -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 11, (100, 100, 115), 1, cv2.LINE_AA)
                cv2.putText(frame, NOMBRES_DEDOS[i], (cx-12, h-16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.28,
                            (200, 200, 210) if (ext and ext[i]) else (70, 70, 82),
                            1, cv2.LINE_AA)

            bx, bw_bar = 285, w - 310
            cv2.rectangle(frame, (bx, h-50), (bx+bw_bar, h-36), (30, 32, 40), -1)
            cv2.rectangle(frame, (bx, h-50), (bx+bw_bar, h-36), (60, 62, 72), 1)
            if len(historial_x) > 1:
                desp = historial_x[-1] - historial_x[0]
                fill = min(int(abs(desp) / DISTANCIA_MINIMA * bw_bar), bw_bar)
                col_b = (0, 200, 80) if desp > 0 else (200, 80, 80)
                cv2.rectangle(frame, (bx, h-50), (bx+fill, h-36), col_b, -1)

            etiquetas_estado = {
                "maximizado": ("MAXIMIZADO", (0, 220, 200)),
                "minimizado": ("MINIMIZADO", (255, 140, 60)),
                "normal":     ("NORMAL",     (140, 140, 160)),
            }
            etiq_txt, etiq_col = etiquetas_estado.get(estado_ventana, ("?", (200, 200, 200)))
            cv2.putText(frame, etiq_txt, (w - 130, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, etiq_col, 1, cv2.LINE_AA)

            if t_flash < 0.5:
                estado  = f"  {flash_dir}  VENTANA MOVIDA  {flash_dir}"
                col_txt = (80, 255, 160)
            elif not result.hand_landmarks:
                estado  = "Pon la mano ante la camara"
                col_txt = (100, 100, 120)
            elif n_dedos == 5:
                if not permitir_maximizar:
                    estado  = "5 dedos  ->  ya esta maximizada"
                    col_txt = (60, 60, 80)
                else:
                    pct    = min(int(progreso_5 * 100), 100)
                    estado  = f"5 dedos  ->  pantalla completa  {pct}%"
                    col_txt = (0, 220, 200)
            elif n_dedos == 0:
                if not permitir_restaurar:
                    estado  = "Puno  ->  ya esta en normal"
                    col_txt = (60, 60, 80)
                else:
                    pct    = min(int(progreso_puno * 100), 100)
                    estado  = f"Puno  ->  restaurar ventana  {pct}%"
                    col_txt = (0, 180, 255)
            elif n_dedos == 4:
                if not permitir_minimizar:
                    estado  = "4 dedos  ->  ya esta minimizada"
                    col_txt = (60, 60, 80)
                else:
                    pct    = min(int(progreso_4 * 100), 100)
                    estado  = f"4 dedos  ->  minimizar  {pct}%"
                    col_txt = (255, 140, 60)
            elif cruce_activo:
                pct     = min(int(progreso_cruce * 100), 100)
                estado  = f"1 dedo  ->  cerrar ventana  {pct}%"
                col_txt = (60, 60, 220)
            elif n_dedos == 2:
                if len(historial_x) > 1:
                    d   = historial_x[-1] - historial_x[0]
                    pct = min(int(abs(d) / DISTANCIA_MINIMA * 100), 100)
                    estado  = f"2 dedos  {'>' if d>0 else '<'}  desliza  {pct}%"
                else:
                    estado  = "2 dedos listos  ->  desliza"
                col_txt = (0, 220, 120)
            else:
                estado  = f"{n_dedos} dedo{'s' if n_dedos!=1 else ''} extendido{'s' if n_dedos!=1 else ''}"
                col_txt = (140, 140, 160)

            cv2.putText(frame, estado, (290, h-18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, col_txt, 1, cv2.LINE_AA)

            # ── Arcos de progreso ──
            if n_dedos == 5 and progreso_5 > 0.0 and permitir_maximizar:
                angulo = int(min(progreso_5, 1.0) * 360)
                cx_arc, cy_arc, radio = w // 2, h // 2, 55
                cv2.ellipse(frame, (cx_arc, cy_arc), (radio, radio),
                            -90, 0, angulo, (0, 230, 160), 6, cv2.LINE_AA)
                cv2.circle(frame, (cx_arc, cy_arc), radio - 8, (18, 18, 24), -1)
                restante = max(0.0, TIEMPO_PANTALLA_COMPLETA - (time.time() - inicio_cinco_dedos))
                cv2.putText(frame, f"{restante:.1f}s", (cx_arc - 22, cy_arc + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 230, 160), 2, cv2.LINE_AA)

            if n_dedos == 0 and progreso_puno > 0.0 and permitir_restaurar:
                angulo = int(min(progreso_puno, 1.0) * 360)
                cx_arc, cy_arc, radio = w // 2, h // 2, 55
                cv2.ellipse(frame, (cx_arc, cy_arc), (radio, radio),
                            -90, 0, angulo, (0, 180, 255), 6, cv2.LINE_AA)
                cv2.circle(frame, (cx_arc, cy_arc), radio - 8, (18, 18, 24), -1)
                restante = max(0.0, TIEMPO_RESTAURAR - (time.time() - inicio_puno))
                cv2.putText(frame, f"{restante:.1f}s", (cx_arc - 22, cy_arc + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2, cv2.LINE_AA)

            if n_dedos == 4 and progreso_4 > 0.0 and permitir_minimizar:
                angulo = int(min(progreso_4, 1.0) * 360)
                cx_arc, cy_arc, radio = w // 2, h // 2, 55
                cv2.ellipse(frame, (cx_arc, cy_arc), (radio, radio),
                            -90, 0, angulo, (255, 140, 60), 6, cv2.LINE_AA)
                cv2.circle(frame, (cx_arc, cy_arc), radio - 8, (18, 18, 24), -1)
                restante = max(0.0, TIEMPO_MINIMIZAR - (time.time() - inicio_cuatro_dedos))
                cv2.putText(frame, f"{restante:.1f}s", (cx_arc - 22, cy_arc + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 140, 60), 2, cv2.LINE_AA)

            if cruce_activo and progreso_cruce > 0.0:
                angulo = int(min(progreso_cruce, 1.0) * 360)
                cx_arc, cy_arc, radio = w // 2, h // 2, 55
                cv2.ellipse(frame, (cx_arc, cy_arc), (radio, radio),
                            -90, 0, angulo, (60, 60, 220), 6, cv2.LINE_AA)
                cv2.circle(frame, (cx_arc, cy_arc), radio - 8, (18, 18, 24), -1)
                restante = max(0.0, TIEMPO_CERRAR - (time.time() - inicio_cruce))
                cv2.putText(frame, f"{restante:.1f}s", (cx_arc - 22, cy_arc + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 60, 220), 2, cv2.LINE_AA)

            cv2.imshow(NOMBRE_VENTANA, frame)

            if not icono_puesto:
                set_window_icon(NOMBRE_VENTANA, resource_path("icon.ico"))
                icono_puesto = True

            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

    cap.release()
    cv2.destroyAllWindows()


# ── Tray ───────────────────────────────────────────────

def stop_app(icon, item):
    global running
    running = False
    icon.stop()


def create_icon():
    try:
        return Image.open(resource_path("icon.ico"))
    except Exception:
        img = Image.new("RGBA", (64, 64), (18, 18, 24, 255))
        d   = ImageDraw.Draw(img)
        d.ellipse((6, 6, 58, 58), fill=(0, 190, 100))
        d.text((22, 18), "G", fill=(255, 255, 255))
        return img


def tray():
    icon = Icon("Gesture Monitor", create_icon(),
                menu=Menu(MenuItem("Salir", stop_app)))
    icon.run()


# ── Arranque ───────────────────────────────────────────

if __name__ == "__main__":
    root_oculto = tk.Tk()
    root_oculto.withdraw()

    splash = mostrar_splash()

    threading.Thread(target=tray, daemon=True).start()

    app_thread = threading.Thread(target=main)
    app_thread.start()

    while not app_ready:
        splash.update()
        time.sleep(0.01)

    # Capturar posición del splash antes de destruirlo
    splash.update()
    splash_pos_x = splash.winfo_x()
    splash_pos_y = splash.winfo_y()

    splash.destroy()
    root_oculto.destroy()

    app_thread.join()
