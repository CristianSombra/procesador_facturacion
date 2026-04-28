from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import ttk
import threading
import os
from main import procesar_archivo


COLUMNAS = [
    ("tipo_factura", "Tipo de comprobante"),
    ("numero_factura", "Número"),
    ("fecha_facturacion", "Fecha facturación"),
    ("fecha_vencimiento", "Fecha vencimiento"),
    ("razon_social", "Razón social"),
    ("cuit", "CUIT"),
    ("condicion_iva", "Condición IVA"),
    ("domicilio", "Domicilio"),
    ("condicion_venta", "Condición de venta"),
    ("periodo", "Período facturado"),
    ("importe_total", "Importe total"),
    ("cae", "CAE"),
]


def agregar_log(texto):
    log.insert("end", texto + "\n")
    log.see("end")


def agregar_fila(datos):
    valores = [datos.get(campo, "") for campo, _ in COLUMNAS]
    tabla.insert("", "end", values=valores)


def procesar_archivos_en_segundo_plano(archivos):
    ventana.after(0, lambda: estado.config(text="Procesando archivos..."))
    ventana.after(0, lambda: agregar_log("Inicio del procesamiento"))

    for archivo in archivos:
        if not archivo.lower().endswith(".pdf"):
            continue

        nombre = os.path.basename(archivo)
        ventana.after(0, lambda n=nombre: agregar_log(f"Procesando: {n}"))

        try:
            datos = procesar_archivo(archivo)

            if datos:
                ventana.after(0, lambda d=datos: agregar_fila(d))
                ventana.after(0, lambda n=nombre: agregar_log(f"OK: {n}"))

        except Exception as error:
            ventana.after(0, lambda n=nombre, e=error: agregar_log(f"ERROR en {n}: {e}"))

    ventana.after(0, lambda: estado.config(text="Proceso terminado"))
    ventana.after(0, lambda: agregar_log("Proceso terminado"))


def soltar_archivos(evento):
    archivos = evento.widget.tk.splitlist(evento.data)

    hilo = threading.Thread(
        target=procesar_archivos_en_segundo_plano,
        args=(archivos,),
        daemon=True
    )
    hilo.start()


def iniciar_interfaz():
    global ventana, tabla, log, estado

    ventana = TkinterDnD.Tk()
    ventana.title("Procesador de Facturación PDF")
    ventana.geometry("1300x750")

    titulo = tk.Label(
        ventana,
        text="Procesador de Facturación PDF",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    zona = tk.Label(
        ventana,
        text="Arrastrá aquí los archivos PDF",
        font=("Arial", 14),
        bg="#d9d9d9",
        width=60,
        height=5,
        relief="ridge",
        bd=2
    )
    zona.pack(pady=10)

    zona.drop_target_register(DND_FILES)
    zona.dnd_bind("<<Drop>>", soltar_archivos)

    estado = tk.Label(
        ventana,
        text="Esperando archivos...",
        font=("Arial", 11, "bold")
    )
    estado.pack(pady=5)

    log = tk.Text(ventana, height=6)
    log.pack(fill="x", padx=20, pady=10)

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

    columnas_ids = [campo for campo, _ in COLUMNAS]

    tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas_ids,
        show="headings"
    )

    for campo, titulo_columna in COLUMNAS:
        tabla.heading(campo, text=titulo_columna)
        tabla.column(campo, width=150)

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)

    tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    ventana.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()