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

### 🛠️ Tecnologias e Padrões Adotados

1.  **Playwright + Stealth:** Navegador automatizado indetectável.
2.  **Busca Heurística:** Algoritmo de scoring para encontrar preços automaticamente.
3.  **Cross-Frame Navigation:** Capacidade de extrair dados de widgets financeiros isolados.
4.  **SMTP Seguro:** Notificação por e-mail configurada para Gmail/Outlook.

### 📈 Análise de Complexidade (Big O)

*   **Tempo:** $O(N \cdot (E + F))$, onde $N$ é o número de checagens, $E$ elementos no DOM e $F$ o número de frames a serem percorridos.
*   **Espaço:** $O(M)$ de memória do navegador, dependente da densidade de mídia do site monitorado.

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
   python -m src.main
   ```

## Integrantes
Iago de Souza Gomes - 2312130087
