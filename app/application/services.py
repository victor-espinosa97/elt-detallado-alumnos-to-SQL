# application/services.py

from datetime import datetime
import math

from app.core.mapping import MAPPING_EXCEL_TO_DB
from app.infrastructure.repositories import EstudianteRepository


def limpiar_nan(r: dict) -> dict:
    for k, v in r.items():
        if isinstance(v, float) and math.isnan(v):
            r[k] = None
    return r


from datetime import datetime

def normalizar_fechas(r: dict) -> dict:

    campos_fecha = ["FECHA_NACIMIENTO", "FECHAINI", "FECHAFIN"]

    for campo in campos_fecha:
        val = r.get(campo)

        if val:
            val = str(val).strip()

            # 🔥 limpiar .0 final
            if val.endswith(".0"):
                val = val[:-2]

            try:
                r[campo] = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
                continue
            except:
                pass

            try:
                r[campo] = datetime.strptime(val, "%d/%m/%Y")
                continue
            except:
                pass

            try:
                r[campo] = datetime.strptime(val, "%d/%m/%y")
                continue
            except:
                pass

            r[campo] = None

    return r


def limpiar_numericos(r):

    campos_numericos = [
        "DANE",
        "CONSECUTIVO",
        "CODIGO_DANE_SEDE",
        "CODIGO_JERARQUIA"
    ]

    for campo in campos_numericos:
        if campo in r and r[campo] is not None:
            try:
                valor = str(r[campo]).replace(",", ".")
                r[campo] = int(float(valor))
            except:
                r[campo] = None

    return r


# 🔥 NUEVO: tipado correcto (EL FIX REAL)
def tipar_datos_bd(r: dict) -> dict:

    for k, v in r.items():

        if v is None:
            continue

        # 🔹 fechas → dejarlas como datetime
        if k in ["FECHA_NACIMIENTO", "FECHAINI", "FECHAFIN"]:
            continue

        # 🔹 numéricos conocidos
        if k in ["EDAD"]:
            try:
                r[k] = int(v)
            except:
                r[k] = None
            continue

        if k == "SISBEN TRES":
            try:
                r[k] = float(v)
            except:
                r[k] = None
            continue

        # 🔹 flags (1 char)
        if k in ["SUBSIDIO", "CAMPESINO", "MATRICULACONTRATADA"]:
            r[k] = str(v)[:1]
            continue

        # 🔥 CORRECCIÓN REAL (usar nombres del Excel)
        if k == "JORNADA":
            r[k] = str(v)[:4]
            continue

        if k == "ZONA_SEDE":
            r[k] = str(v)[:4]
            continue

        if k == "TIPO_DE_SANGRE":
            r[k] = str(v)[:3]
            continue

        if k == "CALENDARIO":
            r[k] = str(v)[:1]
            continue

        # 🔹 default
        r[k] = str(v)

    return r


def truncar_texto(r):

    limites = {
        "SEDE": 255,
        "INSTITUCION": 255,
        "JERARQUIA": 255,
        "MODELO": 100,
        "MOTIVO": 255,
        "BARRIO": 150,
        "EPS": 255,
        "CORREO": 255,
    }

    for campo, limite in limites.items():
        if campo in r and r[campo]:
            r[campo] = str(r[campo])[:limite]

    return r


def mapear_a_bd(r: dict) -> dict:
    nuevo = {}

    for k, v in r.items():
        if k in MAPPING_EXCEL_TO_DB:
            nuevo[MAPPING_EXCEL_TO_DB[k]] = v

    return nuevo

def fila_valida(r):

    doc = str(r.get("DOC", ""))
    nombre = str(r.get("NOMBRE1", ""))

    # 🚨 detectar filas corridas
    if len(doc) > 15:
        print("🚨 DOC sospechoso:", doc)
        return False

    if len(nombre) > 150:
        print("🚨 NOMBRE sospechoso:", nombre)
        return False

    return True


def procesar_registros(registros: list):

    insertados = 0
    omitidos = 0
    batch = []

    for i, r in enumerate(registros):

        try:
            # 🔥 DEBUG CRUDO (ANTES DE TODO)
            if len(str(r.get("DOC", ""))) > 15:
                print("\n🚨 FILA CRUDA CORRUPTA DETECTADA (ANTES DE PROCESAR):")
                print(r)
                omitidos += 1
                continue

            r = limpiar_nan(r)
            r = limpiar_numericos(r)
            r = normalizar_fechas(r)
            r = tipar_datos_bd(r)
            r = truncar_texto(r)

            # 🔥 VALIDACIÓN FINAL
            if not fila_valida(r):
                print("\n🚨 FILA DESCARTADA (DESPUÉS DE LIMPIEZA):")
                print(r)
                omitidos += 1
                continue

            if str(r.get("ESTADO", "")).upper() == "CANCELADO":
                omitidos += 1
                continue

            row = mapear_a_bd(r)

            batch.append(row)

            if len(batch) == 1000:
                EstudianteRepository.insertar_masivo(batch)
                insertados += len(batch)
                batch = []

        except Exception as e:
            print("\n❌ Error fila:", e)
            print("👉 Fila problemática:", r)
            omitidos += 1

    if batch:
        EstudianteRepository.insertar_masivo(batch)
        insertados += len(batch)

    return insertados, omitidos