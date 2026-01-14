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

## Se der erro de autenticação

Se pedir usuário/senha, você pode:

**Opção 1: Usar Personal Access Token (Recomendado)**
1. Vá em GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Gere um novo token com permissão `repo`
3. Use o token como senha quando pedir

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

