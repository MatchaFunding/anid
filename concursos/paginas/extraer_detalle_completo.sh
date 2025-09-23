# Ejecuta todos los scripts generados
FONDO=0
set -e  # Termina en caso de error
while read p; do
	wget $p --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" &
done < enlaces_relevantes.txt
