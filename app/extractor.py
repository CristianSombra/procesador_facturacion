import re
import pdfplumber


def limpiar_texto(texto):
    if not texto:
        return ""
    return " ".join(texto.split())


def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""

    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += "\n" + texto

    return texto_completo


def buscar_patron(texto, patron):
    resultado = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
    if resultado:
        return limpiar_texto(resultado.group(1))
    return ""


def limpiar_importe(valor):
    if not valor:
        return None

    valor = valor.replace(".", "").replace(",", ".").strip()

    try:
        return float(valor)
    except ValueError:
        return None

def limpiar_condicion_venta(valor):
    valor = limpiar_texto(valor)

    cortes = [" Fac. A:", " Fac. B:", " Código Producto", " Alicuota"]
    for corte in cortes:
        if corte in valor:
            valor = valor.split(corte)[0]

    return valor.strip()

def extraer_datos_factura(ruta_pdf):
    texto = extraer_texto_pdf(ruta_pdf)

    datos = {
        "tipo_factura": "",
        "numero_factura": "",
        "fecha_facturacion": "",
        "fecha_vencimiento": "",
        "razon_social": "",
        "cuit": "",
        "condicion_iva": "",
        "domicilio": "",
        "condicion_venta": "",
        "opcion_transferencia": "",
        "periodo": "",
        "importe_total": "",
        "cae": ""
    }

    # Tipo de factura
    if re.search(r"A\s+NOTA\s+DE\s+CR[ÉE]DITO", texto, re.IGNORECASE):
        datos["tipo_factura"] = "A NOTA DE CRÉDITO"
    elif re.search(r"B\s+NOTA\s+DE\s+CR[ÉE]DITO", texto, re.IGNORECASE):
        datos["tipo_factura"] = "B NOTA DE CRÉDITO"
    elif re.search(r"FACTURA DE CR[ÉE]DITO ELECTR[ÓO]NICA A MiPyMEs", texto, re.IGNORECASE):
        datos["tipo_factura"] = "FACTURA DE CRÉDITO ELECTRÓNICA A MiPyMEs (FCE)"
    elif re.search(r"\bA\s+FACTURA\b", texto, re.IGNORECASE):
        datos["tipo_factura"] = "A FACTURA"
    elif re.search(r"\bB\s+FACTURA\b", texto, re.IGNORECASE):
        datos["tipo_factura"] = "B FACTURA"

    datos["numero_factura"] = buscar_patron(
        texto,
        r"Comp\.\s*Nro:\s*([0-9]+)"
    )

    datos["fecha_facturacion"] = buscar_patron(
        texto,
        r"Fecha de Emisión:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    datos["fecha_vencimiento"] = buscar_patron(
        texto,
        r"Fecha de Vto\. para el pago:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    datos["razon_social"] = buscar_patron(
        texto,
        r"Apellido y Nombre / Razón Social:\s*(.+?)\s*(?:Condición frente al IVA:|Domicilio|CUIT:|Condición de venta:)"
    )

    datos["cuit"] = buscar_patron(
        texto,
        r"Apellido y Nombre / Razón Social:.*?\n.*?([0-9]{11})"
    )

    coincidencias_iva = re.findall(
        r"Condición frente al IVA:\s*(.+?)\s*(?:Domicilio|CUIT:|Fecha de Inicio de Actividades:|\n)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    coincidencias_iva = [limpiar_texto(x) for x in coincidencias_iva if limpiar_texto(x)]

    if len(coincidencias_iva) >= 2:
        datos["condicion_iva"] = coincidencias_iva[1]
    elif len(coincidencias_iva) == 1:
        datos["condicion_iva"] = coincidencias_iva[0]

    domicilios = re.findall(
        r"Domicilio(?: Comercial)?:\s*(.+?)\s*(?:CUIT:|Condición de venta:|Condición frente al IVA:)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    domicilios = [limpiar_texto(x) for x in domicilios if limpiar_texto(x)]

    if len(domicilios) >= 2:
        datos["domicilio"] = domicilios[1]
    elif len(domicilios) == 1:
        datos["domicilio"] = domicilios[0]

    condicion_venta = buscar_patron(
        texto,
        r"Condición de venta:\s*([^\n\r]+)"
    )
    
    datos["condicion_venta"] = limpiar_condicion_venta(condicion_venta)

    datos["opcion_transferencia"] = buscar_patron(
        texto,
        r"Opción de Transferencia:\s*(.+?)\s*CBU del Emisor:"
    )

    periodo_desde = buscar_patron(
        texto,
        r"Período Facturado Desde:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    periodo_hasta = buscar_patron(
        texto,
        r"Hasta:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    if periodo_desde or periodo_hasta:
        datos["periodo"] = f"{periodo_desde} - {periodo_hasta}"

    importe_extraido = buscar_patron(
        texto,
        r"Importe Total:\s*\$?\s*([0-9\.\,]+)"
    )

    datos["importe_total"] = limpiar_importe(importe_extraido)

    datos["cae"] = buscar_patron(
        texto,
        r"CAE N°:\s*([0-9]+)"
    )

    return datos