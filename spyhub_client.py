"""
Cliente para consulta de números via SpyHub
Usa apenas web scraping (sem API)
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
import time
import re


class SpyHubClient:
    def __init__(self):
        self.url = config.SPYHUB_URL
        self.username = config.SPYHUB_USER
        self.password = config.SPYHUB_PASSWORD
        self.driver = None
        self.logged_in = False
    
    def _get_driver(self):
        """Inicializa driver Selenium"""
        if self.driver is None:
            chrome_options = Options()
            import os
            
            # Detecta ambiente Railway/Linux
            is_railway = bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_SERVICE_NAME'))
            is_linux = os.path.exists('/usr/bin/chromium') or os.path.exists('/usr/bin/chromium-browser')
            
            print(f"[DEBUG SpyHub] Ambiente detectado - Railway: {is_railway}, Linux: {is_linux}")
            
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
                print(f"[DEBUG SpyHub] Usando Chrome em: /usr/bin/chromium")
            elif os.path.exists('/usr/bin/chromium-browser'):
                chrome_options.binary_location = '/usr/bin/chromium-browser'
                print(f"[DEBUG SpyHub] Usando Chrome em: /usr/bin/chromium-browser")
            elif os.path.exists('/usr/bin/google-chrome'):
                chrome_options.binary_location = '/usr/bin/google-chrome'
                print(f"[DEBUG SpyHub] Usando Chrome em: /usr/bin/google-chrome")
            
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
                            print(f"[DEBUG SpyHub] Tentando usar ChromeDriver em: {chromedriver_path}")
                            service = Service(chromedriver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            print("[DEBUG SpyHub] ChromeDriver inicializado com sucesso!")
                            return self.driver
                        except Exception as e:
                            print(f"[DEBUG SpyHub] Erro ao usar {chromedriver_path}: {e}")
                            continue
            
            # Tenta diferentes métodos para obter o ChromeDriver
            driver_path = None
            
            # Método 1: Tenta usar webdriver-manager (pode falhar no Windows)
            try:
                driver_path = ChromeDriverManager().install()
                # Verifica se o arquivo existe e é válido
                import os
                if os.path.exists(driver_path) and os.path.getsize(driver_path) > 0:
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    return self.driver
            except Exception as e:
                print(f"Aviso: Erro ao usar webdriver-manager: {e}")
            
            # Método 2: Tenta usar ChromeDriver do PATH do sistema
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return self.driver
            except Exception as e:
                print(f"Aviso: Erro ao usar ChromeDriver do PATH: {e}")
            
            # Método 3: Tenta localizar ChromeDriver manualmente
            import os
            possible_paths = [
                os.path.join(os.getcwd(), 'chromedriver.exe'),
                os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', '*', 'chromedriver.exe'),
                'C:\\chromedriver\\chromedriver.exe',
                'C:\\Program Files\\chromedriver\\chromedriver.exe',
            ]
            
            for path in possible_paths:
                try:
                    if '*' in path:
                        import glob
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
            
            # Se nenhum método funcionou, lança erro
            raise Exception(
                "Não foi possível inicializar o ChromeDriver.\n"
                "Por favor, instale o ChromeDriver manualmente:\n"
                "1. Baixe de https://chromedriver.chromium.org/\n"
                "2. Coloque chromedriver.exe na pasta do projeto ou no PATH do sistema"
            )
        
        return self.driver
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def login(self):
        """Realiza login no SpyHub usando Selenium"""
        try:
            print("Fazendo login no SpyHub...")
            driver = self._get_driver()
            driver.get(f"{self.url}/login")
            time.sleep(2)
            
            wait = WebDriverWait(driver, 10)
            
            # Procura campo de email/usuário
            email_selectors = [
                "input[name*='email']",
                "input[name*='user']",
                "input[type='email']",
                "input[type='text']",
                "#email",
                "#username",
                "#user"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = driver.find_element(By.CSS_SELECTOR, selector)
                    if email_field.is_displayed():
                        break
                except:
                    continue
            
            if not email_field:
                print("Campo de email não encontrado")
                return False
            
            # Campo de senha
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Preenche campos
            email_field.clear()
            email_field.send_keys(self.username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)
            
            # Procura botão de submit
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Entrar')",
                "button:contains('Login')",
                ".btn-primary",
                "#login-button"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed():
                        break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
            else:
                password_field.send_keys("\n")
            
            time.sleep(3)
            
            # Verifica se login foi bem-sucedido
            current_url = driver.current_url.lower()
            if 'login' not in current_url or 'dashboard' in current_url or 'home' in current_url:
                self.logged_in = True
                print("Login no SpyHub realizado com sucesso!")
                return True
            else:
                print("Login no SpyHub pode ter falhado")
                return False
                
        except Exception as e:
            print(f"Erro ao fazer login no SpyHub: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def consultar_numeros_por_cpf(self, cpf):
        """
        Consulta números de telefone pelo CPF usando CONSULTA TRACKER
        Fluxo: Login -> Ir para CONSULTA TRACKER -> Clicar na aba CPF -> Preencher CPF -> 
               Rolar até TELEFONES -> Extrair TODOS os números do tipo TELEFONE MÓVEL
        Retorna lista de números móveis encontrados
        """
        if not self.logged_in:
            if not self.login():
                return []
        
        try:
            driver = self._get_driver()
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Passo 1: Acessar diretamente a página CONSULTA TRACKER
            tracker_url = f"{self.url}/search/tracker"
            print(f"    Acessando CONSULTA TRACKER: {tracker_url}")
            driver.get(tracker_url)
            time.sleep(3)  # Aguarda página carregar
            
            # Fecha popups que possam aparecer
            self._fechar_popups(driver)
            time.sleep(1)
            
            # Passo 2: Clicar na aba CPF
            print(f"    Clicando na aba CPF...")
            time.sleep(2)
            
            cpf_aba_encontrada = False
            cpf_aba_xpaths = [
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
                "//li[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
                "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cpf')]",
            ]
            
            for xpath in cpf_aba_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        if elem.is_displayed():
                            texto = elem.text.strip().lower()
                            if 'cpf' in texto:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(0.5)
                                elem.click()
                                print(f"    ✓ Aba CPF clicada")
                                cpf_aba_encontrada = True
                                time.sleep(2)
                                self._fechar_popups(driver)
                                break
                    if cpf_aba_encontrada:
                        break
                except:
                    continue
            
            if not cpf_aba_encontrada:
                print(f"    ⚠ Aba CPF não encontrada, tentando continuar...")
            
            # Passo 3: Preencher CPF
            print(f"    Preenchendo CPF: {cpf_limpo}...")
            time.sleep(2)
            
            # Procura campo de CPF
            cpf_selectors = [
                "input[name*='cpf']",
                "input[name*='document']",
                "input[type='text']",
                "input[placeholder*='CPF']",
                "input[placeholder*='cpf']",
                "#cpf",
                "#document",
                "input[id*='cpf']",
            ]
            
            cpf_field = None
            for selector in cpf_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            cpf_field = elem
                            print(f"    ✓ Campo de CPF encontrado")
                            break
                    if cpf_field:
                        break
                except:
                    continue
            
            if not cpf_field:
                print(f"    ⚠ Campo de CPF não encontrado")
                return []
            
            # Preenche o CPF
            cpf_field.clear()
            time.sleep(0.3)
            cpf_field.click()
            time.sleep(0.2)
            cpf_field.send_keys(cpf_limpo)
            time.sleep(0.5)
            
            # Procura botão de buscar/submit
            search_button = None
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.btn-primary",
                "button.btn-search",
                ".btn-search",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buscar')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pesquisar')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consultar')]",
            ]
            
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        buttons = driver.find_elements(By.XPATH, selector)
                    else:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for btn in buttons:
                        if btn.is_displayed():
                            search_button = btn
                            break
                    if search_button:
                        break
                except:
                    continue
            
            if search_button:
                search_button.click()
            else:
                # Tenta pressionar Enter
                cpf_field.send_keys("\n")
            
            print(f"    Buscando dados do CPF...")
            time.sleep(4)  # Aguarda dados carregarem
            
            # Fecha popups novamente
            self._fechar_popups(driver)
            
            # Passo 4: Rolar até TELEFONES e extrair TODOS os números móveis
            print(f"    Procurando seção 'TELEFONES'...")
            numeros_movels = self._extrair_todos_telefones_moveis(driver)
            
            print(f"    ✓ Encontrados {len(numeros_movels)} número(s) móvel(is): {numeros_movels}")
            
            time.sleep(1)  # Rate limiting
            return numeros_movels
            
        except Exception as e:
            print(f"Erro ao consultar números para CPF {cpf}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def consultar_numero_por_cpf(self, cpf):
        """
        Método de compatibilidade - retorna apenas o primeiro número encontrado
        """
        numeros = self.consultar_numeros_por_cpf(cpf)
        if numeros:
            return self._formatar_numero(numeros[0])
        return None
    
    def _extrair_todos_telefones_moveis(self, driver):
        """
        Rola até a seção TELEFONES e extrai TODOS os números do tipo TELEFONE MÓVEL
        Retorna lista de números móveis encontrados
        """
        numeros_movels = []
        
        try:
            print(f"    Procurando seção 'TELEFONES'...")
            
            # Procura pela seção "Telefones" ou "TELEFONES"
            telefones_encontrado = False
            telefones_element = None
            
            telefones_xpaths = [
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefones')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefone')]",
                "//h2[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefones')]",
                "//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefones')]",
                "//h4[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefones')]",
                "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telefones')]",
            ]
            
            for xpath in telefones_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        texto = elem.text.strip().lower()
                        if 'telefone' in texto:
                            # Scroll até o elemento
                            driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", elem)
                            time.sleep(1)
                            telefones_encontrado = True
                            telefones_element = elem
                            print(f"    ✓ Seção 'TELEFONES' encontrada")
                            break
                    if telefones_encontrado:
                        break
                except:
                    continue
            
            if not telefones_encontrado:
                print(f"    ⚠ Seção 'TELEFONES' não encontrada, fazendo scroll manual...")
                # Faz scroll gradual procurando pela seção
                for i in range(5):
                    driver.execute_script(f"window.scrollBy(0, {500 * (i+1)});")
                    time.sleep(0.5)
                    # Verifica novamente
                    for xpath in telefones_xpaths:
                        try:
                            elements = driver.find_elements(By.XPATH, xpath)
                            for elem in elements:
                                texto = elem.text.strip().lower()
                                if 'telefone' in texto:
                                    telefones_encontrado = True
                                    telefones_element = elem
                                    break
                            if telefones_encontrado:
                                break
                        except:
                            continue
                    if telefones_encontrado:
                        break
            
            # Obtém HTML da página
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procura tabela de telefones
            tabelas = soup.find_all('table')
            if not tabelas:
                # Procura divs que possam conter a lista
                tabelas = soup.find_all(['div', 'section'], class_=re.compile(r'table|list|telefone', re.I))
            
            # Procura TODOS os números móveis
            numeros_encontrados = set()  # Usa set para evitar duplicatas
            
            for tabela in tabelas:
                # Procura linhas (tr) ou itens (div, li)
                rows = tabela.find_all(['tr', 'div', 'li'])
                
                for row in rows:
                    texto_row = row.get_text().upper()
                    
                    # Verifica se contém "TELEFONE MÓVEL" ou "MÓVEL"
                    if 'TELEFONE MÓVEL' in texto_row or ('MÓVEL' in texto_row and 'TELEFONE' in texto_row):
                        # Extrai o número de telefone
                        texto_completo = row.get_text()
                        
                        # Procura padrões de telefone (DDD + número)
                        numero_matches = re.findall(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', texto_completo)
                        for numero_match in numero_matches:
                            # Remove formatação
                            numero_limpo = re.sub(r'[^\d]', '', numero_match)
                            
                            # Verifica se é número móvel (começa com 9 após DDD)
                            if len(numero_limpo) == 11 and numero_limpo[2] == '9':
                                numeros_encontrados.add(numero_limpo)
            
            # Se não encontrou em tabela, procura diretamente no texto da página
            if not numeros_encontrados:
                print(f"    Procurando telefones móveis no texto da página...")
                texto_pagina = driver.find_element(By.TAG_NAME, 'body').text
                
                # Procura padrões que indiquem telefone móvel
                linhas = texto_pagina.split('\n')
                for i, linha in enumerate(linhas):
                    linha_upper = linha.upper()
                    if 'TELEFONE MÓVEL' in linha_upper or ('MÓVEL' in linha_upper and 'TELEFONE' in linha_upper):
                        # Procura número nas linhas próximas (até 5 linhas antes e depois)
                        for j in range(max(0, i-5), min(len(linhas), i+6)):
                            numero_matches = re.findall(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', linhas[j])
                            for numero_match in numero_matches:
                                numero_limpo = re.sub(r'[^\d]', '', numero_match)
                                if len(numero_limpo) == 11 and numero_limpo[2] == '9':
                                    numeros_encontrados.add(numero_limpo)
            
            # Converte set para lista e formata
            numeros_movels = [self._formatar_numero(num) for num in numeros_encontrados if num]
            
            if numeros_movels:
                print(f"    ✓ Encontrados {len(numeros_movels)} número(s) móvel(is)")
            else:
                print(f"    ⚠ Nenhum telefone móvel encontrado")
            
            return numeros_movels
            
        except Exception as e:
            print(f"    Erro ao extrair telefones móveis: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extrair_telefone_movel(self, driver):
        """
        Método de compatibilidade - retorna apenas o primeiro número móvel encontrado
        """
        numeros = self._extrair_todos_telefones_moveis(driver)
        if numeros:
            return self._formatar_numero(numeros[0]) if numeros[0] else None
        return None
    
    def _fechar_popups(self, driver):
        """Fecha popups, modals e dialogs que aparecem na página"""
        try:
            popups_fechados = 0
            max_tentativas = 5
            
            for tentativa in range(max_tentativas):
                popup_encontrado = False
                
                close_selectors = [
                    "button[aria-label='Close']",
                    "button[aria-label='Fechar']",
                    "button.close",
                    ".close",
                    "[class*='close']",
                    "//button[contains(@class, 'close')]",
                    "//button[contains(@aria-label, 'Close')]",
                    ".modal-close",
                    "[data-dismiss='modal']",
                    "[data-bs-dismiss='modal']",
                ]
                
                for selector in close_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for elem in elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.2)
                                    elem.click()
                                    popup_encontrado = True
                                    popups_fechados += 1
                                    time.sleep(0.3)
                                    break
                            except:
                                continue
                        
                        if popup_encontrado:
                            break
                    except:
                        continue
                
                if not popup_encontrado:
                    break
                
                time.sleep(0.3)
            
        except Exception as e:
            pass
    
    def _formatar_numero(self, numero):
        """Formata número removendo caracteres especiais"""
        if not numero:
            return None
        # Remove tudo exceto dígitos
        numero_limpo = ''.join(filter(str.isdigit, str(numero)))
        # Verifica se tem tamanho válido (10 ou 11 dígitos)
        if len(numero_limpo) >= 10:
            return numero_limpo
        return None

