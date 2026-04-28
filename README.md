# MoVen ✋

Controla ventanas de Windows usando **gestos de la mano en tiempo real** mediante visión por computadora.

---

## 🚀 Descripción

**MoVen** es una aplicación que permite interactuar con el sistema operativo utilizando la cámara y gestos de la mano.

Utiliza tecnologías como:

* 📷 OpenCV → Captura de video
* 🧠 MediaPipe → Detección de manos
* ⚙️ PyAutoGUI + Win32 → Control de ventanas

---

## ✨ Funcionalidades

| Gesto              | Acción                          |
| ------------------ | ------------------------------- |
| ✋ 5 dedos          | Pantalla completa               |
| ✊ Puño             | Restaurar ventana               |
| 🖐️ 4 dedos        | Minimizar ventana               |
| ☝️ 1 dedo (índice) | Cerrar ventana                  |
| ✌️ 2 dedos         | Mover ventana izquierda/derecha |

---

## ⬇️ Descarga

👉 [Descargar MoVen (.exe)](https://github.com/SergioHernandezUsal/Moven/releases)

---

## ▶️ Uso

1. Ejecuta `MoVen.exe`
2. Permite acceso a la cámara si Windows lo solicita
3. Coloca la mano frente a la cámara
4. Usa los gestos para controlar las ventanas

---

## 🖥️ Requisitos

* Windows 10 / 11
* Cámara funcional
* Conexión a internet (solo la primera vez)

---

## ⚠️ Notas importantes

* 🔐 Windows puede mostrar aviso de seguridad
  → Click en **"Más información" → "Ejecutar de todos modos"**

* 🌐 La primera ejecución descarga automáticamente el modelo de detección

* 📷 Asegúrate de que ninguna otra aplicación esté usando la cámara

---

## 📦 Instalación (modo desarrollo)

Si quieres ejecutar el proyecto desde código:

```bash
pip install opencv-python mediapipe numpy pyautogui pystray pillow pywin32
```

Ejecutar:

```bash
python MoVen.py
```

---

## 📁 Estructura del proyecto

```
MoVen/
│
├── MoVen.py              # Código principal
├── splash.png            # Pantalla de carga
├── icon.ico              # Icono de la app
├── README.md
├── .gitignore
```

---

## 🛠️ Problemas comunes

### Cámara en negro

* Usar backend DirectShow (`CAP_DSHOW`)
* Cerrar otras aplicaciones (Zoom, navegador, etc.)

---

### No detecta la cámara

* Verificar permisos en Windows
* Probar con diferentes índices (0, 1, 2)

---

### La app no arranca

* Ejecutar como administrador
* Verificar antivirus / Windows Defender

---

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
