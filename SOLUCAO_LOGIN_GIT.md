# Como Fazer Logout e Login no Git

## Problema
Você está logado como `Joao-Vitor-Guerreiro`, mas precisa fazer push no repositório `opaulohvs/automatizacao`.

## Solução: Remover Credenciais Salvas

### No Windows (PowerShell como Administrador):

**Opção 1: Usando Credential Manager (Mais Fácil)**
1. Pressione `Win + R`
2. Digite: `control /name Microsoft.CredentialManager`
3. Vá em "Credenciais do Windows"
4. Procure por `git:https://github.com`
5. Clique e depois em "Remover"

**Opção 2: Via PowerShell**
```powershell
# Remover credenciais do GitHub
cmdkey /list | Select-String "github"
cmdkey /delete:git:https://github.com
```

**Opção 3: Remover do Git Config**
```bash
git config --global --unset credential.helper
git config --system --unset credential.helper
```

## Depois de Remover, Fazer Login Novamente

### Opção 1: Usar Personal Access Token (Recomendado)

1. **Criar Token no GitHub:**
   - Vá em: https://github.com/settings/tokens
   - Clique em "Generate new token" → "Generate new token (classic)"
   - Dê um nome (ex: "automatizacao-repo")
   - Selecione escopo: `repo` (marca todas as opções de repo)
   - Clique em "Generate token"
   - **COPIE O TOKEN** (você só verá uma vez!)

2. **Fazer Push:**
   ```bash
   git push -u origin main
   ```
   - Username: `opaulohvs`
   - Password: **Cole o token** (não sua senha!)

### Opção 2: Usar GitHub CLI

```bash
# Instalar GitHub CLI (se não tiver)
winget install GitHub.cli

# Fazer login
gh auth login

# Escolher:
# - GitHub.com
# - HTTPS
# - Login with a web browser
# - Autorizar
```

### Opção 3: Configurar SSH (Mais Seguro)

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar no GitHub:
# Settings → SSH and GPG keys → New SSH key

# Mudar remote para SSH
git remote set-url origin git@github.com:opaulohvs/automatizacao.git

# Fazer push
git push -u origin main
```

## Verificar Configuração Atual

```bash
# Ver usuário configurado
git config --global user.name
git config --global user.email

# Ver remote configurado
git remote -v

# Ver credenciais salvas
cmdkey /list | Select-String "git"
```

## Configurar Usuário Correto (se necessário)

```bash
git config --global user.name "opaulohvs"
git config --global user.email "seu-email@example.com"
```

