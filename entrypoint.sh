#!/bin/sh
set -e

echo "Esperando a PostgreSQL en $DB_HOST:${DB_PORT:-5432}..."
while ! python -c "
import os, socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect((os.environ.get('DB_HOST', 'db'), int(os.environ.get('DB_PORT', 5432))))
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL disponible."

python manage.py migrate --noinput
python manage.py seed_datos

exec "$@"