# Ejecuta todos los scripts generados
set -e  # Termina en caso de error
while read p; do
	echo "Abriendo pagina del detalle: $p" &
done < enlaces_relevantes.txt
