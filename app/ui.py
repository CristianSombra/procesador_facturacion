from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from main import procesar_archivo
from exportador import exportar_excel, exportar_pdf


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


def exportar_datos():
    formato = formato_exportacion.get()

    try:
        if formato == "Excel":
            exportar_excel()
            agregar_log("Exportación Excel realizada.")
        elif formato == "PDF":
            exportar_pdf()
            agregar_log("Exportación PDF realizada.")
        else:
            messagebox.showwarning("Atención", "Seleccioná un formato de exportación.")

    except Exception as error:
        agregar_log(f"ERROR al exportar: {error}")
        messagebox.showerror("Error", f"No se pudo exportar:\n{error}")


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
    ventana.after(0, lambda: agregar_log("Proceso terminado ✅"))


def soltar_archivos(evento):
    archivos = evento.widget.tk.splitlist(evento.data)

    hilo = threading.Thread(
        target=procesar_archivos_en_segundo_plano,
        args=(archivos,),
        daemon=True
    )
    hilo.start()


def iniciar_interfaz():
    global ventana, tabla, log, estado, formato_exportacion

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

    frame_exportar = tk.Frame(ventana)
    frame_exportar.pack(pady=5)

    tk.Label(
        frame_exportar,
        text="Exportar como:",
        font=("Arial", 10)
    ).pack(side="left", padx=5)

    formato_exportacion = tk.StringVar(value="Excel")

    selector_exportacion = ttk.Combobox(
        frame_exportar,
        textvariable=formato_exportacion,
        values=["Excel", "PDF"],
        state="readonly",
        width=10
    )
    selector_exportacion.pack(side="left", padx=5)

    boton_exportar = tk.Button(
        frame_exportar,
        text="Exportar",
        command=exportar_datos,
        width=15
    )
    boton_exportar.pack(side="left", padx=5)

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

    ANCHOS_COLUMNAS = {
        "tipo_factura": 260,
        "numero_factura": 110,
        "fecha_facturacion": 130,
        "fecha_vencimiento": 130,
        "razon_social": 480,
        "cuit": 120,
        "condicion_iva": 180,
        "domicilio": 380,
        "condicion_venta": 260,
        "periodo": 190,
        "importe_total": 130,
        "cae": 170,
    }

    for campo, titulo_columna in COLUMNAS:
        tabla.heading(campo, text=titulo_columna)
        tabla.column(
            campo,
            width=ANCHOS_COLUMNAS.get(campo, 150),
            minwidth=100,
            anchor="w",
            stretch=False
        )

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