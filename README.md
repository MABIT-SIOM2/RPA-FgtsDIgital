# Automação FGTS Digital

Robô de automação para consulta e emissão de guias no portal FGTS Digital (gov.br). O sistema utiliza **PyAutoGUI** para interação com a interface e **MySQL** para gestão de dados.

## ⚠️ Requisitos e Segurança

1. **Certificado Digital**: O robô utiliza login via certificado digital (A1/A3).
2. **Navegador**: Utiliza o Mozilla Firefox.
3. **Ambiente**: O usuário não deve intervir no mouse ou teclado durante a execução.
4. **Parada de Emergência**: Mova o mouse para o canto superior esquerdo da tela para interromper imediatamente.

## Funcionalidades Principais

- ✅ **Login Automatizado**: Acesso via gov.br com troca de perfil para procurações.
- ✅ **Extração de Valores**: Captura detalhada de FGTS Mensal, FGTS 13º e Empréstimos Consignados.
- ✅ **Extração de Vencimento**: Captura a data de vencimento da guia diretamente na tela de resumo ("Vencimento da Guia:").
- ✅ **Validação Inteligente**:
    - Compara o total extraído com o `totalBase` esperado no banco de dados.
    - Valida se a data de vencimento está no **mês atual** e nos **dias 18, 19 ou 20**.
- ✅ **Emissão Automática**: Efetua a emissão e gera o PDF da guia somente se todas as validações forem bem-sucedidas.
- ✅ **Integração MySQL**: Atualiza status, valores e datas diretamente no banco de dados.

## 🖥️ Configurações Obrigatórias para a Automação

Como o robô utiliza o **PyAutoGUI** (reconhecimento de imagem e controle de mouse/teclado), o computador e o navegador devem estar configurados com os parâmetros abaixo para evitar falhas de clique e identificação visual:

1. **Resolução da Tela:** 1920x1080 (Recomendado para melhor precisão nas imagens).
2. **Escala e Layout (Windows):** 100% (Qualquer valor diferente, como 125% ou 150%, fará o robô clicar nos locais errados).
3. **Navegador:** Mozilla Firefox (Deve estar maximizado durante a execução do robô).
4. **Zoom do Navegador:** 100% (Pressione `Ctrl + 0` para redefinir o zoom antes de iniciar).
5. **Downloads (Como salvar o arquivo):** No Firefox, acesse `Configurações > Geral > Arquivos e Aplicativos` e **ative** a opção `"Sempre perguntar onde salvar arquivos"`. Isso é fundamental para que o robô consiga digitar o caminho exato e salvar a guia na pasta correta do cliente.
6. **Idioma / Região:** O sistema Windows deve estar em Português (Brasil) com padrão de datas `DD/MM/AAAA`.

## 🚀 Como Usar

### 1. Executando via Aplicativo (.exe)
Não é necessário ter o Python instalado.
1. Extraia o arquivo `FgtsDigital_build.zip`.
2. Acesse a pasta extraída `dist\FgtsDigital`.
3. Execute o arquivo **`FgtsDigital.exe`**.
4. O painel web será aberto no seu navegador. Se não abrir automaticamente, acesse `http://127.0.0.1:5001`.
5. Preencha a planilha, atualize a base de dados pelo sistema e inicie a automação.

### 2. Configuração (Código Fonte)
Certifique-se de que o arquivo de configuração do banco de dados (`config_multi.json`) está correto.

### 2. Instalação
```bash
pip install -r requirements.txt
```

### 3. Execução
```bash
python main.py
```

## Fluxo do Robô

1. Inicia o navegador e faz login com Certificado Digital.
2. Troca para o perfil do cliente (CNPJ) baseado na fila do banco de dados.
3. Navega até **Gestão de Guias > Guia Parametrizada**.
4. Pesquisa os débitos da competência desejada.
5. Extrai os valores e a data de vencimento da tela de resumo.
6. Realiza a validação (Valor Total e Dias de Vencimento 18, 19, 20).
7. Se aprovado, emite a guia, salva o PDF e marca como **Concluído (2)**.
8. Se houver divergência ou data fora do prazo, marca como **Erro/Divergente (3)** e não emite a guia.

## Tecnologias
- **Python 3.x**
- **PyAutoGUI**: Automação de Interface.
- **PyMySQL / DatabaseHandler**: Gestão de dados.
- **Regex**: Extração precisa de dados textuais.
