# Variáveis de Ambiente para Railway

## Variáveis Obrigatórias

Configure estas variáveis no painel do Railway (Settings → Variables):

### Credenciais DBFusion
```
DBFUSION_USER = andrade17
DBFUSION_PASSWORD = 284671
```

### Credenciais SpyHub
```
SPYHUB_USER = Prtm999ww
SPYHUB_PASSWORD = 350376
```

## Variáveis Opcionais (com valores padrão)

Estas variáveis têm valores padrão, mas você pode configurar se quiser mudar:

```
DBFUSION_URL = https://dbfusion.me/loja
SPYHUB_URL = https://app.spyhub.io
TARGET_BIN = 406669
TARGET_OPERADORAS = TIM,ALGAR
CONSULTA_OPERADORA_URL = http://consultaoperadora.com.br/site2015/
```

## Como Configurar no Railway

1. Acesse seu projeto no Railway
2. Vá em **Settings** → **Variables**
3. Clique em **+ New Variable**
4. Adicione cada variável uma por uma:

### Passo a Passo:

**Variável 1:**
- Name: `DBFUSION_USER`
- Value: `andrade17`
- Clique em **Add**

**Variável 2:**
- Name: `DBFUSION_PASSWORD`
- Value: `284671`
- Clique em **Add**

**Variável 3:**
- Name: `SPYHUB_USER`
- Value: `Prtm999ww`
- Clique em **Add**

**Variável 4:**
- Name: `SPYHUB_PASSWORD`
- Value: `350376`
- Clique em **Add**

## Lista Completa para Copiar

Se preferir, você pode adicionar todas de uma vez:

```
DBFUSION_USER=andrade17
DBFUSION_PASSWORD=284671
SPYHUB_USER=Prtm999ww
SPYHUB_PASSWORD=350376
TARGET_BIN=406669
TARGET_OPERADORAS=TIM,ALGAR
```

**Nota:** As URLs têm valores padrão, então não precisa configurar a menos que mude.

## Verificar se Está Funcionando

Após configurar, faça um novo deploy e verifique os logs. O sistema deve conseguir:
- Fazer login no DBFusion
- Fazer login no SpyHub
- Processar os dados corretamente

