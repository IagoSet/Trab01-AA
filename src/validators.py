import re
from urllib.parse import urlparse
import validators

def validate_username(name: str) -> bool:
    clean_name = name.replace(" ", "")
    return len(clean_name) >= 3 and clean_name.isalpha()

def validate_url(url: str) -> bool:
    return bool(validators.url(url))

def validate_timeout(timeout_str: str) -> bool:
    try:
        val = int(timeout_str)
        return val > 0
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    return bool(validators.email(email))

def parse_price(price_str: str):
    """
    Tenta extrair um valor inteligente do texto.
    Se for hora (HH:MM:SS), mantém como string.
    Se for preço, converte para float.
    """
    price_str = price_str.strip()
    
    # 1. Verifica se é um horário (HH:MM:SS ou HH:MM)
    if re.search(r'\d{1,2}:\d{2}(?::\d{2})?', price_str):
        # Extrai apenas a parte da hora para evitar lixo ao redor
        match = re.search(r'\d{1,2}:\d{2}(?::\d{2})?', price_str)
        return match.group(0)

    # 2. Lógica Original de Preço
    matches = re.findall(r'\d+[.,\d]*', price_str)
    if not matches:
        # Se não achou nada numérico, retorna o texto bruto como fallback
        return price_str

    clean_str = matches[0].rstrip('.,')

    if ',' in clean_str and '.' in clean_str:
        if clean_str.rfind(',') > clean_str.rfind('.'):
            clean_str = clean_str.replace('.', '').replace(',', '.')
        else:
            clean_str = clean_str.replace(',', '')
    elif ',' in clean_str:
        # Se tem vírgula e parece decimal (ex: 10,50 ou 1.200,00)
        # Se houver apenas uma vírgula e for o separador de milhar/decimal
        clean_str = clean_str.replace(',', '.')
    
    try:
        # Se após a limpeza ainda tiver múltiplos pontos, é formato de milhar sem decimal
        if clean_str.count('.') > 1:
            clean_str = clean_str.replace('.', '')
        return float(clean_str)
    except ValueError:
        return price_str # Retorna bruto se tudo falhar
