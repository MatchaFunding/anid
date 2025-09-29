from bs4 import BeautifulSoup
import numpy as np
import re
import os

# Concurso usado de referencia para hacer Web-Scraping
# https://anid.cl/concursos/concurso-ines-genero-2025-renovacion-competitiva/

meses = np.array(["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"])

def indice_mes(mes):
    return str((np.where(meses == mes)[0]+1)[0]).zfill(2)

def encontrar_mes(fecha):
    for mes in meses:
        mes_hallado = re.findall(f"{mes}", fecha)
        if mes_hallado:
            return indice_mes(mes_hallado)
    return "01"

def encontrar_dia(fecha):
    return re.findall("[0-9]{2}", fecha)[0]

def encontrar_ano(fecha):
    return re.findall("[0-9]{4}", fecha)[0]

def formatear_fecha(fecha):
    ano = encontrar_ano(fecha)
    mes = encontrar_mes(fecha)
    dia = encontrar_dia(fecha)
    return f"{ano}-{mes}-{dia}"

# archivo = "concurso-ines-genero-2025-renovacion-competitiva.html"
archivo = "convocatoria-fondo-gemini-2023.html"
html = open(archivo, 'r', encoding='utf-8')
soup  = BeautifulSoup(html, "html.parser")

titulo = soup.find('title').text
descripcion = soup.find('meta', attrs={'name':'description'}).attrs.get('content')

inicio = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})[1].text
inicio = ''.join(inicio.splitlines())
inicio = formatear_fecha(inicio)

cierre = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})[2].text
cierre = ''.join(cierre.splitlines())
cierre = formatear_fecha(cierre)

fallo = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})[3].text
fallo = ''.join(fallo.splitlines())
fallo = formatear_fecha(fallo)

tipo_de_beneficio = soup.body.find('div', attrs={'class':'jet-listing-grid jet-listing'}).text
tipo_de_beneficio = ''.join(tipo_de_beneficio.splitlines())[1:-1]

publico_objetivo = soup.body.find('div', attrs={'id':'jet-tabs-content-1912'}).text
publico_objetivo = ''.join(publico_objetivo.splitlines())

presentacion = soup.body.find('div', attrs={'id':'jet-tabs-content-1911'}).text

duracion = re.findall("Duración máxima: [0-9]*", presentacion)[0]
meses_duracion = re.findall("[0-9]{1}[0-9]*", duracion)[0]

bases_legales = []
preguntas_frecuentes = []
resultados = []
manuales = []
formularios = []
certificados = []
otros = []

enlaces = soup.find_all('a', href=True)

lista_pdfs = []

for e in enlaces:
    enlace = e['href']
    if ".pdf" in enlace or ".xlsx" in enlace or ".docx" in enlace:
        if "pdf" in enlace:
            lista_pdfs.append(enlace)
        if "base" in enlace.lower():
            bases_legales.append(enlace)
            continue
        if "frecuente" in enlace.lower():
            preguntas_frecuentes.append(enlace)
            continue
        if "rex" in enlace.lower() or "resex" in enlace.lower():
            resultados.append(enlace)
            continue
        if "manual" in enlace.lower():
            manuales.append(enlace)
            continue
        if "formulario" in enlace.lower():
            formularios.append(enlace)
            continue
        if "certificado" in enlace.lower():
            certificados.append(enlace)
            continue
        else:
            otros.append(enlace)
            continue

file = open(archivo, 'r', encoding='utf-8').read()

montos = re.findall("[$][0-9][0-9.]*", file)

for m in range(len(montos)):
    montos[m] = montos[m][1:]
    montos[m] = montos[m].replace(".","")
    montos[m] = int(montos[m])

montos = np.array(montos)

monto_minimo = montos.min()
monto_maximo = montos.max()

enlace_detalle = f"https://anid.cl/concursos/{archivo.strip(".html")}/"

print(f"_Enlace_: {enlace_detalle}")
print(f"_Titulo_: {titulo}")
print(f"_Descripcion_: {descripcion}")
print(f"_Inicio_: {inicio}")
print(f"_Cierre_: {cierre}")
print(f"_Fallo_: {fallo}")
print(f"_Duracion_: {meses_duracion}")
print(f"_Tipo beneficio_: {tipo_de_beneficio}")
print(f"_Monto minimo_: {monto_minimo}")
print(f"_Monto maximo_: {monto_maximo}")
print(f"_Publico objetivo_: {publico_objetivo}")
print(f"_Presentacion_: {presentacion}")

for base in bases_legales:
    print(f"_Bases legales_: {base}")

for pregunta in preguntas_frecuentes:
    print(f"_FAQs_: {pregunta}")

for resultado in resultados:
    print(f"_Resultado_: {resultado}")

for otro in otros:
    print(f"_Otro_: {otro}")