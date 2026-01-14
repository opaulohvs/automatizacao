FROM python:3.13-slim

# Instalar dependências do sistema e Chrome
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    chromium-sandbox \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalação do Chrome
RUN which chromium && chromium --version || echo "Chromium não encontrado"
RUN which chromedriver && chromedriver --version || echo "ChromeDriver não encontrado"
RUN ls -la /usr/bin/chrom* || echo "Nenhum executável chromium encontrado"

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

# Copiar e tornar executável o script de inicialização
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expor porta (Railway define PORT automaticamente)
EXPOSE 8080

# Comando para iniciar a aplicação usando o script
CMD ["/app/start.sh"]

