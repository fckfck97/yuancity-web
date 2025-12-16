# --- build ---
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Copia solo los archivos necesarios para instalar dependencias
COPY setup.cfg setup.py ./
COPY . .

# Instala dependencias y el proyecto como paquete
RUN pip install --upgrade pip && pip install .

# --- runtime ---
FROM python:3.12-slim
WORKDIR /app

# Copia paquetes instalados y binarios
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia el código fuente (sin .env gracias a .dockerignore)
COPY . .

# Variables de entorno necesarias (opcional, pero mejor usar runtime)
ENV DJANGO_SETTINGS_MODULE=config.settings.prod \
  PYTHONUNBUFFERED=1 \
  PORT=8000 \
  PYTHONPATH=/app

# Puerto y comando de inicio
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]