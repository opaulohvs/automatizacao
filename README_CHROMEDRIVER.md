# Como Resolver o Erro do ChromeDriver no Windows

## Erro: `[WinError 193] %1 não é um aplicativo Win32 válido`

Este erro ocorre quando o ChromeDriver baixado está corrompido ou incompatível.

## Soluções

### Solução 1: Instalação Manual (Recomendado)

1. **Descubra a versão do seu Chrome:**
   - Abra o Chrome
   - Digite na barra de endereços: `chrome://version`
   - Anote o número da versão (ex: `120.0.6099.109`)

2. **Baixe o ChromeDriver compatível:**
   - Acesse: https://googlechromelabs.github.io/chrome-for-testing/
   - Ou: https://chromedriver.chromium.org/downloads
   - Baixe a versão que corresponde ao seu Chrome
   - **Importante:** Baixe a versão para Windows (win64)

3. **Extraia e coloque o arquivo:**
   - Extraia `chromedriver.exe` do arquivo ZIP baixado
   - Coloque `chromedriver.exe` na pasta do projeto: `C:\Users\João Vitor Guerreiro\Downloads\automatizacao\`
   - Ou coloque em `C:\chromedriver\` e adicione ao PATH

4. **Teste:**
   ```powershell
   python main.py
   ```

### Solução 2: Limpar Cache e Reinstalar

1. **Limpe o cache do webdriver-manager:**
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.wdm"
   ```

2. **Reinstale as dependências:**
   ```powershell
   pip install --upgrade webdriver-manager
   ```

3. **Execute novamente:**
   ```powershell
   python main.py
   ```

### Solução 3: Usar ChromeDriver do PATH

Se você já tem ChromeDriver instalado no sistema:

1. Verifique se está no PATH:
   ```powershell
   chromedriver --version
   ```

2. Se funcionar, o código tentará usar automaticamente

### Solução 4: Usar Versão Específica do ChromeDriver

Se nenhuma das soluções acima funcionar, você pode especificar manualmente o caminho no código.

Edite `dbfusion_client.py` e `spyhub_client.py`, na função `_get_driver()`, adicione:

```python
# Adicione no início da função _get_driver()
driver_path = r"C:\caminho\para\chromedriver.exe"  # Seu caminho aqui
if os.path.exists(driver_path):
    service = Service(driver_path)
    self.driver = webdriver.Chrome(service=service, options=chrome_options)
    return self.driver
```

## Verificação

Para verificar se está funcionando:

```powershell
python instalar_chromedriver.py
```

Este script verifica se o Chrome está instalado e tenta configurar o ChromeDriver.

## Nota Importante

- O ChromeDriver DEVE ser compatível com a versão do Chrome instalada
- Se atualizar o Chrome, pode precisar atualizar o ChromeDriver também
- Sempre baixe de fontes oficiais (chromium.org ou chrome-for-testing)


