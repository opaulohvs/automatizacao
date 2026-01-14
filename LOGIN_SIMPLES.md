# Login Simples no GitHub - Passo a Passo

## Método Mais Simples: Personal Access Token

### Passo 1: Criar Token (2 minutos)

1. Acesse: **https://github.com/settings/tokens**
2. Faça login com a conta **`opaulohvs`**
3. Clique em **"Generate new token"** → **"Generate new token (classic)"**
4. Preencha:
   - **Note:** `automatizacao`
   - **Expiration:** Escolha (ex: 90 dias)
   - **Selecione:** Marque a caixa **`repo`** (isso marca tudo automaticamente)
5. Clique em **"Generate token"** no final da página
6. **COPIE O TOKEN** (exemplo: `ghp_xxxxxxxxxxxxxxxxxxxx`)

### Passo 2: Fazer Push

Execute no PowerShell:

```bash
git push -u origin main
```

Quando aparecer a janela pedindo credenciais:
- **Username:** Digite `opaulohvs`
- **Password:** Cole o token que você copiou (não é sua senha!)

**Pronto!** O Git vai salvar essas credenciais e você não precisará fazer isso de novo.

---

## Se Não Aparecer Janela de Login

Execute isso primeiro para limpar credenciais antigas:

```bash
git config --global --unset credential.helper
git push -u origin main
```

Depois pode restaurar (opcional):
```bash
git config --global credential.helper manager-core
```

---

## Resumo Rápido

1. ✅ Criar token em: https://github.com/settings/tokens
2. ✅ Copiar o token
3. ✅ Executar: `git push -u origin main`
4. ✅ Username: `opaulohvs`
5. ✅ Password: Cole o token

**É só isso!** 🎉

