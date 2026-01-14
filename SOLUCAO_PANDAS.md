# Solução: Erro de Instalação do Pandas

## Problema
O `pandas 2.1.3` não é compatível com Python 3.13. O erro ocorre durante a compilação.

## Solução

### Opção 1: Atualizar Pandas (Recomendado)
O `requirements.txt` foi atualizado para usar `pandas>=2.2.0` que suporta Python 3.13.

Execute novamente:
```bash
pip install -r requirements.txt
```

### Opção 2: Usar Python 3.11 ou 3.12
Se preferir manter pandas 2.1.3, use uma versão anterior do Python:

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

### Opção 3: Versão Específica Compatível
Se quiser uma versão específica do pandas compatível com Python 3.13:

```bash
pip install pandas==2.2.3
```

## Verificar Versão do Python

```bash
python --version
```

Se estiver usando Python 3.13, a Opção 1 (atualizar pandas) é a melhor solução.

