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
        Utiliza um sistema de pontuação (scoring) para priorizar o preço principal.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                
                # Algoritmo de Scoring Avançado em JavaScript
                candidates = await page.evaluate("""
                    () => {
                        const results = [];
                        const priceRegex = /(R\\$\\s?|\\$|€)?\\s?\\d+([.,]\\d{2,3})*([.,]\\d{2})?/i;
                        const keywords = ['price', 'valor', 'offer', 'sale', 'current', 'main', 'pix', 'boleto'];
                        
                        function getRobustXPath(element) {
                            if (element.id) return `//*[@id="${element.id}"]`;
                            const attrs = ['data-test', 'data-testid', 'data-qa', 'itemprop'];
                            for (const attr of attrs) {
                                if (element.getAttribute(attr)) {
                                    return `//${element.tagName.toLowerCase()}[@${attr}="${element.getAttribute(attr)}"]`;
                                }
                            }
                            // Fallback para XPath hierárquico curto
                            let path = '';
                            let current = element;
                            for (let i = 0; i < 3 && current && current !== document.body; i++) {
                                let tag = current.tagName.toLowerCase();
                                let index = 1;
                                let sibling = current.previousElementSibling;
                                while (sibling) {
                                    if (sibling.tagName === current.tagName) index++;
                                    sibling = sibling.previousElementSibling;
                                }
                                path = `/${tag}[${index}]${path}`;
                                current = current.parentElement;
                            }
                            return `//${current.tagName.toLowerCase()}${path}`;
                        }

                        const elements = document.querySelectorAll('span, p, div, b, strong, h1, h2');
                        for (const el of elements) {
                            const text = el.innerText.trim();
                            if (priceRegex.test(text) && text.length < 25 && el.children.length <= 1) {
                                let score = 0;
                                const content = (el.id + el.className + el.getAttribute('data-test') || '').toLowerCase();
                                
                                // Pontuação por palavras-chave
                                keywords.forEach(word => { if (content.includes(word)) score += 40; });
                                
                                // Pontuação por símbolo de moeda (Prioridade R$)
                                if (text.includes('R$')) score += 50;
                                else if (text.includes('$')) score += 20;
                                
                                // Pontuação por posição na árvore (tags fortes)
                                if (['H1', 'H2', 'B', 'STRONG'].includes(el.tagName)) score += 30;
                                
                                // Penalidade para textos muito longos ou muito curtos
                                if (text.length > 15) score -= 10;
                                
                                results.push({
                                    text: text,
                                    xpath: getRobustXPath(el),
                                    score: score
                                });
                            }
                        }
                        
                        // Ordena pelos melhores scores e remove duplicados
                        return results
                            .sort((a, b) => b.score - a.score)
                            .filter((v, i, a) => a.findIndex(t => t.text === v.text) === i)
                            .slice(0, 5);
                    }
                """)
                return candidates
            except Exception as e:
                self.logger.error(f"Erro na descoberta automática: {e}")
                return []
            finally:
                await browser.close()

    async def simplify_xpath(self, fragile_xpath):
        """
        Recebe um XPath longo/frágil, encontra o elemento no browser
        e tenta gerar um XPath robusto baseado em atributos (ID, data-testid, etc).
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                element = await page.query_selector(f"xpath={fragile_xpath}")
                
                if not element:
                    return fragile_xpath

                robust_xpath = await page.evaluate("""
                    (el) => {
                        if (el.id) return `//*[@id="${el.id}"]`;
                        
                        const attrs = ['data-test', 'data-testid', 'data-qa', 'itemprop', 'name'];
                        for (const attr of attrs) {
                            if (el.getAttribute(attr)) {
                                return `//${el.tagName.toLowerCase()}[@${attr}="${el.getAttribute(attr)}"]`;
                            }
                        }
                        
                        if (el.className && typeof el.className === 'string' && el.className.split(' ').length === 1) {
                            return `//${el.tagName.toLowerCase()}[@class="${el.className}"]`;
                        }
                        
                        return null;
                    }
                """, element)
                
                return robust_xpath if robust_xpath else fragile_xpath
            except Exception:
                return fragile_xpath
            finally:
                await browser.close()

    async def start(self, notifier_callback):
        """
        Inicia o loop de monitoramento.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Aplica camuflagem também no loop principal de monitoramento
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                self.logger.info(f"Navegando para: {self.url}")
                await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                
                # Inicializa o valor atual
                element = await page.wait_for_selector(self.selector, timeout=60000)
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
