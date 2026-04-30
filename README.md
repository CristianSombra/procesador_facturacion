# Procesador de Facturación PDF – CAMSA

Aplicación de escritorio desarrollada en Python para procesar facturas en PDF, extraer información automáticamente y exportarla en formatos utilizables para administración y contabilidad.

---

## Objetivo

Reducir tiempo operativo de carga manual de comprobantes, automatizando la lectura de PDFs y generando bases listas para la contadora.

---

## Funcionalidades principales

### Carga de archivos

- Arrastrar y soltar múltiples PDFs
- Procesamiento masivo
- Estado en tiempo real
- Log de avance por archivo

### Extracción automática de datos

Detecta y guarda:

- Tipo de comprobante
- Número
- Fecha de facturación
- Fecha de vencimiento
- Razón social
- CUIT
- Condición IVA
- Domicilio
- Condición de venta
- Período facturado
- Importe total
- CAE

### Interfaz gráfica

- Tabla visual integrada
- Columnas optimizadas
- Logo corporativo CAMSA
- Botón Nuevo Proceso

### Exportación

#### Excel (.xlsx)

- Columnas autoajustadas
- Formato profesional
- Importes con signo `$`

#### PDF

- Horizontal
- Multipágina automática
- Tabla completa lista para impresión

### Limpieza operativa

Botón **Nuevo proceso**:

- Limpia tabla
- Limpia logs
- Vacía base de datos temporal

---

## Tecnologías utilizadas

- Python 3
- Tkinter
- tkinterdnd2
- PostgreSQL
- psycopg2
- pandas
- openpyxl
- reportlab
- PyInstaller

---

## Ejecutable

Versión Windows:

`ProcesadorFacturacion.exe`

No requiere Visual Studio Code para operar.

---

## Estructura del proyecto

```text
procesador_facturacion/
│── app/
│   ├── ui.py
│   ├── main.py
│   ├── extractor.py
│   ├── database.py
│   ├── exportador.py
│   └── settings.py
│
│── assets/
│   └── logo_camsa.png
│
│── config/
│   └── .env
│
│── pdfs/
│── dist/
│── build/
│── README.md
│── requirements.txt
│── .gitignore