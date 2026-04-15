# app/presentation/api.py

from http.client import HTTPException
import os
from fastapi import APIRouter, Body, UploadFile, File
import shutil

from app.infrastructure.csv_reader import leer_csv
from app.application.services import procesar_registros

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/cargar-estudiantes/")
async def cargar_estudiantes(file: UploadFile = File(...)):

    # ✅ Validar extensión
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos CSV"
        )

    path = f"temp_{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    registros = leer_csv(path)

    insertados, omitidos = procesar_registros(registros)

    # eliminar archivo temporal
    os.remove(path)

    return {
        "insertados": insertados,
        "omitidos": omitidos
    }
