# 1. Imagen base oficial de Python ligera
FROM python:3.11-slim

# 2. Sin archivos .pyc y con logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Requerimientos primero: aprovecha la caché de capas de Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Resto del código fuente
COPY . /app/

# 6. Arranque: espera a Postgres, migra y siembra datos
#    Se invoca con "sh" para no depender del bit de ejecución ni de Windows
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

EXPOSE 8000

# 7. Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]