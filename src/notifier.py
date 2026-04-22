from playwright.async_api import async_playwright

class Notifier:
    """
    Responsável por interagir com a segunda página web para enviar a notificação.
    """
    
    def __init__(self, target_url="https://formspree.io/f/mnnqyzrj"): # URL de exemplo/estável
        self.target_url = target_url

    async def send_notification(self, old_value, new_value):
        """
        Abre a página de destino, preenche os dados e envia o formulário.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(self.target_url)
                
                # Preenche a mensagem com os valores antigo e novo
                # Nota: Seletores variam conforme o formulário, usaremos seletores genéricos robustos
                message = f"ALERTA DE LEILÃO: O valor mudou de {old_value} para {new_value}."
                
                # Exemplo: Tentando preencher campos comuns de formulário de contato
                # Se não encontrar, apenas loga a tentativa (neste mock)
                if await page.query_selector("textarea"):
                    await page.fill("textarea", message)
                    
                if await page.query_selector("input[type='email']"):
                    await page.fill("input[type='email']", "alerta@leilao.com")

                if await page.query_selector("button[type='submit']"):
                    await page.click("button[type='submit']")
                
                return True
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")
                return False
            finally:
                await browser.close()
