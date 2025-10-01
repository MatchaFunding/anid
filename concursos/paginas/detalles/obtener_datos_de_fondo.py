from bs4 import BeautifulSoup
from pypdf import PdfReader
import numpy as np
import sys
import re
import os

# Mapeo de los meses para poder normalizarlos al insertar en MySQL
meses = np.array(["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"])

# Lee un mes en lenguaje natural y devuelve el mes en formato numerico
def indice_mes(mes):
    return str((np.where(meses == mes)[0]+1)[0]).zfill(2)

# Encuentra los meses encontrados en un blob de texto
def encontrar_mes(fecha):
    for mes in meses:
        mes_hallado = re.findall(f"{mes}", fecha)
        if mes_hallado:
            return indice_mes(mes_hallado)
    return "01"

# Encuentra instancias de dia en un blob de texto
def encontrar_dia(fecha):
	dia = re.findall("[0-9]{2}", fecha)
	if dia:
		return re.findall("[0-9]{2}", fecha)[0]
	return "01"

# Encuentra instancias de ano en un blob de texto
def encontrar_ano(fecha):
	ano = re.findall("[0-9]{4}", fecha)
	if ano:
		return re.findall("[0-9]{4}", fecha)[0]
	return "2025"

# Formatea una fecha a formato UNIX estandar
def formatear_fecha(fecha):
    ano = encontrar_ano(fecha)
    mes = encontrar_mes(fecha)
    dia = encontrar_dia(fecha)
    return f"{ano}-{mes}-{dia}"

# Obtiene el texto de un PDF en formato String
def pdf_a_texto(pdf):
	reader = PdfReader(pdf)
	pages_qty = len(reader.pages)
	out = ""
	print(f"Cantidad de paginas: {pages_qty}")
	for p in range(pages_qty):
		page = reader.pages[p]
		text = page.extract_text()
		out += text
	print("Peso del texto leido:", sys.getsizeof(out), "bytes.")
	return out

"""
Script que recibe el nombre de un archivo por medio de entrada estandar e inserta
los instrumentos validos en la base de datos de MySQL / MariaDB
"""
def main():
	# Recibe el archivo por entrada estandar
	#archivo = "convocatoria-fondo-gemini-2023.html"
	archivo = str(sys.argv[1])
	# Muestra el instrumento que va a leer
	print(f"Archivo a leer: {archivo}")
	# Lo abre con BeautifulSoup para poder escanearlo
	html = open(archivo, 'r', encoding='utf-8')
	soup  = BeautifulSoup(html, "html.parser")
	# Extrae el titulo del instrumento
	titulo = soup.find('title').text
	# Extrae la descripcion del instrumento
	descripcion = soup.find('meta', attrs={'name':'description'})
	if descripcion:
		descripcion = descripcion.attrs.get('content')
	if not descripcion:
		descripcion = ""
	# Extrae la fecha de inicio del instrumento
	inicio = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})
	if inicio and len(inicio) >= 2:
		inicio = inicio[1].text
		inicio = ''.join(inicio.splitlines())
		inicio = formatear_fecha(inicio)
	if not inicio:
		inicio = ""
	# Extrae la fecha de cierre del instrumento
	cierre = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})
	if cierre and len(cierre) >= 3:
		cierre = cierre[2].text
		cierre = ''.join(cierre.splitlines())
		cierre = formatear_fecha(cierre)
	if not cierre:
		cierre = ""
	# Extrae la fecha de fallo del instrumento
	fallo = soup.find_all('div', attrs={'class':'jet-listing-dynamic-field__content'})
	if fallo and len(fallo) >= 4:
		fallo = fallo[3].text
		fallo = ''.join(fallo.splitlines())
		fallo = formatear_fecha(fallo)
	if not fallo:
		fallo = ""
	tipo_de_beneficio = ""
	publico_objetivo = ""
	presentacion = ""
	if soup.body:
		# Extrae el tipo de beneficiio del instrumento
		tipo_de_beneficio = soup.body.find('div', attrs={'class':'jet-listing-grid jet-listing'})
		if tipo_de_beneficio:
			tipo_de_beneficio = tipo_de_beneficio.text
			tipo_de_beneficio = ''.join(tipo_de_beneficio.splitlines())[1:-1]
		# Extrae el publico objetivo del instrumento
		publico_objetivo = soup.body.find('div', attrs={'id':'jet-tabs-content-1912'})
		if publico_objetivo:
			publico_objetivo = publico_objetivo.text
			publico_objetivo = ''.join(publico_objetivo.splitlines())
		# Extrae la presentacion del instrumento
		presentacion = soup.body.find('div', attrs={'id':'jet-tabs-content-1911'})
		if presentacion:
			presentacion = presentacion.text
		if not presentacion:
			presentacion = ""
	# Extrae la duracion en meses del instrumento
	duracion = re.findall("Duración máxima: [0-9]*", presentacion)
	meses_duracion = 12
	if duracion:
		duracion = duracion[0]
		meses = re.findall("[0-9]{1}[0-9]*", duracion)
		if meses:
			meses_duracion = meses[0]
	# Extrae los documentos relacionados al instrumento
	bases_legales = []
	preguntas_frecuentes = []
	resultados = []
	manuales = []
	formularios = []
	certificados = []
	otros = []
	# Enlaces de dichos documentos extraidos
	enlaces = soup.find_all('a', href=True)
	lista_pdfs = []
	# Determina de que tipo son los documentos y los separa
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
	# Extrae los montos monetarios que aparecen en la pagina
	file = open(archivo, 'r', encoding='utf-8').read()
	montos = re.findall("[$][0-9][0-9.]*", file)
	monto_minimo = 0
	monto_maximo = 0
	# Transforma los montos a valor entero
	for m in range(len(montos)):
		montos[m] = montos[m][1:]
		montos[m] = montos[m].replace(".","")
		montos[m] = int(montos[m])
	# De todos los montos hallados, busca el maximo y minimo
	if montos:
		montos = np.array(montos)
		monto_minimo = montos.min()
		monto_maximo = montos.max()
	# Extrae la pagina del detalle del instrumento
	enlace_detalle = f"https://anid.cl/concursos/{archivo.strip(".html")}/"
	# Muestra por pantalla
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
	for manual in manuales:
		print(f"_Manual_: {manual}")
	for formulario in formularios:
		print(f"_Formulario: {formulario}")
	for certificado in certificados:
		print(f"_Certificado_: {certificado}")
	for otro in otros:
		print(f"_Otro_: {otro}")

if __name__=="__main__":
    main()
