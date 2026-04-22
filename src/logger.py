import logging
import os
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

# Instância global do Rich Console para UI
console = Console()

def setup_logger(user_name: str):
    """
    Configura o sistema de log persistente e no console.
    
    :param user_name: Nome do usuário para registro inicial no log.
    """
    log_filename = "app.log"
    
    # Configuração básica do logging para arquivo
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            RichHandler(rich_tracebacks=True, console=console)
        ]
    )
    
    logger = logging.getLogger("AuctionAssistant")
    logger.info(f"Sessão iniciada pelo usuário: {user_name}")
    return logger

def log_price_change(logger, old_price, new_price, xpath):
    """
    Registra especificamente uma mudança de preço.
    """
    msg = f"ALTERAÇÃO DETECTADA - XPath: {xpath} | Valor Antigo: {old_price} | Novo Valor: {new_price}"
    logger.info(msg)
    console.print(f"[bold green]{msg}[/bold green]")

def log_action(logger, action_desc):
    """
    Registra uma ação genérica do usuário ou do sistema.
    """
    logger.info(f"AÇÃO: {action_desc}")
