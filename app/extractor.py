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


def extraer_tipo_factura(texto):
    if re.search(r"A\s+NOTA\s+DE\s+CR[ÉE]DITO", texto, re.IGNORECASE):
        return "A NOTA DE CRÉDITO"
    if re.search(r"B\s+NOTA\s+DE\s+CR[ÉE]DITO", texto, re.IGNORECASE):
        return "B NOTA DE CRÉDITO"
    if re.search(r"FACTURA DE CR[ÉE]DITO ELECTR[ÓO]NICA A MiPyMEs", texto, re.IGNORECASE):
        return "FACTURA DE CRÉDITO ELECTRÓNICA A MiPyMEs (FCE)"
    if re.search(r"\bA\s+FACTURA\b", texto, re.IGNORECASE):
        return "A FACTURA"
    if re.search(r"\bB\s+FACTURA\b", texto, re.IGNORECASE):
        return "B FACTURA"
    return ""


def extraer_condicion_venta(texto):
    match = re.search(
        r"Opción de Transferencia:\s*(.+?)(?:\n|CBU del Emisor:|Alias CBU:|Fecha de Vto\. para el pago:)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        valor = limpiar_texto(match.group(1))

        valor = valor.replace("Opción de Transferencia:", "").strip()

        if valor:
            return valor

    if re.search(r"Cuenta Corriente\s*/\s*Transferencia Bancaria", texto, re.IGNORECASE):
        return "Cuenta Corriente / Transferencia Bancaria"

    if re.search(r"Cuenta Corriente", texto, re.IGNORECASE):
        return "Cuenta Corriente"

    return ""


def extraer_receptor_fce(texto):
    lineas = [limpiar_texto(l) for l in texto.splitlines() if limpiar_texto(l)]

    razon_social = ""
    cuit = ""
    domicilio = ""

    for i, linea in enumerate(lineas):
        if "Apellido y Nombre / Razón Social" in linea:
            bloque = lineas[i:i + 12]

            for item in bloque:
                match = re.search(r"\b([0-9]{11})\s+(.+)", item)
                if match:
                    posible_cuit = match.group(1)
                    posible_razon = limpiar_texto(match.group(2))

                    if posible_cuit != "30714918520":
                        cuit = posible_cuit
                        razon_social = posible_razon
                        break

            if razon_social:
                for item in bloque:
                    if (
                        item != razon_social
                        and not re.search(r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$", item)
                        and not item.startswith("CUIT")
                        and not item.startswith("Condición")
                        and not item.startswith("Apellido")
                        and not item.startswith("Domicilio")
                        and not item.startswith("Ingresos")
                        and not re.search(r"\b[0-9]{11}\b", item)
                        and re.search(r"\d", item)
                    ):
                        domicilio = item
                        break

            break

    return razon_social, cuit, domicilio


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
        "periodo": "",
        "importe_total": "",
        "cae": ""
    }

    datos["tipo_factura"] = extraer_tipo_factura(texto)

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

    if "FCE" in datos["tipo_factura"]:
        razon_fce, cuit_fce, domicilio_fce = extraer_receptor_fce(texto)

        if razon_fce:
            datos["razon_social"] = razon_fce
        if cuit_fce:
            datos["cuit"] = cuit_fce
        if domicilio_fce:
            datos["domicilio"] = domicilio_fce

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

    datos["condicion_venta"] = extraer_condicion_venta(texto)

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
        r"CAE N°:.*?([0-9]{14})"
    )

    return datos