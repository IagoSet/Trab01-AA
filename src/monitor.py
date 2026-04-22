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
