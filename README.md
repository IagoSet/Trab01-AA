# Assistente de Lances e Monitoramento Web

Sistema robusto em Python para monitoramento de preços em páginas de leilão dinâmicas e notificação automática em segunda página.

## Requisitos Atendidos
- **Monitoramento em Tempo Real:** Detecta mudanças via XPath/Seletor.
- **Robustez:** Tratamento de exceções em todas as camadas para evitar crashes (Nota Zero evitada).
- **Validações de Entrada:**
  - Nome de usuário (mínimo 3 caracteres alfabéticos).
  - URL válida.
  - Timeout numérico positivo.
  - Valor monitorado convertido para número.
- **Logs Detalhados:** Registro de ações, XPath e alterações de preço no console e arquivo `app.log`.
- **Notificação Automática:** Interação com uma segunda página web ao detectar mudança.
- **Testes Automatizados:** Suíte de testes com `pytest`.
- **Análise de Complexidade:** Big O detalhado abaixo.

## Análise de Complexidade (Big O)

### 1. Loop de Monitoramento (`AuctionMonitor.start`)
- **Complexidade de Tempo:** $O(N \cdot E)$
  - $N$: Número de iterações do loop (dependente do tempo de execução total e do intervalo).
  - $E$: Complexidade da busca no DOM pelo motor do navegador (Playwright/Chromium). O XPath em um DOM com $E$ elementos leva tempo proporcional a $E$ no pior caso.
- **Complexidade de Espaço:** $O(M)$
  - $M$: Memória utilizada pelo processo do navegador para carregar o DOM. O script em si mantém apenas os valores atual e anterior ($O(1)$), mas a infraestrutura do Playwright escala com a complexidade da página.

### 2. Validação e Parsing (`validators.py`)
- **Limpeza de Nome (`validate_username`):** $O(S)$ onde $S$ é o tamanho da string.
- **Parsing de Preço (`parse_price`):** $O(S)$ para limpeza via Regex e conversão.

## 🎓 Guia de Aprendizado e "Cola" para a Equipe (Preparação para o Professor)

Este guia resume o que cada parte do projeto faz e os conceitos técnicos que vocês podem precisar explicar durante a apresentação.

### 📂 Estrutura de Arquivos e Responsabilidades

| Arquivo | O que ele faz? (Explicação Simples) | O que o professor pode perguntar? |
| :--- | :--- | :--- |
| **`main.py`** | O "cérebro" do programa. Ele pede os dados para o usuário, valida tudo e liga o motor de monitoramento. | "Como o programa começa?" R: Pela função `main()` que orquestra a entrada de dados e inicia o loop assíncrono. |
| **`monitor.py`** | O "vigia". Ele abre o navegador (em segundo plano), vai até a página do leilão e fica olhando o preço de tempos em tempos. | "Como você detecta a mudança?" R: Guardamos o valor atual e, a cada intervalo, comparamos com o novo valor lido via XPath. |
| **`notifier.py`** | O "mensageiro". Quando o preço muda, este arquivo abre uma **segunda página** (ex: um formulário) e envia os dados da mudança. | "Por que usar Playwright aqui também?" R: Para simular uma interação real em outra página web, como preencher um log ou enviar um alerta. |
| **`validators.py`** | O "filtro". Garante que o usuário não digite lixo (ex: nome vazio, URL maluca ou intervalo negativo). | "Como você trata o preço que vem como texto (R$ 1.200,00)?" R: Usamos a função `parse_price` com Regex para limpar símbolos e converter para número (`float`). |
| **`logger.py`** | O "diário". Salva tudo o que acontece no arquivo `app.log` e mostra mensagens coloridas no terminal. | "Para que serve o Log?" R: Para rastreabilidade e depuração sem precisar parar o programa, mantendo um histórico das alterações. |

### 🛠️ Tecnologias Chave (Conceitos Técnicos)

1.  **Asyncio (`async`/`await`):** O projeto é **assíncrono**. Isso significa que o programa não fica "travado" esperando o navegador carregar; ele pode gerenciar outras tarefas enquanto espera a resposta da rede.
2.  **Playwright:** É a ferramenta de automação que controla o navegador (Chromium). Ela é mais moderna e rápida que o Selenium.
3.  **XPath/Seletores:** São os "endereços" dos elementos na página HTML. Usamos isso para dizer ao programa exatamente onde está o preço que queremos vigiar.
4.  **Tratamento de Exceções (`try/except`):** Em todos os arquivos, usamos blocos para evitar que o programa feche sozinho caso a internet caia ou o site mude (isso garante a "robustez" cobrada).

### 📈 Análise de Complexidade (Big O)

*   **Tempo:** $O(N \cdot E)$, onde $N$ é o número de vezes que checamos o site e $E$ é a complexidade do navegador para achar o elemento no site (proporcional ao tamanho da página).
*   **Espaço:** $O(1)$ para o nosso código (só guardamos o preço antigo e o novo), mas o navegador consome memória conforme o tamanho da página aberta.

---

## Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Execute o assistente:
   ```bash
   python -m src.main
   ```

3. Para rodar os testes:
   ```bash
   $env:PYTHONPATH = ".;$env:PYTHONPATH"
   pytest
   ```

## Integrantes
Iago de Souza Gomes - 2312130087
