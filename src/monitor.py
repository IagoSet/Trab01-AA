import asyncio
from playwright.async_api import async_playwright
from src.validators import parse_price
from src.logger import log_price_change

class AuctionMonitor:
    """
    Monitora uma URL de leilão em busca de alterações de preço.
    """
    
    def __init__(self, url, selector, interval, logger):
        self.url = url
        self.selector = selector
        self.interval = interval
        self.logger = logger
        self.current_value = None

    async def discover_price_elements(self):
        """
        Tenta encontrar automaticamente elementos que pareçam ser preços na página.
        Retorna uma lista de dicionários com 'text' e 'xpath'.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(self.url, wait_until="networkidle")
                
                # Script JS para encontrar elementos que contenham padrões de preço (R$, $, números com vírgula)
                # Foca em elementos pequenos (folhas da árvore DOM) para precisão
                candidates = await page.evaluate("""
                    () => {
                        const results = [];
                        const regex = /(R\\$\\s?|\\$|€)\\s?\\d+[.,]?\\d*/i;
                        
                        function getXPath(element) {
                            if (element.id !== '') return `//*[@id="${element.id}"]`;
                            if (element === document.body) return '/html/body';
                            let ix = 0;
                            const siblings = element.parentNode.childNodes;
                            for (let i = 0; i < siblings.length; i++) {
                                const sibling = siblings[i];
                                if (sibling === element) return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
                            }
                        }

                        const allElements = document.querySelectorAll('span, div, b, strong, p, h1, h2, h3, h4, h5, li');
                        for (const el of allElements) {
                            const text = el.innerText.trim();
                            // Verifica se o texto combina com preço e se o elemento não tem muitos filhos (é um 'nó folha')
                            if (regex.test(text) && el.children.length <= 2 && text.length < 30) {
                                results.push({
                                    text: text,
                                    xpath: getXPath(el)
                                });
                            }
                        }
                        return results.slice(0, 5); // Retorna os 5 primeiros candidatos
                    }
                """)
                return candidates
            except Exception as e:
                self.logger.error(f"Erro na descoberta automática: {e}")
                return []
            finally:
                await browser.close()

    async def start(self, notifier_callback):
        """
        Inicia o loop de monitoramento.
        
        Complexidade:
        Tempo: O(N) para N verificações periódicas.
        Espaço: O(1) mantém apenas o valor atual e o anterior.
        
        :param notifier_callback: Função assíncrona para chamar ao detectar mudança.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                self.logger.info(f"Navegando para: {self.url}")
                await page.goto(self.url, wait_until="domcontentloaded")
                
                # Inicializa o valor atual
                # O motor de busca do browser por XPath tem complexidade O(E) (E = elementos no DOM)
                element = await page.wait_for_selector(self.selector, timeout=30000)
                if not element:
                    self.logger.error("Elemento não encontrado no início do monitoramento.")
                    return

                text_value = await element.inner_text()
                self.current_value = parse_price(text_value)
                self.logger.info(f"Monitoramento iniciado. Valor atual: {self.current_value}")
                
                while True:
                    await asyncio.sleep(self.interval)
                    
                    try:
                        # Log de batimento cardíaco para mostrar que está ativo
                        self.logger.info(f"Verificando... (O preço continua: {self.current_value})")
                        
                        # Recarrega ou re-seleciona para garantir frescor do dado (SPA-friendly)
                        element = await page.query_selector(self.selector)
                        if element:
                            new_text = await element.inner_text()
                            new_value = parse_price(new_text)
                            
                            if new_value != self.current_value:
                                log_price_change(self.logger, self.current_value, new_value, self.selector)
                                # Dispara notificação
                                await notifier_callback(self.current_value, new_value)
                                self.current_value = new_value
                        else:
                            self.logger.warning(f"Elemento {self.selector} não encontrado nesta iteração.")
                            
                    except Exception as e:
                        self.logger.error(f"Erro durante a iteração de monitoramento: {e}")
                        
            except Exception as e:
                self.logger.critical(f"Erro fatal no monitoramento: {e}")
            finally:
                await browser.close()
