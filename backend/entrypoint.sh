#!/bin/sh
set -e

echo "[entrypoint] Running Django startup tasks..."

echo "[entrypoint] Running makemigrations (safe to ignore if none)"
python manage.py makemigrations || true

MAX_RETRIES=5
TRY=0
while [ "$TRY" -lt "$MAX_RETRIES" ]; do
  TRY=$((TRY+1))
  echo "[entrypoint] Attempting migrate (try ${TRY}/${MAX_RETRIES})"
  if python manage.py migrate --noinput; then
    echo "[entrypoint] migrate succeeded"
    break
  fi

  echo "[entrypoint] migrate failed — attempting targeted fixes"
  # Ensure core Django built-in tables exist first (run separately)
  python manage.py migrate contenttypes --noinput || true
  python manage.py migrate auth --noinput || true
  python manage.py migrate admin --noinput || true
  python manage.py migrate sessions --noinput || true
  # Create tables for apps that may not have migrations (dev only) — only after builtins
  python manage.py migrate --run-syncdb --noinput || true
  sleep 2
done

# Final attempt (best effort)
python manage.py migrate --noinput || true

echo "[entrypoint] Collecting static files (noinput)"
python manage.py collectstatic --noinput || true

if [ "${INSTALL_SPACY}" = "1" ]; then
  echo "[entrypoint] Installing spaCy model en_core_web_md"
  python -m spacy download en_core_web_md || true
fi

echo "[entrypoint] Startup tasks complete — execing command"
exec "$@"
