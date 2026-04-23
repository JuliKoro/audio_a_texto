import time
import os
import json
import getpass
from google import genai

# Configuración Inicial
# Si dejas "TU_API_KEY_ACA", el script te la pedirá por consola. 
# Si pones tu clave real aquí, el script la detectará y omitirá la pregunta.
API_KEY = "TU_API_KEY_ACA"

def transcribe_media():
    print("--- Herramienta de Transcripción Gemini ---")
    
    # Lógica inteligente para la API Key
    global API_KEY
    if API_KEY == "TU_API_KEY_ACA" or not API_KEY.strip():
        print("\n[!] No se detectó una API Key hardcodeada.")
        # getpass oculta los caracteres por seguridad mientras escribes
        API_KEY = getpass.getpass("Ingrese su API Key (el texto será invisible por seguridad): ").strip()
        
    if not API_KEY:
        print("Error: La API Key es obligatoria para continuar.")
        return

    # Inicializamos el cliente con la clave validada
    client = genai.Client(api_key=API_KEY)
    
    # Captura de la ruta de entrada
    file_path = input("\nIngrese la ruta del archivo de audio/video: ").strip()
    
    if not os.path.exists(file_path):
        print(f"Error: No se pudo encontrar el archivo en la ruta: {file_path}")
        return

    # Captura del nombre de salida
    output_base = input("Ingrese el nombre base para los archivos de salida (ej: clase_arquitectura): ").strip()
    # Limpiamos la extensión por si el usuario la puso
    if output_base.endswith(".txt") or output_base.endswith(".json"):
        output_base = output_base.rsplit('.', 1)[0]

    output_txt = f"{output_base}.txt"
    output_json = f"{output_base}_metadata.json"

    print(f"\nIniciando proceso para: {file_path}")
    print(f"Subiendo archivo a la nube...")
    
    try:
        # Subir el archivo
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

        # Generar transcripción
        print("\nGenerando transcripción técnica...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                "Actúa como un transcriptor profesional. Transcribe el siguiente contenido "
                "palabra por palabra, manteniendo tecnicismos y nombres propios de forma precisa.",
                sample_file
            ]
        )

        # Guardar resultado TXT
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        # Construir y guardar metadatos en JSON
        metadatos = {
            "archivo_original": os.path.basename(file_path),
            "ruta_absoluta": os.path.abspath(file_path),
            "id_nube": sample_file.name,
            "uri_acceso": sample_file.uri,
            "mime_type": sample_file.mime_type,
            "fecha_procesamiento": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modelo_utilizado": "gemini-2.0-flash"
        }
        
        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump(metadatos, json_file, indent=4, ensure_ascii=False)
        
        print(f"\n¡Proceso finalizado con éxito!")
        print(f"📄 Transcripción guardada en: {os.path.abspath(output_txt)}")
        print(f"💾 Metadatos guardados en:   {os.path.abspath(output_json)}")

    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    transcribe_media()