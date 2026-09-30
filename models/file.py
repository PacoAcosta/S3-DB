# ¿Cómo representa Python a la tabla files?

import uuid                                                 # Genera identificadores únicos universales (UUID) para la columna id
from sqlalchemy import Column, Text, BigInteger, DateTime   # Define los tipos de datos de las columnas de la tabla files
from sqlalchemy.dialects.postgresql import UUID             # Define el tipo de datos UUID específico de PostgreSQL para la columna id
from sqlalchemy.sql import func                             # Permite usar funciones de SQL como func.now() para establecer valores predeterminados en las columnas de la tabla files
from database import Base                                   # Define la clase base para nuestros modelos SQLAlchemy. Todos los modelos de la base de datos heredarán de esta clase.

# Definición de la clase File que representa la tabla files en la base de datos
class File(Base):
    __tablename__ = "files"

    # Definición de las columnas de la tabla files
    id = Column(
        UUID(as_uuid=True), # Indica que la columna utiliza UUID
        primary_key=True,   # Indica que esta columna es la clave primaria de la tabla
        default=uuid.uuid4  # Indica que el valor predeterminado de esta columna es un UUID generado automáticamente por la función uuid.uuid4(). Si no se lo asignamos nosotros, Python lo hace.
    )

    # Nombre del archivo
    file_name = Column(
        Text,
        nullable=False  # Indica que esta columna no puede ser nula, es decir, debe tener un valor asignado.
    )

    # Tipo de archivo (por ejemplo, "image/png", "application/pdf", etc.)
    file_type = Column(
        Text,
        nullable=False  # Indica que esta columna no puede ser nula, es decir, debe tener un valor asignado.
    )

    # Tamaño del archivo en bytes
    file_size = Column(
        BigInteger,
        nullable=True
    )

    # Esta será la clave/ruta del objeto dentro de S3
    s3_key = Column(
        Text,
        nullable=True
    )
    # Aquí guardaremos la URL que utilicemos para acceder al archivo
    s3_url = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )