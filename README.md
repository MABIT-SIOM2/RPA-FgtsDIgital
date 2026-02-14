# Bot Simples Nacional - PyAutoGUI

Bot de automação que simula interações humanas reais usando PyAutoGUI.

## ⚠️ IMPORTANTE - Antes de Executar

1. **Feche todos os navegadores Chrome abertos**
2. **Não mexa no mouse/teclado** enquanto o bot estiver rodando
3. **Mantenha a tela visível** (não minimize)
4. **Emergência**: Mova o mouse para o canto superior esquerdo para parar

## Como Usar

```bash
# 1. Instalar dependências
pip install pyautogui pyperclip

# 2. Executar
python main.py

# 3. NÃO TOQUE no mouse/teclado!
```

## O que o bot faz

1. ✅ Pressiona tecla Windows
2. ✅ Digita "Chrome"
3. ✅ Abre o Chrome
4. ✅ Digita a URL na barra de endereço
5. ✅ Acessa a página
6. ✅ Navega até o campo CNPJ (Tab)
7. ✅ Digita o CNPJ caractere por caractere
8. ✅ Clica em Consultar
9. ✅ Aguarda resultado

## Vantagens

- ✅ **Impossível de detectar** - Simula humano real
- ✅ **Sem flags de automação** - Usa Chrome normal
- ✅ **Sem hCaptcha** - Navegador real do usuário

## Ajustes

Se precisar ajustar:
- **Número de Tabs**: Linha 62 em `bot_pyautogui.py`
- **Delays**: Ajuste os `time.sleep()` conforme necessário
