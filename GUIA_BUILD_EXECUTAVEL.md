# 📦 Guia Completo: Gerar Executável do RoboSocietario

Este guia mostra o passo a passo para gerar o executável (.exe) do projeto com todas as atualizações funcionando corretamente.

---

## 🔧 Pré-requisitos

Antes de começar, certifique-se de ter:

1. **Python instalado** (versão 3.8 ou superior)
2. **Todas as dependências instaladas**
3. **PyInstaller instalado**

---

## 📋 Passo a Passo Completo

### **Passo 1: Verificar o Ambiente Virtual (Recomendado)**

É altamente recomendado usar um ambiente virtual para evitar conflitos:

```powershell
# Se ainda não tem um ambiente virtual, crie:
python -m venv venv

# Ative o ambiente virtual:
.\venv\Scripts\activate

# Você verá (venv) no início da linha de comando
```

---

### **Passo 2: Instalar/Atualizar Todas as Dependências**

Instale todas as bibliotecas necessárias:

```powershell
# Instalar dependências do requirements.txt
pip install -r requirements.txt

# Garantir que PyInstaller está atualizado
pip install --upgrade pyinstaller
```

**Bibliotecas principais necessárias:**
- `pyautogui` - Automação de mouse/teclado
- `openpyxl` - Leitura de arquivos Excel
- `pillow` - Processamento de imagens
- `pyperclip` - Manipulação de clipboard
- `pygetwindow` - Controle de janelas
- `pyinstaller` - Geração do executável

---

### **Passo 3: Testar o Código Antes de Compilar**

**IMPORTANTE:** Sempre teste o código antes de gerar o executável!

```powershell
# Teste a aplicação normalmente
python gui.py
```

✅ **Checklist de Testes:**
- [ ] A interface abre sem erros
- [ ] Todas as abas aparecem corretamente (SATE, FGTS, Prefeitura MCP)
- [ ] A aba "Certidão CNPJ" NÃO aparece (foi desativada)
- [ ] Consegue selecionar arquivos Excel
- [ ] Consegue selecionar pastas de destino
- [ ] O logo aparece (se houver)

---

### **Passo 4: Limpar Builds Anteriores (Importante!)**

Antes de gerar um novo executável, **sempre** limpe os builds antigos:

```powershell
# Remover pastas de build anteriores
rmdir /s /q build
rmdir /s /q dist

# Ou use o comando do PowerShell:
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

> **Por que limpar?** Builds antigos podem conter código desatualizado e causar problemas.

---

### **Passo 5: Gerar o Executável**

Você tem **duas opções**:

#### **Opção A: Usar o Script Automático (Recomendado)**

```powershell
# Execute o script batch
.\build_exe.bat
```

Este script faz automaticamente:
1. Limpa builds anteriores
2. Gera o executável usando o arquivo `.spec`
3. Verifica se foi criado com sucesso
4. Mostra informações do arquivo gerado

---

#### **Opção B: Comando Manual (Mais Controle)**

```powershell
# Gerar executável usando o arquivo .spec
python -m PyInstaller --clean BotSocietario.spec
```

**Parâmetros importantes:**
- `--clean` - Limpa cache antes de compilar (garante código atualizado)
- `BotSocietario.spec` - Usa as configurações otimizadas do projeto

---

### **Passo 6: Verificar o Executável Gerado**

Após a compilação, verifique se tudo está correto:

```powershell
# Navegar até a pasta do executável
cd dist\RoboSocietario

# Listar arquivos
dir
```

Você deve ver:
- ✅ `RoboSocietario.exe` - O executável principal
- ✅ Pasta `src\assets` - Com o logo e imagens
- ✅ Várias DLLs e arquivos de suporte

---

### **Passo 7: Testar o Executável**

**CRÍTICO:** Sempre teste o executável antes de distribuir!

```powershell
# Execute o .exe diretamente
.\RoboSocietario.exe
```

✅ **Checklist de Testes do Executável:**
- [ ] Abre sem erros
- [ ] Logo aparece corretamente
- [ ] Abas corretas (sem cert_cnpj)
- [ ] Consegue selecionar Excel
- [ ] Consegue selecionar pastas
- [ ] Execução manual funciona
- [ ] Agendamento funciona
- [ ] Salva configurações (cria `config_multi.json`)

---

### **Passo 8: Distribuir o Executável**

Para distribuir para outros computadores:

1. **Copie a pasta completa:**
   ```
   dist\RoboSocietario\  (pasta inteira, não só o .exe)
   ```

2. **Crie um ZIP (opcional):**
   ```powershell
   # Comprimir a pasta
   Compress-Archive -Path dist\RoboSocietario -DestinationPath RoboSocietario_v1.0.zip
   ```

3. **Instruções para o usuário final:**
   - Extrair a pasta completa
   - Executar `RoboSocietario.exe`
   - **NÃO** precisa instalar Python

---

## 🚨 Problemas Comuns e Soluções

### **Erro: "ModuleNotFoundError" ao executar o .exe**

**Causa:** Biblioteca não foi incluída no build

**Solução:** Adicione no arquivo `BotSocietario.spec`, linha 10:
```python
hiddenimports=['openpyxl', 'pyautogui', 'pyperclip', 'PIL', 'pygetwindow', 'NOME_DA_BIBLIOTECA'],
```

---

### **Erro: Logo não aparece no executável**

**Causa:** Arquivo não foi copiado corretamente

**Solução:** Verifique se a pasta `src/assets` existe e contém `logo.png`

---

### **Executável muito grande (>100MB)**

**Causa:** Bibliotecas desnecessárias incluídas

**Solução:** O arquivo `.spec` já está otimizado com exclusões. Se quiser reduzir mais, adicione bibliotecas não usadas na lista `excludes=[]` (linha 14-33 do `.spec`)

---

### **Erro: "Failed to execute script"**

**Causa:** Erro no código Python

**Solução:**
1. Teste com `python gui.py` primeiro
2. Verifique os logs em `build\RoboSocietario\warn-RoboSocietario.txt`
3. Execute o .exe pelo terminal para ver erros:
   ```powershell
   cd dist\RoboSocietario
   .\RoboSocietario.exe
   ```

---

## 📝 Checklist Final

Antes de distribuir o executável:

- [ ] Código testado com `python gui.py`
- [ ] Builds anteriores limpos
- [ ] Executável gerado sem erros
- [ ] Executável testado e funcionando
- [ ] Todas as funcionalidades verificadas
- [ ] Pasta completa `dist\RoboSocietario` pronta
- [ ] Documentação/instruções para usuários (se necessário)

---

## 🔄 Atualizações Futuras

Quando fizer alterações no código:

1. **Edite os arquivos Python** (gui.py, bot_pyautogui.py, etc.)
2. **Teste com** `python gui.py`
3. **Limpe builds antigos** (Passo 4)
4. **Gere novo executável** (Passo 5)
5. **Teste o novo .exe** (Passo 7)
6. **Distribua a nova versão**

> **IMPORTANTE:** Sempre limpe os builds antigos antes de gerar uma nova versão!

---

## 📞 Comandos Rápidos (Resumo)

```powershell
# 1. Ativar ambiente virtual (se usar)
.\venv\Scripts\activate

# 2. Atualizar dependências
pip install -r requirements.txt --upgrade

# 3. Testar código
python gui.py

# 4. Limpar builds antigos
rmdir /s /q build dist

# 5. Gerar executável
.\build_exe.bat
# OU
python -m PyInstaller --clean BotSocietario.spec

# 6. Testar executável
cd dist\RoboSocietario
.\RoboSocietario.exe
```

---

## ✅ Pronto!

Agora você tem um executável atualizado com todas as modificações do código funcionando corretamente!

**Localização final:** `dist\RoboSocietario\RoboSocietario.exe`
