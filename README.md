# 🎙️ Gemini Transcriptor: Audio & Video a Texto
*Versión 0.3*

Esta herramienta de consola desarrollada en Python permite realizar transcripciones precisas de archivos de audio (.mp3) o video (.mp4) utilizando la potencia de los modelos multimodales **Gemini Flash** a través de la API de Google GenAI. 

Está diseñada específicamente para entornos de desarrollo en Linux (WSL2/Debian) y enfocada en la facilidad de uso para estudiantes y profesionales que necesiten procesar seminarios, clases o reuniones técnicas sin preocuparse por el mantenimiento de la API.

## ✨ Características principales

- **Auto-detección de Modelos (Future-Proof):** El script consulta los servidores de Google en tiempo real y selecciona automáticamente la versión "Flash" más reciente y estable habilitada para tu cuenta. Nunca más verás un error `404` por modelos obsoletos.
- **Transcripción de alta fidelidad:** Comprende términos técnicos y contextos complejos de forma nativa.
- **Interfaz Interactiva:** Solicita rutas de archivos y nombres de salida directamente por consola.
- **Seguridad de Credenciales:** La API Key se ingresa de forma oculta (invisible en terminal) para evitar fugas de seguridad en tu código fuente.
- **Doble Salida de Datos:** - Archivo `.txt` con la transcripción íntegra.
  - Archivo `.json` con metadatos del proceso (ID de la nube, fecha, versión exacta del modelo utilizado, etc.).

---

## 🛠️ Configuración del Entorno (WSL2 / Debian)

Para asegurar que el script funcione sin interferir con los paquetes del sistema operativo, utilizaremos un entorno virtual de Python (`venv`).

1. **Instalar dependencias del sistema:**
   ```bash
   sudo apt update
   sudo apt install python3-venv ffmpeg -y
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   # Dentro de la carpeta del proyecto
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar la librería oficial de Google:**
   ```bash
   pip install google-genai
   ```

---

## 💡 Tip: Tamaño y Optimización con FFmpeg
**¡Importante!** Google AI Studio tiene un límite de subida de 2GB por archivo. Además, subir un video pesado solo por su audio consume ancho de banda innecesario.

Si tienes un video de 2 horas (por ejemplo, un seminario de la facultad), extrae solo el audio antes de procesarlo. Esto reducirá el tamaño de megabytes a unos pocos megas y acelerará el proceso:
   ```bash
   ffmpeg -i video_original.mp4 -q:a 0 -map a audio_optimizado.mp3
   ```

---

> [!WARNING]  
> **⚠️ ADVERTENCIA: Límites de Salida (Output Tokens)**
> Aunque los modelos Gemini pueden recibir horas de audio, tienen un límite de salida (aprox. 8,000 tokens). Si un audio es muy largo (más de 45-60 minutos), el modelo se detendrá al alcanzar este límite y la transcripción quedará incompleta.
> Para audios largos, es obligatorio seguir el tutorial de fragmentación a continuación:

## ✂️ Tutorial: Procesamiento de Archivos Largos (> 45 min)
Si tu seminario o clase dura más de 45 minutos, sigue estos pasos para garantizar una transcripción completa:

1. **Fragmentar el audio (Chunking)**
Usa ffmpeg para dividir el archivo en partes de 45 minutos (2700 segundos):
   ```bash
   ffmpeg -i tu_archivo_largo.mp3 -f segment -segment_time 2700 -c copy parte_%03d.mp3
   ```
*Esto generará archivos: `parte_000.mp3`, `parte_001.mp3`, etc.*

2. **Transcribir cada parte**
Ejecuta el script para cada parte generada:

`parte_000.mp3` -> salida: `clase_parte1`

`parte_001.mp3` -> salida: `clase_parte2`

3. **Unir los archivos de texto**
Una vez tengas todos los archivos `.txt`, únelos en uno solo con este comando de Linux:
   ```bash
   cat clase_parte1.txt clase_parte2.txt > transcripcion_completa.txt
   ```
---

## 🚀 Instrucciones de Uso

Una vez que tengas tu entorno activo y tu archivo de audio/video listo, sigue estos pasos:

1. **Ejecutar el script:**
   ```bash
   python audio_to_text.py
   ```

2. **Ingresar la API Key:**
Si no la has dejado fija en el código, el script te la pedirá. Nota: Al pegarla o escribirla, no verás caracteres en pantalla por seguridad; solo presiona `Enter`.

3. **Ruta del archivo:**
Ingresa la ruta del archivo. Si estás en la misma carpeta, solo escribe el nombre (ej: `audio_optimizado.mp3`). Si el archivo está en Windows, recuerda que puedes acceder mediante `/mnt/c/Users/...`.

4. **Nombre base:**
Define cómo quieres que se llamen tus archivos resultantes (ej: `clase_sistemas`).

**Resultados:**
Al finalizar, encontrarás en tu carpeta:
- `nombre_base.txt`: La transcripción completa.
- `nombre_base_metadata.json`: Los datos técnicos del procesamiento.

---

## 📝 Notas técnicas
- **Gestión de Modelos:** La función `obtener_mejor_modelo()` se encarga de filtrar versiones experimentales (`-exp`) y ordenar las versiones disponibles para garantizar el uso de la tecnología de producción más moderna.

- El estado `PROCESSING` en los servidores de Google puede tardar unos minutos dependiendo de la duración del audio. El script incluye un sistema de espera automática con indicadores visuales en la consola.

- Versión de Python: `Python 3.11.2`

---

*Desarrollado para fines educativos y de productividad técnica.*