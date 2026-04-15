# main.py

from fastapi import FastAPI
from app.presentation.api import router

app = FastAPI(title="MVP ETL Alcaldía Rionegro")

app.include_router(router)
