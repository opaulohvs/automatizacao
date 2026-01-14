"""
Script auxiliar para instalar/configurar ChromeDriver
"""
import os
import sys
import subprocess
import platform

def verificar_chrome():
    """Verifica se o Chrome está instalado"""
    print("Verificando instalação do Google Chrome...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Chrome encontrado em: {path}")
            return True
    
    print("✗ Chrome não encontrado. Por favor, instale o Google Chrome primeiro.")
    return False

def instalar_chromedriver_automatico():
    """Tenta instalar ChromeDriver automaticamente"""
    print("\nTentando instalar ChromeDriver automaticamente...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✓ ChromeDriver instalado em: {driver_path}")
        return True
    except Exception as e:
        print(f"✗ Erro ao instalar automaticamente: {e}")
        return False

def instrucoes_manual():
    """Mostra instruções para instalação manual"""
    print("\n" + "="*60)
    print("INSTRUÇÕES PARA INSTALAÇÃO MANUAL DO CHROMEDRIVER")
    print("="*60)
    print("\n1. Verifique a versão do seu Chrome:")
    print("   - Abra o Chrome")
    print("   - Vá em Configurações > Sobre o Chrome")
    print("   - Anote o número da versão (ex: 120.0.6099.109)")
    print("\n2. Baixe o ChromeDriver compatível:")
    print("   - Acesse: https://googlechromelabs.github.io/chrome-for-testing/")
    print("   - Ou: https://chromedriver.chromium.org/downloads")
    print("   - Baixe a versão que corresponde ao seu Chrome")
    print("\n3. Extraia o arquivo:")
    print("   - Extraia chromedriver.exe do arquivo baixado")
    print("\n4. Coloque o chromedriver.exe em uma das opções:")
    print("   a) Na pasta do projeto (recomendado)")
    print("   b) Em C:\\chromedriver\\")
    print("   c) No PATH do sistema")
    print("\n5. Execute o script novamente")
    print("="*60)

def main():
    print("="*60)
    print("CONFIGURAÇÃO DO CHROMEDRIVER")
    print("="*60)
    
    # Verifica Chrome
    if not verificar_chrome():
        instrucoes_manual()
        return
    
    # Tenta instalação automática
    if instalar_chromedriver_automatico():
        print("\n✓ Configuração concluída com sucesso!")
        print("Você pode executar o script principal agora.")
    else:
        instrucoes_manual()
        
        # Verifica se já existe chromedriver.exe na pasta
        if os.path.exists('chromedriver.exe'):
            print("\n✓ chromedriver.exe encontrado na pasta do projeto!")
            print("Tente executar o script principal novamente.")
        else:
            print("\n✗ chromedriver.exe não encontrado na pasta do projeto.")
            print("Siga as instruções acima para instalar manualmente.")

if __name__ == '__main__':
    main()


