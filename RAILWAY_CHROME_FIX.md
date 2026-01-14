# Solução: Chrome não abre no Railway

## Problema
O Railway não tem Chrome/ChromeDriver instalado por padrão, causando erro ao tentar executar o Selenium.

## Solução Implementada

### 1. Arquivos Criados

- **`nixpacks.toml`**: Configuração para instalar Chrome/ChromeDriver automaticamente
- **`railway.json`**: Configuração alternativa para Railway

### 2. Código Atualizado

Os arquivos `dbfusion_client.py`, `spyhub_client.py` e `operadora_checker.py` foram atualizados para:
- Sempre usar modo headless em produção
- Detectar automaticamente ambiente Railway/Render
- Usar caminhos corretos do Chrome no Linux
- Adicionar flags necessárias para Railway (`--single-process`)

### 3. Configuração no Railway

**Opção A: Usar Nixpacks (Recomendado)**

O Railway detecta automaticamente o `nixpacks.toml` e instala Chrome/ChromeDriver.

**Opção B: Configurar Build Command Manualmente**

No painel do Railway, vá em Settings → Build:
- Build Command: `pip install -r requirements.txt && apt-get update && apt-get install -y chromium chromium-driver`

**Opção C: Usar Dockerfile**

Crie um `Dockerfile`:
```dockerfile
FROM python:3.13-slim

# Instalar Chrome e ChromeDriver
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--timeout", "300", "--workers", "1"]
```

## Verificar se Funcionou

1. Faça deploy no Railway
2. Verifique os logs durante o build - deve mostrar instalação do Chrome
3. Tente executar o processamento
4. Verifique os logs - não deve ter erro de "ChromeDriver not found"

## Variáveis de Ambiente Necessárias

Certifique-se de configurar no Railway:
- `DBFUSION_USER`
- `DBFUSION_PASSWORD`
- `SPYHUB_USER`
- `SPYHUB_PASSWORD`

## Troubleshooting

Se ainda não funcionar:

1. **Verificar logs do build**: Procure por erros na instalação do Chrome
2. **Verificar variáveis de ambiente**: Todas as credenciais estão configuradas?
3. **Testar localmente com Docker**: Use o Dockerfile para testar antes de fazer deploy

