import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from src.validators import parse_price
from src.logger import log_price_change

class AuctionMonitor:
    """
    Monitora uma URL em busca de alterações de preço, lidando com iFrames,
    Shadow DOM e proteções anti-bot.
    """
    
    def __init__(self, url, selector, interval, logger):
        self.url = url
        self.selector = selector
        self.interval = interval
        self.logger = logger
        self.current_value = None

    async def _apply_stealth(self, page):
        """Aplica camuflagem para evitar detecção de robôs."""
        await stealth_async(page)

    async def _auto_scroll(self, page):
        """Rola a página para carregar elementos de lazy loading."""
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 100;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)

    async def discover_price_elements(self):
        """
        Tenta encontrar preços na página principal e dentro de todos os iFrames.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await self._apply_stealth(page)
            
            try:
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                await self._auto_scroll(page)
                
                # Script de busca que será executado em cada frame
                search_script = """
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
                            return `//${current ? current.tagName.toLowerCase() : 'body'}${path}`;
                        }

                        const elements = document.querySelectorAll('span, p, div, b, strong, h1, h2, font');
                        for (const el of elements) {
                            const text = el.innerText.trim();
                            if (priceRegex.test(text) && text.length < 25 && el.children.length <= 1) {
                                let score = 0;
                                const content = (el.id + el.className + (el.getAttribute('data-test') || '')).toLowerCase();
                                keywords.forEach(word => { if (content.includes(word)) score += 40; });
                                if (text.includes('R$')) score += 50;
                                else if (text.includes('$')) score += 20;
                                if (['H1', 'H2', 'B', 'STRONG'].includes(el.tagName)) score += 30;
                                results.push({
                                    text: text,
                                    xpath: getRobustXPath(el),
                                    score: score
                                });
                            }
                        }
                        return results;
                    }
                """

                all_candidates = []
                
                # Busca na página principal
                main_results = await page.evaluate(search_script)
                for res in main_results:
                    res['frame_selector'] = None
                    all_candidates.append(res)

                # Busca em todos os frames
                for i, frame in enumerate(page.frames[1:]): # Pula o main frame
                    try:
                        frame_results = await frame.evaluate(search_script)
                        for res in frame_results:
                            # Tenta identificar o frame por ID ou Name, senão usa index
                            f_id = frame.name or f"index={i+1}"
                            res['frame_selector'] = f_id
                            all_candidates.append(res)
                    except:
                        continue

                # Ordena e filtra
                return sorted(all_candidates, key=lambda x: x['score'], reverse=True)[:5]
            except Exception as e:
                self.logger.error(f"Erro na descoberta automática: {e}")
                return []
            finally:
                await browser.close()

    async def start(self, notifier_callback):
        """
        Inicia o loop de monitoramento com suporte a Frames e Stealth.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await self._apply_stealth(page)
            
            try:
                self.logger.info(f"Navegando para: {self.url}")
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(3) # Estabilização
                
                # Lógica de seleção (suporta frame >> seletor)
                async def get_price_element():
                    if " >> " in self.selector:
                        parts = self.selector.split(" >> ", 1)
                        frame_ref = parts[0].replace("frame=", "")
                        inner_selector = parts[1]
                        
                        # Localiza o frame por nome ou id
                        frame = page.frame(name=frame_ref) or page.frame(url=re.compile(frame_ref))
                        if not frame:
                            # Busca por seletor de elemento iframe se não achar por nome
                            frame_element = await page.query_selector(frame_ref)
                            if frame_element:
                                frame = await frame_element.content_frame()
                        
                        return await frame.query_selector(inner_selector) if frame else None
                    else:
                        return await page.query_selector(self.selector)

                element = await get_price_element()
                if not element:
                    self.logger.warning("Aguardando elemento aparecer...")
                    await asyncio.sleep(5)
                    element = await get_price_element()

                if not element:
                    self.logger.error(f"Elemento {self.selector} não encontrado.")
                    return

                text_value = await element.inner_text()
                self.current_value = parse_price(text_value)
                self.logger.info(f"Monitoramento iniciado. Valor atual: {self.current_value}")
                
                while True:
                    await asyncio.sleep(self.interval)
                    try:
                        element = await get_price_element()
                        if element:
                            new_text = await element.inner_text()
                            new_value = parse_price(new_text)
                            
                            if new_value != self.current_value:
                                log_price_change(self.logger, self.current_value, new_value, self.selector)
                                await notifier_callback(self.current_value, new_value)
                                self.current_value = new_value
                        else:
                            self.logger.warning("Elemento sumiu da página. Tentando reconectar...")
                    except Exception as e:
                        self.logger.error(f"Erro na iteração: {e}")
                        
            except Exception as e:
                self.logger.critical(f"Erro fatal: {e}")
            finally:
                await browser.close()
