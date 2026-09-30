# En este archivo se hace la conexión a S3 usando boto3 y se define una función para probar la conexión al bucket especificado.

import os
import boto3 # SDK de AWS para Python
from dotenv import load_dotenv # Carga nuestro archivo .env // No se ponen aquí las llaves porque boto3 las puede leer desde el .env


load_dotenv()

# Cargar las variables de entorno de AWS desde el archivo .env
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Crear un cliente de S3 usando boto3. Este objeto nos permitirá interactuar con el servicio S3 de AWS.
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)

# Función para probar la conexión a S3. Intenta obtener información sobre el bucket especificado y devuelve la respuesta. No hace nada más que comprueba el acceso
def test_s3_connection():
    response = s3_client.head_bucket(
        Bucket=S3_BUCKET_NAME
    )

    return response

# Función para obtener la identidad del usuario de AWS que está haciendo la solicitud. Esto puede ser útil para depuración o para verificar que las credenciales de AWS están configuradas correctamente.
def get_aws_identity():
    sts_client = boto3.client(
        "sts",
        region_name=AWS_REGION
    )

    return sts_client.get_caller_identity()

# Endpoint para subir un archivo a S3. Este endpoint recibe un archivo y lo sube al bucket de S3 usando la función upload_file_to_s3() definida en s3_service.py
def upload_file_to_s3(file, key, content_type):
    s3_client.upload_fileobj(
        file,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": content_type
        }
    )

    return key

# Función para generar una URL pre-firmada para un archivo en S3. Esto permite a los usuarios descargar el archivo sin necesidad de tener credenciales de AWS, ya que la URL es válida solo por un tiempo limitado (por defecto, 1 hora).
def generate_presigned_url(s3_key, expiration=3600):
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": s3_key
        },
        ExpiresIn=expiration
    )

    return url

# Función para eliminar un archivo de S3. Esta función recibe la clave del archivo en S3 y lo elimina del bucket especificado.
def delete_file_from_s3(key):
    s3_client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=key
    )