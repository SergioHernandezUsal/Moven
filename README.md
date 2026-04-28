MoVen ✋🎥

Control de ventanas en Windows mediante gestos de la mano en tiempo real.

🚀 ¿Qué es MoVen?

MoVen es una aplicación de visión por computadora que permite controlar ventanas del sistema usando gestos detectados con la cámara.

Está basada en:

🧠 MediaPipe → detección de mano en tiempo real
📷 OpenCV → captura de vídeo
⚙️ PyAutoGUI + Win32 API → control del sistema

Los sistemas de reconocimiento de gestos como este permiten interacción natural humano-computadora usando solo una cámara RGB ().

✨ Funcionalidades
Gesto	Acción
✋ 5 dedos	Pantalla completa
✊ Puño	Restaurar ventana
🖐️ 4 dedos	Minimizar
☝️ Índice	Cerrar ventana
✌️ 2 dedos	Mover ventana izquierda/derecha
🎥 Cómo funciona
Se captura vídeo desde la cámara
MediaPipe detecta 21 puntos de la mano
Se interpretan los gestos
Se ejecutan acciones en Windows
⬇️ Descarga (Recomendado)

👉 Ve a la sección Releases:
https://github.com/SergioHernandezUsal/Moven/releases

Descarga:

MoVen.exe
▶️ Uso
Ejecuta MoVen.exe
Permite acceso a la cámara
Coloca la mano frente a la cámara
Realiza gestos para controlar ventanas
🖥️ Requisitos
Windows 10 / 11
Cámara funcional
CPU básica (no requiere GPU)
⚠️ Problemas comunes
🔴 Pantalla negra / cámara no funciona
Cierra apps que usen la cámara (Zoom, navegador, etc.)
Cambia backend a CAP_DSHOW
Verifica permisos de cámara en Windows
🔴 No se abre la app
Ejecutar como administrador
Revisar antivirus / Windows Defender
🔴 Splash se queda cargando
Problema de inicialización de cámara
Asegúrate de que app_ready = True se ejecuta
🧪 Ejecutar desde código
1. Instalar dependencias
pip install opencv-python mediapipe numpy pyautogui pystray pillow pywin32
2. Ejecutar
python MoVen.py
🏗️ Compilar .exe

Comando usado:

py -3.11 -m PyInstaller --noconsole --onefile --icon=icon.ico --add-data "splash.png;." --add-data "icon.ico;." --add-data "hand_landmarker.task;." --collect-all mediapipe --collect-all pystray MoVen.py
## 🔮 Mejoras futuras

* Interfaz gráfica más avanzada
* Configuración de gestos personalizados
* Instalador automático
* Soporte para más acciones del sistema

---

## 👨‍💻 Autor

**Sergio Hernández**
🔗 https://github.com/SergioHernandezUsal

---

## ⭐ Contribuciones

Las contribuciones son bienvenidas.

1. Haz un fork
2. Crea una rama (`feature/nueva-funcion`)
3. Haz commit
4. Abre un Pull Request

---

## 📄 Licencia

Proyecto de uso libre para fines educativos y personales.
