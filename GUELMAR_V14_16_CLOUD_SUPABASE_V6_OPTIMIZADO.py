
import os
import re

# PostgreSQL / Supabase Cloud
try:
    import psycopg2
    from psycopg2.extras import DictCursor
    from psycopg2.pool import ThreadedConnectionPool
except ImportError:
    psycopg2 = None
    DictCursor = None
    ThreadedConnectionPool = None
import base64
from io import BytesIO
import hashlib
import secrets
import shutil
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

import pandas as pd
from PIL import Image, ImageChops
import altair as alt
import streamlit as st

# ============================================================
# GUELMAR - SISTEMA INTEGRAL DE GESTIÓN COMERCIAL
# Versión 1.4.16 CLOUD - Inventario central Supabase - V6 Optimizado
# ============================================================


# ===== GUELMAR V10: CONTRASTE TOTAL — MISMA LEGIBILIDAD EN CLARO Y OSCURO =====
st.html("""
<style>
/* Fuerza una interfaz clara y de alto contraste, independientemente del tema del navegador/Streamlit. */
:root { color-scheme: light !important; }
html, body { background:#f4f7fb !important; color:#172033 !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background:#f4f7fb !important;
    color:#172033 !important;
}

/* Texto general: azul muy oscuro, completamente opaco. */
.stApp p, .stApp label, .stApp span, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
[data-testid="stText"], [data-testid="stCaptionContainer"] {
    color:#172033 !important;
    opacity:1 !important;
}

/* Barra superior de Streamlit: evita cualquier franja negra/oscura. */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    background:#ffffff !important;
    color:#172033 !important;
}
[data-testid="stHeader"] * , [data-testid="stToolbar"] * {
    color:#172033 !important;
    fill:#172033 !important;
}

/* Barra lateral: fondo claro + texto oscuro siempre. */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background:#eef5ff !important;
    color:#102a56 !important;
    border-right:1px solid #c9d9ec !important;
}
[data-testid="stSidebar"] * { color:#102a56 !important; opacity:1 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background:transparent !important;
    color:#102a56 !important;
    border-radius:10px !important;
    font-weight:750 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#dcecff !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background:#cfe4ff !important;
    color:#063b7a !important;
    box-shadow:inset 4px 0 0 #1769d1 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * { color:#063b7a !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#405979 !important; }
[data-testid="stSidebar"] hr { border-color:#c9d9ec !important; }

/* Logo de la barra lateral y logo principal: siempre sobre blanco. */
.sidebar-logo {
    background:#ffffff !important;
    border:1px solid #cbd9e8 !important;
    box-shadow:0 5px 16px rgba(15,23,42,.08) !important;
}
.guelmar-header {
    background:#ffffff !important;
    color:#102a56 !important;
    border:2px solid #cbd9e8 !important;
    box-shadow:0 10px 28px rgba(15,23,42,.10) !important;
}
.guelmar-header h1, .guelmar-header p { color:#102a56 !important; opacity:1 !important; }
.guelmar-header p { color:#3d5878 !important; font-weight:700 !important; }

/* Tarjetas y contenedores: blanco, con texto oscuro. */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stExpander"], [data-testid="stExpander"] > details,
[data-testid="stForm"], .metric-card {
    background:#ffffff !important;
    color:#172033 !important;
    border-color:#d5deea !important;
}
.metric-title { color:#41536c !important; }
.metric-value { color:#0f1f3d !important; }
.metric-note { color:#52657e !important; }
.section-title { color:#102a56 !important; }

/* Inputs, selectores y áreas de texto. */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"],
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[role="combobox"],
[data-testid="stMultiSelect"] div[role="combobox"] {
    background:#ffffff !important;
    color:#172033 !important;
    border-color:#b9c8da !important;
    opacity:1 !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
[data-baseweb="select"] input, [data-baseweb="select"] [role="combobox"],
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    color:#172033 !important;
    -webkit-text-fill-color:#172033 !important;
    background:#ffffff !important;
}
input::placeholder, textarea::placeholder { color:#64748b !important; opacity:1 !important; }

/* Dropdowns */
[role="listbox"], [role="option"], [data-baseweb="popover"] {
    background:#ffffff !important;
    color:#172033 !important;
    opacity:1 !important;
}
[role="option"] * { color:#172033 !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background:#e6f0ff !important; }

/* Botones: fondo con contraste y texto siempre legible. */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] button, button {
    color:#102a56 !important;
    -webkit-text-fill-color:#102a56 !important;
    opacity:1 !important;
    font-weight:800 !important;
}
.stButton > button:not([kind="primary"]), .stDownloadButton > button {
    background:#e7f1ff !important;
    border:1px solid #a9c5e6 !important;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
    background:#1769d1 !important;
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
    border:1px solid #0f55ad !important;
}

/* Tabs, métricas, tablas y carrito. */
.stTabs [data-baseweb="tab"] { color:#243b5a !important; font-weight:800 !important; opacity:1 !important; }
.stTabs [aria-selected="true"] { color:#0b5ed7 !important; }
[data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stDataEditor"] {
    background:#ffffff !important; color:#172033 !important; opacity:1 !important;
}
[data-testid="stDataFrame"] *, [data-testid="stTable"] *, [data-testid="stDataEditor"] * {
    color:#172033 !important; opacity:1 !important;
}
.carrito, .cart, .cart-item, .producto-carrito, .item-carrito,
.detalle-carrito, .resumen-carrito {
    background:#ffffff !important; color:#172033 !important; opacity:1 !important;
}
.carrito *, .cart *, .cart-item *, .producto-carrito *, .item-carrito *,
.detalle-carrito *, .resumen-carrito * { color:#172033 !important; opacity:1 !important; }

/* Alertas y mensajes. */
[data-testid="stAlert"], [data-testid="stAlert"] * { opacity:1 !important; }
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color:inherit !important; }

/* Evita que el tema oscuro del sistema vuelva a oscurecer los componentes. */
/* Refuerzo: aunque el sistema operativo esté en modo oscuro, GUELMAR conserva fondos claros. */
[data-testid="stMain"] *, [data-testid="stMainBlockContainer"] * {
    text-shadow:none !important;
}
[data-testid="stMain"] [data-baseweb="popover"],
[data-testid="stMain"] [data-baseweb="menu"],
[data-testid="stMain"] [role="listbox"] {
    background:#ffffff !important;
    color:#172033 !important;
}

@media (prefers-color-scheme: dark) {
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:#f4f7fb !important; color:#172033 !important;
    }
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] { background:#eef5ff !important; }
    [data-testid="stSidebar"] * { color:#102a56 !important; }
    .guelmar-header, .sidebar-logo, [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"], [data-testid="stForm"], .metric-card,
    [data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stDataEditor"] {
        background:#ffffff !important; color:#172033 !important;
    }
    .stApp p, .stApp label, .stApp span, .stApp div, .stApp h1, .stApp h2,
    .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color:#172033 !important; }
    [data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        background:#ffffff !important; color:#172033 !important; -webkit-text-fill-color:#172033 !important;
    }
}
</style>
""")

st.set_page_config(
    page_title="GUELMAR | Gestión Comercial",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
# GUELMAR CLOUD: la base local se conserva únicamente como respaldo histórico.
# Este archivo NO abre ni modifica guelmar.db.
DB_PATH = BASE_DIR / "guelmar.db"
IMG_DIR = BASE_DIR / "imagenes_productos"
BACKUP_DIR = BASE_DIR / "backups"

IMG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)


def _database_url():
    """Obtiene la conexión PostgreSQL sin guardar contraseñas dentro del código."""
    try:
        url = st.secrets.get("SUPABASE_DB_URL", "")
    except Exception:
        url = ""
    return (url or os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL") or "").strip()


class CloudCursor:
    """Pequeña capa de compatibilidad para conservar el código SQL de GUELMAR."""

    def __init__(self, raw_conn):
        self._conn = raw_conn
        self._cur = raw_conn.cursor(cursor_factory=DictCursor)
        self._lastrowid = None

    @staticmethod
    def _translate(sql):
        # El programa original usa ?; CloudCursor lo adapta a PostgreSQL.
        # PostgreSQL utiliza %s.
        sql = sql.replace("?", "%s")
        # Compatibilidad con el único INSERT OR IGNORE histórico del módulo fiscal.
        sql = re.sub(r"^\s*INSERT\s+OR\s+IGNORE\s+INTO", "INSERT INTO", sql,
                     flags=re.IGNORECASE)
        return sql

    def execute(self, sql, params=()):
        sql = self._translate(sql)
        # Para INSERTs del sistema necesitamos recuperar el id generado,
        # equivalente a lastrowid para el código histórico de GUELMAR.
        is_insert = bool(re.match(r"^\s*INSERT\s+INTO\b", sql, re.IGNORECASE))
        if is_insert and "RETURNING" not in sql.upper():
            sql = sql.rstrip().rstrip(";") + " RETURNING id"
        self._cur.execute(sql, params or ())
        self._lastrowid = None
        if is_insert:
            try:
                row = self._cur.fetchone()
                if row is not None:
                    self._lastrowid = row["id"] if "id" in row.keys() else row[0]
            except Exception:
                self._lastrowid = None
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    @property
    def lastrowid(self):
        return self._lastrowid


class CloudConnection:
    def __init__(self, raw_conn, pool=None):
        self._raw = raw_conn
        self._pool = pool
        self._closed = False

    def execute(self, sql, params=()):
        return CloudCursor(self._raw).execute(sql, params)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            # Devuelve la conexión al pool en vez de cerrar el socket SSL.
            if self._pool is not None:
                self._pool.putconn(self._raw)
            else:
                self._raw.close()
        except Exception:
            try:
                self._raw.close()
            except Exception:
                pass

    def begin(self):
        self._raw.autocommit = False


@st.cache_resource(show_spinner=False)
def _get_connection_pool():
    """Mantiene conexiones reutilizables para no abrir una conexión SSL nueva en cada consulta."""
    if psycopg2 is None or ThreadedConnectionPool is None:
        raise RuntimeError(
            "Falta instalar psycopg2-binary. Ejecuta: py -m pip install psycopg2-binary"
        )
    url = _database_url()
    if not url:
        raise RuntimeError(
            "GUELMAR CLOUD no tiene configurada SUPABASE_DB_URL. "
            "La conexión se configurará en el siguiente paso sin modificar guelmar.db."
        )
    return ThreadedConnectionPool(1, 10, dsn=url, sslmode="require", connect_timeout=10)


def get_conn():
    pool = _get_connection_pool()
    raw = pool.getconn()
    raw.autocommit = False
    return CloudConnection(raw, pool)


@st.cache_data(show_spinner=False, max_entries=64)
def preparar_imagen_pos_sin_espacios(imagen_path: Path, padding: int = 6):
    """Recorta márgenes blancos de la foto solo para mostrarla en el POS.

    IMPORTANTE: no modifica el archivo original.
    Se usa detección por diferencia respecto al fondo blanco.
    La máscara alfa solo se usa cuando la imagen realmente tiene transparencia;
    en JPG/PNG opacos no se considera el alfa porque sería 255 en toda la foto
    y anularía el recorte.
    """
    try:
        with Image.open(imagen_path) as original:
            img = original.convert("RGBA")
            w, h = img.size
            if w < 2 or h < 2:
                return img.copy()

            rgb = img.convert("RGB")
            # Detecta píxeles que no son prácticamente blancos.
            # 245 permite eliminar fondos blancos y pequeños bordes de JPG.
            pix = rgb.load()
            threshold = 245

            # Primero buscamos el contenido por filas/columnas, evitando que
            # pequeños puntos aislados del borde impidan el recorte.
            xs = []
            ys = []
            step = max(1, min(w, h) // 500)
            for y in range(0, h, step):
                for x in range(0, w, step):
                    r, g, b = pix[x, y]
                    if min(r, g, b) < threshold:
                        xs.append(x)
                        ys.append(y)

            if not xs:
                return img.copy()

            left, top, right, bottom = min(xs), min(ys), max(xs) + 1, max(ys) + 1

            # Si existe transparencia real, cualquier píxel visible cuenta como contenido.
            if "A" in original.getbands():
                alpha = img.getchannel("A")
                amin, amax = alpha.getextrema()
                if amin < 250:  # solo si realmente hay transparencia
                    abox = alpha.point(lambda p: 255 if p > 12 else 0).getbbox()
                    if abox:
                        left = min(left, abox[0])
                        top = min(top, abox[1])
                        right = max(right, abox[2])
                        bottom = max(bottom, abox[3])

            # Evita recortes extremos por ruido puntual: exige que haya margen.
            if left <= 1 and top <= 1 and right >= w - 1 and bottom >= h - 1:
                return img.copy()

            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(w, right + padding)
            bottom = min(h, bottom + padding)

            return img.crop((left, top, right, bottom))
    except Exception:
        return None


CATEGORIAS = ["Inalámbricas", "Manuales", "Eléctricas", "Repuestos", "Accesorios", "Insumos"]
MARCAS = ["INGCO", "TOTAL", "UYUSTOOLS", "MEWEE", "Otra"]
METODOS_PAGO = ["Efectivo", "QR", "Tarjeta"]



# Logo GUELMAR integrado en el sistema (PNG con fondo transparente)
GUELMAR_LOGO_B64 = """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"""

@st.cache_data(show_spinner=False)
def logo_data_uri():
    return "data:image/png;base64," + GUELMAR_LOGO_B64

@st.cache_data(show_spinner=False)
def logo_bytes():
    return base64.b64decode(GUELMAR_LOGO_B64)


def guardar_imagen_producto(uploaded_file, producto_id: int, codigo: str) -> str:
    """Guarda la imagen subida en la carpeta controlada por GUELMAR y devuelve su ruta relativa."""
    if uploaded_file is None:
        return ""

    nombre_original = Path(uploaded_file.name).name
    extension = Path(nombre_original).suffix.lower()
    extensiones_permitidas = {".jpg", ".jpeg", ".png"}
    if extension not in extensiones_permitidas:
        raise ValueError("Formato de imagen no permitido. Usa JPG, JPEG o PNG.")

    codigo_limpio = "".join(ch if ch.isalnum() else "_" for ch in str(codigo).strip())
    codigo_limpio = codigo_limpio[:60] or "producto"
    destino = IMG_DIR / f"producto_{producto_id}_{codigo_limpio}{extension}"

    # Evita conservar rutas proporcionadas por el usuario: solo se guarda dentro de IMG_DIR.
    destino.write_bytes(uploaded_file.getvalue())
    return str(destino.relative_to(BASE_DIR))


def ruta_imagen_producto(valor: str) -> Path | None:
    """Resuelve de forma segura la ruta de imagen guardada por GUELMAR."""
    if not valor:
        return None
    ruta = Path(valor)
    if not ruta.is_absolute():
        ruta = BASE_DIR / ruta
    try:
        ruta = ruta.resolve()
        carpeta = IMG_DIR.resolve()
        if ruta.parent != carpeta or not ruta.is_file():
            return None
        return ruta
    except Exception:
        return None

# ---------------------- TICKET DE VENTA -----------------------
def generar_pdf_ticket(venta_id, ancho_mm=80):
    """Genera un comprobante de venta no fiscal en formato térmico 58/80 mm."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import portrait
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import mm
    except ImportError:
        return None

    ancho = 58 * mm if int(ancho_mm) == 58 else 80 * mm
    conn = get_conn()
    try:
        venta = conn.execute("""
            SELECT v.id, v.fecha, COALESCE(s.nombre,'El Alto') AS sucursal, v.subtotal, v.descuento, v.total,
                   v.metodo_pago, v.recibido, v.cambio,
                   COALESCE(c.nombre,'Cliente General') AS cliente,
                   COALESCE(c.nit_ci,'') AS nit_ci,
                   COALESCE(u.usuario,'') AS vendedor
            FROM ventas v
            LEFT JOIN sucursales s ON s.id=v.sucursal_id
            LEFT JOIN clientes c ON c.id=v.cliente_id
            LEFT JOIN usuarios u ON u.id=v.vendedor_id
            WHERE v.id=?
        """, (int(venta_id),)).fetchone()
        if not venta:
            return None
        detalles = conn.execute("""
            SELECT codigo, nombre, cantidad, precio_unitario, total
            FROM detalle_ventas WHERE venta_id=? ORDER BY id
        """, (int(venta_id),)).fetchall()
    finally:
        conn.close()

    # Altura aproximada: crece con la cantidad de productos.
    alto = max(120 * mm, (72 + len(detalles) * 15) * mm)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=(ancho, alto),
        leftMargin=4 * mm, rightMargin=4 * mm,
        topMargin=4 * mm, bottomMargin=4 * mm,
        title=f"Ticket GUELMAR #{venta_id}", author="GUELMAR"
    )

    normal = ParagraphStyle("TicketNormal", fontName="Helvetica", fontSize=7.5, leading=9)
    bold = ParagraphStyle("TicketBold", parent=normal, fontName="Helvetica-Bold")
    centro = ParagraphStyle("TicketCentro", parent=bold, alignment=TA_CENTER, fontSize=10, leading=12)
    pequeno_centro = ParagraphStyle("TicketPequeno", parent=normal, alignment=TA_CENTER, fontSize=6.5, leading=8)
    derecha = ParagraphStyle("TicketDerecha", parent=normal, alignment=TA_RIGHT)
    derecha_bold = ParagraphStyle("TicketDerechaBold", parent=bold, alignment=TA_RIGHT, fontSize=9)

    story = [
        Paragraph("GUELMAR", centro),
        Paragraph("HERRAMIENTAS", ParagraphStyle("SubTicket", parent=centro, fontSize=8, leading=9)),
        Paragraph("COMPROBANTE DE VENTA", centro),
        Paragraph(f"Sucursal: {venta['sucursal'] or 'El Alto'}", pequeno_centro),
        Paragraph(str(venta["fecha"]), pequeno_centro),
        Spacer(1, 2 * mm),
        Paragraph(f"Cliente: {venta['cliente']}", normal),
    ]
    if venta["nit_ci"]:
        story.append(Paragraph(f"NIT/CI: {venta['nit_ci']}", normal))
    story.append(Spacer(1, 2 * mm))

    filas = [[Paragraph("Producto", bold), Paragraph("Cant.", bold), Paragraph("Total", bold)]]
    for d in detalles:
        nombre = str(d["nombre"])
        codigo = str(d["codigo"])
        texto = f"{nombre}<br/><font size=6>{codigo}</font>"
        filas.append([
            Paragraph(texto, normal),
            Paragraph(f"{float(d['cantidad']):g}", derecha),
            Paragraph(money(d["total"]), derecha),
        ])
    tabla = Table(filas, colWidths=[ancho-35*mm, 12*mm, 19*mm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 0.5, colors.black),
        ("LINEBELOW", (0,0), (-1,0), 0.5, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 1),
        ("RIGHTPADDING", (0,0), (-1,-1), 1),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    story += [tabla, Spacer(1, 2*mm)]

    resumen = [
        [Paragraph("Subtotal", normal), Paragraph(money(venta["subtotal"]), derecha)],
        [Paragraph("Descuento", normal), Paragraph(money(venta["descuento"]), derecha)],
        [Paragraph("TOTAL Bs", bold), Paragraph(money(venta["total"]), derecha_bold)],
        [Paragraph("Pago", normal), Paragraph(str(venta["metodo_pago"]), derecha)],
    ]
    if venta["metodo_pago"] == "Efectivo":
        resumen += [
            [Paragraph("Recibido", normal), Paragraph(money(venta["recibido"]), derecha)],
            [Paragraph("Cambio", bold), Paragraph(money(venta["cambio"]), derecha_bold)],
        ]
    rt = Table(resumen, colWidths=[ancho-32*mm, 32*mm])
    rt.setStyle(TableStyle([
        ("LINEABOVE", (0,2), (-1,2), 0.8, colors.black),
        ("LEFTPADDING", (0,0), (-1,-1), 1),
        ("RIGHTPADDING", (0,0), (-1,-1), 1),
        ("TOPPADDING", (0,0), (-1,-1), 1.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1.5),
    ]))
    story += [rt, Spacer(1, 4*mm), Paragraph("¡GRACIAS POR SU COMPRA!", centro),
              Spacer(1, 1*mm), Paragraph("ESTE DOCUMENTO NO ES FACTURA", pequeno_centro),
              Paragraph(f"Vendedor: {venta['vendedor']}", pequeno_centro)]
    doc.build(story)
    return buffer.getvalue()



# ---------------------- PDF COTIZACIÓN -------------------------
def generar_pdf_cotizacion(cotizacion_id):
    """Genera una cotización comercial A4 lista para imprimir y entregar al cliente."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        )
        from reportlab.lib.units import mm
    except ImportError:
        return None

    conn = get_conn()
    try:
        cot = conn.execute("""
            SELECT q.id, q.fecha, q.subtotal, q.total, q.estado,
                   COALESCE(c.nombre,'Cliente General') AS cliente,
                   COALESCE(c.nit_ci,'') AS nit_ci,
                   COALESCE(u.usuario,'') AS vendedor
            FROM cotizaciones q
            LEFT JOIN clientes c ON c.id=q.cliente_id
            LEFT JOIN usuarios u ON u.id=q.usuario_id
            WHERE q.id=?
        """, (int(cotizacion_id),)).fetchone()

        if not cot:
            return None

        detalles = conn.execute("""
            SELECT codigo, nombre, cantidad, precio_unitario, total
            FROM detalle_cotizaciones
            WHERE cotizacion_id=?
            ORDER BY id
        """, (int(cotizacion_id),)).fetchall()
    finally:
        conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
        title=f"Cotización GUELMAR #{cotizacion_id:06d}",
        author="GUELMAR",
    )

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "CotTitulo",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#172033"),
        spaceAfter=3,
    )
    subtitulo = ParagraphStyle(
        "CotSubtitulo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#52657E"),
    )
    normal = ParagraphStyle(
        "CotNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#172033"),
    )
    bold = ParagraphStyle(
        "CotBold",
        parent=normal,
        fontName="Helvetica-Bold",
    )
    # Estilo exclusivo para encabezados con fondo oscuro.
    # Evita que ReportLab conserve el color oscuro del estilo normal
    # y produzca texto negro sobre fondo negro.
    encabezado_tabla = ParagraphStyle(
        "CotEncabezadoTabla",
        parent=bold,
        textColor=colors.white,
    )
    centro = ParagraphStyle(
        "CotCentro",
        parent=bold,
        alignment=TA_CENTER,
    )
    derecha = ParagraphStyle(
        "CotDerecha",
        parent=normal,
        alignment=TA_RIGHT,
    )
    derecha_bold = ParagraphStyle(
        "CotDerechaBold",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#102A56"),
    )

    logo = Image(BytesIO(logo_bytes()), width=50 * mm, height=33 * mm)

    fecha = str(cot["fecha"] or "")
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        fecha = fecha_dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass

    encabezado_derecha = [
        Paragraph("COTIZACIÓN", titulo),
        Paragraph(f"N.º {int(cotizacion_id):06d}", subtitulo),
        Paragraph(f"Fecha: {fecha}", subtitulo),
    ]
    encabezado = Table(
        [[logo, encabezado_derecha]],
        colWidths=[90 * mm, 95 * mm],
    )
    encabezado.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    datos_cliente = [
        [Paragraph("<b>CLIENTE</b>", bold), Paragraph("<b>DATOS DE LA COTIZACIÓN</b>", bold)],
        [
            Paragraph(str(cot["cliente"]), normal),
            Paragraph(f"Vendedor: {cot['vendedor'] or '—'}", normal),
        ],
    ]
    if cot["nit_ci"]:
        datos_cliente.append([
            Paragraph(f"NIT/CI: {cot['nit_ci']}", normal),
            Paragraph("Moneda: Bolivianos (Bs)", normal),
        ])
    else:
        datos_cliente.append([
            Paragraph("NIT/CI: —", normal),
            Paragraph("Moneda: Bolivianos (Bs)", normal),
        ])

    cliente_tabla = Table(datos_cliente, colWidths=[92.5 * mm, 92.5 * mm])
    cliente_tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF5FF")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD9E8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DEEA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    filas = [[
        Paragraph("N.º", encabezado_tabla),
        Paragraph("Código", encabezado_tabla),
        Paragraph("Producto", encabezado_tabla),
        Paragraph("Cantidad", encabezado_tabla),
        Paragraph("P. Unitario", encabezado_tabla),
        Paragraph("Total", encabezado_tabla),
    ]]

    for i, d in enumerate(detalles, start=1):
        filas.append([
            Paragraph(str(i), centro),
            Paragraph(str(d["codigo"]), normal),
            Paragraph(str(d["nombre"]), normal),
            Paragraph(f"{float(d['cantidad']):g}", derecha),
            Paragraph(money(d["precio_unitario"]), derecha),
            Paragraph(money(d["total"]), derecha),
        ])

    tabla = Table(
        filas,
        colWidths=[10*mm, 27*mm, 70*mm, 20*mm, 27*mm, 30*mm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#202734")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D0D5DD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F7F8FA")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    resumen = [
        [Paragraph("Subtotal", normal), Paragraph(money(cot["subtotal"]), derecha)],
        [Paragraph("TOTAL Bs", bold), Paragraph(money(cot["total"]), derecha_bold)],
    ]
    resumen_tabla = Table(resumen, colWidths=[45*mm, 45*mm], hAlign="RIGHT")
    resumen_tabla.setStyle(TableStyle([
        ("LINEABOVE", (0, 1), (-1, 1), 1, colors.HexColor("#172033")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    story = [
        encabezado,
        Spacer(1, 8 * mm),
        cliente_tabla,
        Spacer(1, 8 * mm),
        tabla,
        Spacer(1, 5 * mm),
        resumen_tabla,
        Spacer(1, 18 * mm),
        Paragraph("Gracias por su preferencia.", centro),
    ]

    doc.build(story)
    return buffer.getvalue()


# ---------------------- PDF INVENTARIO ------------------------
def generar_pdf_inventario(df):
    """Genera un PDF del inventario actual con valores de compra y venta."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.units import mm
    except ImportError:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm, leftMargin=10 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
        title="Inventario GUELMAR", author="GUELMAR"
    )

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloGUELMAR", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=18, leading=22,
        alignment=TA_CENTER, spaceAfter=5
    )
    subtitulo = ParagraphStyle(
        "SubtituloGUELMAR", parent=styles["Normal"],
        fontSize=9, alignment=TA_CENTER,
        textColor=colors.HexColor("#667085"), spaceAfter=10
    )
    derecha = ParagraphStyle(
        "Derecha", parent=styles["Normal"],
        fontSize=8, alignment=TA_RIGHT
    )

    columnas = [
        "Código", "Producto", "Categoría", "Marca", "Stock", "Mínimo",
        "Costo compra", "Costo venta", "Total compra", "Total venta"
    ]
    datos = [columnas]

    for _, r in df.iterrows():
        datos.append([
            str(r["Código"]), str(r["Producto"]), str(r["Categoría"]),
            str(r["Marca"]), f'{float(r["Stock"]):g}', f'{float(r["Mínimo"]):g}',
            f'Bs {float(r["Costo compra"]):,.2f}',
            f'Bs {float(r["Costo venta"]):,.2f}',
            f'Bs {float(r["Total compra"]):,.2f}',
            f'Bs {float(r["Total venta"]):,.2f}',
        ])

    total_compra = float(df["Total compra"].sum()) if not df.empty else 0.0
    total_venta = float(df["Total venta"].sum()) if not df.empty else 0.0
    total_unidades = float(df["Stock"].sum()) if not df.empty else 0.0

    datos.append([
        "", "", "", "TOTALES", f"{total_unidades:g}", "",
        "", "", f"Bs {total_compra:,.2f}", f"Bs {total_venta:,.2f}"
    ])

    col_widths = [
        24*mm, 49*mm, 29*mm, 25*mm, 15*mm, 15*mm,
        27*mm, 27*mm, 31*mm, 31*mm
    ]
    tabla = Table(datos, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#202734")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 6.8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D0D5DD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2),
         [colors.white, colors.HexColor("#F7F8FA")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8EEF7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    fecha_pdf = datetime.now().strftime("%d/%m/%Y %H:%M")
    logo_pdf = Image(BytesIO(logo_bytes()), width=55*mm, height=36*mm)
    elementos = [
        # El logo ya contiene la identidad GUELMAR; no se agrega un segundo
        # titulo de texto para evitar el GUELMAR negro duplicado.
        logo_pdf,
        Paragraph(
            f"Inventario de existencias · Generado el {fecha_pdf}", subtitulo
        ),
        tabla,
        Spacer(1, 8),
        Paragraph(
            f"<b>Valor total de compra:</b> Bs {total_compra:,.2f}",
            derecha
        ),
    ]
    doc.build(elementos)
    return buffer.getvalue()


def generar_pdf_catalogo_productos(df, titulo_catalogo="CATÁLOGO DE PRODUCTOS"):
    """Genera un catálogo comercial A4 de 3 productos por fila, con imágenes."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.units import mm
    except ImportError:
        return None

    if df is None or df.empty:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=8*mm, leftMargin=8*mm,
        topMargin=8*mm, bottomMargin=8*mm,
        title="Catálogo de productos GUELMAR", author="GUELMAR"
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "CatalogoTituloV4", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=18, leading=21, alignment=TA_CENTER,
        textColor=colors.HexColor("#202734"), spaceAfter=2
    )
    subtitulo = ParagraphStyle(
        "CatalogoSubtituloV4", parent=styles["Normal"], fontSize=7.5,
        leading=9.5, alignment=TA_CENTER, textColor=colors.HexColor("#667085"),
        spaceAfter=7
    )
    nombre_style = ParagraphStyle(
        "CatalogoNombreV4", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=10.5, alignment=TA_CENTER,
        textColor=colors.HexColor("#202734"), spaceAfter=2
    )
    detalle_style = ParagraphStyle(
        "CatalogoDetalleV4", parent=styles["Normal"], fontSize=6.8, leading=8.5,
        alignment=TA_CENTER, textColor=colors.HexColor("#667085")
    )
    precio_style = ParagraphStyle(
        "CatalogoPrecioV4", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=11, leading=12.5, alignment=TA_CENTER,
        textColor=colors.HexColor("#d9573f"), spaceBefore=2
    )

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos = [
        Image(BytesIO(logo_bytes()), width=34*mm, height=22*mm),
        Paragraph(titulo_catalogo, titulo),
        Paragraph(f"GUELMAR HERRAMIENTAS · Precios en bolivianos · {fecha}", subtitulo),
    ]

    tarjetas = []
    for _, r in df.iterrows():
        imagen_path = ruta_imagen_producto(str(r.get("imagen", "")))
        if imagen_path:
            try:
                img = Image(str(imagen_path), width=50*mm, height=39*mm)
                img.hAlign = "CENTER"
                img.preserveAspectRatio = True
            except Exception:
                img = Paragraph("Sin imagen", detalle_style)
        else:
            img = Paragraph("Sin imagen", detalle_style)

        nombre = str(r.get("Producto", ""))
        codigo = str(r.get("Código", ""))
        categoria = str(r.get("Categoría", ""))
        marca = str(r.get("Marca", ""))
        precio = float(r.get("Precio", 0) or 0)

        contenido = [
            [img],
            [Paragraph(nombre, nombre_style)],
            [Paragraph(f"Código: {codigo}", detalle_style)],
            [Paragraph(f"Marca: {marca}", detalle_style)],
            [Paragraph(f"Categoría: {categoria}", detalle_style)],
            [Paragraph(f"Bs {precio:,.2f}", precio_style)],
        ]
        tarjeta = Table(contenido, colWidths=[59*mm], hAlign="CENTER")
        tarjeta.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.white),
            ("BOX", (0,0), (-1,-1), 0.55, colors.HexColor("#D0D5DD")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        tarjetas.append(tarjeta)

    filas = []
    for i in range(0, len(tarjetas), 3):
        fila = tarjetas[i:i+3]
        while len(fila) < 3:
            fila.append("")
        filas.append(fila)

    rejilla = Table(
        filas,
        colWidths=[61*mm, 61*mm, 61*mm],
        hAlign="CENTER",
        repeatRows=0,
    )
    rejilla.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 1.5),
        ("RIGHTPADDING", (0,0), (-1,-1), 1.5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    elementos.append(rejilla)
    elementos.append(Spacer(1, 5))
    elementos.append(Paragraph(
        "Consulte disponibilidad y precio actualizado al momento de la compra.",
        subtitulo
    ))
    doc.build(elementos)
    return buffer.getvalue()


# ------------------------- ESTILO ----------------------------

st.markdown("""
<style>
/* ===== GUELMAR UI V4 ===== */
.stApp {
    background: linear-gradient(135deg, #f6f7f9 0%, #ffffff 52%, #eef1f5 100%);
}
/* ===== BARRA LATERAL: CLARA, PROFESIONAL Y DE ALTO CONTRASTE ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%) !important;
    border-right: 1px solid #d8e2ef !important;
}
[data-testid="stSidebar"] * {
    color: #102a56 !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #102a56 !important;
    border-radius: 10px;
    padding: 7px 9px;
    margin: 2px 0;
    font-weight: 650;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #e0efff !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #d7eaff !important;
    color: #0b4fa3 !important;
    box-shadow: inset 3px 0 0 #1769d1;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * {
    color: #0b4fa3 !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #526a87 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #d5e0ec !important;
}

/* ===== CABECERA / LOGO PRINCIPAL: FONDO CLARO PARA NO OSCURECER EL LOGO ===== */
.guelmar-header {
    padding: 22px 26px;
    border-radius: 18px;
    background: linear-gradient(135deg, #f7fbff 0%, #eaf3fc 58%, #dceafa 100%) !important;
    color: #102a56 !important;
    border: 1px solid #c9d9ea;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(15,23,42,.09);
}
.guelmar-header h1 { color:#102a56 !important; }
.guelmar-header p { color:#415a78 !important; opacity:1 !important; font-weight:600; }
.section-title {
    font-size: 23px;
    font-weight: 850;
    color: #1f2937;
    margin: 8px 0 12px;
}
.metric-card {
    background: rgba(255,255,255,.96);
    border: 1px solid #e7ebf0;
    border-radius: 16px;
    padding: 18px;
    min-height: 116px;
    box-shadow: 0 5px 18px rgba(15,23,42,.055);
}
.metric-title { color:#667085; font-size:13px; font-weight:700; }
.metric-value { color:#171b24; font-size:27px; font-weight:850; margin-top:7px; }
.metric-note { color:#8a93a1; font-size:12px; margin-top:4px; }
.login-card {
    max-width: 560px;
    margin: 6vh auto 18px;
    padding: 40px 46px 30px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    box-shadow: 0 18px 55px rgba(20,25,35,.12);
    text-align: center;
}
.login-g {
    font-family: Arial, sans-serif;
    font-size:58px;
    line-height:1;
    font-weight:900;
    color:#d9573f;
}
.login-name {
    font-family: Arial, sans-serif;
    font-size:34px;
    line-height:1.1;
    font-weight:900;
    color:#20242e;
    letter-spacing:4px;
}
.login-tagline {
    font-size:13px;
    color:#687180;
    letter-spacing:1px;
    margin-top:10px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background:#fff !important;
    color:#20242e !important;
    -webkit-text-fill-color:#20242e !important;
    border:1px solid #cbd1d9 !important;
    border-radius:10px !important;
    min-height:46px !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color:#8a93a1 !important;
    -webkit-text-fill-color:#8a93a1 !important;
}
div[data-testid="stTextInput"] label p,
div[data-testid="stNumberInput"] label p {
    color:#27303d !important;
    font-weight:700 !important;
}
.stButton > button,
div[data-testid="stFormSubmitButton"] button {
    border-radius:10px !important;
    min-height:46px !important;
    font-weight:800 !important;
    border:0 !important;
}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 18px rgba(15,23,42,.10);
}
[data-testid="stDataFrame"] {
    border-radius:12px;
    overflow:hidden;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { font-weight:700; }
.small-muted { color:#7c8592; font-size:12px; }
.warning-box {
    padding:13px 16px; border-radius:12px;
    background:#fff7ed; border:1px solid #fed7aa; color:#9a3412;
}
.success-box {
    padding:13px 16px; border-radius:12px;
    background:#f0fdf4; border:1px solid #bbf7d0; color:#166534;
}
@media print {
    [data-testid="stSidebar"], header, footer { display:none !important; }
}
</style>
""", unsafe_allow_html=True)



# ===== V13: GUARDIA FINAL DE CONTRASTE =====
st.html("""
<style>
:root { color-scheme:light !important; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stHeader"] { background:#f4f7fb !important; color:#172033 !important; }
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMain"] [data-testid="stExpander"], [data-testid="stMain"] [data-testid="stForm"], [data-testid="stMain"] [data-testid="stDataFrame"], [data-testid="stMain"] [data-testid="stTable"] { background:#ffffff !important; color:#172033 !important; }
[data-testid="stMain"] [data-baseweb="input"], [data-testid="stMain"] [data-baseweb="select"], [data-testid="stMain"] [data-baseweb="textarea"], [data-testid="stMain"] input, [data-testid="stMain"] textarea { background:#ffffff !important; color:#172033 !important; -webkit-text-fill-color:#172033 !important; color-scheme:light !important; }
[data-testid="stMain"] [data-baseweb="popover"], [data-testid="stMain"] [data-baseweb="menu"], [data-testid="stMain"] [role="listbox"], [data-testid="stMain"] [role="option"] { background:#ffffff !important; color:#172033 !important; }
[data-testid="stMain"] [role="option"] * { color:#172033 !important; }
[data-testid="stMain"] button:not([kind="primary"]) { background:#eaf3ff !important; color:#173b68 !important; -webkit-text-fill-color:#173b68 !important; border:1px solid #bfd7f2 !important; }
[data-testid="stMain"] .stTabs [data-baseweb="tab"] { color:#243b5a !important; opacity:1 !important; }
[data-testid="stMain"] .stTabs [aria-selected="true"] { color:#0b5ed7 !important; }
</style>
""")


# ---------------------- BASE DE DATOS ------------------------

# La conexión Cloud get_conn() está definida arriba y usa PostgreSQL/Supabase.


def hash_password(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 120_000
    )
    return f"pbkdf2_sha256$120000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        if stored.startswith("pbkdf2_sha256$"):
            _, rounds, salt_hex, digest_hex = stored.split("$", 3)
            test = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(rounds),
            ).hex()
            return secrets.compare_digest(test, digest_hex)
        return secrets.compare_digest(password, stored)
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def init_db():
    """Comprueba la conexión al PostgreSQL central. No toca guelmar.db."""
    conn = get_conn()
    try:
        # Las tablas se crean mediante el SQL de Supabase preparado para GUELMAR.
        conn.execute("SELECT 1")
        conn.commit()

        # Primer arranque: crea los usuarios históricos si todavía no existen.
        if conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            branch = conn.execute(
                "SELECT id FROM sucursales WHERE activa=TRUE ORDER BY id LIMIT 1"
            ).fetchone()
            branch_id = branch["id"] if branch else None
            now = datetime.now()
            conn.execute(
                """INSERT INTO usuarios
                   (usuario,password,rol,activo,sucursal_id,creado_en)
                   VALUES(?,?,?,?,?,?)""",
                ("admin", hash_password("1234"), "Administrador", True, branch_id, now)
            )
            conn.execute(
                """INSERT INTO usuarios
                   (usuario,password,rol,activo,sucursal_id,creado_en)
                   VALUES(?,?,?,?,?,?)""",
                ("cajero", hash_password("1234"), "Vendedor", True, branch_id, now)
            )

        if conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0:
            conn.execute(
                """INSERT INTO clientes
                   (nit_ci,nombre,telefono,direccion,tipo,creado_en)
                   VALUES(?,?,?,?,?,?)""",
                ("0", "Cliente General", "", "", "Particular", datetime.now())
            )

        conn.commit()
    finally:
        conn.close()


@st.cache_resource(show_spinner=False)
def init_fiscal_db():
    """En GUELMAR CLOUD la estructura fiscal se crea desde Supabase SQL."""
    conn = get_conn()
    try:
        conn.execute("SELECT 1 FROM configuracion_fiscal LIMIT 1")
        conn.commit()
    finally:
        conn.close()


try:
    init_db()
    init_fiscal_db()
except Exception as _startup_error:
    st.error("No se pudo conectar con la base central de GUELMAR.")
    st.code(str(_startup_error))
    st.info("Primero configuraremos la conexión segura con Supabase. Tu guelmar.db local no se modifica.")
    st.stop()

# ---------------------- UTILIDADES ----------------------------

@st.cache_data(ttl=30, show_spinner=False)
def query_df(sql, params=()):
    """Consultas de solo lectura cacheadas brevemente para acelerar los reruns de Streamlit."""
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        columns = [d.name for d in cur._cur.description] if cur._cur.description else []
        return pd.DataFrame([dict(r) for r in rows], columns=columns)
    finally:
        conn.close()


@st.cache_data(ttl=15, show_spinner=False)
def scalar(sql, params=()):
    """Valores de solo lectura cacheados brevemente para reducir viajes a Supabase."""
    conn = get_conn()
    try:
        row = conn.execute(sql, params).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


CENTAVOS = Decimal("0.01")

def dec_money(value):
    try:
        return Decimal(str(value or 0)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")

def money(value):
    return f"Bs {dec_money(value):,.2f}"

def money_float(value):
    return float(dec_money(value))


def get_product(product_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM productos WHERE id=? AND activo=TRUE", (product_id,)
    ).fetchone()
    conn.close()
    return row


def registrar_movimiento(conn, producto_id, tipo, cantidad, anterior, nuevo, motivo, usuario_id, sucursal_id=None):
    sucursal_id = sucursal_id or st.session_state.get("sucursal_id") or st.session_state.get("usuario", {}).get("sucursal_id")
    conn.execute(
        """INSERT INTO movimientos_inventario
        (fecha,producto_id,tipo,cantidad,stock_anterior,stock_nuevo,motivo,usuario_id,sucursal_id)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            datetime.now(),
            producto_id, tipo, cantidad, anterior, nuevo, motivo, usuario_id, sucursal_id
        )
    )


# ---------------- SEGURIDAD E INTEGRIDAD V14 ------------------
def verificar_integridad_db(db_path=None):
    """Verifica la estructura mínima de la base central PostgreSQL/Supabase.

    db_path se conserva por compatibilidad con llamadas antiguas, pero se ignora:
    GUELMAR CLOUD nunca abre ni modifica guelmar.db.
    """
    conn = get_conn()
    esenciales = {
        "sucursales", "usuarios", "clientes", "productos", "ventas",
        "detalle_ventas", "movimientos_inventario", "cotizaciones",
        "detalle_cotizaciones", "configuracion_fiscal", "facturas",
        "detalle_facturas", "eventos_facturacion", "sincronizacion_sin",
    }
    try:
        filas = conn.execute(
            """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema='public'
                 AND table_type='BASE TABLE'"""
        ).fetchall()
        tablas = {r["table_name"] for r in filas}
        faltantes = sorted(esenciales - tablas)
        if faltantes:
            return {
                "ok": False,
                "integrity": "Faltan tablas en la base central.",
                "foreign_keys": [],
                "quick": "",
                "faltantes": faltantes,
            }

        # Consulta sencilla de cada tabla esencial para comprobar acceso.
        for tabla in sorted(esenciales):
            conn.execute(f"SELECT 1 FROM {tabla} LIMIT 1").fetchone()

        return {
            "ok": True,
            "integrity": "PostgreSQL/Supabase respondió correctamente.",
            "foreign_keys": [],
            "quick": "Estructura esencial verificada.",
            "faltantes": [],
        }
    except Exception as exc:
        return {
            "ok": False,
            "integrity": str(exc),
            "foreign_keys": [],
            "quick": "",
            "faltantes": [],
        }
    finally:
        conn.close()


def reiniciar_datos_prueba_sin_backup():
    """Reinicia datos transaccionales en la base CENTRAL.

    Conserva productos, usuarios, sucursales y configuración fiscal.
    Pone el stock central en 0 y elimina ventas, cotizaciones, clientes
    y registros de facturación de prueba.

    Esta acción afecta al inventario central compartido por las sucursales
    y está protegida por el rol Administrador en la interfaz.
    """
    conn = get_conn()
    tablas_transaccionales = [
        "detalle_facturas",
        "eventos_facturacion",
        "sincronizacion_sin",
        "facturas",
        "detalle_cotizaciones",
        "cotizaciones",
        "detalle_ventas",
        "ventas",
        "movimientos_inventario",
        "clientes",
    ]
    try:
        conn.execute("BEGIN")

        # Se eliminan primero las tablas hijas para respetar las FK.
        for tabla in tablas_transaccionales:
            conn.execute(f"DELETE FROM {tabla}")

        # Los productos registrados se conservan; solo se reinicia su stock.
        conn.execute("UPDATE productos SET stock=0")

        # Reiniciar numeración fiscal de prueba para todas las sucursales.
        conn.execute("UPDATE configuracion_fiscal SET numero_factura_actual=0")

        # Cliente técnico requerido por ventas/cotizaciones.
        conn.execute(
            """INSERT INTO clientes
               (nit_ci,nombre,telefono,direccion,tipo,creado_en)
               VALUES(?,?,?,?,?,?)""",
            ("0", "Cliente General", "", "", "Particular", datetime.now())
        )

        conn.commit()
        # Invalidar lecturas cacheadas tras cualquier escritura.
        st.cache_data.clear()

        # Las copias de seguridad de la base central corresponden a Supabase;
        # no se manipulan archivos .db locales.
        return True, (
            "Reinicio completado en la base central. Se conservaron todos los "
            "productos y sus datos; el stock quedó en 0. Se eliminaron los "
            "datos de pruebas, clientes, ventas, cotizaciones y movimientos. "
            "El Cliente General quedó como cliente técnico."
        )
    except Exception as exc:
        conn.rollback()
        return False, f"No se pudo completar el reinicio: {exc}"
    finally:
        conn.close()


# ------------------------- LOGIN ------------------------------

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "carrito" not in st.session_state:
    st.session_state.carrito = []

if "cliente_pos" not in st.session_state:
    st.session_state.cliente_pos = 1

if st.session_state.usuario is None:

    st.markdown("""
    <style>
    .login-card {
        max-width: 560px;
        margin: 6vh auto 18px auto;
        padding: 40px 46px 30px 46px;
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 24px !important;
        box-shadow: 0 18px 55px rgba(20,25,35,.12) !important;
        text-align: center;
    }
    .login-g {
        font-family: Arial, sans-serif !important;
        font-size: 58px !important;
        line-height: 1 !important;
        font-weight: 900 !important;
        color: #d9573f !important;
        margin: 0 0 5px 0 !important;
    }
    .login-name {
        font-family: Arial, sans-serif !important;
        font-size: 34px !important;
        line-height: 1.1 !important;
        font-weight: 900 !important;
        color: #20242e !important;
        letter-spacing: 4px !important;
        margin: 0 !important;
    }
    .login-tagline {
        font-family: Arial, sans-serif !important;
        font-size: 13px !important;
        color: #687180 !important;
        letter-spacing: 1px !important;
        margin-top: 10px !important;
    }

    div[data-testid="stTextInput"] {
        max-width: 560px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextInput"] label p {
        color: #20242e !important;
        font-weight: 700 !important;
        text-align: left !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #20242e !important;
        -webkit-text-fill-color: #20242e !important;
        border: 1px solid #c9ced6 !important;
        border-radius: 10px !important;
        min-height: 50px !important;
        color-scheme: light !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #8a93a1 !important;
        -webkit-text-fill-color: #8a93a1 !important;
    }
    div[data-testid="stFormSubmitButton"] {
        max-width: 560px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        background: #d9573f !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 50px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }
    .login-note {
        max-width: 560px;
        margin: 15px auto;
        text-align: center;
        color: #7b8491 !important;
        font-size: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="login-card" style="text-align:center;">
            <img src="{logo_data_uri()}"
                 style="width:360px;max-width:90%;height:auto;display:block;margin:0 auto 8px auto;">
            <div class="login-tagline">SISTEMA INTEGRAL DE GESTIÓN COMERCIAL</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("login_form_v3", clear_on_submit=False):
        usuario = st.text_input(
            "Usuario",
            placeholder="Escribe tu usuario",
            key="login_usuario_v3"
        )
        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Escribe tu contraseña",
            key="login_password_v3"
        )
        entrar = st.form_submit_button(
            "🔐 INGRESAR AL SISTEMA",
            width="stretch"
        )

        if entrar:
            conn = get_conn()
            row = conn.execute(
                "SELECT * FROM usuarios WHERE LOWER(TRIM(usuario))=LOWER(TRIM(?)) AND activo=TRUE",
                (usuario.strip(),)
            ).fetchone()
            conn.close()

            if row and verify_password(password, row["password"]):
                st.session_state.usuario = dict(row)
                st.session_state.sucursal_id = row["sucursal_id"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    st.markdown(
        '<div class="login-note">Ingresa con las credenciales configuradas para tu sistema.</div>',
        unsafe_allow_html=True
    )
    st.stop()


user = st.session_state.usuario
sucursal_id_usuario = user.get("sucursal_id")
if sucursal_id_usuario is None:
    conn = get_conn()
    try:
        b = conn.execute("SELECT id FROM sucursales WHERE activa=TRUE ORDER BY id LIMIT 1").fetchone()
        sucursal_id_usuario = b["id"] if b else None
        if sucursal_id_usuario is not None:
            conn.execute("UPDATE usuarios SET sucursal_id=? WHERE id=?", (sucursal_id_usuario, user["id"]))
            conn.commit()
            # Invalidar lecturas cacheadas tras cualquier escritura.
            st.cache_data.clear()
            user["sucursal_id"] = sucursal_id_usuario
            st.session_state.usuario = user
    finally:
        conn.close()

def sucursal_actual_id():
    return st.session_state.get("sucursal_id") or user.get("sucursal_id")

def nombre_sucursal(sid=None):
    sid = sid or sucursal_actual_id()
    if sid is None:
        return "Sin sucursal"
    conn = get_conn()
    try:
        row = conn.execute("SELECT nombre FROM sucursales WHERE id=?", (sid,)).fetchone()
        return row["nombre"] if row else "Sin sucursal"
    finally:
        conn.close()

# ------------------------- SIDEBAR ----------------------------

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-logo" style="text-align:center;padding:10px 8px 12px 8px;background:#ffffff;border:1px solid #dbe5f0;border-radius:16px;margin-bottom:8px;box-shadow:0 4px 14px rgba(15,23,42,.06);">
            <img src="{logo_data_uri()}"
                 style="width:190px;max-width:100%;height:auto;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption("Sistema Integral de Gestión Comercial")
    st.divider()

    st.markdown(f"**👤 {user['usuario']}**")
    st.caption(f"Rol: {user['rol']}")
    st.caption(f"🏢 Sucursal: {nombre_sucursal()}")
    st.divider()

    opciones = [
        "📊 Dashboard",
        "🛒 Punto de Venta",
        "📦 Productos",
        "📋 Inventario",
        "👥 Clientes",
        "💰 Ventas",
        "🧾 Cotizaciones",
        "🧾 Facturación",
    ]

    if user["rol"] == "Administrador":
        opciones += ["👤 Usuarios", "💾 Copias de seguridad"]

    pagina = st.radio("MENÚ", opciones)

    st.divider()

    if st.button("🚪 Cerrar sesión", width="stretch"):
        st.session_state.usuario = None
        st.session_state.carrito = []
        st.rerun()


# ------------------------- CABECERA ---------------------------

st.markdown(
    f"""
    <div class="guelmar-header" style="text-align:center;">
        <img src="{logo_data_uri()}"
             style="width:260px;max-width:70%;height:auto;margin-bottom:2px;">
    </div>
    """,
    unsafe_allow_html=True
)


# ========================= DASHBOARD ==========================

if pagina == "📊 Dashboard":
    st.markdown('<div class="section-title">📊 Resumen general</div>', unsafe_allow_html=True)

    hoy = date.today().strftime("%Y-%m-%d")

    # PostgreSQL: fecha es TIMESTAMP/TIMESTAMPTZ; no usar LIKE ni strftime.
    resumen = query_df("""
        SELECT
            (SELECT COALESCE(SUM(total),0) FROM ventas
             WHERE fecha::date = CURRENT_DATE AND estado='ACTIVA') AS ventas_hoy,
            (SELECT COALESCE(SUM(total),0) FROM ventas
             WHERE fecha >= date_trunc('month', CURRENT_DATE)
               AND fecha < date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
               AND estado='ACTIVA') AS ventas_mes,
            (SELECT COUNT(*) FROM productos WHERE activo=TRUE) AS productos,
            (SELECT COALESCE(SUM(stock),0) FROM productos WHERE activo=TRUE) AS stock_total,
            (SELECT COUNT(*) FROM productos
             WHERE activo=TRUE AND stock>0 AND stock<=stock_minimo) AS stock_bajo,
            (SELECT COUNT(*) FROM productos WHERE activo=TRUE AND stock<=0) AS agotados
    """)
    rsum = resumen.iloc[0]
    ventas_hoy = rsum['ventas_hoy']
    ventas_mes = rsum['ventas_mes']
    productos = rsum['productos']
    stock_total = rsum['stock_total']
    stock_bajo = rsum['stock_bajo']
    agotados = rsum['agotados']

    cols = st.columns(6)
    metrics = [
        ("Ventas de hoy", money(ventas_hoy), "Total activo"),
        ("Ventas del mes", money(ventas_mes), "Acumulado"),
        ("Productos", int(productos), "Catálogo activo"),
        ("Unidades", f"{stock_total:,.0f}", "Stock total"),
        ("Stock bajo", int(stock_bajo), "Requiere atención"),
        ("Agotados", int(agotados), "Sin existencia"),
    ]

    for col, (title, value, note) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-title">{title}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")

    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.subheader("📈 Ventas de los últimos 14 días")
        df = query_df("""
            SELECT fecha::date AS dia, COALESCE(SUM(total),0) AS total
            FROM ventas
            WHERE estado='ACTIVA' AND fecha >= CURRENT_DATE - INTERVAL '13 days'
            GROUP BY fecha::date
            ORDER BY dia
        """)
        if not df.empty:
            df["dia"] = pd.to_datetime(df["dia"])
            chart_df = df.copy()
            chart = (
                alt.Chart(chart_df)
                .mark_line(point=alt.OverlayMarkDef(filled=True, size=70), strokeWidth=3)
                .encode(
                    x=alt.X("dia:T", title="Fecha", axis=alt.Axis(labelColor="#172033", titleColor="#172033", gridColor="#e2e8f0")),
                    y=alt.Y("total:Q", title="Ventas (Bs)", axis=alt.Axis(labelColor="#172033", titleColor="#172033", gridColor="#e2e8f0")),
                    tooltip=[
                        alt.Tooltip("dia:T", title="Fecha", format="%d/%m/%Y"),
                        alt.Tooltip("total:Q", title="Ventas (Bs)", format=",.2f")
                    ]
                )
                .properties(background="#ffffff", height=330)
                .configure_view(stroke="#d5deea", fill="#ffffff")
                .configure_axis(domainColor="#b9c8da", tickColor="#b9c8da")
            )
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Todavía no hay ventas registradas.")

    with c2:
        st.subheader("⚠️ Productos con stock bajo")
        bajos = query_df("""
            SELECT codigo AS "Código", nombre AS "Producto", stock AS "Stock",
                   stock_minimo AS "Mínimo"
            FROM productos
            WHERE activo=TRUE AND stock<=stock_minimo
            ORDER BY stock ASC
            LIMIT 10
        """)
        if bajos.empty:
            st.success("No hay alertas de stock.")
        else:
            st.dataframe(bajos, width="stretch", hide_index=True)


# ========================= PRODUCTOS ==========================

elif pagina == "📦 Productos":
    st.markdown('<div class="section-title">📦 Catálogo de productos</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Productos", "➕ Nuevo producto", "📚 Catálogo para clientes", "✏️ Editar producto"])

    with tab1:
        buscar = st.text_input("🔎 Buscar por código, nombre, marca o categoría")
        df = query_df("""
            SELECT id, codigo AS "Código", nombre AS "Producto",
                   categoria AS "Categoría", marca AS "Marca",
                   precio AS "Precio", costo AS "Costo",
                   stock AS "Stock", stock_minimo AS "Mínimo", imagen
            FROM productos
            WHERE activo=TRUE
            ORDER BY nombre
        """)

        if buscar.strip() and not df.empty:
            q = buscar.lower()
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(q, na=False)
            ).any(axis=1)
            df = df[mask]

        st.dataframe(
            df.drop(columns=["id", "imagen"]) if not df.empty else df,
            width="stretch",
            hide_index=True
        )

        if not df.empty:
            st.subheader("🖼️ Vista de imágenes")
            cols = st.columns(4)
            for i, (_, r) in enumerate(df.iterrows()):
                with cols[i % 4]:
                    ruta = ruta_imagen_producto(str(r.get("imagen", "")))
                    if ruta:
                        st.image(str(ruta), width="stretch")
                    else:
                        st.markdown("<div style='height:140px;border:1px dashed #cbd5e1;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#64748b;'>Sin imagen</div>", unsafe_allow_html=True)
                    st.markdown(f"**{r['Producto']}**")
                    st.caption(f"{r['Código']} · {r['Marca']} · Bs {float(r['Precio']):,.2f}")

            st.subheader("🗑️ Desactivar producto")
            mapa = {f"{r['Código']} · {r['Producto']}": int(r["id"]) for _, r in df.iterrows()}
            elegido = st.selectbox("Producto", list(mapa.keys()))
            if user["rol"] == "Administrador":
                if st.button("Desactivar producto"):
                    conn = get_conn()
                    conn.execute("UPDATE productos SET activo=FALSE WHERE id=?", (mapa[elegido],))
                    conn.commit()
                    # Invalidar lecturas cacheadas tras cualquier escritura.
                    st.cache_data.clear()
                    conn.close()
                    st.success("Producto desactivado.")
                    st.rerun()

    with tab2:
        with st.form("nuevo_producto"):
            a, b = st.columns(2)
            codigo = a.text_input("Código *")
            nombre = b.text_input("Nombre del producto *")
            categoria = a.selectbox("Categoría", CATEGORIAS)
            marca = b.selectbox("Marca", MARCAS)
            precio = a.number_input("Precio de venta (Bs)", min_value=0.0, step=0.50)
            costo = b.number_input("Costo (Bs)", min_value=0.0, step=0.50)
            stock = a.number_input("Stock inicial", min_value=0.0, step=1.0)
            minimo = b.number_input("Stock mínimo", min_value=0.0, step=1.0, value=1.0)

            st.markdown("### 🖼️ Imagen del producto")
            imagen_subida = st.file_uploader(
                "Selecciona una imagen",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False,
                help="La imagen se guarda dentro de GUELMAR y se utilizará en el catálogo para clientes."
            )
            if imagen_subida is not None:
                st.image(imagen_subida, caption=imagen_subida.name, width=220)

            guardar = st.form_submit_button("💾 Guardar producto", width="stretch")

            if guardar:
                if not codigo.strip() or not nombre.strip():
                    st.error("Código y nombre son obligatorios.")
                else:
                    conn = get_conn()
                    imagen_relativa = ""
                    imagen_guardada = None
                    try:
                        cur = conn.execute(
                            """INSERT INTO productos
                            (codigo,nombre,categoria,marca,precio,costo,stock,stock_minimo,imagen,activo,creado_en)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                            (
                                codigo.strip(), nombre.strip(), categoria, marca,
                                precio, costo, stock, minimo, "", True,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                        )
                        producto_id = cur.lastrowid

                        if imagen_subida is not None:
                            imagen_relativa = guardar_imagen_producto(
                                imagen_subida, producto_id, codigo.strip()
                            )
                            imagen_guardada = BASE_DIR / imagen_relativa
                            conn.execute(
                                "UPDATE productos SET imagen=? WHERE id=?",
                                (imagen_relativa, producto_id)
                            )

                        if stock > 0:
                            registrar_movimiento(
                                conn, producto_id, "ENTRADA", stock, 0, stock,
                                "Stock inicial", user["id"]
                            )
                        conn.commit()
                        # Invalidar lecturas cacheadas tras cualquier escritura.
                        st.cache_data.clear()
                        st.success("Producto creado correctamente." + (" Imagen guardada." if imagen_relativa else ""))
                    except (psycopg2.IntegrityError,):
                        if imagen_guardada and imagen_guardada.exists():
                            imagen_guardada.unlink()
                        st.error("El código ya existe.")
                    except ValueError as e:
                        conn.rollback()
                        if imagen_guardada and imagen_guardada.exists():
                            imagen_guardada.unlink()
                        st.error(str(e))
                    except Exception as e:
                        conn.rollback()
                        if imagen_guardada and imagen_guardada.exists():
                            imagen_guardada.unlink()
                        st.error(f"No se pudo guardar el producto: {e}")
                    finally:
                        conn.close()

    with tab3:
        st.markdown("### 📚 Catálogo comercial para clientes")
        st.info(
            "El catálogo muestra productos activos con fotografía, nombre, código, "
            "marca, categoría y precio de venta. Puedes filtrar antes de exportarlo."
        )

        df_cat = query_df("""
            SELECT codigo AS "Código", nombre AS "Producto", categoria AS "Categoría",
                   marca AS "Marca", precio AS "Precio", imagen
            FROM productos
            WHERE activo=TRUE
            ORDER BY categoria, nombre
        """)

        if df_cat.empty:
            st.warning("Todavía no hay productos activos para generar el catálogo.")
        else:
            f1, f2, f3 = st.columns([1.2, 1.2, 1])
            with f1:
                buscar_cat = st.text_input("🔎 Buscar producto", key="catalogo_buscar")
            categorias_cat = ["Todas"] + sorted(df_cat["Categoría"].dropna().astype(str).unique().tolist())
            with f2:
                categoria_cat = st.selectbox("📂 Categoría", categorias_cat, key="catalogo_categoria")
            marcas_cat = ["Todas"] + sorted(df_cat["Marca"].dropna().astype(str).unique().tolist())
            with f3:
                marca_cat = st.selectbox("🏷️ Marca", marcas_cat, key="catalogo_marca")

            df_filtrado = df_cat.copy()
            if buscar_cat.strip():
                q = buscar_cat.strip().lower()
                mask = df_filtrado.astype(str).apply(
                    lambda col: col.str.lower().str.contains(q, na=False)
                ).any(axis=1)
                df_filtrado = df_filtrado[mask]
            if categoria_cat != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Categoría"].astype(str) == categoria_cat]
            if marca_cat != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Marca"].astype(str) == marca_cat]

            total_imagenes = int(
                df_filtrado["imagen"].fillna("").astype(str).str.strip().ne("").sum()
            )
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("📦 Productos", len(df_filtrado))
            with m2:
                st.metric("🖼️ Con imagen", total_imagenes)
            with m3:
                st.metric("📄 Formato PDF", "A4 · 3 por fila")

            if df_filtrado.empty:
                st.warning("No hay productos que coincidan con los filtros seleccionados.")
            else:
                pdf_catalogo = generar_pdf_catalogo_productos(df_filtrado)
                if pdf_catalogo is None:
                    st.warning(
                        "Para generar el catálogo PDF instala ReportLab en CMD: "
                        "pip install reportlab"
                    )
                else:
                    st.download_button(
                        "📄 EXPORTAR CATÁLOGO EN PDF",
                        data=pdf_catalogo,
                        file_name=f"catalogo_guelmar_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key="descargar_catalogo_pdf_v4",
                    )

                st.markdown("### 👀 Vista previa del catálogo")
                st.caption(
                    "La vista previa utiliza el mismo orden y los mismos datos que se enviarán al PDF."
                )
                vista_cols = st.columns(3, gap="medium")
                for i, (_, r) in enumerate(df_filtrado.iterrows()):
                    with vista_cols[i % 3]:
                        st.markdown(
                            "<div style='border:1px solid #d9dee7;border-radius:14px;"
                            "padding:12px;margin-bottom:18px;background:#ffffff;"
                            "box-shadow:0 2px 8px rgba(0,0,0,.06);'>",
                            unsafe_allow_html=True
                        )
                        ruta = ruta_imagen_producto(str(r.get("imagen", "")))
                        if ruta:
                            st.image(str(ruta), width="stretch")
                        else:
                            st.markdown(
                                "<div style='height:190px;border:1px dashed #cbd5e1;"
                                "border-radius:10px;display:flex;align-items:center;"
                                "justify-content:center;color:#64748b;'>Sin imagen</div>",
                                unsafe_allow_html=True
                            )
                        st.markdown(
                            f"<div style='font-size:17px;font-weight:800;margin-top:9px;"
                            f"color:#202734;'>{r['Producto']}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='font-size:12px;color:#667085;margin-top:4px;'>"
                            f"<b>Código:</b> {r['Código']}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='font-size:12px;color:#667085;'>"
                            f"<b>Marca:</b> {r['Marca']}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='font-size:12px;color:#667085;'>"
                            f"<b>Categoría:</b> {r['Categoría']}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='font-size:19px;font-weight:900;color:#d9573f;"
                            f"margin-top:7px;'>Bs {float(r['Precio']):,.2f}</div></div>",
                            unsafe_allow_html=True
                        )

                st.markdown(
                    """
                    <div style="margin-top:18px;padding:14px 16px;border-radius:12px;
                                background:#eaf3ff;color:#173b68;font-weight:700;border:1px solid #bfd7f2;">
                        🖨️ <b>Para imprimir:</b> exporta primero el catálogo a PDF y luego
                        selecciona <b>Imprimir</b> en el visor de PDF. Las fotografías quedan
                        incluidas en el documento.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



    with tab4:
        st.subheader("✏️ Editar producto")
        st.caption(
            "Modifica los datos del producto sin crear uno nuevo. "
            "El ID interno se conserva para mantener stock, ventas e historial."
        )

        if user["rol"] != "Administrador":
            st.info("🔒 Solo el Administrador puede editar productos.")
        else:
            df_edit = query_df("""
                SELECT id, codigo, nombre, categoria, marca,
                       precio, costo, stock, stock_minimo, imagen
                FROM productos
                WHERE activo=TRUE
                ORDER BY nombre
            """)

            if df_edit.empty:
                st.info("No hay productos activos para editar.")
            else:
                mapa_edit = {
                    f"{r.codigo} · {r.nombre} · stock {float(r.stock or 0):g}": int(r.id)
                    for r in df_edit.itertuples()
                }
                elegido_edit = st.selectbox(
                    "Selecciona el producto",
                    list(mapa_edit.keys()),
                    key="editar_producto_selector"
                )
                producto_edit = get_product(mapa_edit[elegido_edit])

                if producto_edit:
                    with st.form("form_editar_producto"):
                        e1, e2 = st.columns(2)
                        codigo_edit = e1.text_input(
                            "Código *",
                            value=str(producto_edit["codigo"] or ""),
                            key="editar_codigo"
                        )
                        nombre_edit = e2.text_input(
                            "Nombre del producto *",
                            value=str(producto_edit["nombre"] or ""),
                            key="editar_nombre"
                        )

                        categoria_actual = str(producto_edit["categoria"] or "")
                        categoria_edit = e1.selectbox(
                            "Categoría",
                            CATEGORIAS,
                            index=(CATEGORIAS.index(categoria_actual)
                                   if categoria_actual in CATEGORIAS else 0),
                            key="editar_categoria"
                        )
                        marca_actual = str(producto_edit["marca"] or "")
                        marca_edit = e2.selectbox(
                            "Marca",
                            MARCAS,
                            index=(MARCAS.index(marca_actual)
                                   if marca_actual in MARCAS else 0),
                            key="editar_marca"
                        )

                        precio_edit = e1.number_input(
                            "Precio de venta (Bs)",
                            min_value=0.0,
                            value=float(producto_edit["precio"] or 0),
                            step=0.50,
                            key="editar_precio"
                        )
                        costo_edit = e2.number_input(
                            "Costo de compra (Bs)",
                            min_value=0.0,
                            value=float(producto_edit["costo"] or 0),
                            step=0.50,
                            key="editar_costo"
                        )

                        st.markdown(
                            f"**Stock actual:** {float(producto_edit['stock'] or 0):g} unidades  "
                            "· Para cambiar existencias utiliza **Inventario → Movimiento → AJUSTE**."
                        )

                        minimo_edit = st.number_input(
                            "Stock mínimo",
                            min_value=0.0,
                            value=float(producto_edit["stock_minimo"] or 0),
                            step=1.0,
                            key="editar_minimo"
                        )

                        guardar_edicion = st.form_submit_button(
                            "💾 Guardar cambios",
                            width="stretch"
                        )

                    if guardar_edicion:
                        codigo_nuevo = codigo_edit.strip()
                        nombre_nuevo = nombre_edit.strip()

                        if not codigo_nuevo or not nombre_nuevo:
                            st.error("Código y nombre son obligatorios.")
                        else:
                            conn = get_conn()
                            try:
                                duplicado = conn.execute(
                                    "SELECT id FROM productos WHERE codigo=? AND id<>?",
                                    (codigo_nuevo, int(producto_edit["id"]))
                                ).fetchone()

                                if duplicado:
                                    st.error(
                                        f"El código '{codigo_nuevo}' ya pertenece a otro producto."
                                    )
                                else:
                                    conn.execute("BEGIN")

                                    cur_edit = conn.execute(
                                        """
                                        UPDATE productos
                                        SET codigo=?, nombre=?, categoria=?, marca=?,
                                            precio=?, costo=?, stock_minimo=?
                                        WHERE id=? AND activo=TRUE
                                        """,
                                        (
                                            codigo_nuevo, nombre_nuevo, categoria_edit, marca_edit,
                                            precio_edit, costo_edit, minimo_edit, int(producto_edit["id"])
                                        )
                                    )

                                    if cur_edit.rowcount != 1:
                                        raise RuntimeError("El producto ya no está disponible para editar.")

                                    # Sincronizar las copias de código/nombre guardadas en
                                    # ventas y cotizaciones para que búsquedas, detalles y
                                    # comprobantes existentes reflejen el nuevo dato.
                                    conn.execute(
                                        "UPDATE detalle_ventas SET codigo=?, nombre=? WHERE producto_id=?",
                                        (codigo_nuevo, nombre_nuevo, int(producto_edit["id"]))
                                    )
                                    conn.execute(
                                        "UPDATE detalle_cotizaciones SET codigo=?, nombre=? WHERE producto_id=?",
                                        (codigo_nuevo, nombre_nuevo, int(producto_edit["id"]))
                                    )
                                    # Preparación fiscal: si existieran detalles de facturas
                                    # para este producto, también se mantienen sincronizados.
                                    conn.execute(
                                        """
                                        UPDATE detalle_facturas
                                        SET codigo_producto=?, descripcion=?
                                        WHERE producto_id=?
                                        """,
                                        (codigo_nuevo, nombre_nuevo, int(producto_edit["id"]))
                                    )

                                    conn.commit()
                                    # Invalidar lecturas cacheadas tras cualquier escritura.
                                    st.cache_data.clear()

                                    # Sincronizar un carrito abierto para que el cambio se
                                    # vea inmediatamente y no se venda con datos antiguos.
                                    for key_carrito in ("carrito", "cot_carrito"):
                                        carrito = st.session_state.get(key_carrito)
                                        if isinstance(carrito, list):
                                            for item in carrito:
                                                if int(item.get("producto_id", -1)) == int(producto_edit["id"]):
                                                    item["codigo"] = codigo_nuevo
                                                    item["nombre"] = nombre_nuevo
                                                    item["precio"] = float(precio_edit)
                                                    if key_carrito == "carrito":
                                                        item["costo"] = float(costo_edit)
                                                    item["total"] = round(
                                                        float(item.get("cantidad", 0)) * float(precio_edit), 2
                                                    )

                                    st.success(
                                        f"Producto actualizado: {codigo_nuevo} · {nombre_nuevo}. "
                                        "El cambio se reflejará automáticamente en el sistema."
                                    )
                                    st.rerun()
                            except Exception as exc:
                                conn.rollback()
                                st.error(f"No se pudieron guardar los cambios: {exc}")
                            finally:
                                conn.close()

# ========================= INVENTARIO ==========================

elif pagina == "📋 Inventario":
    st.markdown('<div class="section-title">📋 Control de inventario</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📦 Existencias", "↕️ Movimiento"])

    with tab1:
        df = query_df("""
            SELECT codigo AS "Código", nombre AS "Producto", categoria AS "Categoría",
                   marca AS "Marca", stock AS "Stock", stock_minimo AS "Mínimo",
                   costo AS "Costo compra", precio AS "Costo venta"
            FROM productos
            WHERE activo=TRUE
            ORDER BY nombre
        """)

        if df.empty:
            st.info("No hay productos activos en el inventario.")
        else:
            df["Total compra"] = df["Stock"].astype(float) * df["Costo compra"].astype(float)
            df["Total venta"] = df["Stock"].astype(float) * df["Costo venta"].astype(float)

            total_unidades = float(df["Stock"].sum())
            total_compra = float(df["Total compra"].sum())
            total_venta = float(df["Total venta"].sum())
            margen_potencial = total_venta - total_compra

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("📦 Unidades en stock", f"{total_unidades:,.0f}")
            with m2:
                st.metric("💰 Total costo compra", f"Bs {total_compra:,.2f}")
            with m3:
                st.metric("🏷️ Total costo venta", f"Bs {total_venta:,.2f}")
            with m4:
                st.metric("📈 Margen potencial", f"Bs {margen_potencial:,.2f}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Stock": st.column_config.NumberColumn("Stock", format="%.0f"),
                    "Mínimo": st.column_config.NumberColumn("Mínimo", format="%.0f"),
                    "Costo compra": st.column_config.NumberColumn(
                        "Costo de compra", format="Bs %.2f"
                    ),
                    "Costo venta": st.column_config.NumberColumn(
                        "Costo de venta", format="Bs %.2f"
                    ),
                    "Total compra": st.column_config.NumberColumn(
                        "Total compra", format="Bs %.2f"
                    ),
                    "Total venta": st.column_config.NumberColumn(
                        "Total venta", format="Bs %.2f"
                    ),
                },
            )

            st.markdown(
                f"""
                <div style="margin-top:12px;padding:16px 18px;border-radius:14px;
                            background:linear-gradient(135deg,#1769d1 0%,#0b4fa3 100%) !important;
                            color:#ffffff !important;font-size:17px;font-weight:800;
                            border:1px solid #0b4fa3;box-shadow:0 4px 12px rgba(11,79,163,.18);">
                    <span style="color:#ffffff !important;">📦 TOTAL INVENTARIO</span>
                    <span style="float:right;color:#ffffff !important;">
                        Compra: Bs {total_compra:,.2f}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        Venta: Bs {total_venta:,.2f}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if user["rol"] == "Administrador":
                st.markdown("### 🖨️ Imprimir y generar PDF")
                st.markdown("**¿Qué productos deseas incluir en la exportación?**")
                filtro_exportacion = st.radio(
                    "Selecciona una opción",
                    [
                        "1. Incluir productos con 0 stock",
                        "2. Exportar solo productos con existencia",
                    ],
                    horizontal=True,
                    key="filtro_exportacion_inventario",
                    label_visibility="collapsed",
                )

                if filtro_exportacion.startswith("1."):
                    df_export = df.copy()
                    nombre_filtro = "completo"
                    st.caption(f"Se exportarán {len(df_export)} productos, incluyendo los que tienen 0 stock.")
                else:
                    df_export = df[df["Stock"].astype(float) > 0].copy()
                    nombre_filtro = "con_existencia"
                    st.caption(f"Se exportarán {len(df_export)} productos con existencia. Los productos con 0 stock quedarán fuera.")

                pdf = generar_pdf_inventario(df_export)
                c_pdf, c_print = st.columns(2)

                with c_pdf:
                    if pdf is None:
                        st.warning(
                            "Para generar PDF instala ReportLab. En CMD ejecuta: "
                            "pip install reportlab"
                        )
                    else:
                        st.download_button(
                            "📄 Generar PDF del inventario",
                            data=pdf,
                            file_name=f"inventario_guelmar_{nombre_filtro}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            width="stretch",
                        )

                with c_print:
                    st.markdown(
                        """
                        <button onclick="window.print()" style="
                            width:100%;height:46px;border:0;border-radius:10px;
                            background:#d9573f;color:white;font-size:16px;
                            font-weight:800;cursor:pointer;">
                            🖨️ Imprimir inventario
                        </button>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("🔒 El vendedor puede consultar el inventario, pero no puede generar PDF ni imprimirlo.")

    with tab2:
        if user["rol"] != "Administrador":
            st.info("🔒 Solo el Administrador puede registrar entradas, salidas o ajustes de inventario.\n\nPuedes consultar las existencias y el historial de movimientos.")
        else:
            dfp = query_df("SELECT id, codigo, nombre, stock FROM productos WHERE activo=TRUE ORDER BY nombre")
            if dfp.empty:
                st.info("Primero registra productos.")
            else:
                opciones = {f"{r.codigo} · {r.nombre} (stock: {r.stock:g})": int(r.id) for r in dfp.itertuples()}
                elegido = st.selectbox("Producto", list(opciones.keys()))
                tipo = st.selectbox("Tipo de movimiento", ["ENTRADA", "SALIDA", "AJUSTE"])
                if tipo == "AJUSTE":
                    st.caption("En AJUSTE, la cantidad representa el nuevo stock final.")
                cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0)
                motivo = st.text_input("Motivo")
                if st.button("💾 Registrar movimiento"):
                    producto = get_product(opciones[elegido])
                    if not producto:
                        st.error("Producto no encontrado.")
                    elif cantidad <= 0:
                        st.error("La cantidad debe ser mayor a cero.")
                    elif not motivo.strip():
                        st.error("Escribe un motivo para registrar el movimiento.")
                    else:
                        anterior = float(producto["stock"])
                        if tipo == "ENTRADA":
                            nuevo = anterior + cantidad
                        elif tipo == "SALIDA":
                            nuevo = anterior - cantidad
                            if nuevo < 0:
                                st.error("No hay stock suficiente.")
                                st.stop()
                        else:
                            nuevo = cantidad
                        conn = get_conn()
                        try:
                            conn.execute("BEGIN")
                            producto_bloqueado = conn.execute(
                                "SELECT stock FROM productos WHERE id=? FOR UPDATE",
                                (producto["id"],)
                            ).fetchone()
                            if not producto_bloqueado:
                                raise ValueError("El producto ya no existe.")
                            anterior = float(producto_bloqueado["stock"])
                            if tipo == "ENTRADA":
                                nuevo = anterior + cantidad
                            elif tipo == "SALIDA":
                                nuevo = anterior - cantidad
                                if nuevo < 0:
                                    raise ValueError("No hay stock suficiente.")
                            else:
                                nuevo = cantidad
                            conn.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo, producto["id"]))
                            registrar_movimiento(conn, producto["id"], tipo, cantidad, anterior, nuevo, motivo.strip(), user["id"])
                            conn.commit()
                            # Invalidar lecturas cacheadas tras cualquier escritura.
                            st.cache_data.clear()
                            st.success(f"Stock actualizado: {nuevo:g} unidades.")
                            st.rerun()
                        except Exception as exc:
                            conn.rollback()
                            st.error(f"No se pudo registrar el movimiento: {exc}")
                        finally:
                            conn.close()

    st.subheader("🕘 Historial de movimientos")
    hist = query_df("""
        SELECT m.fecha AS "Fecha", p.codigo AS "Código", p.nombre AS "Producto",
               m.tipo AS "Tipo",
               CASE WHEN m.tipo='AJUSTE' THEN (m.stock_nuevo - m.stock_anterior) ELSE m.cantidad END AS "Cantidad / Variación",
               m.stock_anterior AS "Anterior", m.stock_nuevo AS "Nuevo",
               m.motivo AS "Motivo"
        FROM movimientos_inventario m
        JOIN productos p ON p.id=m.producto_id
        ORDER BY m.id DESC
        LIMIT 200
    """)
    st.dataframe(hist, width="stretch", hide_index=True)


# =========================== CLIENTES ==========================

elif pagina == "👥 Clientes":
    st.markdown('<div class="section-title">👥 Clientes</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📋 Lista",
        "➕ Nuevo cliente",
        "✏️ Editar cliente"
    ])

    # ------------------------- LISTA -------------------------
    with tab1:
        buscar = st.text_input(
            "🔎 Buscar por NIT/CI, nombre, teléfono o dirección",
            key="buscar_cliente_v11"
        )

        df = query_df("""
            SELECT id,
                   nit_ci AS "NIT/CI",
                   nombre AS "Nombre",
                   telefono AS "Teléfono",
                   direccion AS "Dirección",
                   tipo AS "Tipo"
            FROM clientes
            ORDER BY nombre
        """)

        if buscar.strip() and not df.empty:
            q = buscar.lower().strip()
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(q, na=False)
            ).any(axis=1)
            df = df[mask]

        if df.empty:
            st.info("No hay clientes registrados.")
        else:
            st.dataframe(
                df.drop(columns=["id"]),
                width="stretch",
                hide_index=True
            )

    # ---------------------- NUEVO CLIENTE --------------------
    with tab2:
        st.subheader("➕ Registrar nuevo cliente")
        st.caption("Puedes registrar el NIT o Carnet de Identidad del cliente.")

        with st.form("nuevo_cliente_v11"):
            c1, c2 = st.columns(2)

            with c1:
                nit = st.text_input("NIT / Carnet de Identidad *")
                nombre = st.text_input("Nombre / Razón social *")
                telefono = st.text_input("Teléfono")

            with c2:
                direccion = st.text_input("Dirección")
                tipo = st.selectbox(
                    "Tipo de cliente",
                    ["Particular", "Empresa"]
                )

            guardar = st.form_submit_button(
                "💾 Guardar cliente",
                width="stretch"
            )

            if guardar:
                if not nit.strip() or not nombre.strip():
                    st.error("NIT/CI y nombre son obligatorios.")
                else:
                    conn = get_conn()
                    try:
                        conn.execute(
                            """INSERT INTO clientes
                            (nit_ci,nombre,telefono,direccion,tipo,creado_en)
                            VALUES(?,?,?,?,?,?)""",
                            (
                                nit.strip(),
                                nombre.strip(),
                                telefono.strip(),
                                direccion.strip(),
                                tipo,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                        )
                        conn.commit()
                        # Invalidar lecturas cacheadas tras cualquier escritura.
                        st.cache_data.clear()
                        st.success("✅ Cliente creado correctamente.")
                    except (psycopg2.IntegrityError,):
                        st.error("⚠️ Ese NIT/CI ya está registrado.")
                    finally:
                        conn.close()

    # ---------------------- EDITAR CLIENTE -------------------
    with tab3:
        st.subheader("✏️ Editar cliente")
        st.caption(
            "Puedes corregir el nombre, cambiar el NIT/CI y actualizar "
            "los demás datos. El ID interno del cliente se conserva."
        )

        clientes_edit = query_df("""
            SELECT id, nit_ci, nombre, telefono, direccion, tipo
            FROM clientes
            ORDER BY nombre
        """)

        if clientes_edit.empty:
            st.info("No hay clientes registrados para editar.")
        else:
            opciones_clientes = {
                f"{str(r.nit_ci).strip() or 'SIN NIT/CI'} · {r.nombre}": int(r.id)
                for r in clientes_edit.itertuples()
            }

            cliente_elegido = st.selectbox(
                "Selecciona el cliente que deseas editar",
                list(opciones_clientes.keys()),
                key="cliente_editar_sel_v11"
            )

            cliente_id = opciones_clientes[cliente_elegido]
            cliente_row = clientes_edit[
                clientes_edit["id"] == cliente_id
            ].iloc[0]

            with st.form("editar_cliente_v11"):
                e1, e2 = st.columns(2)

                with e1:
                    nuevo_nit = st.text_input(
                        "NIT / Carnet de Identidad *",
                        value=str(cliente_row["nit_ci"] or "")
                    )
                    nuevo_nombre = st.text_input(
                        "Nombre / Razón social *",
                        value=str(cliente_row["nombre"] or "")
                    )
                    nuevo_telefono = st.text_input(
                        "Teléfono",
                        value=str(cliente_row["telefono"] or "")
                    )

                with e2:
                    nueva_direccion = st.text_input(
                        "Dirección",
                        value=str(cliente_row["direccion"] or "")
                    )

                    tipos_cliente = ["Particular", "Empresa"]
                    tipo_actual = str(cliente_row["tipo"] or "Particular")
                    tipo_index = (
                        tipos_cliente.index(tipo_actual)
                        if tipo_actual in tipos_cliente else 0
                    )

                    nuevo_tipo = st.selectbox(
                        "Tipo de cliente",
                        tipos_cliente,
                        index=tipo_index
                    )

                actualizar = st.form_submit_button(
                    "💾 Guardar cambios",
                    width="stretch"
                )

                if actualizar:
                    if not nuevo_nit.strip() or not nuevo_nombre.strip():
                        st.error("NIT/CI y nombre son obligatorios.")
                    else:
                        conn = get_conn()
                        try:
                            conn.execute(
                                """UPDATE clientes
                                   SET nit_ci=?,
                                       nombre=?,
                                       telefono=?,
                                       direccion=?,
                                       tipo=?
                                 WHERE id=?""",
                                (
                                    nuevo_nit.strip(),
                                    nuevo_nombre.strip(),
                                    nuevo_telefono.strip(),
                                    nueva_direccion.strip(),
                                    nuevo_tipo,
                                    cliente_id
                                )
                            )
                            conn.commit()
                            # Invalidar lecturas cacheadas tras cualquier escritura.
                            st.cache_data.clear()
                            st.success("✅ Cliente actualizado correctamente.")
                            st.rerun()
                        except (psycopg2.IntegrityError,):
                            st.error(
                                "⚠️ Ese NIT/CI ya pertenece a otro cliente. "
                                "Verifica el número ingresado."
                            )
                        except Exception as exc:
                            conn.rollback()
                            st.error(f"No se pudo actualizar el cliente: {exc}")
                        finally:
                            conn.close()


# # ========================= PUNTO DE VENTA ======================

elif pagina == "🛒 Punto de Venta":
    # POS profesional: se rediseña únicamente la interfaz, manteniendo
    # la lógica existente de stock, descuentos, clientes, pagos, venta,
    # movimientos, tickets y anulaciones.
    st.markdown("""
    <style>
    /* ===== GUELMAR POS PROFESIONAL ===== */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background: linear-gradient(180deg,#17212b 0%,#0f1720 100%) !important;
        border-right: 1px solid #2b3948 !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebarContent"] * {
        color:#f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color:#f8fafc !important;
        background:transparent !important;
        border-radius:10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background:#263443 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background:linear-gradient(90deg,#f97316,#ea580c) !important;
        color:#ffffff !important;
        box-shadow:none !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * {
        color:#ffffff !important;
    }
    .pos-topbar {
        background:#ffffff;
        border:1px solid #dce3ec;
        border-radius:16px;
        padding:12px 16px;
        box-shadow:0 5px 18px rgba(15,23,42,.06);
        margin-bottom:14px;
    }
    .pos-brand {
        font-size:20px;
        font-weight:900;
        color:#162334 !important;
        line-height:1.05;
    }
    .pos-brand small {
        display:block;
        font-size:11px;
        color:#64748b !important;
        letter-spacing:.08em;
        margin-top:2px;
    }
    .pos-kicker {
        font-size:12px;
        color:#64748b !important;
        font-weight:700;
        text-transform:uppercase;
        letter-spacing:.05em;
    }
    .pos-panel {
        background:#ffffff;
        border:1px solid #dce3ec;
        border-radius:18px;
        padding:16px;
        box-shadow:0 7px 24px rgba(15,23,42,.06);
        margin-bottom:14px;
    }
    .pos-panel-title {
        font-size:18px;
        font-weight:900;
        color:#172033 !important;
        margin:0 0 3px 0;
    }
    .pos-panel-subtitle {
        font-size:12px;
        color:#64748b !important;
        margin-bottom:12px;
    }
    .pos-card {
        background:#ffffff;
        border:1px solid #e1e7ef;
        border-radius:15px;
        padding:8px;
        min-height:0;
        box-shadow:0 3px 12px rgba(15,23,42,.05);
        transition:.15s ease;
        margin-bottom:8px;
    }
    .pos-card [data-testid="stImage"] {
        margin:0 !important;
        padding:0 !important;
        line-height:0 !important;
    }
    .pos-card [data-testid="stImage"] img {
        display:block !important;
        width:100% !important;
        height:auto !important;
        object-fit:contain !important;
        margin:0 !important;
        padding:0 !important;
    }
    .pos-card:hover {
        border-color:#f97316;
        box-shadow:0 7px 18px rgba(249,115,22,.12);
    }
    .pos-card-name {
        color:#172033 !important;
        font-weight:850;
        font-size:13px;
        line-height:1.2;
        min-height:31px;
        margin-top:7px;
    }
    .pos-card-code {
        color:#64748b !important;
        font-size:11px;
        margin-top:2px;
    }
    .pos-card-price {
        color:#172033 !important;
        font-size:18px;
        font-weight:900;
        margin-top:7px;
    }
    .pos-stock-ok {
        display:inline-block;
        background:#dcfce7;
        color:#15803d !important;
        border-radius:7px;
        padding:3px 7px;
        font-size:11px;
        font-weight:800;
        margin-top:5px;
    }
    .pos-stock-low {
        display:inline-block;
        background:#fff3cd;
        color:#a16207 !important;
        border-radius:7px;
        padding:3px 7px;
        font-size:11px;
        font-weight:800;
        margin-top:5px;
    }
    .pos-stock-out {
        display:inline-block;
        background:#fee2e2;
        color:#b91c1c !important;
        border-radius:7px;
        padding:3px 7px;
        font-size:11px;
        font-weight:800;
        margin-top:5px;
    }
    .pos-cart {
        background:#ffffff;
        border:1px solid #dce3ec;
        border-radius:18px;
        padding:16px;
        box-shadow:0 7px 24px rgba(15,23,42,.07);
        position:sticky;
        top:12px;
    }
    .pos-cart-title {
        color:#e85d04 !important;
        font-size:19px;
        font-weight:900;
        border-bottom:2px solid #f97316;
        padding-bottom:9px;
        margin-bottom:12px;
    }
    .pos-item {
        border-bottom:1px solid #e8edf3;
        padding:9px 0;
    }
    .pos-item-name {
        color:#172033 !important;
        font-weight:850;
        font-size:12px;
    }
    .pos-item-code {
        color:#64748b !important;
        font-size:10px;
    }
    .pos-item-total {
        color:#172033 !important;
        font-weight:900;
        text-align:right;
    }
    .pos-total-box {
        background:#fff5eb;
        border:1px solid #fed7aa;
        border-radius:14px;
        padding:13px 15px;
        margin:10px 0;
    }
    .pos-total-label {
        color:#9a3412 !important;
        font-size:14px;
        font-weight:800;
    }
    .pos-total-value {
        color:#c2410c !important;
        font-size:26px;
        font-weight:950;
        text-align:right;
    }
    .pos-payment-title {
        color:#172033 !important;
        font-size:14px;
        font-weight:900;
        margin-top:8px;
        margin-bottom:6px;
    }
    .pos-success {
        background:#ecfdf3;
        border:1px solid #bbf7d0;
        color:#166534 !important;
        border-radius:14px;
        padding:12px 15px;
        font-weight:800;
        margin-bottom:12px;
    }
    .pos-shortcut {
        background:#f1f5f9;
        border:1px solid #e2e8f0;
        border-radius:7px;
        padding:2px 6px;
        color:#475569 !important;
        font-size:10px;
        font-weight:800;
    }
    /* Botón principal del POS */
    .pos-main-button + div button,
    .pos-confirm-slot + div button {
        min-height:48px !important;
        border-radius:12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Venta recién registrada: permite sacar el ticket sin buscarla nuevamente.
    if st.session_state.get("ultima_venta_id"):
        ultima = int(st.session_state["ultima_venta_id"])
        st.markdown(f'<div class="pos-success">✓ Venta #{ultima:06d} registrada correctamente.</div>', unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns([1,1,1])
        with tc1:
            ticket58 = generar_pdf_ticket(ultima, 58)
            if ticket58:
                st.download_button(
                    "🧾 Ticket 58 mm", data=ticket58,
                    file_name=f"ticket_guelmar_{ultima:06d}_58mm.pdf",
                    mime="application/pdf", width="stretch", key=f"ticket58_{ultima}"
                )
        with tc2:
            ticket80 = generar_pdf_ticket(ultima, 80)
            if ticket80:
                st.download_button(
                    "🧾 Ticket 80 mm", data=ticket80,
                    file_name=f"ticket_guelmar_{ultima:06d}_80mm.pdf",
                    mime="application/pdf", width="stretch", key=f"ticket80_{ultima}"
                )
        with tc3:
            if st.button("🆕 Nueva venta", width="stretch", key=f"nueva_venta_{ultima}"):
                st.session_state.pop("ultima_venta_id", None)
                st.rerun()

    dfp = query_df("""
        SELECT id, codigo, nombre, categoria, marca, precio, costo, stock, stock_minimo, imagen
        FROM productos
        WHERE activo=TRUE
        ORDER BY nombre
    """)

    if dfp.empty:
        st.warning("No hay productos registrados. Ve a 📦 Productos.")
    else:
        # Cabecera POS
        st.markdown("""
        <div class="pos-topbar">
            <div class="pos-kicker">GUELMAR · HERRAMIENTAS</div>
            <div class="pos-brand">Punto de Venta <small>VENTA RÁPIDA · CONTROL DE STOCK · COMPROBANTE</small></div>
        </div>
        """, unsafe_allow_html=True)

        izquierda, derecha = st.columns([1.72, 1.0], gap="large")

        with izquierda:
            st.markdown('<div class="pos-panel-title">Productos</div><div class="pos-panel-subtitle">Busca por código, nombre o marca y agrega directamente al carrito.</div>', unsafe_allow_html=True)
            s1, s2 = st.columns([2.5,1])
            with s1:
                buscar = st.text_input("Buscar", placeholder="🔎  Código, nombre o marca...", label_visibility="collapsed", key="pos_buscar_prof")
            with s2:
                categorias = ["Todas"] + sorted(dfp["categoria"].fillna("").astype(str).unique().tolist())
                categoria_sel = st.selectbox("Categoría", categorias, label_visibility="collapsed", key="pos_categoria_prof")

            filtrados = dfp.copy()
            if buscar.strip():
                q = buscar.lower().strip()
                mask = (
                    filtrados["codigo"].astype(str).str.lower().str.contains(q, na=False)
                    | filtrados["nombre"].astype(str).str.lower().str.contains(q, na=False)
                    | filtrados["marca"].astype(str).str.lower().str.contains(q, na=False)
                )
                filtrados = filtrados[mask]
            if categoria_sel != "Todas":
                filtrados = filtrados[filtrados["categoria"].astype(str) == categoria_sel]

            st.caption(f"Mostrando {len(filtrados)} producto(s)")

            if filtrados.empty:
                st.info("No se encontraron productos con esos criterios.")
            else:
                # Cuadrícula de 2 productos para aprovechar mejor el espacio del POS.
                filas = [filtrados.iloc[i:i+2] for i in range(0, len(filtrados), 2)]
                for fila in filas:
                    cols = st.columns(2, gap="small")
                    for col, (_, r) in zip(cols, fila.iterrows()):
                        with col:
                            stock = float(r["stock"] or 0)
                            minimo = float(r["stock_minimo"] or 1)
                            imagen = ruta_imagen_producto(str(r.get("imagen", "") or ""))
                            st.markdown('<div class="pos-card">', unsafe_allow_html=True)
                            if imagen and imagen.exists():
                                imagen_pos = preparar_imagen_pos_sin_espacios(imagen)
                                if imagen_pos is not None:
                                    st.image(imagen_pos, width="stretch")
                                else:
                                    st.markdown('<div style="height:150px;border:1px dashed #cbd5e1;border-radius:12px;display:flex;align-items:center;justify-content:center;background:#f8fafc;color:#64748b;font-size:12px;">Sin imagen</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height:150px;border:1px dashed #cbd5e1;border-radius:12px;display:flex;align-items:center;justify-content:center;background:#f8fafc;color:#64748b;font-size:12px;">Sin imagen</div>', unsafe_allow_html=True)
                            st.markdown(
                                f'<div class="pos-card-name">{str(r["nombre"])}</div>'
                                f'<div class="pos-card-code">{str(r["codigo"])} · {str(r["marca"])}</div>'
                                f'<div class="pos-card-price">{money(r["precio"])}</div>',
                                unsafe_allow_html=True
                            )
                            if stock <= 0:
                                st.markdown('<span class="pos-stock-out">Sin stock</span>', unsafe_allow_html=True)
                                st.button("Sin stock", disabled=True, width="stretch", key=f"pos_add_disabled_{int(r['id'])}")
                            elif stock <= minimo:
                                st.markdown(f'<span class="pos-stock-low">Stock: {stock:g}</span>', unsafe_allow_html=True)
                                if st.button("＋ Agregar", width="stretch", key=f"pos_add_{int(r['id'])}"):
                                    pid = int(r["id"])
                                    prod = r
                                    existente = next((x for x in st.session_state.carrito if x["producto_id"] == pid), None)
                                    cantidad_nueva = 1 + (existente["cantidad"] if existente else 0)
                                    if cantidad_nueva > float(prod["stock"]):
                                        st.error("La cantidad supera el stock disponible.")
                                    else:
                                        if existente:
                                            existente["cantidad"] = cantidad_nueva
                                            existente["total"] = money_float(dec_money(cantidad_nueva) * dec_money(existente["precio"]))
                                        else:
                                            st.session_state.carrito.append({
                                                "producto_id": pid, "codigo": prod["codigo"], "nombre": prod["nombre"],
                                                "cantidad": 1.0, "precio": money_float(prod["precio"]),
                                                "costo": money_float(prod["costo"]), "stock": float(prod["stock"] or 0), "total": money_float(dec_money(prod["precio"]))
                                            })
                                        st.rerun()
                            else:
                                st.markdown(f'<span class="pos-stock-ok">Stock: {stock:g}</span>', unsafe_allow_html=True)
                                if st.button("＋ Agregar", width="stretch", key=f"pos_add_{int(r['id'])}"):
                                    pid = int(r["id"])
                                    prod = r
                                    existente = next((x for x in st.session_state.carrito if x["producto_id"] == pid), None)
                                    cantidad_nueva = 1 + (existente["cantidad"] if existente else 0)
                                    if cantidad_nueva > float(prod["stock"]):
                                        st.error("La cantidad supera el stock disponible.")
                                    else:
                                        if existente:
                                            existente["cantidad"] = cantidad_nueva
                                            existente["total"] = money_float(dec_money(cantidad_nueva) * dec_money(existente["precio"]))
                                        else:
                                            st.session_state.carrito.append({
                                                "producto_id": pid, "codigo": prod["codigo"], "nombre": prod["nombre"],
                                                "cantidad": 1.0, "precio": money_float(prod["precio"]),
                                                "costo": money_float(prod["costo"]), "stock": float(prod["stock"] or 0), "total": money_float(dec_money(prod["precio"]))
                                            })
                                        st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

        with derecha:
            st.markdown('<div class="pos-cart"><div class="pos-cart-title">🛒 Venta actual</div>', unsafe_allow_html=True)

            clientes = query_df("SELECT id, nit_ci, nombre FROM clientes ORDER BY nombre")
            clientes_map = {f"{r.nit_ci} · {r.nombre}": int(r.id) for r in clientes.itertuples()}
            cliente_sel = st.selectbox("Cliente", list(clientes_map.keys()), key="pos_cliente_prof")

            if not st.session_state.carrito:
                st.info("El carrito está vacío. Agrega productos desde la izquierda.")
            else:
                for i, item in enumerate(st.session_state.carrito):
                    st.markdown(
                        f'<div class="pos-item"><div class="pos-item-name">{item["nombre"]}</div>'
                        f'<div class="pos-item-code">{item["codigo"]} · {money(item["precio"])} c/u</div></div>',
                        unsafe_allow_html=True
                    )
                    q1, q2, q3, q4 = st.columns([.8,1.1,.8,.55])
                    with q1:
                        if st.button("−", key=f"pos_minus_{i}"):
                            nueva = float(item["cantidad"]) - 1
                            if nueva <= 0:
                                st.session_state.carrito.pop(i)
                            else:
                                item["cantidad"] = nueva
                                item["total"] = money_float(dec_money(nueva) * dec_money(item["precio"]))
                            st.rerun()
                    with q2:
                        st.markdown(f'<div style="text-align:center;padding-top:7px;font-weight:900;color:#172033;">{item["cantidad"]:g}</div>', unsafe_allow_html=True)
                    with q3:
                        if st.button("+", key=f"pos_plus_{i}"):
                            nueva = float(item["cantidad"]) + 1
                            # La venta final vuelve a comprobar el stock en PostgreSQL.
                            stock_item = float(item.get("stock", 0) or 0)
                            if nueva > stock_item:
                                st.error("Stock insuficiente.")
                            else:
                                item["cantidad"] = nueva
                                item["total"] = money_float(dec_money(nueva) * dec_money(item["precio"]))
                                st.rerun()
                    with q4:
                        if st.button("🗑", key=f"pos_del_{i}"):
                            st.session_state.carrito.pop(i)
                            st.rerun()
                    st.markdown(f'<div class="pos-item-total">{money(item["total"])}</div>', unsafe_allow_html=True)

                subtotal = money_float(sum((dec_money(x["total"]) for x in st.session_state.carrito), Decimal("0.00")))
                descuento = st.number_input("Descuento (Bs)", min_value=0.0, max_value=float(subtotal), step=1.0, key="pos_descuento_prof")
                total = money_float(max(Decimal("0.00"), dec_money(subtotal) - dec_money(descuento)))

                st.markdown(
                    f'<div class="pos-total-box"><div class="pos-total-label">TOTAL A COBRAR</div>'
                    f'<div class="pos-total-value">{money(total)}</div></div>',
                    unsafe_allow_html=True
                )

                st.markdown('<div class="pos-payment-title">Forma de pago</div>', unsafe_allow_html=True)
                metodo = st.selectbox("Forma de pago", METODOS_PAGO, key="pos_metodo_prof", label_visibility="collapsed")

                recibido = total
                if metodo == "Efectivo":
                    recibido = st.number_input(
                        "Efectivo recibido (Bs)", min_value=0.0, value=float(total), step=1.0, key="pos_recibido_prof"
                    )
                    cambio = money_float(max(Decimal("0.00"), dec_money(recibido) - dec_money(total)))
                    if recibido < total:
                        st.warning(f"Faltan {money(total-recibido)}")
                    else:
                        st.success(f"Cambio: {money(cambio)}")
                else:
                    cambio = 0.0

                a1, a2 = st.columns(2)
                with a1:
                    if st.button("🗑 Vaciar carrito", width="stretch", key="vaciar_carrito_pos_prof"):
                        st.session_state.carrito = []
                        st.rerun()
                with a2:
                    vender = st.button("💳 REGISTRAR VENTA", width="stretch", type="primary", key="registrar_venta_pos_prof")

                if vender:
                    if metodo == "Efectivo" and recibido < total:
                        st.error("El efectivo recibido es insuficiente.")
                    else:
                        conn = get_conn()
                        try:
                            conn.execute("BEGIN")
                            cur = conn.execute(
                                """INSERT INTO ventas
                                (fecha,cliente_id,vendedor_id,sucursal_id,subtotal,descuento,total,metodo_pago,recibido,cambio,estado)
                                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                                (datetime.now(), clientes_map[cliente_sel], user["id"], sucursal_actual_id(),
                                 subtotal, descuento, total, metodo, recibido, cambio, "ACTIVA")
                            )
                            venta_id = cur.lastrowid
                            for item in st.session_state.carrito:
                                prod = conn.execute("SELECT * FROM productos WHERE id=? AND activo=TRUE FOR UPDATE", (item["producto_id"],)).fetchone()
                                if not prod:
                                    raise ValueError(f"Producto no encontrado: {item['codigo']}")
                                stock_anterior = float(prod["stock"])
                                cantidad_item = float(item["cantidad"])
                                if cantidad_item > stock_anterior:
                                    raise ValueError(f"Stock insuficiente para {prod['nombre']}.")
                                nuevo_stock = stock_anterior - cantidad_item
                                conn.execute(
                                    """INSERT INTO detalle_ventas
                                    (venta_id,producto_id,codigo,nombre,cantidad,precio_unitario,costo_unitario,total)
                                    VALUES(?,?,?,?,?,?,?,?)""",
                                    (venta_id, prod["id"], prod["codigo"], prod["nombre"], cantidad_item,
                                     money_float(item["precio"]), money_float(prod["costo"]), money_float(item["total"]))
                                )
                                conn.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo_stock, prod["id"]))
                                registrar_movimiento(conn, prod["id"], "VENTA", cantidad_item,
                                                     stock_anterior, nuevo_stock, f"Venta #{venta_id}", user["id"])
                            conn.commit()
                            # Invalidar lecturas cacheadas tras cualquier escritura.
                            st.cache_data.clear()
                            st.session_state.carrito = []
                            st.session_state.ultima_venta_id = int(venta_id)
                            st.rerun()
                        except Exception as exc:
                            conn.rollback()
                            st.error(f"No se pudo registrar la venta: {exc}")
                        finally:
                            conn.close()

            st.markdown('</div>', unsafe_allow_html=True)


# ============================ VENTAS ===========================

elif pagina == "💰 Ventas":
    st.markdown("""
    <style>
    .anulacion-card {
        border: 2px solid #e53935;
        border-bottom: 0;
        border-radius: 12px 12px 0 0;
        background: linear-gradient(90deg, #fff1f1 0%, #fffafa 100%);
        padding: 14px 18px 10px 18px;
        margin-top: 10px;
    }
    .anulacion-title {
        color: #c62828;
        font-size: 22px;
        font-weight: 800;
    }
    .anulacion-subtitle {
        color: #555;
        font-size: 14px;
        margin-top: 5px;
    }
    .anulacion-info {
        background: #fff0f0;
        border: 1px solid #ffcaca;
        border-radius: 10px;
        padding: 15px;
        color: #8f1d1d;
        line-height: 1.55;
        margin: 8px 0 10px 0;
    }
    .anulacion-divider {
        height: 1px;
        background: #f0c5c5;
        margin: 8px 0 12px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="section-title">💰 Historial de ventas</div>', unsafe_allow_html=True)
    st.caption("Consulta, búsqueda, reimpresión y anulación de ventas. Las anulaciones restauran automáticamente el stock.")

    # ---------------------- FILTROS ----------------------
    st.subheader("🔎 Filtros de búsqueda")
    f1, f2, f3, f4 = st.columns(4)
    fecha_desde = f1.date_input("Fecha desde", value=date.today(), key="ventas_desde")
    fecha_hasta = f2.date_input("Fecha hasta", value=date.today(), key="ventas_hasta")
    sucursal_sel = f3.selectbox("Sucursal", ["Todas", "El Alto"], key="ventas_sucursal")
    estado_sel = f4.selectbox("Estado", ["Todos", "ACTIVA", "ANULADA"], key="ventas_estado")

    f5, f6, f7, f8 = st.columns(4)
    cliente_buscar = f5.text_input("Cliente", placeholder="Nombre del cliente...", key="ventas_cliente")
    producto_buscar = f6.text_input("Producto", placeholder="Nombre o código...", key="ventas_producto")
    vendedor_sel = f7.selectbox("Vendedor", ["Todos"] + [str(x) for x in query_df("SELECT DISTINCT usuario FROM usuarios WHERE activo=TRUE ORDER BY usuario")["usuario"].tolist()], key="ventas_vendedor")
    pago_sel = f8.selectbox("Método de pago", ["Todos"] + METODOS_PAGO, key="ventas_pago")

    if fecha_hasta < fecha_desde:
        st.error("La fecha hasta no puede ser anterior a la fecha desde.")
        st.stop()

    where = ["v.fecha::date BETWEEN ? AND ?"]
    params = [fecha_desde.isoformat(), fecha_hasta.isoformat()]
    if sucursal_sel != "Todas":
        where.append("COALESCE(s.nombre,'El Alto') = ?")
        params.append(sucursal_sel)
    if estado_sel != "Todos":
        where.append("v.estado = ?")
        params.append(estado_sel)
    if vendedor_sel != "Todos":
        where.append("COALESCE(u.usuario,'') = ?")
        params.append(vendedor_sel)
    if pago_sel != "Todos":
        where.append("v.metodo_pago = ?")
        params.append(pago_sel)
    if cliente_buscar.strip():
        where.append("LOWER(COALESCE(c.nombre,'')) LIKE ?")
        params.append(f"%{cliente_buscar.strip().lower()}%")
    if producto_buscar.strip():
        where.append("EXISTS (SELECT 1 FROM detalle_ventas dvf WHERE dvf.venta_id=v.id AND (LOWER(dvf.nombre) LIKE ? OR LOWER(dvf.codigo) LIKE ?))")
        qprod = f"%{producto_buscar.strip().lower()}%"
        params.extend([qprod, qprod])

    where_sql = " AND ".join(where)
    df = query_df(f"""
        SELECT v.id AS "ID",
               v.fecha AS "Fecha",
               COALESCE(c.nombre,'Cliente General') AS "Cliente",
               COALESCE(u.usuario,'') AS "Vendedor",
               COALESCE(s.nombre,'El Alto') AS "Sucursal",
               (SELECT COUNT(*) FROM detalle_ventas dv0 WHERE dv0.venta_id=v.id) AS "Producto"s,
               v.subtotal AS "Subtotal",
               v.descuento AS "Descuento",
               v.total AS "Total",
               v.metodo_pago AS "Pago",
               v.estado AS "Estado"
        FROM ventas v
        LEFT JOIN clientes c ON c.id=v.cliente_id
        LEFT JOIN usuarios u ON u.id=v.vendedor_id
        WHERE {where_sql}
        ORDER BY v.id DESC
    """, tuple(params))

    # ---------------------- RESUMEN ----------------------
    activos = df[df["Estado"] == "ACTIVA"] if not df.empty else df
    total_ventas = float(activos["Total"].sum()) if not activos.empty else 0.0
    total_productos = float(activos["Productos"].sum()) if not activos.empty else 0.0
    total_efectivo = float(activos.loc[activos["Pago"] == "Efectivo", "Total"].sum()) if not activos.empty else 0.0
    total_descuentos = float(activos["Descuento"].sum()) if not activos.empty else 0.0
    tickets = int(len(activos))
    promedio = total_ventas / tickets if tickets else 0.0
    periodo_txt = "hoy" if fecha_desde == fecha_hasta == date.today() else "del período"

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(f"💰 Total ventas ({periodo_txt})", money(total_ventas))
    m2.metric("🛒 Productos vendidos", f"{total_productos:g}")
    m3.metric("💵 Efectivo", money(total_efectivo))
    m4.metric("🏷️ Descuentos", money(total_descuentos))
    m5.metric("🧾 Ticket promedio", money(promedio))

    # ---------------------- EXPORTACIÓN ----------------------
    ec1, ec2 = st.columns([1, 4])
    with ec1:
        csv_data = df.to_csv(index=False).encode("utf-8-sig") if not df.empty else "ID,Fecha,Cliente,Vendedor,Sucursal,Productos,Subtotal,Descuento,Total,Pago,Estado\n".encode("utf-8")
        st.download_button(
            "📊 Descargar CSV",
            data=csv_data,
            file_name=f"historial_ventas_{fecha_desde.isoformat()}_{fecha_hasta.isoformat()}.csv",
            mime="text/csv",
            width="stretch",
            key="descargar_historial_ventas_csv",
        )
    with ec2:
        if not df.empty:
            st.caption(f"{len(df)} venta(s) encontrada(s). Las métricas excluyen ventas anuladas.")
        else:
            st.caption("No se encontraron ventas con los filtros seleccionados.")

    # ---------------------- TABLA ----------------------
    st.subheader("📋 Ventas registradas")
    if df.empty:
        st.info("No hay ventas que coincidan con los filtros.")
    else:
        df_show = df.copy()
        df_show["Subtotal"] = df_show["Subtotal"].map(lambda x: money(x))
        df_show["Descuento"] = df_show["Descuento"].map(lambda x: money(x))
        df_show["Total"] = df_show["Total"].map(lambda x: money(x))
        st.dataframe(
            df_show,
            width="stretch",
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Productos": st.column_config.NumberColumn("Productos", width="small"),
                "Estado": st.column_config.TextColumn("Estado", width="small"),
            },
        )

        # ---------------------- ACCIONES ----------------------
        st.subheader("⚙️ Acciones sobre una venta")
        opciones = {
            f"#{int(r.ID):06d} · {r.Fecha} · {r.Cliente} · {money(r.Total)} · {r.Estado}": int(r.ID)
            for r in df.itertuples()
        }
        accion_sel = st.selectbox("Seleccione la venta", list(opciones.keys()), key="venta_accion")
        venta_accion_id = opciones[accion_sel]
        estado_actual = scalar("SELECT estado FROM ventas WHERE id=?", (venta_accion_id,))

        # Mantener el detalle después de cualquier interacción/rerun.
        if "venta_detalle_id" not in st.session_state:
            st.session_state.venta_detalle_id = None

        a1, a2, a3 = st.columns(3)
        with a1:
            if st.button("👁️ Ver detalle", width="stretch", key=f"ver_{venta_accion_id}"):
                st.session_state.venta_detalle_id = venta_accion_id
                st.rerun()
        with a2:
            p58 = generar_pdf_ticket(venta_accion_id, 58)
            if p58:
                st.download_button(
                    "🧾 Ticket 58 mm",
                    data=p58,
                    file_name=f"ticket_guelmar_{venta_accion_id:06d}_58mm.pdf",
                    mime="application/pdf",
                    width="stretch",
                    key=f"hist58_{venta_accion_id}",
                )
        with a3:
            p80 = generar_pdf_ticket(venta_accion_id, 80)
            if p80:
                st.download_button(
                    "🧾 Ticket 80 mm",
                    data=p80,
                    file_name=f"ticket_guelmar_{venta_accion_id:06d}_80mm.pdf",
                    mime="application/pdf",
                    width="stretch",
                    key=f"hist80_{venta_accion_id}",
                )

        if st.session_state.get("venta_detalle_id") == venta_accion_id:
            detalle = query_df("""
                SELECT codigo AS "Código", nombre AS "Producto",
                       cantidad AS "Cantidad", precio_unitario AS "Precio",
                       total AS "Total"
                FROM detalle_ventas
                WHERE venta_id=?
                ORDER BY id
            """, (venta_accion_id,))
            st.markdown(f"**Detalle de la venta #{venta_accion_id:06d}**")
            if not detalle.empty:
                detalle["Precio"] = detalle["Precio"].map(lambda x: money(x))
                detalle["Total"] = detalle["Total"].map(lambda x: money(x))
            st.dataframe(detalle, width="stretch", hide_index=True)

        
        # ====== DISEÑO VISUAL: ANULACIÓN DE VENTA — CLARO ======
        st.markdown("""
        <style>
        div[data-testid="stExpander"] { border:2px solid #dc2626 !important; border-radius:12px !important; background:#ffffff !important; color:#172033 !important; color-scheme:light !important; }
        div[data-testid="stExpander"] details, div[data-testid="stExpander"] details > div, div[data-testid="stExpander"] [data-testid="stExpanderDetails"] { background:#ffffff !important; color:#172033 !important; }
        div[data-testid="stExpander"] details > summary, div[data-testid="stExpander"] summary { background:#fff1f2 !important; color:#991b1b !important; font-weight:900 !important; font-size:17px !important; min-height:54px !important; padding:0 18px !important; border-bottom:1px solid #fecaca !important; opacity:1 !important; }
        div[data-testid="stExpander"] details > summary:hover, div[data-testid="stExpander"] summary:hover { background:#ffe4e6 !important; }
        div[data-testid="stExpander"] label, div[data-testid="stExpander"] p, div[data-testid="stExpander"] span, div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] { color:#172033 !important; opacity:1 !important; }
        div[data-testid="stExpander"] div[data-testid="stAlert"] { background:#eff6ff !important; border:1px solid #93c5fd !important; color:#1e3a8a !important; }
        div[data-testid="stExpander"] textarea, div[data-testid="stExpander"] textarea:focus { background:#ffffff !important; color:#172033 !important; -webkit-text-fill-color:#172033 !important; caret-color:#172033 !important; border:2px solid #cbd5e1 !important; border-radius:8px !important; color-scheme:light !important; }
        div[data-testid="stExpander"] textarea::placeholder { color:#64748b !important; opacity:1 !important; }
        div[data-testid="stExpander"] [data-baseweb="textarea"], div[data-testid="stExpander"] [data-baseweb="textarea"] > div { background:#ffffff !important; border-color:#cbd5e1 !important; }
        div[data-testid="stExpander"] div[data-testid="stCheckbox"] { background:#f8fafc !important; border:2px solid #cbd5e1 !important; border-radius:8px !important; padding:10px 12px !important; }
        div[data-testid="stExpander"] div[data-testid="stCheckbox"] label { color:#172033 !important; font-weight:700 !important; }
        div[data-testid="stExpander"] button[kind="primary"], div[data-testid="stExpander"] button[data-testid="baseButton-primary"] { background:#dc2626 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; border:2px solid #b91c1c !important; font-weight:900 !important; border-radius:9px !important; min-height:46px !important; }
        div[data-testid="stExpander"] button[kind="primary"]:disabled, div[data-testid="stExpander"] button[data-testid="baseButton-primary"]:disabled { background:#e2e8f0 !important; color:#475569 !important; -webkit-text-fill-color:#475569 !important; border-color:#cbd5e1 !important; opacity:1 !important; }
        </style>
        """, unsafe_allow_html=True)

# ===================== ANULACIÓN DE VENTA =====================
        # La anulación queda como una casilla desplegable independiente,
        # al mismo nivel visual que los tickets. Al abrirla aparecen las
        # medidas de seguridad, el motivo y la confirmación final.
        if user["rol"] == "Administrador" and estado_actual == "ACTIVA":
            st.markdown("---")
            with st.expander(
                "🗑️  ANULAR VENTA",
                expanded=False,
                key=f"exp_anular_{venta_accion_id}",
            ):
                st.markdown(
                    """
                    <div style="background:#fff7ed;color:#9a3412;border:1px solid #fdba74;border-radius:8px;padding:12px 14px;margin-bottom:14px;">
                        <b>⚠️ Atención:</b> esta acción devolverá automáticamente al inventario
                        las cantidades vendidas y la venta permanecerá registrada en el historial
                        como <b>ANULADA</b>.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("**Venta seleccionada**")
                total_venta = float(scalar(
                    "SELECT total FROM ventas WHERE id=?", (venta_accion_id,)
                ) or 0)
                st.markdown(
                    f"""
                    <div style="background:#eff6ff;color:#1e3a8a;border:1px solid #93c5fd;border-radius:8px;padding:12px 14px;margin-bottom:14px;">
                        Venta <b>#{venta_accion_id:06d}</b> · <b>{money(total_venta)}</b>
                        · Estado: <b>{estado_actual}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c_an1, c_an2 = st.columns([1.0, 1.35], gap="large")
                with c_an1:
                    st.markdown("**☑️ Confirmación de seguridad**")
                    confirmar_anul = st.checkbox(
                        "Confirmo que deseo anular esta venta y restaurar el stock",
                        key=f"confirm_anul_{venta_accion_id}",
                    )
                    st.caption(
                        "La anulación no se puede deshacer. El stock será restaurado "
                        "y la operación quedará registrada."
                    )

                with c_an2:
                    st.markdown("**📝 Motivo de anulación (obligatorio)**")
                    motivo_anulacion = st.text_area(
                        "Motivo",
                        placeholder="Ej.: Error en el registro, devolución del cliente, producto equivocado...",
                        key=f"motivo_anul_{venta_accion_id}",
                        height=105,
                        label_visibility="collapsed",
                    )

                if not motivo_anulacion.strip():
                    st.caption("El motivo es obligatorio para confirmar la anulación.")

                st.markdown("---")
                confirmar_click = st.button(
                    "🗑️ CONFIRMAR ANULACIÓN",
                    type="primary",
                    disabled=(not confirmar_anul or not motivo_anulacion.strip()),
                    width="stretch",
                    key=f"anular_{venta_accion_id}",
                )

                if confirmar_click:
                    conn = get_conn()
                    try:
                        conn.execute("BEGIN")
                        detalles = conn.execute(
                            "SELECT * FROM detalle_ventas WHERE venta_id=?",
                            (venta_accion_id,)
                        ).fetchall()

                        for item in detalles:
                            prod = conn.execute(
                                "SELECT * FROM productos WHERE id=?",
                                (item["producto_id"],)
                            ).fetchone()
                            if prod:
                                anterior = float(prod["stock"])
                                nuevo = anterior + float(item["cantidad"])
                                conn.execute(
                                    "UPDATE productos SET stock=? WHERE id=?",
                                    (nuevo, prod["id"])
                                )
                                registrar_movimiento(
                                    conn, prod["id"], "ANULACION", float(item["cantidad"]),
                                    anterior, nuevo,
                                    f"Anulación venta #{venta_accion_id} · {motivo_anulacion.strip()}",
                                    user["id"]
                                )

                        cur_anul = conn.execute(
                            "UPDATE ventas SET estado='ANULADA' WHERE id=? AND estado='ACTIVA'",
                            (venta_accion_id,)
                        )
                        if cur_anul.rowcount != 1:
                            raise ValueError("La venta ya no está activa o fue modificada por otro usuario.")

                        conn.commit()
                        # Invalidar lecturas cacheadas tras cualquier escritura.
                        st.cache_data.clear()
                        st.success(
                            f"Venta #{venta_accion_id:06d} anulada correctamente. "
                            "El stock fue restaurado y la operación quedó registrada."
                        )
                        st.rerun()
                    except Exception as exc:
                        conn.rollback()
                        st.error(f"No se pudo anular la venta: {exc}")
                    finally:
                        conn.close()

        elif estado_actual == "ANULADA":
            st.info("Esta venta ya está ANULADA. No se puede anular nuevamente.")

# ========================= COTIZACIONES =======================

elif pagina == "🧾 Cotizaciones":
    st.markdown('<div class="section-title">🧾 Cotizaciones</div>', unsafe_allow_html=True)

    if "cot_carrito" not in st.session_state:
        st.session_state.cot_carrito = []

    tab1, tab2 = st.tabs(["➕ Nueva cotización", "📋 Historial"])

    with tab1:
        dfp = query_df("""
            SELECT id, codigo, nombre, precio
            FROM productos WHERE activo=TRUE ORDER BY nombre
        """)
        if dfp.empty:
            st.info("No hay productos.")
        else:
            opciones = {
                f"{r.codigo} · {r.nombre} — {money(r.precio)}": int(r.id)
                for r in dfp.itertuples()
            }
            elegido = st.selectbox("Producto", list(opciones.keys()), key="cot_prod")
            cantidad = st.number_input("Cantidad", min_value=0.01, step=1.0, value=1.0, key="cot_qty")

            if st.button("➕ Agregar a cotización"):
                prod = get_product(opciones[elegido])
                st.session_state.cot_carrito.append({
                    "producto_id": prod["id"],
                    "codigo": prod["codigo"],
                    "nombre": prod["nombre"],
                    "cantidad": cantidad,
                    "precio": money_float(prod["precio"]),
                    "total": money_float(dec_money(cantidad) * dec_money(prod["precio"])),
                })
                st.rerun()

            if st.session_state.cot_carrito:
                st.dataframe(pd.DataFrame(st.session_state.cot_carrito), width="stretch", hide_index=True)

                clientes = query_df("SELECT id,nit_ci,nombre FROM clientes ORDER BY nombre")
                cmap = {f"{r.nit_ci} · {r.nombre}": int(r.id) for r in clientes.itertuples()}

                if not cmap:
                    st.warning("No hay clientes registrados. Ve a Clientes → Nuevo cliente para registrar uno.")
                    cliente = None
                else:
                    cliente = st.selectbox(
                        "Cliente",
                        list(cmap.keys()),
                        key="cot_cliente",
                        help="Selecciona el cliente de la cotización. También puedes editar sus datos con el botón de abajo."
                    )

                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✏️ Editar cliente", width="stretch", key="cot_editar_cliente"):
                            st.session_state["cot_mostrar_editar_cliente"] = not st.session_state.get("cot_mostrar_editar_cliente", False)
                    with ec2:
                        if st.button("➕ Nuevo cliente", width="stretch", key="cot_nuevo_cliente"):
                            st.session_state["cot_mostrar_nuevo_cliente"] = not st.session_state.get("cot_mostrar_nuevo_cliente", False)

                    if st.session_state.get("cot_mostrar_editar_cliente") and cliente:
                        cliente_id_edit = cmap[cliente]
                        conn = get_conn()
                        cliente_db = conn.execute(
                            "SELECT id, nit_ci, nombre FROM clientes WHERE id=?",
                            (cliente_id_edit,)
                        ).fetchone()
                        conn.close()

                        if cliente_db:
                            st.markdown("**Editar datos del cliente seleccionado**")
                            ce1, ce2 = st.columns(2)
                            with ce1:
                                nombre_cliente_edit = st.text_input(
                                    "Nombre del cliente",
                                    value=cliente_db["nombre"] or "",
                                    key=f"cot_nombre_cliente_{cliente_id_edit}"
                                )
                            with ce2:
                                nit_cliente_edit = st.text_input(
                                    "NIT / Carnet",
                                    value=cliente_db["nit_ci"] or "",
                                    key=f"cot_nit_cliente_{cliente_id_edit}"
                                )

                            if st.button("💾 Guardar cambios del cliente", width="stretch", key=f"cot_guardar_cliente_{cliente_id_edit}"):
                                nombre_cliente_edit = nombre_cliente_edit.strip()
                                nit_cliente_edit = nit_cliente_edit.strip()

                                if not nombre_cliente_edit:
                                    st.error("El nombre del cliente es obligatorio.")
                                elif not nit_cliente_edit:
                                    st.error("El NIT o Carnet es obligatorio.")
                                else:
                                    conn = get_conn()
                                    try:
                                        conn.execute(
                                            "UPDATE clientes SET nombre=?, nit_ci=?, direccion='' WHERE id=?",
                                            (nombre_cliente_edit, nit_cliente_edit, cliente_id_edit)
                                        )
                                        conn.commit()
                                        # Invalidar lecturas cacheadas tras cualquier escritura.
                                        st.cache_data.clear()
                                        st.success("Cliente actualizado correctamente.")
                                        st.session_state["cot_mostrar_editar_cliente"] = False
                                        st.rerun()
                                    except (psycopg2.IntegrityError,):
                                        conn.rollback()
                                        st.error("Ese NIT/Carnet ya está registrado para otro cliente.")
                                    except Exception as exc:
                                        conn.rollback()
                                        st.error(f"No se pudo actualizar el cliente: {exc}")
                                    finally:
                                        conn.close()

                    if st.session_state.get("cot_mostrar_nuevo_cliente"):
                        st.markdown("**Registrar nuevo cliente**")
                        cn1, cn2 = st.columns(2)
                        with cn1:
                            nombre_cliente_nuevo = st.text_input(
                                "Nombre del cliente",
                                key="cot_nuevo_nombre"
                            )
                        with cn2:
                            nit_cliente_nuevo = st.text_input(
                                "NIT / Carnet",
                                key="cot_nuevo_nit"
                            )

                        if st.button("💾 Registrar cliente", width="stretch", key="cot_registrar_cliente"):
                            nombre_cliente_nuevo = nombre_cliente_nuevo.strip()
                            nit_cliente_nuevo = nit_cliente_nuevo.strip()

                            if not nombre_cliente_nuevo:
                                st.error("El nombre del cliente es obligatorio.")
                            elif not nit_cliente_nuevo:
                                st.error("El NIT o Carnet es obligatorio.")
                            else:
                                conn = get_conn()
                                try:
                                    conn.execute(
                                        """INSERT INTO clientes
                                        (nit_ci, nombre, telefono, direccion, tipo, creado_en)
                                        VALUES (?, ?, '', '', 'Particular', ?)""",
                                        (nit_cliente_nuevo, nombre_cliente_nuevo, datetime.now().isoformat())
                                    )
                                    conn.commit()
                                    # Invalidar lecturas cacheadas tras cualquier escritura.
                                    st.cache_data.clear()
                                    st.success("Cliente registrado correctamente. Ahora aparecerá en la lista.")
                                    st.session_state["cot_mostrar_nuevo_cliente"] = False
                                    st.rerun()
                                except (psycopg2.IntegrityError,):
                                    conn.rollback()
                                    st.error("Ese NIT/Carnet ya está registrado.")
                                except Exception as exc:
                                    conn.rollback()
                                    st.error(f"No se pudo registrar el cliente: {exc}")
                                finally:
                                    conn.close()

                subtotal = money_float(sum((dec_money(x["total"]) for x in st.session_state.cot_carrito), Decimal("0.00")))
                # Las cotizaciones ya no manejan descuentos. Se conserva la columna
                # histórica en la base de datos por compatibilidad y se guarda siempre en 0.
                descuento = 0.0
                total = subtotal

                if st.button("💾 Guardar cotización"):
                    if not cliente:
                        st.error("Selecciona o registra un cliente antes de guardar la cotización.")
                        st.stop()

                    conn = get_conn()
                    try:
                        cur = conn.execute(
                            """INSERT INTO cotizaciones
                            (fecha,cliente_id,usuario_id,sucursal_id,subtotal,descuento,total,estado)
                            VALUES(?,?,?,?,?,?,?,?)""",
                            (
                                datetime.now(), cmap[cliente], user["id"], sucursal_actual_id(),
                                subtotal, descuento, total, "VIGENTE"
                            )
                        )
                        cot_id = cur.lastrowid
                        for item in st.session_state.cot_carrito:
                            conn.execute(
                                """INSERT INTO detalle_cotizaciones
                                (cotizacion_id,producto_id,codigo,nombre,cantidad,precio_unitario,total)
                                VALUES(?,?,?,?,?,?,?)""",
                                (
                                    cot_id, item["producto_id"], item["codigo"], item["nombre"],
                                    item["cantidad"], item["precio"], item["total"]
                                )
                            )
                        conn.commit()
                        # Invalidar lecturas cacheadas tras cualquier escritura.
                        st.cache_data.clear()
                        st.session_state.cot_carrito = []
                        st.session_state.ultima_cotizacion_id = int(cot_id)
                        st.success(f"Cotización #{cot_id} guardada.")
                    except Exception as exc:
                        conn.rollback()
                        st.error(f"No se pudo guardar la cotización: {exc}")
                    finally:
                        conn.close()

                ultima_cot_id = st.session_state.get("ultima_cotizacion_id")
                if ultima_cot_id:
                    pdf_cot = generar_pdf_cotizacion(ultima_cot_id)
                    if pdf_cot:
                        st.download_button(
                            "📄 Generar / descargar PDF para imprimir",
                            data=pdf_cot,
                            file_name=f"cotizacion_guelmar_{ultima_cot_id:06d}.pdf",
                            mime="application/pdf",
                            width="stretch",
                            key=f"pdf_cot_{ultima_cot_id}",
                        )
                    else:
                        st.error(
                            "No se pudo generar el PDF. Verifica que ReportLab esté instalado."
                        )

    with tab2:
        st.subheader("📋 Historial de cotizaciones")
        df = query_df("""
            SELECT q.id AS "ID", q.fecha AS "Fecha",
                   COALESCE(c.nombre,'Cliente General') AS "Cliente",
                   q.subtotal AS "Subtotal",
                   q.total AS "Total", q.estado AS "Estado"
            FROM cotizaciones q
            LEFT JOIN clientes c ON c.id=q.cliente_id
            ORDER BY q.id DESC
        """)

        if df.empty:
            st.info("Todavía no hay cotizaciones guardadas.")
        else:
            st.dataframe(df, width="stretch", hide_index=True)

            opciones_cot = {
                f"Cotización #{int(r.ID):06d} · {r.Cliente} · Bs {float(r.Total):,.2f} · {r.Fecha}": int(r.ID)
                for r in df.itertuples()
            }
            seleccion_cot = st.selectbox(
                "Seleccione una cotización para imprimir",
                list(opciones_cot.keys()),
                key="cot_historial_seleccion"
            )
            cot_hist_id = opciones_cot[seleccion_cot]

            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                if st.button("👁️ Ver detalle", width="stretch", key=f"ver_cot_{cot_hist_id}"):
                    detalle = query_df("""
                        SELECT codigo AS "Código", nombre AS "Producto",
                               cantidad AS "Cantidad", precio_unitario AS "Precio unitario",
                               total AS "Total"
                        FROM detalle_cotizaciones
                        WHERE cotizacion_id=?
                        ORDER BY id
                    """, (cot_hist_id,))
                    st.session_state.cot_detalle_id = cot_hist_id
                    st.session_state.cot_detalle_df = detalle

            with hc2:
                pdf_hist = generar_pdf_cotizacion(cot_hist_id)
                if pdf_hist:
                    st.download_button(
                        "🖨️ Generar / descargar PDF",
                        data=pdf_hist,
                        file_name=f"cotizacion_guelmar_{cot_hist_id:06d}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key=f"pdf_hist_cot_{cot_hist_id}",
                    )
                else:
                    st.error("No se pudo generar el PDF. Verifica que ReportLab esté instalado.")

            with hc3:
                eliminar_cot = st.checkbox(
                    "Confirmar eliminación",
                    key=f"confirmar_eliminar_cot_{cot_hist_id}"
                )
                if st.button("🗑️ Eliminar cotización", width="stretch", key=f"eliminar_cot_{cot_hist_id}", disabled=not eliminar_cot):
                    conn = get_conn()
                    try:
                        # Eliminamos primero el detalle y luego la cabecera para
                        # que la eliminación sea segura incluso si SQLite no
                        # tiene activado ON DELETE CASCADE.
                        conn.execute(
                            "DELETE FROM detalle_cotizaciones WHERE cotizacion_id=?",
                            (cot_hist_id,)
                        )
                        cur_del = conn.execute(
                            "DELETE FROM cotizaciones WHERE id=?",
                            (cot_hist_id,)
                        )
                        if cur_del.rowcount == 0:
                            raise RuntimeError("La cotización seleccionada ya no existe.")
                        conn.commit()
                        # Invalidar lecturas cacheadas tras cualquier escritura.
                        st.cache_data.clear()

                        if st.session_state.get("cot_detalle_id") == cot_hist_id:
                            st.session_state.pop("cot_detalle_id", None)
                            st.session_state.pop("cot_detalle_df", None)
                        if st.session_state.get("ultima_cotizacion_id") == cot_hist_id:
                            st.session_state.pop("ultima_cotizacion_id", None)

                        st.success(f"Cotización #{cot_hist_id:06d} eliminada correctamente.")
                        st.rerun()
                    except Exception as exc:
                        conn.rollback()
                        st.error(f"No se pudo eliminar la cotización: {exc}")
                    finally:
                        conn.close()

            if st.session_state.get("cot_detalle_id") == cot_hist_id:
                st.markdown("### 🔎 Detalle de la cotización")
                detalle = st.session_state.get("cot_detalle_df")
                if detalle is not None and not detalle.empty:
                    st.dataframe(detalle, width="stretch", hide_index=True)
                else:
                    st.info("Esta cotización no tiene productos registrados.")


# =========================== USUARIOS ==========================

elif pagina == "👤 Usuarios":
    if user["rol"] != "Administrador":
        st.error("No tienes permisos para esta sección.")
    else:
        st.markdown('<div class="section-title">👤 Usuarios</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["📋 Usuarios", "➕ Nuevo usuario"])

        with tab1:
            df = query_df("""
                SELECT u.id, u.usuario AS "Usuario", u.rol AS "Rol",
                       COALESCE(s.nombre,'Sin sucursal') AS "Sucursal",
                       CASE WHEN u.activo=TRUE THEN 'Activo' ELSE 'Inactivo' END AS "Estado",
                       u.creado_en AS "Creado"
                FROM usuarios u
                LEFT JOIN sucursales s ON s.id=u.sucursal_id
                ORDER BY u.usuario
            """)
            st.dataframe(df, width="stretch", hide_index=True)

        with tab2:
            with st.form("nuevo_usuario"):
                nuevo_usuario = st.text_input("Usuario *")
                nueva_password = st.text_input("Contraseña *", type="password")
                rol = st.selectbox("Rol", ["Vendedor", "Administrador"])
                ramas = query_df("SELECT id, nombre FROM sucursales WHERE activa=TRUE ORDER BY id")
                ramas_map = {r["nombre"]: int(r["id"]) for _, r in ramas.iterrows()}
                sucursal_nueva = st.selectbox("Sucursal", list(ramas_map.keys()))
                guardar = st.form_submit_button("💾 Crear usuario", width="stretch")

                if guardar:
                    if not nuevo_usuario.strip() or not nueva_password:
                        st.error("Completa usuario y contraseña.")
                    else:
                        conn = get_conn()
                        try:
                            conn.execute(
                                """INSERT INTO usuarios(usuario,password,rol,activo,sucursal_id,creado_en)
                                VALUES(?,?,?,?,?,?)""",
                                (
                                    nuevo_usuario.strip(), hash_password(nueva_password),
                                    rol, True, ramas_map[sucursal_nueva], datetime.now()
                                )
                            )
                            conn.commit()
                            # Invalidar lecturas cacheadas tras cualquier escritura.
                            st.cache_data.clear()
                            st.success("Usuario creado.")
                        except (psycopg2.IntegrityError,):
                            st.error("Ese usuario ya existe.")
                        finally:
                            conn.close()



# ======================== FACTURACIÓN ==========================
elif pagina == "🧾 Facturación":
    st.markdown('<div class="section-title">🧾 Preparación para Facturación Fiscal</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="warning-box">
            <b>Modo preparación fiscal</b><br>
            GUELMAR todavía NO envía facturas al SIN. Esta etapa organiza la información,
            estructura las facturas y prepara la base de datos para una futura integración
            autorizada.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Administrador puede trabajar la configuración fiscal de cualquiera de las sucursales.
    # Los demás usuarios solo pueden ver/configurar su propia sucursal.
    if user["rol"] == "Administrador":
        ramas_cfg = query_df("SELECT id, nombre FROM sucursales WHERE activa=TRUE ORDER BY id")
        ramas_map_cfg = {r["nombre"]: int(r["id"]) for _, r in ramas_cfg.iterrows()}
        nombres_cfg = list(ramas_map_cfg.keys())
        seleccion_cfg = st.selectbox("🏢 Sucursal a configurar", nombres_cfg,
                                      index=max(0, nombres_cfg.index(nombre_sucursal()) if nombre_sucursal() in nombres_cfg else 0))
        sucursal_fiscal_id = ramas_map_cfg[seleccion_cfg]
    else:
        sucursal_fiscal_id = sucursal_actual_id()
        st.info(f"Configuración fiscal de: **{nombre_sucursal(sucursal_fiscal_id)}**")

    cfg = query_df(
        "SELECT * FROM configuracion_fiscal WHERE sucursal_id=?",
        (sucursal_fiscal_id,)
    )
    cfg_row = cfg.iloc[0].to_dict() if not cfg.empty else {}

    tab_cfg, tab_fact, tab_prep = st.tabs([
        "🏢 Datos fiscales",
        "📋 Historial de facturas",
        "🛠️ Preparar factura"
    ])

    with tab_cfg:
        st.subheader("🏢 Datos del emisor")
        with st.form("config_fiscal"):
            c1, c2 = st.columns(2)
            with c1:
                razon_social = st.text_input("Razón social", value=cfg_row.get("razon_social", ""))
                nombre_comercial = st.text_input(
                    "Nombre comercial", value=cfg_row.get("nombre_comercial", "GUELMAR")
                )
                nit = st.text_input("NIT", value=cfg_row.get("nit", ""))
                actividad = st.text_input(
                    "Actividad económica", value=cfg_row.get("actividad_economica", "")
                )
                direccion = st.text_input("Dirección", value=cfg_row.get("direccion", ""))
                municipio = st.text_input("Municipio", value=cfg_row.get("municipio", ""))
            with c2:
                departamento = st.text_input(
                    "Departamento", value=cfg_row.get("departamento", "")
                )
                telefono = st.text_input("Teléfono", value=cfg_row.get("telefono", ""))
                correo = st.text_input("Correo", value=cfg_row.get("correo", ""))
                sucursal = st.text_input(
                    "Código de sucursal", value=str(cfg_row.get("codigo_sucursal", "0"))
                )
                punto_venta = st.text_input(
                    "Código de punto de venta", value=str(cfg_row.get("codigo_punto_venta", "0"))
                )
                modalidad = st.selectbox(
                    "Modalidad prevista",
                    ["Computarizada en Línea", "Electrónica en Línea"],
                    index=(
                        1 if cfg_row.get("modalidad") == "Electrónica en Línea" else 0
                    ),
                )
                ambiente = st.selectbox(
                    "Ambiente",
                    ["PILOTO", "PRODUCCION"],
                    index=1 if cfg_row.get("ambiente") == "PRODUCCION" else 0,
                )
            leyenda = st.text_input(
                "Leyenda", value=cfg_row.get("leyenda", "")
            )

            guardar_cfg = st.form_submit_button(
                "💾 Guardar configuración fiscal", width="stretch"
            )

            if guardar_cfg:
                conn = get_conn()
                conn.execute("""
                    UPDATE configuracion_fiscal
                    SET razon_social=?, nombre_comercial=?, nit=?, actividad_economica=?,
                        direccion=?, municipio=?, departamento=?, telefono=?, correo=?,
                        codigo_sucursal=?, codigo_punto_venta=?, modalidad=?,
                        ambiente=?, leyenda=?, actualizado_en=?
                    WHERE sucursal_id=?
                """, (
                    razon_social.strip(), nombre_comercial.strip(), nit.strip(),
                    actividad.strip(), direccion.strip(), municipio.strip(),
                    departamento.strip(), telefono.strip(), correo.strip(),
                    sucursal.strip() or "0", punto_venta.strip() or "0",
                    modalidad, ambiente, leyenda.strip(),
                    datetime.now(),
                    sucursal_fiscal_id
                ))
                conn.commit()
                # Invalidar lecturas cacheadas tras cualquier escritura.
                st.cache_data.clear()
                conn.close()
                st.success("Configuración fiscal guardada.")
                st.rerun()

        st.info(
            "Los campos CUF, CUFD, XML, código de recepción y envío al SIN "
            "quedan reservados para la etapa de integración autorizada."
        )

    with tab_fact:
        st.subheader("📋 Facturas registradas en GUELMAR")
        df_fact = query_df("""
            SELECT f.id AS "ID",
                   f.numero_factura AS "N.º Factura",
                   f.fecha_emision AS "Fecha",
                   f.nit_cliente AS "NIT/CI",
                   f.nombre_cliente AS "Cliente",
                   f.total AS "Total",
                   f.estado AS "Estado",
                   f.cuf AS "CUF",
                   f.codigo_recepcion AS "Código recepción"
            FROM facturas f
            ORDER BY f.id DESC
            LIMIT 300
        """)
        if df_fact.empty:
            st.info("Todavía no hay facturas preparadas.")
        else:
            st.dataframe(
                df_fact,
                width="stretch",
                hide_index=True,
                column_config={
                    "Total": st.column_config.NumberColumn("Total", format="Bs %.2f")
                },
            )

    with tab_prep:
        st.subheader("🛠️ Crear factura a partir de una venta")
        ventas = query_df("""
            SELECT v.id, v.fecha, v.total, v.metodo_pago, v.sucursal_id,
                   c.nit_ci, c.nombre
            FROM ventas v
            LEFT JOIN sucursales s ON s.id=v.sucursal_id
            LEFT JOIN clientes c ON c.id=v.cliente_id
            WHERE v.estado='ACTIVA'
            ORDER BY v.id DESC
            LIMIT 200
        """)

        if ventas.empty:
            st.info("No hay ventas activas disponibles para preparar una factura.")
        else:
            opciones_ventas = {
                f"Venta #{int(r.id)} · {r.fecha} · {r.nombre or 'Cliente General'} · {money(r.total)}":
                int(r.id)
                for r in ventas.itertuples()
            }
            venta_label = st.selectbox("Selecciona la venta", list(opciones_ventas.keys()))
            venta_id = opciones_ventas[venta_label]

            venta = query_df("""
                SELECT v.*, c.nit_ci, c.nombre, c.tipo_documento,
                       c.complemento, c.razon_social
                FROM ventas v
                LEFT JOIN clientes c ON c.id=v.cliente_id
                WHERE v.id=?
            """, (venta_id,))

            if not venta.empty:
                vr = venta.iloc[0]
                st.write(
                    f"**Cliente:** {vr['nombre'] or 'Cliente General'}  \n"
                    f"**NIT/CI:** {vr['nit_ci'] or '0'}  \n"
                    f"**Total venta:** {money(vr['total'])}"
                )

                if st.button("🧾 Preparar factura", width="stretch"):
                    conn = get_conn()
                    try:
                        existente = conn.execute(
                            "SELECT id FROM facturas WHERE venta_id=? ORDER BY id DESC LIMIT 1",
                            (venta_id,)
                        ).fetchone()

                        if existente:
                            st.warning(
                                f"La venta #{venta_id} ya tiene una factura preparada (ID {existente['id']})."
                            )
                        else:
                            cfg_db = conn.execute(
                                "SELECT * FROM configuracion_fiscal WHERE sucursal_id=?",
                                (int(vr["sucursal_id"]),)
                            ).fetchone()
                            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            numero = int(cfg_db["numero_factura_actual"] or 0) + 1

                            cur = conn.execute("""
                                INSERT INTO facturas
                                (venta_id, sucursal_id, fecha_emision, numero_factura, nit_cliente,
                                 nombre_cliente, tipo_documento_cliente, complemento_cliente,
                                 subtotal, descuento, monto_iva, total, metodo_pago,
                                 modalidad, estado, ambiente, leyenda, creado_en, actualizado_en)
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """, (
                                venta_id, int(vr["sucursal_id"]), ahora, numero,
                                str(vr["nit_ci"] or "0"),
                                str(vr["nombre"] or "Cliente General"),
                                str(vr["tipo_documento"] or "1"),
                                str(vr["complemento"] or ""),
                                float(vr["subtotal"] or 0),
                                float(vr["descuento"] or 0),
                                0.0,
                                float(vr["total"] or 0),
                                str(vr["metodo_pago"] or ""),
                                str(cfg_db["modalidad"] or "Computarizada en Línea"),
                                "BORRADOR",
                                str(cfg_db["ambiente"] or "PILOTO"),
                                str(cfg_db["leyenda"] or ""),
                                ahora, ahora
                            ))
                            factura_id = cur.lastrowid

                            detalles = conn.execute("""
                                SELECT producto_id, codigo, nombre, cantidad,
                                       precio_unitario, total
                                FROM detalle_ventas
                                WHERE venta_id=?
                                ORDER BY id
                            """, (venta_id,)).fetchall()

                            for d in detalles:
                                prod = conn.execute(
                                    "SELECT codigo_sin, unidad_medida FROM productos WHERE id=?",
                                    (d["producto_id"],)
                                ).fetchone()
                                conn.execute("""
                                    INSERT INTO detalle_facturas
                                    (factura_id, producto_id, codigo_producto,
                                     codigo_producto_sin, descripcion, cantidad,
                                     unidad_medida, precio_unitario, descuento,
                                     subtotal, monto_iva)
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                                """, (
                                    factura_id, d["producto_id"], d["codigo"],
                                    str(prod["codigo_sin"] if prod else ""),
                                    d["nombre"], float(d["cantidad"]),
                                    str(prod["unidad_medida"] if prod else "UNIDAD"),
                                    float(d["precio_unitario"]), 0.0,
                                    float(d["total"]), 0.0
                                ))

                            conn.execute("""
                                UPDATE configuracion_fiscal
                                SET numero_factura_actual=?, actualizado_en=?
                                WHERE sucursal_id=?
                            """, (numero, ahora, int(vr["sucursal_id"])))
                            conn.commit()
                            # Invalidar lecturas cacheadas tras cualquier escritura.
                            st.cache_data.clear()
                            st.success(
                                f"Factura borrador #{numero} creada correctamente. "
                                "Todavía no fue enviada al SIN."
                            )
                    finally:
                        conn.close()
                        st.rerun()

                detalle = query_df("""
                    SELECT codigo_producto AS "Código",
                           codigo_producto_sin AS "Código SIN",
                           descripcion AS "Producto",
                           cantidad AS "Cantidad",
                           unidad_medida AS "Unidad",
                           precio_unitario AS 'Precio unitario',
                           subtotal AS "Subtotal"
                    FROM detalle_facturas
                    WHERE factura_id = (
                        SELECT id FROM facturas
                        WHERE venta_id=? ORDER BY id DESC LIMIT 1
                    )
                """, (venta_id,))
                if not detalle.empty:
                    st.dataframe(detalle, width="stretch", hide_index=True)

        st.markdown("---")
        st.caption(
            "Próxima etapa: homologación de productos/códigos SIN, generación XML, "
            "CUF/CUFD, firma cuando corresponda, contingencia, validación y conexión "
            "con los servicios del SIN."
        )


# ======================== BACKUPS =============================

elif pagina == "💾 Copias de seguridad":
    if user["rol"] != "Administrador":
        st.error("No tienes permisos para esta sección.")
    else:
        st.markdown('<div class="section-title">💾 Copias de seguridad y reinicio</div>', unsafe_allow_html=True)

        st.subheader("🧪 Reiniciar sistema para nuevas pruebas")
        st.warning(
            "Esta acción conservará TODOS los productos registrados y pondrá su stock en 0. "
            "Eliminará ventas, movimientos, cotizaciones, facturación de prueba y clientes. "
            "También eliminará las copias de seguridad existentes. Usuarios y configuración se conservan."
        )
        confirmar_reinicio = st.checkbox(
            "Entiendo que los datos de prueba y las copias de seguridad serán eliminados",
            key="v1415_confirmar_reinicio"
        )
        if st.button(
            "🔴 REINICIAR TODO PARA NUEVAS PRUEBAS",
            width="stretch",
            type="primary",
            key="v1415_reiniciar"
        ):
            if not confirmar_reinicio:
                st.error("Marca la casilla de confirmación antes de continuar.")
            else:
                ok, mensaje = reiniciar_datos_prueba_sin_backup()
                st.session_state.carrito = []
                st.session_state.cot_carrito = []
                st.session_state.pop("ultima_venta_id", None)
                st.session_state.pop("ultima_cotizacion_id", None)
                if ok:
                    st.success(mensaje)
                    st.session_state.v1415_confirmar_reinicio = False
                    st.rerun()
                else:
                    st.error(mensaje)

        st.divider()
        st.subheader("🛡️ Estado de la base de datos central")
        if st.button("🔍 Verificar conexión e integridad", width="stretch", key="v14_verificar_integridad"):
            resultado = verificar_integridad_db()
            if resultado["ok"]:
                st.success(
                    "Base central PostgreSQL/Supabase conectada y estructura esencial verificada."
                )
            else:
                st.error(f"Se detectaron problemas en la base central: {resultado.get('integrity')}")
                if resultado.get("faltantes"):
                    st.warning(f"Tablas faltantes: {', '.join(resultado['faltantes'])}")

        st.subheader("☁️ Copias de seguridad")
        st.info(
            "GUELMAR CLOUD no crea archivos .db locales. La base central utiliza "
            "las copias y mecanismos de recuperación de Supabase."
        )


# ------------------------- PIE -------------------------------

# ------------------------- PIE -------------------------------

st.divider()
st.caption(
    f"GUELMAR · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"Usuario: {user['usuario']} · Base de datos central Supabase / PostgreSQL"
)
