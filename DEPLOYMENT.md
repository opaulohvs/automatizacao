# Guia de Deploy - Sistema de Automação

## ⚠️ Problema: Vercel não suporta Selenium

O **Vercel** é uma plataforma serverless que **NÃO suporta**:
- Execução de processos longos (timeout de 10-60 segundos)
- Abertura de navegadores (Chrome/Selenium)
- Instalação de dependências do sistema (ChromeDriver, Chrome)
- Processos em background

**Por isso o sistema não funciona no Vercel!**

## ✅ Soluções Recomendadas

### 1. **Railway** (Recomendado) ⭐
- ✅ Suporta processos longos
- ✅ Permite instalação de dependências do sistema
- ✅ Suporta Selenium/Chrome
- ✅ Plano gratuito disponível
- ✅ Fácil configuração

**Como fazer:**
1. Crie conta em https://railway.app
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. Railway detecta automaticamente Flask/Python
5. Adicione no `requirements.txt`:
   ```
   gunicorn
   ```

**Configuração necessária:**
- Adicione `Procfile`:
  ```
  web: gunicorn app:app --bind 0.0.0.0:$PORT
  ```

### 2. **Render**
- ✅ Suporta processos longos
- ✅ Permite Selenium (com configuração)
- ✅ Plano gratuito disponível
- ⚠️ Requer configuração adicional para Chrome

**Como fazer:**
1. Crie conta em https://render.com
2. Conecte repositório
3. Configure como "Web Service"
4. Adicione build command:
   ```bash
   pip install -r requirements.txt && apt-get update && apt-get install -y chromium-browser chromium-chromedriver
   ```

### 3. **DigitalOcean App Platform**
- ✅ Suporta processos longos
- ✅ Permite Selenium
- ⚠️ Plano pago (a partir de $5/mês)

### 4. **AWS EC2 / VPS Dedicado**
- ✅ Controle total
- ✅ Suporta tudo
- ⚠️ Requer configuração manual
- ⚠️ Custo variável

**Recomendado para produção:**
- DigitalOcean Droplet ($5-10/mês)
- AWS EC2 t2.micro (free tier disponível)
- Linode / Vultr

## 🔧 Configuração para Deploy

### 1. Adicionar `Procfile` (Railway/Render)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300
```

### 2. Atualizar `requirements.txt`
```
flask
gunicorn
selenium
webdriver-manager
beautifulsoup4
requests
pandas
python-dotenv
```

### 3. Configurar Chrome para Headless (Produção)

No `dbfusion_client.py`, `spyhub_client.py` e `operadora_checker.py`, descomente:
```python
chrome_options.add_argument('--headless')  # Rodar sem interface gráfica
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
```

### 4. Variáveis de Ambiente

Configure no painel do serviço (Railway/Render/etc):
- `DBFUSION_URL` (opcional, padrão: https://dbfusion.me/loja)
- `DBFUSION_USER` (obrigatório)
- `DBFUSION_PASSWORD` (obrigatório)
- `SPYHUB_URL` (opcional, padrão: https://app.spyhub.io)
- `SPYHUB_USER` (obrigatório)
- `SPYHUB_PASSWORD` (obrigatório)
- `TARGET_BIN` (opcional, padrão: 406669)
- `TARGET_OPERADORAS` (opcional, padrão: TIM,ALGAR)
- `CONSULTA_OPERADORA_URL` (opcional, padrão: http://consultaoperadora.com.br/site2015/)

**Importante:** O arquivo `config.py` agora lê de variáveis de ambiente automaticamente. Configure as variáveis acima no painel do seu serviço de deploy.

## 📋 Checklist de Deploy

- [ ] Escolher plataforma (Railway recomendado)
- [ ] Conectar repositório GitHub
- [ ] Adicionar `Procfile`
- [ ] Configurar variáveis de ambiente
- [ ] Ativar modo headless no Chrome
- [ ] Testar processamento
- [ ] Configurar domínio (opcional)

## 🚀 Deploy Rápido no Railway

1. **Instale Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Inicialize projeto:**
   ```bash
   railway init
   ```

4. **Configure variáveis:**
   ```bash
   railway variables set DBFUSION_USER=seu_usuario
   railway variables set DBFUSION_PASSWORD=sua_senha
   # ... outras variáveis
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

## ⚠️ Limitações Importantes

1. **Processos longos**: Algumas plataformas têm timeout. Considere:
   - Processar em lotes menores
   - Usar fila de processamento (Redis + Celery)
   - Webhooks para notificar conclusão

2. **Recursos**: Processos de scraping consomem CPU/memória
   - Monitore uso de recursos
   - Considere upgrade de plano se necessário

3. **Rate Limiting**: Sites podem bloquear requisições excessivas
   - Mantenha delays entre requisições
   - Use proxies se necessário (futuro)

## 📞 Suporte

Se tiver problemas com deploy, verifique:
1. Logs da plataforma
2. Se Chrome/ChromeDriver está instalado
3. Se variáveis de ambiente estão configuradas
4. Se timeout está adequado para processos longos

