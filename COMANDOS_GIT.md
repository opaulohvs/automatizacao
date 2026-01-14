# Comandos Git para Subir o Projeto

## Passo a Passo

### 1. Inicializar repositório (se ainda não fez)
```bash
git init
```

### 2. Adicionar todos os arquivos
```bash
git add .
```

### 3. Fazer o primeiro commit
```bash
git commit -m "Initial commit: Sistema de automação BM"
```

### 4. Adicionar o repositório remoto do GitHub
```bash
git remote add origin https://github.com/opaulohvs/automatizacao.git
```

### 5. Verificar se o remote foi adicionado
```bash
git remote -v
```

### 6. Renomear branch para main (se necessário)
```bash
git branch -M main
```

### 7. Fazer push para o GitHub
```bash
git push -u origin main
```

## Se der erro de autenticação (403 Permission denied)

**Problema:** Você está logado com outra conta (`Joao-Vitor-Guerreiro`) mas precisa fazer push no repositório `opaulohvs`.

### Solução: Remover credenciais antigas

**No Windows (PowerShell como Administrador):**
```powershell
# Remover credenciais do GitHub
cmdkey /delete:git:https://github.com
```

**Ou via Interface Gráfica:**
1. Pressione `Win + R`
2. Digite: `control /name Microsoft.CredentialManager`
3. Vá em "Credenciais do Windows"
4. Procure por `git:https://github.com`
5. Clique e depois em "Remover"

### Depois, fazer login novamente:

**Opção 1: Usar Personal Access Token (Recomendado)**
1. Vá em: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Dê um nome (ex: "automatizacao-repo")
4. Selecione escopo: `repo` (marca todas as opções)
5. Clique em "Generate token"
6. **COPIE O TOKEN** (você só verá uma vez!)
7. Ao fazer push:
   - Username: `opaulohvs`
   - Password: **Cole o token** (não sua senha!)

**Opção 2: Usar GitHub CLI**
```bash
gh auth login
```

**Opção 3: Configurar SSH**
```bash
# Gerar chave SSH (se ainda não tem)
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Adicionar ao GitHub em Settings → SSH and GPG keys
# Depois mudar o remote para SSH:
git remote set-url origin git@github.com:opaulohvs/automatizacao.git
```

## Comandos úteis

### Ver status dos arquivos
```bash
git status
```

### Ver o que será commitado
```bash
git diff --cached
```

### Desfazer último commit (mantendo arquivos)
```bash
git reset --soft HEAD~1
```

### Ver histórico de commits
```bash
git log
```

