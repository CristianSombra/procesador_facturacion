import psycopg2
from settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def crear_tabla():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id SERIAL PRIMARY KEY,
        tipo_factura TEXT,
        numero_factura TEXT UNIQUE,
        fecha_facturacion TEXT,
        fecha_vencimiento TEXT,
        razon_social TEXT,
        cuit TEXT,
        condicion_iva TEXT,
        domicilio TEXT,
        condicion_venta TEXT,
        periodo TEXT,
        importe_total NUMERIC,
        cae TEXT
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def guardar_factura(datos):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO facturas (
            tipo_factura,
            numero_factura,
            fecha_facturacion,
            fecha_vencimiento,
            razon_social,
            cuit,
            condicion_iva,
            domicilio,
            condicion_venta,
            periodo,
            importe_total,
            cae
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get("tipo_factura"),
            datos.get("numero_factura"),
            datos.get("fecha_facturacion"),
            datos.get("fecha_vencimiento"),
            datos.get("razon_social"),
            datos.get("cuit"),
            datos.get("condicion_iva"),
            datos.get("domicilio"),
            datos.get("condicion_venta"),
            datos.get("periodo"),
            datos.get("importe_total"),
            datos.get("cae")
        ))

        conn.commit()
        print(f"OK: factura guardada {datos.get('numero_factura')}")

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"DUPLICADA: {datos.get('numero_factura')}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    crear_tabla()