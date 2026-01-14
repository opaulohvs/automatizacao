"""
Verificador de operadora de telefone usando consultaoperadora.com.br
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import config
import re
import time
import glob
import os


class OperadoraChecker:
    def __init__(self):
        self.target_operadoras = config.TARGET_OPERADORAS
        self.driver = None
        self.url_consulta = "http://consultaoperadora.com.br/site2015/"
    
    def _get_driver(self):
        """Inicializa driver Selenium (reutiliza se já existir)"""
        if self.driver is None:
            chrome_options = Options()
            import os
            
            # Detecta ambiente Railway/Linux
            is_railway = bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_SERVICE_NAME'))
            is_linux = os.path.exists('/usr/bin/chromium') or os.path.exists('/usr/bin/chromium-browser')
            
            print(f"[DEBUG Operadora] Ambiente detectado - Railway: {is_railway}, Linux: {is_linux}")
            
            # Sempre usar headless em servidores (Railway, Render, etc)
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--single-process')  # Importante para Railway
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Define caminho do Chrome se estiver em Railway/Linux
            if os.path.exists('/usr/bin/chromium'):
                chrome_options.binary_location = '/usr/bin/chromium'
                print(f"[DEBUG Operadora] Usando Chrome em: /usr/bin/chromium")
            elif os.path.exists('/usr/bin/chromium-browser'):
                chrome_options.binary_location = '/usr/bin/chromium-browser'
                print(f"[DEBUG Operadora] Usando Chrome em: /usr/bin/chromium-browser")
            elif os.path.exists('/usr/bin/google-chrome'):
                chrome_options.binary_location = '/usr/bin/google-chrome'
                print(f"[DEBUG Operadora] Usando Chrome em: /usr/bin/google-chrome")
            
            # Em Linux/Railway, tenta usar ChromeDriver do sistema primeiro
            if is_linux:
                chromedriver_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/usr/lib/chromium-browser/chromedriver',
                ]
                
                for chromedriver_path in chromedriver_paths:
                    if os.path.exists(chromedriver_path):
                        try:
                            print(f"[DEBUG Operadora] Tentando usar ChromeDriver em: {chromedriver_path}")
                            service = Service(chromedriver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            print("[DEBUG Operadora] ChromeDriver inicializado com sucesso!")
                            return self.driver
                        except Exception as e:
                            print(f"[DEBUG Operadora] Erro ao usar {chromedriver_path}: {e}")
                            continue
            
            # Tenta diferentes métodos para obter o ChromeDriver
            driver_path = None
            
            # Método 1: Tenta usar webdriver-manager
            try:
                driver_path = ChromeDriverManager().install()
                import os
                if os.path.exists(driver_path) and os.path.getsize(driver_path) > 0:
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    return self.driver
            except Exception as e:
                print(f"Aviso: Erro ao usar webdriver-manager: {e}")
            
            # Método 2: Tenta usar ChromeDriver do PATH
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return self.driver
            except Exception as e:
                print(f"Aviso: Erro ao usar ChromeDriver do PATH: {e}")
            
            # Método 3: Tenta localizar ChromeDriver manualmente
            possible_paths = [
                os.path.join(os.getcwd(), 'chromedriver.exe'),
                'C:\\chromedriver\\chromedriver.exe',
                'C:\\Program Files\\chromedriver\\chromedriver.exe',
            ]
            
            # Adiciona caminhos do webdriver-manager
            wdm_path = os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', '*', 'chromedriver.exe')
            possible_paths.append(wdm_path)
            
            for path in possible_paths:
                try:
                    if '*' in path:
                        matches = glob.glob(path)
                        if matches:
                            path = matches[0]
                    
                    if os.path.exists(path):
                        service = Service(path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        return self.driver
                except:
                    continue
            
            raise Exception("Não foi possível inicializar o ChromeDriver")
        
        return self.driver
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def verificar_operadora(self, numero):
        """
        Verifica a operadora do número usando consultaoperadora.com.br
        Retorna nome da operadora ou None
        """
        if not numero:
            return None
        
        # Remove formatação
        numero_limpo = ''.join(filter(str.isdigit, str(numero)))
        
        if len(numero_limpo) < 10:
            return None
        
        # Consulta no site consultaoperadora.com.br
        operadora = self._consultar_operadora_site(numero_limpo)
        if operadora:
            return operadora
        
        return None
    
    def _consultar_operadora_site(self, numero):
        """
        Consulta operadora via consultaoperadora.com.br usando Selenium
        Formato esperado: DDD + Número (ex: 11987654321)
        """
        try:
            print(f"    Consultando operadora no site consultaoperadora.com.br...")
            driver = self._get_driver()
            driver.get(self.url_consulta)
            time.sleep(2)
            
            # Procura campo de input para o número
            # O site tem um campo "Digite o número do telefone: DDD + Número"
            numero_selectors = [
                "input[name*='numero']",
                "input[name*='telefone']",
                "input[name*='phone']",
                "input[type='text']",
                "input[placeholder*='DDD']",
                "input[placeholder*='número']",
                "#numero",
                "#telefone",
                "input[id*='numero']",
                "input[id*='telefone']",
            ]
            
            numero_field = None
            for selector in numero_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            # Verifica se o campo está relacionado a telefone
                            placeholder = elem.get_attribute('placeholder') or ''
                            name = elem.get_attribute('name') or ''
                            if 'ddd' in placeholder.lower() or 'numero' in placeholder.lower() or 'telefone' in name.lower():
                                numero_field = elem
                                break
                    if numero_field:
                        break
                except:
                    continue
            
            # Se não encontrou por seletor, tenta encontrar pelo texto próximo
            if not numero_field:
                try:
                    # Procura pelo texto "Digite o número" ou "DDD + Número"
                    xpath_texto = "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'digite o número') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ddd')]"
                    elementos_texto = driver.find_elements(By.XPATH, xpath_texto)
                    for elem in elementos_texto:
                        try:
                            # Procura input próximo ao elemento (várias estratégias)
                            xpaths_input = [
                                "./following-sibling::input[@type='text']",
                                "./parent::*/input[@type='text']",
                                "./ancestor::*//input[@type='text']",
                                "./following::input[@type='text'][1]",
                            ]
                            for xpath_input in xpaths_input:
                                try:
                                    inp = elem.find_element(By.XPATH, xpath_input)
                                    if inp.is_displayed() and inp.is_enabled():
                                        numero_field = inp
                                        break
                                except:
                                    continue
                            if numero_field:
                                break
                        except:
                            continue
                except:
                    pass
            
            if not numero_field:
                # Última tentativa: pega o primeiro input de texto visível
                try:
                    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    for inp in inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            numero_field = inp
                            break
                except:
                    pass
            
            if not numero_field:
                print(f"    ⚠ Campo de número não encontrado no site")
                return None
            
            # Preenche o número (formato: DDD + Número, ex: 11987654321)
            numero_field.clear()
            time.sleep(0.3)
            numero_field.send_keys(numero)
            time.sleep(0.5)
            
            # Procura botão "Consultar"
            consultar_button = None
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.btn-primary",
                "button.btn",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consultar')]",
                "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consultar')]",
            ]
            
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        buttons = driver.find_elements(By.XPATH, selector)
                    else:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for btn in buttons:
                        if btn.is_displayed():
                            consultar_button = btn
                            break
                    if consultar_button:
                        break
                except:
                    continue
            
            if consultar_button:
                consultar_button.click()
            else:
                # Tenta pressionar Enter
                numero_field.send_keys("\n")
            
            print(f"    Aguardando resultado da consulta...")
            time.sleep(3)  # Aguarda resultado carregar
            
            # Extrai a operadora do resultado
            operadora = self._extrair_operadora_resultado(driver)
            
            return operadora
            
        except Exception as e:
            print(f"    Erro ao consultar operadora no site: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extrair_operadora_resultado(self, driver):
        """Extrai o nome da operadora do resultado da consulta"""
        try:
            # Aguarda um pouco para garantir que o resultado carregou
            time.sleep(2)
            
            # Obtém HTML da página
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procura por texto que contenha operadoras conhecidas
            texto_pagina = driver.find_element(By.TAG_NAME, 'body').text.upper()
            
            # Procura especificamente por "Operadora: CTBC (Móvel/SMP)" que é ALGAR
            # Padrões possíveis: "Operadora: CTBC (Móvel/SMP)", "CTBC (Móvel/SMP)", "CTBC Móvel", etc.
            pattern_ctbc_algar = re.compile(r'OPERADORA[:\s]*CTBC.*?(?:MÓVEL|SMP|\(MÓVEL/SMP\))', re.IGNORECASE | re.DOTALL)
            if pattern_ctbc_algar.search(texto_pagina):
                print(f"    ✓ Operadora encontrada: CTBC (Móvel/SMP) = ALGAR")
                return 'ALGAR'
            
            # Procura também por CTBC sem o padrão completo (fallback)
            if 'CTBC' in texto_pagina:
                # Verifica se está no contexto de operadora móvel
                if 'MÓVEL' in texto_pagina or 'SMP' in texto_pagina or 'OPERADORA' in texto_pagina:
                    pattern = re.compile(r'CTBC.*?(?:MÓVEL|SMP|OPERADORA)', re.IGNORECASE | re.DOTALL)
                    if pattern.search(texto_pagina):
                        print(f"    ✓ Operadora encontrada: CTBC = ALGAR")
                        return 'ALGAR'
            
            # Lista de operadoras para buscar
            operadoras = ['TIM', 'ALGAR', 'VIVO', 'CLARO', 'OI', 'NEXTEL', 'SERCOMTEL']
            
            for op in operadoras:
                if op in texto_pagina:
                    # Verifica se está em um contexto válido (não é apenas parte de outra palavra)
                    # Procura por padrões como "Operadora: TIM" ou "TIM" próximo a "operadora"
                    pattern = re.compile(rf'\b{op}\b', re.IGNORECASE)
                    if pattern.search(texto_pagina):
                        print(f"    ✓ Operadora encontrada: {op}")
                        return self._normalizar_operadora(op)
            
            # Tenta encontrar em elementos específicos
            operadora_elements = soup.find_all(['div', 'span', 'p', 'td', 'th'], 
                                               string=re.compile(r'TIM|ALGAR|CTBC|VIVO|CLARO|OI', re.I))
            
            for elem in operadora_elements:
                texto = elem.get_text().upper().strip()
                
                # Verifica CTBC primeiro (ALGAR)
                if 'CTBC' in texto and ('MÓVEL' in texto or 'SMP' in texto or 'OPERADORA' in texto):
                    print(f"    ✓ Operadora encontrada: CTBC (ALGAR)")
                    return 'ALGAR'
                
                for op in operadoras:
                    if op in texto:
                        print(f"    ✓ Operadora encontrada: {op}")
                        return self._normalizar_operadora(op)
            
            print(f"    ⚠ Operadora não identificada no resultado")
            return None
            
        except Exception as e:
            print(f"    Erro ao extrair operadora: {e}")
            return None
    
    def _normalizar_operadora(self, operadora):
        """Normaliza nome da operadora"""
        if not operadora:
            return None
        
        operadora_upper = operadora.upper().strip()
        
        # Mapeamentos comuns
        if 'TIM' in operadora_upper:
            return 'TIM'
        elif 'ALGAR' in operadora_upper:
            return 'ALGAR'
        elif 'CTBC' in operadora_upper:
            # CTBC (Móvel/SMP) é ALGAR
            return 'ALGAR'
        elif 'VIVO' in operadora_upper:
            return 'VIVO'
        elif 'CLARO' in operadora_upper:
            return 'CLARO'
        elif 'OI' in operadora_upper:
            return 'OI'
        
        return operadora_upper
    
    def is_target_operadora(self, operadora):
        """Verifica se a operadora é uma das alvo (TIM ou Algar)"""
        if not operadora:
            return False
        return operadora.upper() in [op.upper() for op in self.target_operadoras]
    
    def verificar_disponibilidade(self, numero, operadora):
        """
        Verifica se o número está disponível para compra automática
        Retorna True se disponível, False caso contrário
        """
        # Esta verificação pode depender de APIs específicas
        # Por enquanto, retorna True se for TIM ou Algar
        if self.is_target_operadora(operadora):
            # Lógica adicional de verificação pode ser adicionada aqui
            return True
        return False


