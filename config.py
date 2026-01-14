"""
Configurações do sistema de automação
Lê de variáveis de ambiente ou usa valores padrão
"""
import os

# Credenciais DBFusion
DBFUSION_URL = os.getenv("DBFUSION_URL", "https://dbfusion.me/loja")
DBFUSION_USER = os.getenv("DBFUSION_USER", "andrade17")
DBFUSION_PASSWORD = os.getenv("DBFUSION_PASSWORD", "284671")

# Credenciais SpyHub
SPYHUB_URL = os.getenv("SPYHUB_URL", "https://app.spyhub.io")
SPYHUB_USER = os.getenv("SPYHUB_USER", "Prtm999ww")
SPYHUB_PASSWORD = os.getenv("SPYHUB_PASSWORD", "350376")

# Filtro BIN
TARGET_BIN = os.getenv("TARGET_BIN", "406669")

# URL de consulta de operadora (usando web scraping)
CONSULTA_OPERADORA_URL = os.getenv("CONSULTA_OPERADORA_URL", "http://consultaoperadora.com.br/site2015/")

# Operadoras alvo
TARGET_OPERADORAS = os.getenv("TARGET_OPERADORAS", "TIM,ALGAR").split(",")


