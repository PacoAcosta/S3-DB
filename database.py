# Aquí ponemos cómo se conecta la base de datos, en este caso a PostgreSQL usando SQLAlchemy

from sqlalchemy import create_engine                        # Administra la conexión a PostgreSQL
from sqlalchemy.orm import sessionmaker, declarative_base   # Permite hacer sesiones de DB y permite crear la clase base de nuestros modelos SQLAlchemy
from dotenv import load_dotenv                              # Función para cargar variables de entorno desde un archivo .env
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de la base de datos usando SQLAlchemy. Este objeto sabe cómo conectarse a PostreSQL y ejecutar consultas.
engine = create_engine(DATABASE_URL)

# Crear una clase de sesión que nos permitirá interactuar con la base de datos. Esta clase se usará para crear sesiones de base de datos.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Crear la clase base para nuestros modelos SQLAlchemy. Todos los modelos de la base de datos heredarán de esta clase.
Base = declarative_base()

# Función para obtener una sesión de base de datos. Esta función se puede usar como dependencia en FastAPI para obtener una sesión de base de datos en cada solicitud.
def get_db():
    db = SessionLocal()

    # Usamos un bloque try/finally para asegurarnos de que la sesión se cierre correctamente después de usarla.
    try:
        yield db
    finally:
        db.close()