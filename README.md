# Assistente de Lances e Monitoramento Web

Sistema robusto em Python para monitoramento de preços em páginas de leilão dinâmicas e notificação automática.

## 🚀 Capacidades Técnicas e Resiliência
O sistema foi projetado para operar em ambientes web complexos, garantindo a extração de dados mesmo em cenários de alta interatividade.

| Cenário de Uso | Descrição Técnica | Implementação |
| :--- | :--- | :--- |
| **iFrames & Frames** | Conteúdo renderizado em documentos aninhados (comum em widgets financeiros). | Busca recursiva em múltiplos contextos e endereçamento via seletores compostos. |
| **Arquitetura Anti-Bot** | Proteções de cabeçalho e detecção de automação. | Integração com `playwright-stealth` para mimetização de comportamento humano. |
| **Carregamento Assíncrono** | Elementos carregados sob demanda ou via Lazy Loading. | Lógica de `auto-scroll` e sincronização por estado de rede (`networkidle`). |
| **Shadow DOM** | Encapsulamento de componentes modernos (Web Components). | Utilização de seletores profundos que atravessam a árvore do Shadow DOM. |
| **Single Page Apps (SPA)** | Atualizações de estado sem recarregamento de página. | Observadores de mudança de valor com delay de estabilização configurável. |

---

## Requisitos Atendidos
- **Monitoramento em Tempo Real:** Detecta mudanças via XPath/Seletor.
- **Robustez:** Tratamento de exceções em todas as camadas para evitar crashes.
- **Validações de Entrada:** Nome, URL, Timeout e Email com regex e validação de domínio.
- **Logs Detalhados:** Registro de ações no console e arquivo `app.log`.
- **Notificação Automática:** Envio de e-mail seguro utilizando SSL/TLS e senhas de app.
- **Testes Automatizados:** Suíte de testes com `pytest`.

## 🏗️ Arquitetura e Decisões de Projeto

### 📂 Estrutura de Módulos

| Módulo | Responsabilidade Técnica |
| :--- | :--- |
| **`main.py`** | Orquestração e Interface com Usuário. |
| **`monitor.py`** | Motor de Monitoramento com suporte a Frames e Anti-Bot. |
| **`notifier.py`** | Notificações via E-mail (SMTP). |
| **`validators.py`** | Sanitização de dados e Extração Numérica (Regex). |
| **`logger.py`** | Observabilidade e persistência de eventos. |
| **`api.py`** | Motor lógico de automação. |
| **`index.html`** | Interface visual do usuário. |

### 🛠️ Tecnologias e Padrões Adotados

1.  **Playwright + Stealth:** Navegador automatizado indetectável.
2.  **Busca Heurística:** Algoritmo de scoring para encontrar preços automaticamente.
3.  **Cross-Frame Navigation:** Capacidade de extrair dados de widgets financeiros isolados.
4.  **SMTP Seguro:** Notificação por e-mail configurada para Gmail/Outlook.

## 📈 Análise de Complexidade (Big O)

O sistema foi projetado sob a ótica da eficiência algorítmica e escalabilidade, garantindo estabilidade mesmo em sites com estruturas DOM (Document Object Model) extremamente densas e dinâmicas.

### 1. Complexidade de Tempo (Time Complexity)
*Equação de Pior Caso:* $O(N \cdot (E + F))$

* *$N$ (Número de Iterações):* Como o monitoramento é contínuo, a complexidade temporal total é linear em relação à duração da sessão e à frequência de checagem definida pelo usuário.
* *$E$ (Elementos no DOM):* Na fase de *Descoberta Automática* e em casos de fallback (perda de seletor), o sistema realiza uma varredura heurística em todos os elementos da página para aplicar um algoritmo de scoring. Isso garante resiliência contra mudanças sutis no layout do site.
* *$F$ (Frames/Contextos):* Dada a arquitetura de portais modernos que utilizam widgets financeiros e anúncios, o sistema executa buscas transversais em múltiplos frames. A complexidade é proporcional à soma dos elementos em todos os contextos ativos que o driver precisa percorrer.

### 2. Complexidade de Espaço (Space Complexity)
*Equação:* $O(M)$

* *$M$ (Pegada de Memória do Browser):* Enquanto o script Python mantém um estado de memória constante $O(1)$ (armazenando apenas o valor de preço atual e anterior), a utilização de recursos do sistema é dominada pela instância do Chromium (via Playwright). O consumo de RAM ($M$) é ditado pela densidade de mídia, scripts de terceiros e buffers de renderização do site monitorado.

### 3. Eficiência de Parsing e Extração
* *Conversão Numérica:* $O(k)$, onde $k$ é o comprimento da string capturada. 
* *Justificativa:* A extração via Expressões Regulares (Regex) percorre o texto de forma linear para sanitização e conversão. Por operar em strings curtas (preços), a execução é de tempo desprezível, garantindo que o gargalo do sistema seja apenas a latência de rede (I/O Bound).

---

## Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Configure suas credenciais (Opcional - recomendável criar um arquivo `.env`):
   ```env
   BOT_EMAIL=seu_email@gmail.com
   BOT_PASSWORD=sua_senha_de_app_16_digitos
   ```

3. Execute o assistente:
   ```bash
   python -m http.server 8000

   Em outro terminal:
   python api.py

   Entrar no link:
   http://localhost:8000/front/index.html
   ```

## Integrantes
Iago de Souza Gomes - 2312130087
Sofia Vaz da Costa Xavier - 2312130112
Rafael Augusto Santos Abreu - 2312130113
Lucas Faria - 2312130040
