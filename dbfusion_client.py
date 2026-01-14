"""
Cliente para consulta na base de dados DBFusion
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
import platform

# Import para emitir som (Windows)
if platform.system() == 'Windows':
    try:
        import winsound
        SOUND_AVAILABLE = True
    except:
        SOUND_AVAILABLE = False
else:
    SOUND_AVAILABLE = False


class DBFusionClient:
    def __init__(self):
        self.url = config.DBFUSION_URL
        self.username = config.DBFUSION_USER
        self.password = config.DBFUSION_PASSWORD
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
            
            print(f"[DEBUG DBFusion] Ambiente detectado - Railway: {is_railway}, Linux: {is_linux}")
            print(f"[DEBUG DBFusion] PORT: {os.getenv('PORT')}, RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
            
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
            chrome_binary = None
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_binary = chrome_path
                    chrome_options.binary_location = chrome_binary
                    print(f"[DEBUG DBFusion] ✓ Chrome encontrado em: {chrome_binary}")
                    break
            
            if not chrome_binary:
                print("[DEBUG DBFusion] ⚠ Chrome não encontrado nos caminhos padrão, tentando usar do PATH")
                # Tenta encontrar via which
                import subprocess
                try:
                    result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
                    if result.returncode == 0:
                        chrome_binary = result.stdout.strip()
                        chrome_options.binary_location = chrome_binary
                        print(f"[DEBUG DBFusion] ✓ Chrome encontrado via PATH: {chrome_binary}")
                except:
                    pass
            
            # Tenta diferentes métodos para obter o ChromeDriver
            driver_path = None
            
            # Método 1: Em Linux/Railway, tenta usar ChromeDriver do sistema primeiro
            if is_linux:
                chromedriver_paths = [
                    '/usr/local/bin/chromedriver',  # Instalado pelo Dockerfile
                    '/usr/bin/chromedriver',
                    '/usr/lib/chromium-browser/chromedriver',
                ]
                
                for chromedriver_path in chromedriver_paths:
                    if os.path.exists(chromedriver_path):
                        try:
                            print(f"[DEBUG DBFusion] Tentando usar ChromeDriver em: {chromedriver_path}")
                            # Verifica permissões
                            import stat
                            if not os.access(chromedriver_path, os.X_OK):
                                print(f"[DEBUG DBFusion] Adicionando permissão de execução...")
                                os.chmod(chromedriver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                            
                            service = Service(chromedriver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            print(f"[DEBUG DBFusion] ✓ ChromeDriver inicializado com sucesso em: {chromedriver_path}")
                            return self.driver
                        except Exception as e:
                            print(f"[DEBUG DBFusion] ✗ Erro ao usar {chromedriver_path}: {e}")
                            import traceback
                            traceback.print_exc()
                            continue
            
            # Método 2: Tenta usar webdriver-manager
            try:
                print("[DEBUG] Tentando usar webdriver-manager...")
                driver_path = ChromeDriverManager().install()
                print(f"[DEBUG] ChromeDriver baixado em: {driver_path}")
                # Verifica se o arquivo existe e é válido
                if os.path.exists(driver_path):
                    file_size = os.path.getsize(driver_path)
                    if file_size > 100000:  # ChromeDriver deve ter pelo menos 100KB
                        service = Service(driver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        print("[DEBUG] ChromeDriver inicializado com sucesso via webdriver-manager!")
                        return self.driver
                    else:
                        print(f"[DEBUG] ChromeDriver baixado parece corrompido (tamanho: {file_size} bytes)")
            except Exception as e:
                print(f"[DEBUG] Erro ao usar webdriver-manager: {e}")
                import traceback
                traceback.print_exc()
            
            # Método 3: Tenta usar ChromeDriver do PATH do sistema
            try:
                print("[DEBUG] Tentando usar ChromeDriver do PATH...")
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("[DEBUG] ChromeDriver inicializado com sucesso do PATH!")
                return self.driver
            except Exception as e:
                print(f"[DEBUG] Erro ao usar ChromeDriver do PATH: {e}")
            
            # Método 3: Tenta localizar ChromeDriver manualmente (Windows e Linux)
            import os
            import platform
            possible_paths = []
            
            if platform.system() == 'Windows':
                possible_paths = [
                    os.path.join(os.getcwd(), 'chromedriver.exe'),
                    os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', 'win64', '*', 'chromedriver.exe'),
                    'C:\\chromedriver\\chromedriver.exe',
                    'C:\\Program Files\\chromedriver\\chromedriver.exe',
                ]
            else:
                # Linux (Railway, Render, etc)
                possible_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/usr/lib/chromium-browser/chromedriver',
                    os.path.join(os.getcwd(), 'chromedriver'),
                    os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver', '*', '*', 'chromedriver'),
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
    
    def _emitir_alerta_sonoro(self):
        """Emite alerta sonoro para chamar atenção do usuário"""
        try:
            if platform.system() == 'Windows' and SOUND_AVAILABLE:
                # Toca beep (frequência 1000 Hz, duração 300ms) - mais curto para repetição contínua
                winsound.Beep(1000, 300)
            else:
                # Fallback: apenas print se não conseguir emitir som
                print("\a", end='', flush=True)  # Caractere de beep ASCII
        except Exception as e:
            # Silencia erros para não interromper o loop
            pass
    
    def _detectar_captcha(self, driver):
        """Detecta se há CAPTCHA na página"""
        try:
            # Seletores comuns para CAPTCHA
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[src*='captcha']",
                "iframe[src*='google.com/recaptcha']",
                "div[class*='recaptcha']",
                "div[class*='captcha']",
                "div[id*='recaptcha']",
                "div[id*='captcha']",
                "//iframe[contains(@src, 'recaptcha')]",
                "//iframe[contains(@src, 'captcha')]",
                "//div[contains(@class, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//*[contains(text(), 'CAPTCHA')]",
                "//*[contains(text(), 'captcha')]",
                "//*[contains(text(), 'Não sou um robô')]",
            ]
            
            for selector in captcha_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                # Verifica se está visível na página
                                location = elem.location
                                size = elem.size
                                if location['x'] >= 0 and location['y'] >= 0 and size['width'] > 0 and size['height'] > 0:
                                    return True
                        except:
                            continue
                except:
                    continue
            
            # Verifica no texto da página também
            try:
                page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
                if 'captcha' in page_text or 'não sou um robô' in page_text or 'recaptcha' in page_text:
                    return True
            except:
                pass
            
            return False
        except Exception as e:
            return False
    
    def _aguardar_captcha_resolvido(self, driver, timeout=300):
        """
        Aguarda até que o CAPTCHA seja resolvido pelo usuário
        timeout: tempo máximo de espera em segundos (padrão 5 minutos)
        Emite som continuamente até o CAPTCHA ser resolvido
        """
        print("\n" + "="*60)
        print("⚠️  CAPTCHA DETECTADO!")
        print("="*60)
        print("🛑 O PROCESSAMENTO FOI PAUSADO")
        print("📝 Por favor, resolva o CAPTCHA no navegador")
        print("🔊 Alerta sonoro contínuo será emitido até resolver...")
        print("="*60 + "\n")
        
        # Aguarda até que o CAPTCHA seja resolvido
        inicio = time.time()
        captcha_resolvido = False
        contador_verificacao = 0
        
        while time.time() - inicio < timeout:
            # Verifica se ainda há CAPTCHA
            if not self._detectar_captcha(driver):
                captcha_resolvido = True
                break
            
            # Emite alerta sonoro continuamente (a cada 2 segundos)
            self._emitir_alerta_sonoro()
            
            # Mostra status a cada 10 segundos
            tempo_decorrido = int(time.time() - inicio)
            if contador_verificacao % 5 == 0:  # A cada 5 verificações (10 segundos)
                print(f"⏳ Aguardando resolução do CAPTCHA... ({tempo_decorrido}s)")
            
            contador_verificacao += 1
            time.sleep(2)  # Verifica a cada 2 segundos
        
        if captcha_resolvido:
            print("\n" + "="*60)
            print("✅ CAPTCHA RESOLVIDO!")
            print("🔄 Continuando processamento...")
            print("="*60 + "\n")
            time.sleep(2)  # Aguarda um pouco após resolver
            return True
        else:
            print("\n" + "="*60)
            print("⏱️  TIMEOUT: CAPTCHA não foi resolvido no tempo limite")
            print("🔄 Tentando continuar mesmo assim...")
            print("="*60 + "\n")
            return False
    
    def _fechar_popups(self, driver):
        """Fecha popups, modals e dialogs que aparecem na página"""
        try:
            print("  Fechando popups/modal...")
            
            # Verifica CAPTCHA antes de fechar popups
            if self._detectar_captcha(driver):
                self._aguardar_captcha_resolvido(driver)
            
            popups_fechados = 0
            max_tentativas = 10  # Limite de tentativas para evitar loop infinito
            
            for tentativa in range(max_tentativas):
                popup_encontrado = False
                
                # Seletores para botões de fechar (X)
                close_selectors = [
                    # Botões de fechar comuns
                    "button[aria-label='Close']",
                    "button[aria-label='Fechar']",
                    "button.close",
                    ".close",
                    "[class*='close']",
                    "[class*='Close']",
                    "button[class*='close']",
                    # XPath para elementos com X
                    "//button[contains(@class, 'close')]",
                    "//button[contains(@aria-label, 'Close')]",
                    "//button[contains(@aria-label, 'Fechar')]",
                    "//span[contains(@class, 'close')]",
                    "//*[contains(@class, 'close') and contains(text(), '×')]",
                    "//*[contains(@class, 'close') and contains(text(), '✕')]",
                    "//*[contains(@class, 'close') and contains(text(), 'X')]",
                    # Modal close buttons
                    ".modal-close",
                    ".modal .close",
                    "[data-dismiss='modal']",
                    "[data-bs-dismiss='modal']",
                    "//button[@data-dismiss='modal']",
                    "//button[@data-bs-dismiss='modal']",
                    # Overlay/backdrop close
                    ".overlay .close",
                    ".backdrop .close",
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
                                    # Scroll até o elemento
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.2)
                                    elem.click()
                                    popup_encontrado = True
                                    popups_fechados += 1
                                    print(f"    ✓ Popup fechado (tentativa {tentativa + 1})")
                                    time.sleep(0.5)  # Aguarda popup fechar
                                    break
                            except:
                                continue
                        
                        if popup_encontrado:
                            break
                    except:
                        continue
                
                # Se não encontrou popup nesta tentativa, para
                if not popup_encontrado:
                    break
                
                # Aguarda um pouco antes da próxima tentativa
                time.sleep(0.5)
            
            if popups_fechados > 0:
                print(f"  ✓ Total de {popups_fechados} popup(s) fechado(s)")
            else:
                print("  Nenhum popup encontrado para fechar")
                
        except Exception as e:
            print(f"  Erro ao fechar popups: {e}")
    
    def login(self):
        """Realiza login na plataforma DBFusion usando Selenium"""
        try:
            print("Fazendo login no DBFusion...")
            driver = self._get_driver()
            driver.get(self.url)
            time.sleep(2)  # Aguarda carregar
            
            # Tenta encontrar campos de login
            wait = WebDriverWait(driver, 10)
            
            # Procura campo de usuário
            username_selectors = [
                "input[name*='user']",
                "input[name*='login']",
                "input[name*='email']",
                "input[type='text']",
                "input[type='email']",
                "#username",
                "#user",
                "#email",
                "#login"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = driver.find_element(By.CSS_SELECTOR, selector)
                    if username_field.is_displayed():
                        break
                except:
                    continue
            
            if not username_field:
                print("Campo de usuário não encontrado")
                return False
            
            # Procura campo de senha
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Preenche campos
            username_field.clear()
            username_field.send_keys(self.username)
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
                # Tenta pressionar Enter no campo de senha
                password_field.send_keys("\n")
            
            # Aguarda redirecionamento ou mudança de página
            time.sleep(3)
            
            # Verifica se apareceu CAPTCHA após tentar login
            if self._detectar_captcha(driver):
                self._aguardar_captcha_resolvido(driver)
            
            # Fecha popups/modal que possam aparecer após login
            self._fechar_popups(driver)
            
            # Verifica se login foi bem-sucedido
            current_url = driver.current_url.lower()
            if 'login' not in current_url or 'dashboard' in current_url or 'home' in current_url:
                self.logged_in = True
                print("Login realizado com sucesso!")
                return True
            else:
                # Verifica se há mensagem de erro
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .alert-danger")
                    if error_elements:
                        print(f"Erro no login: {error_elements[0].text}")
                except:
                    pass
                print("Login pode ter falhado")
                return False
            
        except Exception as e:
            print(f"Erro ao fazer login no DBFusion: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_pessoas_by_bin(self, bin_number, limit=None):
        """
        Busca pessoas filtradas por BIN usando web scraping
        Retorna lista de dicionários com informações das pessoas
        Lida com paginação se houver múltiplos registros
        
        Args:
            bin_number: BIN para filtrar
            limit: Limite de registros a retornar (None = todos)
        """
        if not self.logged_in:
            if not self.login():
                return []
        
        try:
            print(f"Buscando registros com BIN: {bin_number}")
            if limit:
                print(f"  Limite: {limit} registros (modo teste)")
            pessoas = self._scrape_pessoas(bin_number, limit=limit)
            print(f"Encontrados {len(pessoas)} registros via scraping")
            return pessoas
                
        except Exception as e:
            print(f"Erro ao buscar pessoas: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _scrape_pessoas(self, bin_number, limit=None):
        """
        Busca pessoas usando web scraping com Selenium
        Fluxo: Login -> Clicar em "Loja" -> Clicar em "BIN" -> Preencher filtro -> Extrair tabela
        Lida com paginação para pegar TODOS os registros (ou até o limite se especificado)
        
        Args:
            bin_number: BIN para filtrar
            limit: Limite de registros a retornar (None = todos)
        """
        todas_pessoas = []
        driver = self._get_driver()
        
        try:
            print("Navegando para a seção de BIN...")
            wait = WebDriverWait(driver, 10)
            
            # Verifica CAPTCHA antes de começar
            if self._detectar_captcha(driver):
                self._aguardar_captcha_resolvido(driver)
            
            # Passo 1: Clicar em "Loja"
            print("  Passo 1: Clicando em 'Loja'...")
            loja_encontrado = False
            
            # Tenta diferentes formas de encontrar o link/botão "Loja"
            # XPath é mais confiável para buscar por texto
            loja_xpaths = [
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//li[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
            ]
            
            # CSS Selectors para href e classes
            loja_css = [
                "a[href*='loja']",
                "a[href*='Loja']",
                "[class*='loja']",
                "[id*='loja']",
            ]
            
            # Tenta XPath primeiro (mais confiável para texto)
            for xpath in loja_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            texto = elem.text.strip().lower()
                            if 'loja' in texto and elem.is_displayed():
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(0.5)
                                elem.click()
                                print(f"    ✓ 'Loja' clicado (XPath)")
                                loja_encontrado = True
                        except Exception as e:
                            continue
                    if loja_encontrado:
                        break
                except:
                    continue
            
            # Se não encontrou com XPath, tenta CSS
            if not loja_encontrado:
                for css in loja_css:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, css)
                        for elem in elements:
                            try:
                                if elem.is_displayed():
                                    texto = elem.text.strip().lower()
                                    if not texto or 'loja' in texto:
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                        time.sleep(0.5)
                                        elem.click()
                                        print(f"    ✓ 'Loja' clicado (CSS: {css})")
                                        loja_encontrado = True
                                        time.sleep(2)
                                        # Fecha popups que possam aparecer
                                        self._fechar_popups(driver)
                                        time.sleep(1)
                                        break
                            except:
                                continue
                        if loja_encontrado:
                            break
                    except:
                        continue
            
            if not loja_encontrado:
                print("    ⚠ Não foi possível encontrar 'Loja', tentando continuar...")
            
            # Passo 2: Clicar em "BIN"
            print("  Passo 2: Clicando em 'BIN'...")
            bin_encontrado = False
            
            # XPath para buscar por texto (case-insensitive)
            bin_xpaths = [
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//li[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
            ]
            
            # CSS Selectors
            bin_css = [
                "a[href*='bin']",
                "a[href*='BIN']",
                "[class*='bin']",
                "[id*='bin']",
            ]
            
            # Tenta XPath primeiro
            for xpath in bin_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            texto = elem.text.strip().upper()
                            # Verifica se contém "BIN" e não é parte de outra palavra
                            if ('BIN' in texto or 'bin' in texto.lower()) and elem.is_displayed():
                                # Verifica se não é parte de outra palavra (ex: "COMBINAR")
                                texto_lower = texto.lower()
                                if texto_lower == 'bin' or ' bin ' in f' {texto_lower} ' or texto_lower.startswith('bin ') or texto_lower.endswith(' bin'):
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.5)
                                    elem.click()
                                    print(f"    ✓ 'BIN' clicado (XPath)")
                                    bin_encontrado = True
                                    time.sleep(2)  # Aguarda carregar página de BIN
                                    
                                    # Verifica CAPTCHA após clicar em BIN
                                    if self._detectar_captcha(driver):
                                        self._aguardar_captcha_resolvido(driver)
                                    
                                    # Fecha popups que possam aparecer
                                    self._fechar_popups(driver)
                                    time.sleep(1)
                                    break
                        except Exception as e:
                            continue
                    if bin_encontrado:
                        break
                except:
                    continue
            
            # Se não encontrou com XPath, tenta CSS
            if not bin_encontrado:
                for css in bin_css:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, css)
                        for elem in elements:
                            try:
                                if elem.is_displayed():
                                    texto = elem.text.strip().upper()
                                    if not texto or 'BIN' in texto:
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                        time.sleep(0.5)
                                        elem.click()
                                        print(f"    ✓ 'BIN' clicado (CSS: {css})")
                                        bin_encontrado = True
                                        time.sleep(2)
                                        # Fecha popups que possam aparecer
                                        self._fechar_popups(driver)
                                        time.sleep(1)
                                        break
                            except:
                                continue
                        if bin_encontrado:
                            break
                    except:
                        continue
            
            if not bin_encontrado:
                print("    ⚠ Não foi possível encontrar 'BIN', tentando continuar...")
            
            # Passo 3: Encontrar campo de filtro e preencher com BIN
            print(f"  Passo 3: Preenchendo filtro com BIN: {bin_number}...")
            time.sleep(3)  # Aguarda página carregar completamente
            
            # Fecha popups antes de procurar o filtro
            self._fechar_popups(driver)
            time.sleep(1)
            
            # Procura campo de filtro - tenta múltiplas estratégias
            filter_field = None
            
            # Estratégia 1: Busca por atributos específicos (case-insensitive usando XPath)
            filter_selectors_xpath = [
                "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filter')]",
                "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filtro')]",
                "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filtro')]",
                "//input[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//input[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filter')]",
            ]
            
            for xpath in filter_selectors_xpath:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            filter_field = elem
                            print(f"    ✓ Campo de filtro encontrado (XPath: {xpath[:50]}...)")
                            break
                    if filter_field:
                        break
                except:
                    continue
            
            # Estratégia 2: Busca por CSS selectors (case-sensitive, mas tenta variações)
            if not filter_field:
                filter_selectors_css = [
                    "input[name*='bin']",
                    "input[name*='BIN']",
                    "input[name*='filter']",
                    "input[name*='Filter']",
                    "input[name*='filtro']",
                    "input[placeholder*='BIN']",
                    "input[placeholder*='bin']",
                    "input[placeholder*='Filtro']",
                    "input[placeholder*='filtro']",
                    "input[id*='bin']",
                    "input[id*='BIN']",
                    "input[id*='filter']",
                    "input[class*='filter']",
                    "input[class*='search']",
                ]
                
                for selector in filter_selectors_css:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                location = elem.location
                                size = elem.size
                                if location['y'] >= 0 and size['height'] > 0:
                                    filter_field = elem
                                    print(f"    ✓ Campo de filtro encontrado (CSS: {selector})")
                                    break
                        if filter_field:
                            break
                    except:
                        continue
            
            # Estratégia 3: Busca todos os inputs e verifica qual parece ser o campo de filtro
            if not filter_field:
                try:
                    all_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search'], input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='checkbox']):not([type='radio'])")
                    print(f"    Encontrados {len(all_inputs)} campos de input na página")
                    
                    for inp in all_inputs:
                        try:
                            if inp.is_displayed() and inp.is_enabled():
                                # Verifica atributos que indicam campo de filtro
                                name = (inp.get_attribute('name') or '').lower()
                                placeholder = (inp.get_attribute('placeholder') or '').lower()
                                input_id = (inp.get_attribute('id') or '').lower()
                                classes = (inp.get_attribute('class') or '').lower()
                                
                                # Se tem alguma indicação de ser filtro/busca
                                if any(keyword in name + placeholder + input_id + classes 
                                      for keyword in ['bin', 'filter', 'filtro', 'search', 'buscar', 'pesquisar']):
                                    filter_field = inp
                                    print(f"    ✓ Campo de filtro encontrado por análise de atributos (name: {name}, id: {input_id})")
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"    Erro ao buscar inputs: {e}")
            
            # Estratégia 4: Se ainda não encontrou, pega o primeiro input visível próximo ao topo da página
            if not filter_field:
                try:
                    visible_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
                    # Ordena por posição Y (mais próximo do topo primeiro)
                    visible_inputs.sort(key=lambda x: x.location['y'] if x.is_displayed() else 9999)
                    for inp in visible_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            filter_field = inp
                            print(f"    ✓ Usando primeiro campo de texto visível como filtro (Y: {inp.location['y']})")
                            break
                except Exception as e:
                    print(f"    Erro ao buscar primeiro input: {e}")
            
            if filter_field:
                print(f"    Campo de filtro encontrado! Aplicando BIN: {bin_number}")
                
                # Scroll até o campo
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter_field)
                    time.sleep(0.5)
                except:
                    pass
                
                # Limpa o campo e preenche
                try:
                    # Foca no campo primeiro
                    filter_field.click()
                    time.sleep(0.3)
                    
                    # Seleciona todo o conteúdo e apaga (Ctrl+A, Delete)
                    from selenium.webdriver.common.keys import Keys
                    filter_field.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.2)
                    filter_field.send_keys(Keys.DELETE)
                    time.sleep(0.2)
                    
                    # Limpa novamente usando clear()
                    filter_field.clear()
                    time.sleep(0.3)
                    
                    # Foca novamente
                    filter_field.click()
                    time.sleep(0.2)
                    
                    # Preenche o BIN completo de uma vez
                    bin_str = str(bin_number)
                    print(f"    Tentando preencher BIN completo: '{bin_str}'")
                    filter_field.send_keys(bin_str)
                    time.sleep(0.5)
                    
                    # Verifica se o valor foi preenchido
                    valor_preenchido = filter_field.get_attribute('value')
                    print(f"    Valor no campo após preenchimento: '{valor_preenchido}'")
                    
                    # Se não preencheu corretamente, tenta método alternativo
                    if valor_preenchido != bin_str:
                        print(f"    ⚠ Valor não corresponde. Tentando método alternativo...")
                        
                        # Método alternativo: usar JavaScript para definir o valor
                        try:
                            driver.execute_script("arguments[0].value = arguments[1];", filter_field, bin_str)
                            time.sleep(0.3)
                            
                            # Dispara eventos para garantir que o campo reconheça a mudança
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", filter_field)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", filter_field)
                            time.sleep(0.3)
                            
                            valor_preenchido = filter_field.get_attribute('value')
                            print(f"    Valor após JavaScript: '{valor_preenchido}'")
                        except Exception as e:
                            print(f"    Erro ao usar JavaScript: {e}")
                        
                        # Se ainda não funcionou, tenta digitar novamente
                        if valor_preenchido != bin_str:
                            filter_field.clear()
                            time.sleep(0.2)
                            filter_field.click()
                            time.sleep(0.2)
                            
                            # Digita caractere por caractere mais devagar
                            for i, char in enumerate(bin_str):
                                filter_field.send_keys(char)
                                time.sleep(0.1)
                                # Verifica após cada caractere
                                valor_atual = filter_field.get_attribute('value')
                                if valor_atual and len(valor_atual) < i + 1:
                                    print(f"    ⚠ Caractere {i+1} não foi digitado. Tentando novamente...")
                                    filter_field.send_keys(char)
                                    time.sleep(0.1)
                            
                            valor_preenchido = filter_field.get_attribute('value')
                            print(f"    Valor após digitação caractere por caractere: '{valor_preenchido}'")
                    
                    if valor_preenchido == bin_str:
                        print(f"    ✓ BIN '{bin_number}' digitado corretamente no campo de filtro")
                    else:
                        print(f"    ⚠ ATENÇÃO: Valor no campo ('{valor_preenchido}') não corresponde ao BIN esperado ('{bin_number}')")
                        print(f"    Continuando mesmo assim...")
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"    Erro ao preencher campo: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Procura botão de aplicar filtro ou pressiona Enter
                filtro_aplicado = False
                
                # Tenta encontrar botão de filtrar/buscar primeiro
                button_selectors = [
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filtrar')]",
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buscar')]",
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aplicar')]",
                    "//input[@type='submit' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'filtrar')]",
                    "button[type='submit']",
                    ".btn-filter",
                    ".btn-primary",
                    "input[type='submit']",
                ]
                
                for btn_selector in button_selectors:
                    try:
                        if btn_selector.startswith("//"):
                            buttons = driver.find_elements(By.XPATH, btn_selector)
                        else:
                            buttons = driver.find_elements(By.CSS_SELECTOR, btn_selector)
                        
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                time.sleep(0.3)
                                btn.click()
                                print(f"    ✓ Botão de filtro clicado")
                                filtro_aplicado = True
                                time.sleep(4)  # Aguarda filtro ser aplicado
                                break
                        if filtro_aplicado:
                            break
                    except Exception as e:
                        continue
                
                # Se não encontrou botão, tenta pressionar Enter
                if not filtro_aplicado:
                    try:
                        from selenium.webdriver.common.keys import Keys
                        filter_field.send_keys(Keys.RETURN)
                        print("    ✓ Filtro aplicado (Enter/Return pressionado)")
                        time.sleep(4)  # Aguarda filtro ser aplicado
                        filtro_aplicado = True
                    except Exception as e:
                        try:
                            filter_field.send_keys("\n")
                            print("    ✓ Filtro aplicado (\\n enviado)")
                            time.sleep(4)
                            filtro_aplicado = True
                        except Exception as e2:
                            print(f"    ⚠ Erro ao pressionar Enter: {e2}")
                
                # Verifica se apareceu CAPTCHA após aplicar filtro
                if self._detectar_captcha(driver):
                    self._aguardar_captcha_resolvido(driver)
                
                # Fecha popups que possam aparecer após aplicar filtro
                self._fechar_popups(driver)
                time.sleep(1)
                
                # Verifica se o filtro foi aplicado verificando se a URL mudou ou se há resultados
                if filtro_aplicado:
                    print("    ✓ Filtro aplicado com sucesso")
                else:
                    print("    ⚠ Aviso: Não foi possível confirmar se o filtro foi aplicado")
            else:
                print("    ⚠ ERRO CRÍTICO: Campo de filtro não encontrado!")
                print("    O filtro por BIN NÃO será aplicado e podem retornar resultados incorretos.")
                print("    Verifique se a página carregou corretamente e se o elemento 'BIN' foi clicado.")
            
            # Passo 4: Configurar paginação para 200 registros por página
            print("  Passo 4: Configurando paginação para 200 registros por página...")
            time.sleep(2)  # Aguarda página carregar após aplicar filtro
            
            # Fecha popups que possam aparecer
            self._fechar_popups(driver)
            
            # Procura o seletor de paginação (50, 100, 200)
            paginacao_200_encontrada = False
            
            # Seletores para encontrar o seletor de paginação
            paginacao_selectors = [
                # XPath para elementos que contêm "200"
                "//select[contains(@class, 'pagination')]",
                "//select[contains(@name, 'per_page')]",
                "//select[contains(@name, 'perPage')]",
                "//select[contains(@name, 'limit')]",
                "//select[contains(@id, 'pagination')]",
                "//select[contains(@id, 'per_page')]",
                "//select[contains(@id, 'limit')]",
                "//select",
                # CSS Selectors
                "select.pagination",
                "select[name*='per_page']",
                "select[name*='perPage']",
                "select[name*='limit']",
                "select[id*='pagination']",
                "select[id*='per_page']",
                "select[id*='limit']",
            ]
            
            for selector in paginacao_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for select_elem in elements:
                        try:
                            if select_elem.is_displayed():
                                # Tenta selecionar a opção 200
                                from selenium.webdriver.support.ui import Select
                                select = Select(select_elem)
                                
                                # Tenta encontrar opção 200
                                try:
                                    select.select_by_value("200")
                                    paginacao_200_encontrada = True
                                    print(f"    ✓ Paginação configurada para 200 registros (por value)")
                                    time.sleep(2)  # Aguarda página recarregar
                                    break
                                except:
                                    try:
                                        select.select_by_visible_text("200")
                                        paginacao_200_encontrada = True
                                        print(f"    ✓ Paginação configurada para 200 registros (por texto)")
                                        time.sleep(2)
                                        break
                                    except:
                                        # Tenta encontrar opção que contém "200"
                                        options = select.options
                                        for option in options:
                                            if "200" in option.text or "200" in option.get_attribute('value'):
                                                select.select_by_visible_text(option.text)
                                                paginacao_200_encontrada = True
                                                print(f"    ✓ Paginação configurada para 200 registros (opção: {option.text})")
                                                time.sleep(2)
                                                break
                                        if paginacao_200_encontrada:
                                            break
                        except:
                            continue
                    
                    if paginacao_200_encontrada:
                        break
                except:
                    continue
            
            # Se não encontrou select, tenta encontrar botões/links com "200"
            if not paginacao_200_encontrada:
                print("    Tentando encontrar botão/link de paginação 200...")
                paginacao_buttons = [
                    "//a[contains(text(), '200')]",
                    "//button[contains(text(), '200')]",
                    "//span[contains(text(), '200')]",
                    "//*[contains(@class, 'pagination')]//*[contains(text(), '200')]",
                ]
                
                for xpath in paginacao_buttons:
                    try:
                        elements = driver.find_elements(By.XPATH, xpath)
                        for elem in elements:
                            try:
                                if elem.is_displayed():
                                    texto = elem.text.strip()
                                    if "200" in texto:
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                        time.sleep(0.5)
                                        elem.click()
                                        paginacao_200_encontrada = True
                                        print(f"    ✓ Paginação configurada para 200 registros (botão/link)")
                                        time.sleep(2)
                                        break
                            except:
                                continue
                        if paginacao_200_encontrada:
                            break
                    except:
                        continue
            
            if not paginacao_200_encontrada:
                print("    ⚠ Não foi possível configurar paginação para 200, continuando com padrão...")
            
            # Fecha popups novamente após mudar paginação
            self._fechar_popups(driver)
            
            # Passo 5: Aguarda tabela carregar e extrai registros
            print("  Passo 5: Aguardando tabela carregar...")
            time.sleep(2)  # Aguarda tabela carregar após mudar paginação
            
            # Verifica se tabela carregou
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                print("    ✓ Tabela encontrada")
            except:
                print("    ⚠ Tabela não encontrada, tentando continuar...")
            
            # Agora extrai os registros com paginação
            pagina = 1
            while True:
                print(f"\nExtraindo registros da página {pagina}...")
                
                # Verifica se apareceu CAPTCHA antes de extrair
                if self._detectar_captcha(driver):
                    self._aguardar_captcha_resolvido(driver)
                
                # Aguarda um pouco para garantir que carregou
                time.sleep(2)
                
                # Extrai registros da página atual
                pessoas_pagina = self._extrair_registros_pagina(driver)
                
                if not pessoas_pagina:
                    print(f"  Nenhum registro encontrado na página {pagina}")
                    # Se é a primeira página e não encontrou nada, pode ser que o filtro não funcionou
                    if pagina == 1:
                        print("  ⚠ Nenhum resultado na primeira página. Verifique se o filtro foi aplicado corretamente.")
                    break
                
                todas_pessoas.extend(pessoas_pagina)
                print(f"  ✓ Página {pagina}: {len(pessoas_pagina)} registros encontrados")
                
                # Verifica se atingiu o limite
                if limit and len(todas_pessoas) >= limit:
                    todas_pessoas = todas_pessoas[:limit]
                    print(f"  Limite de {limit} registros atingido. Parando busca.")
                    break
                
                # Verifica se apareceu CAPTCHA antes de ir para próxima página
                if self._detectar_captcha(driver):
                    self._aguardar_captcha_resolvido(driver)
                
                # Verifica se há próxima página
                if not self._ir_proxima_pagina(driver):
                    print(f"  Não há mais páginas. Total: {len(todas_pessoas)} registros")
                    break
                
                # Verifica CAPTCHA após ir para próxima página
                if self._detectar_captcha(driver):
                    self._aguardar_captcha_resolvido(driver)
                
                pagina += 1
                time.sleep(1)
            
            return todas_pessoas
            
        except Exception as e:
            print(f"Erro no web scraping: {e}")
            import traceback
            traceback.print_exc()
            return todas_pessoas
    
    def _verifica_resultados_carregados(self, driver):
        """Verifica se a página carregou resultados"""
        try:
            # Procura por tabela ou lista de resultados
            selectors = [
                "table",
                ".table",
                ".data-table",
                ".results",
                "tbody tr",
                ".list-group",
                ".card",
                "[class*='row']",
                "[class*='item']",
                "[class*='registro']",
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        print(f"Elementos encontrados com seletor '{selector}': {len(elements)}")
                        return True
                except:
                    continue
            
            # Verifica se há texto na página que indica resultados
            page_text = driver.page_source.lower()
            if 'cpf' in page_text or 'registro' in page_text or 'dados' in page_text:
                print("Página parece ter conteúdo relevante")
                return True
            
            return False
        except Exception as e:
            print(f"Erro ao verificar resultados: {e}")
            return False
    
    def _extrair_registros_pagina(self, driver):
        """Extrai registros da página atual"""
        pessoas = []
        
        try:
            # Aguarda um pouco para garantir que a página carregou
            time.sleep(2)
            
            # Obtém HTML da página
            html = driver.page_source
            
            # Salva HTML para debug (opcional)
            # with open('debug_html.html', 'w', encoding='utf-8') as f:
            #     f.write(html)
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Método 1: Tenta encontrar tabela
            tabelas = soup.find_all('table')
            if not tabelas:
                # Tenta encontrar por classe
                tabelas = soup.find_all('table', class_=re.compile(r'data|table|list|result', re.I))
            
            if tabelas:
                print(f"Encontradas {len(tabelas)} tabela(s)")
                for tabela in tabelas:
                    rows = tabela.find_all('tr')
                    print(f"  Tabela tem {len(rows)} linhas")
                    
                    # Pula cabeçalho (primeira linha)
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 1:  # Pelo menos 1 célula
                            pessoa = self._extrair_pessoa_de_celulas(cells)
                            if pessoa and 'cpf' in pessoa:
                                pessoas.append(pessoa)
            
            # Método 2: Se não encontrou tabela, tenta cards/divs/listas
            if not pessoas:
                print("Tentando extrair de cards/divs...")
                
                # Procura por diferentes estruturas
                estruturas = [
                    soup.find_all('div', class_=re.compile(r'card|item|row|registro|result', re.I)),
                    soup.find_all('li', class_=re.compile(r'item|row|registro', re.I)),
                    soup.find_all('tr', class_=re.compile(r'row|item|registro', re.I)),
                    soup.find_all('div', {'data-cpf': True}),
                ]
                
                for estrutura in estruturas:
                    if estrutura:
                        print(f"Encontrados {len(estrutura)} elementos")
                        for elem in estrutura:
                            # Procura CPF no texto do elemento
                            texto = elem.get_text()
                            cpf_match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', texto)
                            if cpf_match:
                                pessoa = {
                                    'cpf': cpf_match.group().replace('.', '').replace('-', ''),
                                    'bin': config.TARGET_BIN
                                }
                                # Tenta extrair nome
                                linhas = texto.split('\n')
                                for linha in linhas:
                                    linha = linha.strip()
                                    if linha and not re.match(r'^\d+$', linha) and len(linha) > 3:
                                        pessoa['nome'] = linha
                                        break
                                pessoas.append(pessoa)
                        if pessoas:
                            break
            
            # Método 3: Busca CPFs diretamente no texto da página
            if not pessoas:
                print("Buscando CPFs diretamente no texto da página...")
                texto_pagina = soup.get_text()
                cpfs_encontrados = re.findall(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', texto_pagina)
                cpfs_unicos = list(set(cpfs_encontrados))
                print(f"Encontrados {len(cpfs_unicos)} CPFs no texto")
                
                for cpf_formatado in cpfs_unicos:
                    cpf_limpo = cpf_formatado.replace('.', '').replace('-', '')
                    # Verifica se é um CPF válido (não é só números sequenciais)
                    if len(set(cpf_limpo)) > 3:  # CPF válido tem pelo menos 4 dígitos diferentes
                        pessoa = {
                            'cpf': cpf_limpo,
                            'bin': config.TARGET_BIN
                        }
                        pessoas.append(pessoa)
        
        except Exception as e:
            print(f"Erro ao extrair registros: {e}")
            import traceback
            traceback.print_exc()
        
        return pessoas
    
    def _extrair_pessoa_de_celulas(self, cells):
        """Extrai informações de pessoa de células de tabela"""
        pessoa = {}
        
        # Extrai CPF
        for cell in cells:
            text = cell.text.strip()
            # Procura CPF formatado
            cpf_match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', text)
            if cpf_match:
                pessoa['cpf'] = cpf_match.group().replace('.', '').replace('-', '')
                break
        
        # Se não encontrou CPF formatado, tenta números de 11 dígitos
        if 'cpf' not in pessoa:
            for cell in cells[:10]:  # Verifica até 10 células
                text = cell.text.strip().replace('.', '').replace('-', '').replace(' ', '')
                # CPF tem exatamente 11 dígitos
                if re.match(r'^\d{11}$', text):
                    # Verifica se não é só números repetidos
                    if len(set(text)) > 3:
                        pessoa['cpf'] = text
                        break
        
        # Extrai nome (texto que não é número e tem mais de 3 caracteres)
        if 'cpf' in pessoa:
            for cell in cells:
                text = cell.text.strip()
                # Ignora números, CPF, e textos muito curtos
                if (not re.match(r'^\d+$', text) and 
                    'cpf' not in text.lower() and 
                    len(text) > 3 and
                    len(text) < 100):  # Nome não deve ser muito longo
                    pessoa['nome'] = text
                    break
            
            pessoa['bin'] = config.TARGET_BIN
        
        return pessoa if 'cpf' in pessoa else None
    
    def _ir_proxima_pagina(self, driver):
        """Tenta ir para próxima página, retorna True se conseguiu"""
        try:
            # Procura botão/link de próxima página usando múltiplos métodos
            next_selectors = [
                # XPath (mais confiável para texto)
                "//a[contains(text(), 'Próxima')]",
                "//a[contains(text(), 'Próximo')]",
                "//a[contains(text(), 'Next')]",
                "//button[contains(text(), 'Próxima')]",
                "//button[contains(text(), 'Next')]",
                "//a[@aria-label='Next']",
                "//a[@aria-label='Próxima']",
                # CSS Selectors
                ".pagination .next",
                ".pagination a.next",
                ".pagination button.next",
                "a.pagination-next",
                "button.pagination-next",
                "[class*='next']",
                "[class*='pagination-next']",
                # Números de página
                "//a[contains(@class, 'page-link') and contains(text(), '>')]",
                "//button[contains(@class, 'page-link') and contains(text(), '>')]",
            ]
            
            for selector in next_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for next_button in elements:
                        try:
                            if next_button.is_displayed():
                                # Verifica se não está desabilitado
                                classes = next_button.get_attribute('class') or ''
                                disabled = next_button.get_attribute('disabled')
                                
                                if 'disabled' not in classes.lower() and disabled is None:
                                    # Scroll até o botão
                                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                                    time.sleep(0.5)
                                    next_button.click()
                                    time.sleep(2)  # Aguarda próxima página carregar
                                    print(f"    → Próxima página (seletor: {selector})")
                                    return True
                        except Exception as e:
                            continue
                except:
                    continue
            
            # Tenta encontrar pelo número da página atual e próxima
            try:
                pagination = driver.find_elements(By.CSS_SELECTOR, ".pagination, .pager, [class*='pagination']")
                if pagination:
                    # Procura links numéricos de página
                    page_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a, .pagination button, [class*='page']")
                    current_page = None
                    next_page_num = None
                    
                    for link in page_links:
                        try:
                            text = link.text.strip()
                            classes = link.get_attribute('class') or ''
                            
                            # Se é a página atual
                            if 'active' in classes.lower() or 'current' in classes.lower():
                                try:
                                    current_page = int(text)
                                except:
                                    pass
                            
                            # Se é um número maior que a página atual
                            if current_page:
                                try:
                                    page_num = int(text)
                                    if page_num == current_page + 1:
                                        next_page_num = link
                                        break
                                except:
                                    pass
                        except:
                            continue
                    
                    if next_page_num:
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_num)
                        time.sleep(0.5)
                        next_page_num.click()
                        time.sleep(2)
                        print("    → Próxima página (por número)")
                        return True
            except:
                pass
            
            return False
        except Exception as e:
            print(f"    Erro ao tentar ir para próxima página: {e}")
            return False
    

