import time
import os
import json
import getpass
from google import genai

# Configuración Inicial
API_KEY = "TU_API_KEY_ACA"

def obtener_mejor_modelo(client):
    """
    Consulta a la API los modelos disponibles, filtra los de la familia 'Flash'
    y selecciona automáticamente la versión más reciente.
    """
    modelos_flash = []
    for model in client.models.list():
        # Buscamos modelos que sean 'flash' y que no sean experimentales ('exp') si es posible
        if "flash" in model.name.lower() and "exp" not in model.name.lower():
            # Limpiamos el prefijo 'models/' que a veces devuelve la API
            nombre_limpio = model.name.replace("models/", "")
            modelos_flash.append(nombre_limpio)
            
    if not modelos_flash:
        raise ValueError("No se encontraron modelos Flash disponibles para esta cuenta.")

    # Al ordenar alfabéticamente en reversa, gemini-3.x queda arriba de gemini-2.x o 1.5
    modelos_flash.sort(reverse=True)
    modelo_elegido = modelos_flash[0]
    
    return modelo_elegido

def transcribe_media():
    print("--- Herramienta de Transcripción Gemini ---")
    
    global API_KEY
    if API_KEY == "TU_API_KEY_ACA" or not API_KEY.strip():
        print("\n[!] No se detectó una API Key hardcodeada.")
        API_KEY = getpass.getpass("Ingrese su API Key (invisible): ").strip()
        
    if not API_KEY:
        print("Error: La API Key es obligatoria.")
        return

    # Inicializamos el cliente
    client = genai.Client(api_key=API_KEY)
    
    try:
        modelo_actual = obtener_mejor_modelo(client)
        print(f"[*] Modelo detectado y auto-seleccionado: {modelo_actual}")
    except Exception as e:
        print(f"Error al buscar modelos: {e}")
        return

    # Captura de rutas
    file_path = input("\nIngrese la ruta del archivo de audio/video: ").strip()
    
    if not os.path.exists(file_path):
        print(f"Error: No se pudo encontrar el archivo en: {file_path}")
        return

    output_base = input("Ingrese el nombre base para la salida (ej: apunte): ").strip()
    if output_base.endswith(".txt") or output_base.endswith(".json"):
        output_base = output_base.rsplit('.', 1)[0]

    output_txt = f"{output_base}.txt"
    output_json = f"{output_base}_metadata.json"

    print(f"\nIniciando proceso para: {file_path}")
    print(f"Subiendo archivo a la nube...")
    
    try:
        # Subir archivo
        sample_file = client.files.upload(file=file_path)
        print(f"Archivo subido exitosamente (ID: {sample_file.name})")

        # Esperar procesamiento
        while sample_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            sample_file = client.files.get(name=sample_file.name)

        if sample_file.state.name == "FAILED":
            print("\nError: El procesamiento falló en el servidor.")
            return

        # Generar transcripción con sistema de reintentos (Exponential Backoff)
        print(f"\nTranscribiendo con {modelo_actual}...")
        
        max_reintentos = 3
        response = None
        
        for intento in range(max_reintentos):
            try:
                response = client.models.generate_content(
                    model=modelo_actual,
                    contents=[
                        "Actúa como un transcriptor profesional. Transcribe el siguiente contenido "
                        "palabra por palabra, manteniendo tecnicismos y nombres propios de forma precisa.",
                        sample_file
                    ]
                )
                break # Si tiene éxito, rompemos el ciclo for y continuamos
                
            except Exception as e:
                error_str = str(e)
                # Si el error es 503 (Servidor ocupado) o 429 (Cuota excedida temporalmente)
                if "503" in error_str or "UNAVAILABLE" in error_str or "429" in error_str:
                    espera = (2 ** intento) * 5 # Esperará 5s, luego 10s, luego 20s...
                    print(f"\n[!] Servidor congestionado. Reintentando en {espera} segundos... (Intento {intento + 1} de {max_reintentos})")
                    time.sleep(espera)
                else:
                    # Si es otro tipo de error (ej. clave incorrecta), lanzamos el error y abortamos
                    raise e
        
        # Validamos si después de todos los reintentos seguimos sin respuesta
        if not response:
            print("\nError: No se pudo obtener la transcripción después de varios intentos. Intenta más tarde.")
            return

        # Guardar TXT
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        # Guardar JSON
        metadatos = {
            "archivo_original": os.path.basename(file_path),
            "ruta_absoluta": os.path.abspath(file_path),
            "id_nube": sample_file.name,
            "modelo_utilizado": modelo_actual, # Guardamos qué modelo se usó realmente
            "fecha_procesamiento": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump(metadatos, json_file, indent=4, ensure_ascii=False)
        
        print(f"\n¡Proceso finalizado con éxito!")
        print(f"📄 Texto: {os.path.abspath(output_txt)}")
        print(f"💾 Datos: {os.path.abspath(output_json)}")

    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    transcribe_media()