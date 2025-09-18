from pypdf import PdfReader
import sys

"""
Script para obtener el texto de un PDF
"""
reader = PdfReader('bases3.pdf')
pages_qty = len(reader.pages)
out = ""
print(f"Cantidad de paginas: {pages_qty}")
for p in range(pages_qty):
    page = reader.pages[p]
    text = page.extract_text()
    out += text
print(out)

print("Peso del texto leido:", sys.getsizeof(out), "bytes.")
