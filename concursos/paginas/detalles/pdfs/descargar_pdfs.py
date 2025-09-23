import requests
import os
import time
from urllib.parse import urlparse
import sys

def descargar_pdf(url, carpeta_destino):
    try:
        # Obtener el nombre del archivo desde la URL
        parsed_url = urlparse(url)
        nombre_archivo = os.path.basename(parsed_url.path)
        
        # Si no hay extensión .pdf, agregarla
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf'
        
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
        
        # Verificar si el archivo ya existe
        if os.path.exists(ruta_archivo):
            print(f"Saltando {nombre_archivo} (ya existe)")
            return True
        
        print(f"Descargando: {nombre_archivo}")
        
        # Realizar la petición HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Guardar el archivo
        with open(ruta_archivo, 'wb') as archivo:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    archivo.write(chunk)
        
        print(f"Descargado: {nombre_archivo}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error descargando {url}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado con {url}: {e}")
        return False

def leer_urls_desde_archivo(archivo_urls):
    urls = []
    try:
        with open(archivo_urls, 'r', encoding='utf-8') as f:
            for linea in f:
                url = linea.strip()
                if url and url.startswith('http'):
                    urls.append(url)
        return urls
    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo: {archivo_urls}")
        return []
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        return []

def main():
    # Obtener la carpeta actual del script
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    archivo_urls = os.path.join(carpeta_script, 'enlaces_a_pdfs.txt')
    
    # Verificar que existe el archivo de URLs
    if not os.path.exists(archivo_urls):
        print(f"No se encontró el archivo: {archivo_urls}")
        sys.exit(1)
    
    # Leer las URLs
    print("Leyendo URLs del archivo...")
    urls = leer_urls_desde_archivo(archivo_urls)
    
    if not urls:
        print("No se encontraron URLs válidas en el archivo")
        sys.exit(1)
    
    print(f"Se encontraron {len(urls)} URLs para descargar")
    
    # Crear carpeta de destino si no existe (en este caso, la misma carpeta)
    if not os.path.exists(carpeta_script):
        os.makedirs(carpeta_script)
    
    # Contadores
    exitosos = 0
    fallidos = 0
    
    # Descargar cada PDF
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] ", end="")
        
        if descargar_pdf(url, carpeta_script):
            exitosos += 1
        else:
            fallidos += 1
        
        # Pequeña pausa entre descargas 
        time.sleep(0.5)
    
    print(f"Exitosas: {exitosos}")
    print(f"Fallidas: {fallidos}")
    print(f"Archivos guardados en: {carpeta_script}")

if __name__ == "__main__":
    main()