# Fazer Push para GitHub - Comandos Rápidos

## Passo a Passo

### 1. Adicionar todos os arquivos
```bash
git add .
```

### 2. Fazer commit
```bash
git commit -m "Initial commit: Sistema de automação BM"
```

### 3. Verificar se o remote está configurado
```bash
git remote -v
```

Se não aparecer `origin`, adicione:
```bash
git remote add origin https://github.com/opaulohvs/automatizacao.git
```

### 4. Fazer push
```bash
git push -u origin main
```

**Quando pedir credenciais:**
- **Username:** `opaulohvs`
- **Password:** Cole o Personal Access Token (não sua senha!)

---

## Se Der Erro 403 (Permission Denied)

Você precisa criar um Personal Access Token:

1. Acesse: https://github.com/settings/tokens
2. Faça login com a conta `opaulohvs`
3. Clique em "Generate new token" → "Generate new token (classic)"
4. Nome: `automatizacao`
5. Marque `repo`
6. Clique em "Generate token"
7. **COPIE O TOKEN**
8. Use o token como senha quando pedir

---

## Comandos Completos (Copiar e Colar)

```bash
git add .
git commit -m "Initial commit: Sistema de automação BM"
git remote add origin https://github.com/opaulohvs/automatizacao.git
git branch -M main
git push -u origin main
```

Quando pedir credenciais, use:
- Username: `opaulohvs`
- Password: Seu Personal Access Token

