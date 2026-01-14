FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    && apt-get clean

# Instalar Google Chrome (mais confiável que Chromium)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver compatível
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1 | cut -d. -f1) && \
    echo "Chrome version detected: $CHROME_VERSION" && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}" || echo "131.0.6778.85") && \
    echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver* && \
    chromedriver --version

# Verificar instalação
RUN echo "=== Verificando instalação ===" && \
    google-chrome --version && \
    chromedriver --version && \
    ls -la /usr/bin/google-chrome* /usr/local/bin/chromedriver

# Definir variáveis de ambiente para Chrome
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Criar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar e tornar executável o script de inicialização
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expor porta (Railway define PORT automaticamente)
EXPOSE 8080

# Comando para iniciar a aplicação usando o script
CMD ["/app/start.sh"]

