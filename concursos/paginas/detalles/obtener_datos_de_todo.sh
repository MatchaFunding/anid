for f in *.html; do
	python obtener_datos_de_fondo.py $f &
done
