#!/bin/bash
# Script de inicialização para Railway
# Lê a variável PORT e inicia o Gunicorn

PORT=${PORT:-8080}
echo "Starting server on port $PORT"
exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1

