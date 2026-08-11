FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first so Docker can cache this layer.
# Change your code, and pip install does not run again.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Gather CSS and JS into STATIC_ROOT so WhiteNoise can serve them.
# SECRET_KEY is a throwaway here; it is only needed for settings to import.
RUN SECRET_KEY=build-time-only DEBUG=False python manage.py collectstatic --noinput

# Migrate, then start Gunicorn. Render's free tier has no shell,
# so migrations run here on every deploy.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn accessPoint_main.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]