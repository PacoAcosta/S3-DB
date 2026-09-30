# Endpoints de la API usando FastAPI y SQLAlchemy para conectarse a PostgreSQL

from fastapi import FastAPI, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, get_db
from models.file import File
import uuid
from uuid import UUID
from datetime import datetime

from s3_service import test_s3_connection, get_aws_identity, upload_file_to_s3, generate_presigned_url, delete_file_from_s3

app = FastAPI()

@app.get("/")
def root():
    return {"mensaje": "API funcionando"}

# Endpoint para probar la conexión a la base de datos PostgreSQL
@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": "conectada",
            "resultado": result.scalar()
        }

# Endpoint para crear un nuevo archivo en la base de datos
@app.post("/files")
# Necesitamos una sesión de base de datos, que obtenemos usando la función get_db() como dependencia de FastAPI. FastAPI se encargará de crear y cerrar la sesión automáticamente.
def create_file(db: Session = Depends(get_db)): # Esta línea es para crear una sesión con la DB y pasarle el resultado con el yield
    # Construimos un objeto con las columnas de la base de datos que tenemos en supabase
    new_file = File(
        file_name="foto-prueba.jpg",
        file_type="image/jpeg",
        file_size=123456,
        s3_key="uploads/foto-prueba.jpg",
        s3_url="https://ejemplo.com/foto-prueba.jpg"
    )

    db.add(new_file)        # Con esto agregamos el objeto a la DB. "Quiero guardar esto"
    db.commit()             # Con esto guardamos los cambios en la DB. "Confirma y guarda"
    db.refresh(new_file)    # Con esto refrescamos el objeto para obtener el ID generado por la DB. "Vuelve a consultar este registro desde la DB y actualiza el objeto"

    return {
        "mensaje": "Archivo creado",
        "id": str(new_file.id),
        "file_name": new_file.file_name
    }

# Endpoint para obtener todos los archivos de la base de datos
@app.get("/files")
def get_files(db: Session = Depends(get_db)):
    files = db.query(File).all()  # Obtenemos todos los registros de la tabla File. Es como tener "SELECT * FROM files;". File es la tabla y files los archivos

    # Retornamos una lista de diccionarios con la información de cada archivo, convirtiendo el ID a string para evitar problemas de serialización. Por cada archivo en archivos
    return [
        {
            "id": str(file.id),
            "file_name": file.file_name,
            "file_type": file.file_type,
            "file_size": file.file_size,
            "s3_key": file.s3_key,
            "s3_url": file.s3_url,
            "created_at": file.created_at,
        }
        for file in files # Convierte cada objeto SQLAlchemy en un diccionario para que FastAPI pueda devolverlo como JSON. Por cada archivo en archivos
    ]

# Endpoint para probar la conexión a S3 usando la función test_s3_connection() definida en s3_service.py
@app.get("/s3-test")
def s3_test():
    test_s3_connection()

    return {
        "s3": "conectado",
        "bucket": "fotoapp-s3"
    }

# Endpoint para obtener la identidad del usuario de AWS que está haciendo la solicitud usando la función get_aws_identity() definida en s3_service.py
@app.get("/aws-identity")
def aws_identity():
    return get_aws_identity()

@app.post("/files/upload")
def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    file_id = uuid.uuid4()

    extension = ""

    if file.filename and "." in file.filename:
        extension = "." + file.filename.split(".")[-1]

    s3_key = (
        f"uploads/"
        f"{datetime.now().year}/"
        f"{datetime.now().month:02d}/"
        f"{file_id}{extension}"
    )

    file_size = 0

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    upload_file_to_s3(
        file.file,
        s3_key,
        file.content_type
    )

    new_file = File(
        id=file_id,
        file_name=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        s3_key=s3_key
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "mensaje": "Archivo subido correctamente",
        "id": str(new_file.id),
        "file_name": new_file.file_name,
        "file_type": new_file.file_type,
        "file_size": new_file.file_size,
        "s3_key": new_file.s3_key
    }

# Endpoint para obtener un archivo específico de la base de datos y generar una URL pre-firmada para descargarlo desde S3. La URL pre-firmada permite a los usuarios descargar el archivo sin necesidad de tener credenciales de AWS, ya que la URL es válida solo por un tiempo limitado (por defecto, 1 hora).
@app.get("/files/{file_id}")
def get_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    file = db.query(File).filter(
        File.id == file_id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )

    url = generate_presigned_url(
        s3_key=file.s3_key
    )

    return {
        "id": str(file.id),
        "file_name": file.file_name,
        "file_type": file.file_type,
        "file_size": file.file_size,
        "s3_key": file.s3_key,
        "url": url
    }

#
@app.delete("/files/{file_id}")
def delete_file(
    file_id: UUID,
    db: Session = Depends(get_db)
):
    file = db.query(File).filter(
        File.id == file_id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )

    if file.s3_key:
        delete_file_from_s3(file.s3_key)

    db.delete(file)
    db.commit()

    return {
        "mensaje": "Archivo eliminado correctamente",
        "id": str(file.id),
        "file_name": file.file_name
    }


# A través de keys podemos conectar la base de datos con S3 para acceder al archivo. Nos da una ruta de AWS para identificar el archivo