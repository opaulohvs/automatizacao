# Solução: Erros de Instalação com Python 3.13

## Problema
Tanto `pandas 2.1.3` quanto `lxml 4.9.3` não são compatíveis com Python 3.13. Os erros ocorrem durante a compilação.

## Solução

### Opção 1: Atualizar Dependências (Recomendado)
O `requirements.txt` foi atualizado para usar versões compatíveis com Python 3.13:
- `pandas>=2.2.0` (suporta Python 3.13)
- `lxml>=5.0.0` (suporta Python 3.13)

Execute novamente:
```bash
pip install -r requirements.txt
```

### Opção 2: Usar Python 3.11 ou 3.12
Se preferir manter as versões antigas, use uma versão anterior do Python:

```bash
# Com mise (se estiver usando)
mise install python@3.12
mise use python@3.12

# Ou com pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Depois instalar dependências
pip install -r requirements.txt
```

### Opção 3: Versões Específicas Compatíveis
Se quiser versões específicas compatíveis com Python 3.13:

```bash
pip install pandas==2.2.3 lxml==5.3.0
```

## Verificar Versão do Python

```bash
python --version
```

Se estiver usando Python 3.13, a Opção 1 (atualizar dependências) é a melhor solução.

