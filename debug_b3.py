import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()
        print("--- Iniciando Inspeção Técnica B3 ---")
        try:
            await page.goto('https://www.b3.com.br/pt_br/para-voce', wait_until='load', timeout=60000)
            await page.wait_for_timeout(8000) # Tempo extra para carregar widgets
            
            print(f"Total de Frames: {len(page.frames)}")
            for i, frame in enumerate(page.frames):
                url = frame.url
                try:
                    # Procura por números na faixa de 100.000 a 150.000
                    found = await frame.evaluate("""
                        () => {
                            const results = [];
                            const elements = document.querySelectorAll('span, div, p, b');
                            for (const el of elements) {
                                const text = el.innerText.trim();
                                // Regex para número de 6 dígitos (ex: 125.432 ou 125432)
                                if (/\\d{2,3}[.,]\\d{3}/.test(text) && text.length < 15) {
                                    results.push({
                                        text: text,
                                        path: el.tagName,
                                        parent: el.parentElement ? el.parentElement.tagName : ''
                                    });
                                }
                            }
                            return results;
                        }
                    """)
                    if found and len(found) > 0:
                        print(f"[!] Candidatos encontrados no Frame {i} (URL: {url[:50]}):")
                        for f in found[:3]:
                            print(f"    -> {f['text']} (Tag: {f['path']})")
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Erro na navegação: {e}")
        finally:
            await browser.close()
            print("--- Fim da Inspeção ---")

asyncio.run(inspect())
