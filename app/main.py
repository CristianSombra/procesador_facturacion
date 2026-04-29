import os
from extractor import extraer_datos_factura
from database import guardar_factura, crear_tabla


def procesar_archivo(ruta_pdf):
    crear_tabla()

    nombre_archivo = os.path.basename(ruta_pdf)
    print(f"Procesando: {nombre_archivo}")

    datos = extraer_datos_factura(ruta_pdf)
    guardar_factura(datos)

    return datos


def main():
    crear_tabla()

    carpeta_pdfs = "pdfs"
    archivos = [f for f in os.listdir(carpeta_pdfs) if f.lower().endswith(".pdf")]

    if not archivos:
        print("No hay PDFs en la carpeta pdfs.")
        return

    for archivo in archivos:
        ruta_pdf = os.path.join(carpeta_pdfs, archivo)
        procesar_archivo(ruta_pdf)

    print("Proceso terminado. ✅")


if __name__ == "__main__":
    main()