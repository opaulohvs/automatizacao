# Como Trocar de Conta Git (Joao-Vitor-Guerreiro → opaulohvs)

## Passo 1: Remover Credenciais Salvas

Execute no PowerShell (como Administrador):

```powershell
cmdkey /delete:git:https://github.com
```

**OU via Interface Gráfica:**
1. Pressione `Win + R`
2. Digite: `control /name Microsoft.CredentialManager`
3. Vá em "Credenciais do Windows"
4. Procure por `git:https://github.com`
5. Clique e depois em "Remover"

## Passo 2: Configurar Usuário Git (Opcional)

Se quiser configurar o nome/email para a conta opaulohvs:

```bash
git config --global user.name "opaulohvs"
git config --global user.email "seu-email-da-conta-opaulohvs@example.com"
```

**OU manter como está** (o user.name não afeta o push, só as credenciais)

## Passo 3: Fazer Login com opaulohvs

### Opção 1: Personal Access Token (Recomendado)

1. **Criar Token:**
   - Acesse: https://github.com/settings/tokens
   - Clique em "Generate new token" → "Generate new token (classic)"
   - Nome: "automatizacao-repo"
   - Escopo: Marque `repo` (todas as opções)
   - Clique em "Generate token"
   - **COPIE O TOKEN** (você só verá uma vez!)

2. **Fazer Push:**
   ```bash
   git push -u origin main
   ```
   - Username: `opaulohvs`
   - Password: **Cole o token** (não sua senha!)

### Opção 2: GitHub CLI

```bash
# Instalar (se não tiver)
winget install GitHub.cli

# Fazer login
gh auth login

# Escolher:
# - GitHub.com
# - HTTPS
# - Login with a web browser
# - Faça login com a conta opaulohvs
```

### Opção 3: SSH (Mais Seguro)

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email-opaulohvs@example.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub
# OU no Windows:
type ~/.ssh/id_ed25519.pub

# Adicionar no GitHub (conta opaulohvs):
# Settings → SSH and GPG keys → New SSH key
# Cole a chave pública

# Mudar remote para SSH
git remote set-url origin git@github.com:opaulohvs/automatizacao.git

# Fazer push
git push -u origin main
```

## Verificar se Funcionou

```bash
# Ver remote configurado
git remote -v

# Tentar push
git push -u origin main
```

Se pedir credenciais, use:
- Username: `opaulohvs`
- Password: Personal Access Token

