# Ejecuta todos los scripts generados
set -e  # Termina en caso de error
for f in *.sh; do
	echo "Ejecutando el script: $f" && \
	bash "$f"
done

