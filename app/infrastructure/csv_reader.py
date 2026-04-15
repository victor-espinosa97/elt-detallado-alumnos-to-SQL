# infrastructure/csv_reader.py

import pandas as pd
import json
from datetime import datetime


def leer_csv(path: str):

    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
        engine="python",
        dtype=str,
        on_bad_lines="skip"
    )

    df = df.dropna(how="all")

    # 🔥 función para detectar filas corruptas
    def fila_corrupta(row):

        errores = []

        # 🔥 Validación REAL: estructura, no contenido

        # 1. DOC no puede estar vacío
        doc = str(row.get("DOC", "")).strip()
        if doc == "" or doc.lower() == "nan":
            errores.append("DOC vacío")

        # 2. INSTITUCION no puede parecer un número
        institucion = str(row.get("INSTITUCION", "")).strip()
        if institucion.isdigit():
            errores.append("INSTITUCION numérica (columna corrida)")

        # 3. NOMBRE1 no puede ser extremadamente largo
        nombre = str(row.get("NOMBRE1", "")).strip()
        if len(nombre) > 100:
            errores.append("NOMBRE demasiado largo")

        # 4. JORNADA debe ser corta
        jornada = str(row.get("JORNADA", "")).strip()
        if len(jornada) > 20:
            errores.append("JORNADA sospechosa")

        # 5. DETECCIÓN CLAVE (la más importante)
        # si ESTADO aparece donde no debe
        if doc.upper() in ["MATRICULADO", "RETIRADO"]:
            errores.append("columnas corridas (DOC contiene ESTADO)")

        # 🔥 marcar error
        if errores:
            row["__errores__"] = ", ".join(errores)
            return True

        return False

    # 🔥 separar
    df_corruptas = df[df.apply(fila_corrupta, axis=1)]
    df_validas = df[~df.apply(fila_corrupta, axis=1)]

    # 🔥 guardar corruptas si existen
    if not df_corruptas.empty:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        path_json = f"corruptas_{timestamp}.json"
        path_csv = f"corruptas_{timestamp}.csv"

        # guardar JSON
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(
                df_corruptas.to_dict(orient="records"),
                f,
                ensure_ascii=False,
                indent=2
            )

        # guardar CSV
        df_corruptas.to_csv(path_csv, index=False, sep=";")

        print(f"\n🚨 Filas corruptas detectadas: {len(df_corruptas)}")
        print(f"📁 JSON: {path_json}")
        print(f"📁 CSV: {path_csv}\n")

    return df_validas.to_dict(orient="records")