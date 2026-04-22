import asyncio
import sys
from rich.prompt import Prompt
from rich.panel import Panel
from src.validators import validate_username, validate_url, validate_timeout
from src.logger import setup_logger, console, log_action
from src.monitor import AuctionMonitor
from src.notifier import Notifier

async def main():
    """
    Função principal do assistente de leilão.
    """
    console.print(Panel("[bold cyan]Assistente de Lances Automático[/bold cyan]\nMonitor de Preços em Tempo Real", expand=False))
    
    # Coleta de dados com validação obrigatória
    while True:
        user_name = Prompt.ask("[bold yellow]Digite seu nome[/bold yellow] (mín. 3 caracteres alfabéticos)")
        if validate_username(user_name):
            break
        console.print("[bold red]Nome inválido. Use pelo menos 3 caracteres alfabéticos (apenas letras).[/bold red]")

    logger = setup_logger(user_name)
    log_action(logger, f"Usuário {user_name} logado com sucesso.")

    while True:
        auction_url = Prompt.ask("[bold yellow]URL da página de leilão[/bold yellow]")
        if validate_url(auction_url):
            break
        console.print("[bold red]URL inválida. Por favor, insira uma URL completa (ex: http://...)[/bold red]")

    xpath_selector = Prompt.ask("[bold yellow]XPath ou Seletor do campo de preço[/bold yellow]")
    
    while True:
        timeout_str = Prompt.ask("[bold yellow]Intervalo de monitoramento (segundos)[/bold yellow]", default="5")
        if validate_timeout(timeout_str):
            interval = int(timeout_str)
            break
        console.print("[bold red]Timeout inválido. Insira um número inteiro positivo.[/bold red]")

    # Inicializa componentes
    notifier = Notifier()
    monitor = AuctionMonitor(auction_url, xpath_selector, interval, logger)

    async def on_price_change(old_val, new_val):
        log_action(logger, f"Iniciando notificação de mudança: {old_val} -> {new_val}")
        success = await notifier.send_notification(old_val, new_val)
        if success:
            log_action(logger, "Notificação enviada com sucesso para a segunda página.")
        else:
            log_action(logger, "Falha ao enviar notificação para a segunda página.")

    console.print(f"\n[bold green]Iniciando monitoramento em: {auction_url}[/bold green]")
    console.print("[italic blue]Pressione Ctrl+C para encerrar com segurança.[/italic blue]\n")
    
    try:
        await monitor.start(on_price_change)
    except KeyboardInterrupt:
        log_action(logger, "Monitoramento encerrado pelo usuário via Ctrl+C.")
        console.print("\n[bold yellow]Encerrando assistente...[/bold yellow]")
    except Exception as e:
        logger.critical(f"Erro inesperado no sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
