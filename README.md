# Sistema de Automação - Saldo de Info para BM

Sistema automatizado para consulta de números de telefone por CPF, verificação de operadoras (TIM/Algar) e geração de relatórios para BM.

## Funcionalidades

1. **Consulta na Base de Dados DBFusion** (Web Scraping com Selenium)
   - Acessa a base de dados em `https://dbfusion.me/loja`
   - Realiza login automático
   - Filtra pessoas por BIN 406669
   - Extrai TODOS os CPFs das pessoas (com paginação automática)

2. **Consulta de Números via SpyHub** (Web Scraping com Selenium)
   - Realiza login automático no SpyHub
   - Consulta número de telefone por CPF
   - Identifica números móveis

3. **Verificação de Operadora**
   - Consulta operadora em múltiplos serviços
   - Foca em identificar TIM e Algar
   - Verifica disponibilidade para compra automática

4. **Geração de Relatórios**
   - Gera relatórios em JSON e CSV
   - Filtra apenas resultados relevantes (TIM/Algar disponíveis)
   - Formato pronto para importação em BM

## ⚠️ Importante

**Este sistema usa apenas Web Scraping (sem APIs)**, pois os sites não possuem APIs públicas. O sistema utiliza Selenium para automatizar o navegador e extrair informações.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as credenciais no arquivo `config.py` (já configurado)

## Uso

### Via Linha de Comando

Execute o script principal:
```bash
python main.py
```

### Via Interface Web (SaaS)

Inicie o servidor Flask:
```bash
python app.py
```

Acesse no navegador: `http://localhost:5000`

## Estrutura do Projeto

- `config.py` - Configurações e credenciais
- `dbfusion_client.py` - Cliente para acesso à base DBFusion
- `spyhub_client.py` - Cliente para consulta no SpyHub
- `operadora_checker.py` - Verificador de operadoras
- `processador.py` - Orquestrador principal do processo
- `main.py` - Script CLI
- `app.py` - Aplicação web Flask
- `templates/index.html` - Interface web

## Notas Importantes

- **O sistema usa Selenium para web scraping** - requer Chrome/Chromium instalado
- O ChromeDriver é baixado automaticamente via webdriver-manager
- Pode ser necessário ajustar os seletores CSS/HTML conforme mudanças nos sites
- Rate limiting implementado para evitar bloqueios
- As credenciais estão no código - considere usar variáveis de ambiente em produção
- Para rodar sem interface gráfica, descomente `--headless` nos arquivos de cliente

## Próximos Passos

1. Testar integração com cada serviço
2. Ajustar parsers conforme estrutura real das respostas
3. Implementar cache para evitar consultas duplicadas
4. Adicionar tratamento de erros mais robusto
5. Implementar fila de processamento para grandes volumes

