# Como Fazer Push com Personal Access Token

## Passo 1: Criar Personal Access Token

1. **Acesse o GitHub com a conta `opaulohvs`:**
   - https://github.com/login
   - Faça login com a conta `opaulohvs`

2. **Criar o Token:**
   - Vá em: https://github.com/settings/tokens
   - Clique em "Generate new token" → "Generate new token (classic)"
   - **Nome:** `automatizacao-repo`
   - **Expiration:** Escolha (ex: 90 dias ou No expiration)
   - **Escopo:** Marque `repo` (isso marca todas as opções de repo automaticamente)
   - Clique em "Generate token"
   - **⚠️ IMPORTANTE: COPIE O TOKEN AGORA!** (você só verá uma vez)

## Passo 2: Fazer Push

Execute no PowerShell:

```bash
git push -u origin main
```

Quando pedir credenciais:
- **Username:** `opaulohvs`
- **Password:** Cole o token que você copiou (não sua senha!)

## Se não pedir credenciais (já está salvo)

Você pode forçar a remoção e pedir novamente:

```bash
# Remover helper de credenciais temporariamente
git config --global --unset credential.helper

# Tentar push novamente
git push -u origin main

# Depois pode restaurar (opcional)
git config --global credential.helper manager-core
```

## Alternativa: Usar Token na URL (não recomendado, mas funciona)

```bash
# Substitua SEU_TOKEN pelo token que você criou
git remote set-url origin https://opaulohvs:SEU_TOKEN@github.com/opaulohvs/automatizacao.git

# Fazer push
git push -u origin main

# Depois, volte para a URL normal (por segurança)
git remote set-url origin https://github.com/opaulohvs/automatizacao.git
```

## Verificar se Funcionou

```bash
# Ver o remote configurado
git remote -v

# Tentar push
git push -u origin main
```

Se der erro 403, significa que:
- O token está errado
- O token não tem permissão `repo`
- Você não está usando o token como senha

## Dica de Segurança

Depois de fazer o push, você pode:
1. Manter o token salvo (Git vai usar automaticamente)
2. Ou remover e criar um novo token quando precisar

