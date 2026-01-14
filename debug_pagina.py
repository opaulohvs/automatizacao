"""
Script de debug para inspecionar a página do DBFusion
"""
from dbfusion_client import DBFusionClient
from selenium.webdriver.common.by import By
import os

def debug_pagina():
    """Salva HTML e screenshot da página para análise"""
    client = DBFusionClient()
    
    try:
        print("Fazendo login...")
        if client.login():
            print("Login realizado!")
            
            driver = client._get_driver()
            
            # Salva screenshot
            driver.save_screenshot('debug_screenshot.png')
            print("Screenshot salvo: debug_screenshot.png")
            
            # Salva HTML
            html = driver.page_source
            with open('debug_html.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("HTML salvo: debug_html.html")
            
            # Mostra informações da página
            print(f"\nURL atual: {driver.current_url}")
            print(f"Título: {driver.title}")
            
            print("\n" + "="*60)
            print("PROCURANDO ELEMENTOS 'LOJA'")
            print("="*60)
            
            # Procura "Loja"
            loja_xpaths = [
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'loja')]",
            ]
            
            for xpath in loja_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        print(f"\nEncontrados {len(elements)} elementos com XPath: {xpath[:50]}...")
                        for i, elem in enumerate(elements[:5]):  # Primeiros 5
                            try:
                                print(f"  Elemento {i+1}: tag={elem.tag_name}, texto='{elem.text[:50]}', visível={elem.is_displayed()}")
                            except:
                                pass
                except:
                    pass
            
            print("\n" + "="*60)
            print("PROCURANDO ELEMENTOS 'BIN'")
            print("="*60)
            
            # Procura "BIN"
            bin_xpaths = [
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bin')]",
            ]
            
            for xpath in bin_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        print(f"\nEncontrados {len(elements)} elementos com XPath: {xpath[:50]}...")
                        for i, elem in enumerate(elements[:5]):
                            try:
                                texto = elem.text.strip()
                                print(f"  Elemento {i+1}: tag={elem.tag_name}, texto='{texto[:50]}', visível={elem.is_displayed()}")
                            except:
                                pass
                except:
                    pass
            
            print("\n" + "="*60)
            print("CAMPOS DE INPUT")
            print("="*60)
            
            # Inputs
            inputs = driver.find_elements(By.TAG_NAME, 'input')
            print(f"Total de inputs encontrados: {len(inputs)}")
            for i, inp in enumerate(inputs):
                try:
                    if inp.is_displayed():
                        name = inp.get_attribute('name') or ''
                        input_type = inp.get_attribute('type') or ''
                        placeholder = inp.get_attribute('placeholder') or ''
                        input_id = inp.get_attribute('id') or ''
                        classes = inp.get_attribute('class') or ''
                        print(f"\n  Input {i+1} (VISÍVEL):")
                        print(f"    type: {input_type}")
                        print(f"    name: {name}")
                        print(f"    id: {input_id}")
                        print(f"    placeholder: {placeholder}")
                        print(f"    class: {classes}")
                except:
                    pass
            
            print("\n" + "="*60)
            print("LINKS E BOTÕES")
            print("="*60)
            
            # Links
            links = driver.find_elements(By.TAG_NAME, 'a')
            print(f"Total de links: {len(links)}")
            print("Primeiros 20 links visíveis:")
            count = 0
            for link in links:
                try:
                    if link.is_displayed() and count < 20:
                        texto = link.text.strip()
                        href = link.get_attribute('href') or ''
                        if texto or 'loja' in href.lower() or 'bin' in href.lower():
                            print(f"  Link: texto='{texto[:30]}', href='{href[:50]}'")
                            count += 1
                except:
                    pass
            
            # Botões
            botoes = driver.find_elements(By.TAG_NAME, 'button')
            print(f"\nTotal de botões: {len(botoes)}")
            print("Primeiros 10 botões visíveis:")
            count = 0
            for btn in botoes:
                try:
                    if btn.is_displayed() and count < 10:
                        texto = btn.text.strip()
                        if texto:
                            print(f"  Botão: texto='{texto[:30]}'")
                            count += 1
                except:
                    pass
            
            print("\n✓ Debug concluído! Verifique os arquivos gerados.")
            print("Arquivos criados:")
            print("  - debug_screenshot.png (imagem da página)")
            print("  - debug_html.html (código HTML completo)")
            
        else:
            print("Erro no login")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == '__main__':
    debug_pagina()

