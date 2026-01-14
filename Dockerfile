FROM python:3.13-slim

# Instalar dependências do sistema e Chrome
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente para Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Criar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (Railway define PORT automaticamente)
EXPOSE 8080

# Comando para iniciar a aplicação
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --timeout 300 --workers 1

