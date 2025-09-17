# Archivo con todos los enlaces encontrados
filename='enlaces_relevantes.txt'

# Lee el archivo con enlaces relevantes e intenta
# descargar las paginas en formato HTML
while IFS= read -r line; do
	echo "Descargando pagina: $line" && \
	wget -Ep $line &
done < "$filename"

