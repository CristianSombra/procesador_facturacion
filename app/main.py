import os
from extractor import extraer_datos_factura
from database import guardar_factura, crear_tabla


def main():
    crear_tabla()

    carpeta_pdfs = "pdfs"
    archivos = [f for f in os.listdir(carpeta_pdfs) if f.lower().endswith(".pdf")]

    if not archivos:
        print("No hay PDFs en la carpeta pdfs.")
        return

    for archivo in archivos:
        ruta_pdf = os.path.join(carpeta_pdfs, archivo)
        print(f"Procesando: {archivo}")

        datos = extraer_datos_factura(ruta_pdf)
        guardar_factura(datos)

    print("Proceso terminado.")


if __name__ == "__main__":
    main()