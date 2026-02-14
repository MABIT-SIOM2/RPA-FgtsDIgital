# Automação FGTS Digital

Robô de automação para consulta e emissão de guias no portal FGTS Digital (gov.br). O sistema utiliza **PyAutoGUI** para interação com a interface e **MySQL** para gestão de dados.

## ⚠️ Requisitos e Segurança

1. **Certificado Digital**: O robô utiliza login via certificado digital (A1/A3).
2. **Navegador**: Utiliza o Google Chrome.
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

## Como Usar

### 1. Configuração
Certifique-se de que o arquivo de configuração do banco de dados está correto.

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
