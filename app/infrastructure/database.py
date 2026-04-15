# app/infrastructure/database.py

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    # echo=True,
    fast_executemany=True
)

# 🔥 asegurar fast_executemany en pyodbc
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if executemany:
        cursor.fast_executemany = True


SessionLocal = sessionmaker(bind=engine)


# 🔎 Validar conexión
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("✅ Conexión a la BD exitosa")
except Exception as e:
    print("❌ Error conectando a la BD:", e)