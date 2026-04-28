# MoVen ✋🎥

Control de ventanas en Windows mediante gestos de la mano en tiempo real.

---

## 🚀 ¿Qué es MoVen?

**MoVen** es una aplicación de visión por computadora que permite controlar ventanas del sistema usando gestos detectados con la cámara.

Está basada en:

* 🧠 **MediaPipe** → detección de mano en tiempo real
* 📷 **OpenCV** → captura de vídeo
* ⚙️ **PyAutoGUI + Win32 API** → control del sistema

Los sistemas de reconocimiento de gestos como este permiten interacción natural humano-computadora usando solo una cámara RGB ([arXiv][1]).

---

## ✨ Funcionalidades

| Gesto       | Acción                          |
| ----------- | ------------------------------- |
| ✋ 5 dedos   | Pantalla completa               |
| ✊ Puño      | Restaurar ventana               |
| 🖐️ 4 dedos | Minimizar                       |
| ☝️ Índice   | Cerrar ventana                  |
| ✌️ 2 dedos  | Mover ventana izquierda/derecha |

---

## 🎥 Cómo funciona

1. Se captura vídeo desde la cámara
2. MediaPipe detecta 21 puntos de la mano
3. Se interpretan los gestos
4. Se ejecutan acciones en Windows

---

## ⬇️ Descarga (Recomendado)

👉 Ve a la sección **Releases**:
https://github.com/SergioHernandezUsal/Moven/releases

Descarga:

```
MoVen.exe
```

---

## ▶️ Uso

1. Ejecuta `MoVen.exe`
2. Permite acceso a la cámara
3. Coloca la mano frente a la cámara
4. Realiza gestos para controlar ventanas

---

## 🖥️ Requisitos

* Windows 10 / 11
* Cámara funcional
* CPU básica (no requiere GPU)

---

## ⚠️ Problemas comunes

### 🔴 Pantalla negra / cámara no funciona

* Cierra apps que usen la cámara (Zoom, navegador, etc.)
* Cambia backend a `CAP_DSHOW`
* Verifica permisos de cámara en Windows

---

### 🔴 No se abre la app

* Ejecutar como administrador
* Revisar antivirus / Windows Defender

---


## 🧪 Ejecutar desde código

### 1. Instalar dependencias

```bash
pip install opencv-python mediapipe numpy pyautogui pystray pillow pywin32
```

### 2. Ejecutar

```bash
python MoVen.py
```

---

## 🏗️ Compilar .exe

Comando usado:

```bash
py -3.11 -m PyInstaller --noconsole --onefile --icon=icon.ico --add-data "splash.png;." --add-data "icon.ico;." --add-data "hand_landmarker.task;." --collect-all mediapipe --collect-all pystray MoVen.py
```


## 🔮 Mejoras futuras

* UI configurable
* Sensibilidad de gestos ajustable
* Multi-monitor support
* Más gestos personalizados

---

## 👨‍💻 Autor

**Sergio Hernández**
🔗 https://github.com/SergioHernandezUsal

---

## ⭐ Contribuir

1. Fork
2. Nueva rama
3. Pull request

---

## 📄 Licencia

Uso educativo y personal.

[1]: https://arxiv.org/abs/2111.00038?utm_source=chatgpt.com "On-device Real-time Hand Gesture Recognition"
