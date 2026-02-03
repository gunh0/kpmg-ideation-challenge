FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=0 \
    DJANGO_DB_PATH=/data/db.sqlite3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# DuckDB reads the public patent data over HTTPS with its httpfs extension;
# install it now, the running container has no writable place to load it from.
ENV DUCKDB_EXTENSION_DIRECTORY=/opt/duckdb/extensions
RUN python -c "import duckdb; duckdb.connect(config={'extension_directory': '$DUCKDB_EXTENSION_DIRECTORY'}).install_extension('httpfs')"

COPY . .
RUN DJANGO_SECRET_KEY=collectstatic python manage.py collectstatic --noinput \
    && useradd --system --uid 1000 app \
    && mkdir /data && chown app /data

USER app
VOLUME /data
EXPOSE 8000

# The first start fills the empty database from the bundled snapshot.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py load_seed && gunicorn config.wsgi"]
