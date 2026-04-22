import re
from urllib.parse import urlparse
import validators

def validate_username(name: str) -> bool:
    """
    Valida se o nome de usuário tem pelo menos 3 caracteres alfabéticos.
    
    :param name: Nome a ser validado.
    :return: True se válido, False caso contrário.
    """
    # Remove espaços e verifica se contém apenas letras e tem tamanho >= 3
    clean_name = name.replace(" ", "")
    return len(clean_name) >= 3 and clean_name.isalpha()

def validate_url(url: str) -> bool:
    """
    Valida se a string fornecida é uma URL válida.
    
    :param url: URL a ser validada.
    :return: True se válida, False caso contrário.
    """
    return bool(validators.url(url))

def validate_timeout(timeout_str: str) -> bool:
    """
    Valida se o timeout fornecido é um número inteiro positivo.
    
    :param timeout_str: String representando o timeout.
    :return: True se válido, False caso contrário.
    """
    try:
        val = int(timeout_str)
        return val > 0
    except ValueError:
        return False

def parse_price(price_str: str) -> float:
    """
    Converte uma string de preço (ex: 'R$ 1.234,50') em um float.
    
    :param price_str: String do preço extraída da web.
    :return: Valor em float.
    :raises ValueError: Se a string não contiver um valor numérico válido.
    """
    # Remove caracteres não numéricos, exceto vírgula e ponto
    # Substitui vírgula por ponto se necessário para o padrão float
    clean_str = re.sub(r'[^\d,.]', '', price_str)
    
    if not clean_str:
        raise ValueError(f"Não foi possível encontrar um valor numérico em: {price_str}")

    # Lógica para tratar formatos brasileiros (1.234,50) e americanos (1,234.50)
    if ',' in clean_str and '.' in clean_str:
        if clean_str.rfind(',') > clean_str.rfind('.'):
            # Formato brasileiro: 1.234,50 -> 1234.50
            clean_str = clean_str.replace('.', '').replace(',', '.')
        else:
            # Formato americano: 1,234.50 -> 1234.50
            clean_str = clean_str.replace(',', '')
    elif ',' in clean_str:
        # Apenas vírgula: assumimos que é o separador decimal (ex: 1234,50)
        clean_str = clean_str.replace(',', '.')
    
    return float(clean_str)
