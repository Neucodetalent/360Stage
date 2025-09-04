# Python base (Debian 12)
FROM python:3.12-slim

# System deps + MS ODBC Driver 18
USER root
ENV ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl gnupg apt-transport-https ca-certificates \
      unixodbc unixodbc-dev build-essential \
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
  && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
       > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update && apt-get install -y --no-install-recommends msodbcsql18 \
  && rm -rf /var/lib/apt/lists/*

# App dir
WORKDIR /app

# Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn

# Copy app
COPY . .

# Optional: collect static at build time (skips if settings/env missing)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Start script runs migrations then gunicorn
CMD ["bash", "-lc", "python manage.py migrate && gunicorn NFS_360.wsgi --bind 0.0.0.0:8000 --timeout 600"]
