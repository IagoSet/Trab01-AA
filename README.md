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

## 🏗️ Arquitetura e Decisões de Projeto

O sistema foi desenvolvido seguindo princípios de modularidade e separação de responsabilidades. Abaixo, detalhamos a função de cada módulo e as justificativas técnicas adotadas.

### 📂 Estrutura de Módulos

| Módulo | Responsabilidade Técnica | Detalhes de Implementação / Justificativa |
| :--- | :--- | :--- |
| **`main.py`** | Ponto de entrada e Orquestração | Gerencia o ciclo de vida da aplicação, coordenando a captura de inputs validados e a inicialização do loop de eventos assíncronos (`asyncio`). |
| **`monitor.py`** | Motor de Monitoramento Web | Utiliza a engine do Playwright para interação com o DOM. A lógica de detecção baseia-se em *polling* periódico e comparação de estados (valor anterior vs. atual). |
| **`notifier.py`** | Integração e Notificação Externa | Implementa a automação de uma segunda página web para persistência ou alerta de dados, garantindo que a notificação ocorra em um ambiente isolado. |
| **`validators.py`** | Camada de Integridade e Sanitização | Centraliza as regras de negócio para validação de dados. O processamento de preços utiliza Expressões Regulares (Regex) para garantir a conversão correta de diferentes formatos monetários. |
| **`logger.py`** | Observabilidade e Rastreabilidade | Implementa logs persistentes em arquivo (`app.log`) e feedback em tempo real via terminal (Rich), essencial para depuração e auditoria do sistema em execução. |

### 🛠️ Tecnologias e Padrões Adotados

1.  **Programação Assíncrona (`asyncio`):** Escolhida para permitir que o sistema realize operações de I/O (como navegação web e rede) sem bloquear a execução principal, otimizando o consumo de recursos.
2.  **Engine Playwright:** Adotada pela sua superioridade em lidar com SPAs (Single Page Applications) e sites dinâmicos modernos, oferecendo seletores mais robustos que o Selenium tradicional.
3.  **Seletores Semânticos (XPath):** Priorizamos o uso de XPaths baseados em atributos (ex: `@id`, `@data-testid`) para aumentar a resiliência do robô frente a mudanças de layout nas páginas monitoradas.
4.  **Tratamento de Exceções e Robustez:** Implementamos blocos de controle em todas as camadas críticas para garantir que falhas de conexão ou mudanças abruptas no DOM não causem o encerramento inesperado do serviço.

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
