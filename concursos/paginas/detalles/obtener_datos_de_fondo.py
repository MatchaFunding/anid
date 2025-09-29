from bs4 import BeautifulSoup
import numpy as np
import re

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

html = open("concurso-ines-genero-2025-renovacion-competitiva.html", 'r', encoding='utf-8')
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

file = open("concurso-ines-genero-2025-renovacion-competitiva.html", 'r', encoding='utf-8').read()

montos = re.findall("[$][0-9][0-9.]*", file)

for m in range(len(montos)):
    montos[m] = montos[m][1:]
    montos[m] = montos[m].replace(".","")
    montos[m] = int(montos[m])

montos = np.array(montos)

monto_minimo = montos.min()
monto_maximo = montos.max()

print(f"Titulo: {titulo}")
print(f"Descripcion: {descripcion}")
print(f"Inicio: {inicio}")
print(f"Cierre: {cierre}")
print(f"Fallo: {fallo}")
print(f"Tipo de beneficio: {tipo_de_beneficio}")
print(f"Monto minimo: {monto_minimo}")
print(f"Monto maximo: {monto_maximo}")
print(f"Publico objetivo: {publico_objetivo}")
print(f"Presentacion: {presentacion}")