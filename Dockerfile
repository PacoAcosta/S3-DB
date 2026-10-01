# Esto es para que Docker use la imagen base de Python 3.12 en su versión slim, que es más ligera y adecuada para entornos de producción.
FROM python:3.12-slim

# Crea /app como directorio de trabajo
WORKDIR /app

# Copia todo el requirement.txt 
COPY requirements.txt .

# Instala las dependencias que usamos pero en el contenedor de Docker, no en la compu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]