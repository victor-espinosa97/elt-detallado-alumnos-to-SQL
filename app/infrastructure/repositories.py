# infraestructure/repositories.py

import time
from app.infrastructure.database import engine


class EstudianteRepository:

    @staticmethod
    def insertar_masivo(data: list):

        if not data:
            return

        # columnas = list(data[0].keys())
        columnas = [
            "idnuip","iddocumento","cdtipodoc","idperid","nmnombre1","nmnombre2",
            "nmapellido1","nmapellido2","txgenero","dtfechanacimiento","ctedad",
            "txbarrio","cdestrato","nmpaisorigen","txtipodesangre","txeps",
            "txdiscapacidad","cdestado","txmodelo","cdgradocod","cdgrupo",
            "cdjornada","nminstitucion","nmsede","cddane","cdsector","cdzonasede",
            "cdcalendario","dhfechaini","dhfechafin","fgsubsidio","fgcampesino",
            "txetnia","txtraespaprescolar","txapoyoacademicoespecial",
            "txlistacapexcepcionales","cdsisbeniv","nmano","nmgrado",
            "cdcodigojerarquia","txcategoriaaula","nmpaisnacionalidad2",
            "nmpaisnacimiento","fgestaactivosrpa","fghaestadovinculadosrpa",
            "cdrenombre","cdsisben","vlsisbentres","txobservacion","txcorreo",
            "txsrpa","idnumcontrato","txinternado","txfuenterecursos",
            "fgmatriculacontratada","txmotivo","idconsecutivo",
            "idcodigodanesede","nmjerarquia","nmetc","nmarchivoorigen"
        ]

        query = f"""
            INSERT INTO edc001001 ({",".join(columnas)})
            VALUES ({",".join(["?" for _ in columnas])})
        """

        conn = None

        try:
            conn = engine.raw_connection()
            cursor = conn.cursor()
            cursor.fast_executemany = True

            valores = []

            for row in data:
                fila = []
                for col in columnas:
                    val = row.get(col)

                    if isinstance(val, str):
                        if len(val) > 1000:  # seguridad extrema
                            val = val[:1000]

                    fila.append(val)

                valores.append(tuple(fila))

            # 🔥 intento masivo normal
            cursor.executemany(query, valores)
            conn.commit()

            print(f"✅ Insertados: {len(data)} registros")
            return

        except Exception as e:
            print("\n💥 ERROR MASIVO DETECTADO:", e)
            print("🔎 Iniciando aislamiento real del error...\n")

            print("\n🚨 POSIBLE COLUMNA PROBLEMA:")
            for col, val in zip(columnas, row.values()):
                if isinstance(val, str):
                    print(f"{col}: len={len(val)} → {val}")

            # 🔥 AQUÍ ESTÁ LA DIFERENCIA CLAVE:
            # NUEVA CONEXIÓN LIMPIA PARA DEBUG
            conn_debug = engine.raw_connection()
            cursor_debug = conn_debug.cursor()

            for i, row in enumerate(data):

                try:
                    cursor_debug.execute(
                        query,
                        tuple(row.get(col) for col in columnas)
                    )

                except Exception as row_error:

                    print(f"\n💥 FILA CON ERROR: {i}")

                    for col in columnas:
                        val = row.get(col)

                        if isinstance(val, str):
                            print(f"➡️ {col} = '{val}' (len={len(val)})")

                    print("\n❌ ERROR DETALLE REAL:", row_error)

                    conn_debug.close()
                    raise Exception("❌ Fila problemática encontrada")

            conn_debug.close()
            time.sleep(1)

        finally:
            if conn:
                conn.close()

        raise Exception("❌ Falló inserción tras reintentos")