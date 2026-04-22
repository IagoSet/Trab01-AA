import pytest
from src.validators import validate_username, validate_url, validate_timeout, parse_price

def test_validate_username():
    # Válidos
    assert validate_username("Iago") is True
    assert validate_username("Ana Paula") is True # Nome composto, alfabético
    # Inválidos
    assert validate_username("Ia") is False # Muito curto
    assert validate_username("12345") is False # Numérico
    assert validate_username("Iag0") is False # Alfa-numérico
    assert validate_username(" ") is False # Apenas espaços

def test_validate_url():
    # Válidos
    assert validate_url("http://google.com") is True
    assert validate_url("https://www.leilao.com.br/produto/123") is True
    # Inválidos
    assert validate_url("google.com") is False # Sem protocolo
    assert validate_url("leilao") is False
    assert validate_url("htt://malformada.com") is False

def test_validate_timeout():
    # Válidos
    assert validate_timeout("5") is True
    assert validate_timeout("60") is True
    # Inválidos
    assert validate_timeout("0") is False # Não positivo
    assert validate_timeout("-10") is False
    assert validate_timeout("abc") is False
    assert validate_timeout("1.5") is False # Não inteiro

def test_parse_price():
    # Formatos comuns
    assert parse_price("R$ 1.234,50") == 1234.50
    assert parse_price("1,234.50") == 1234.50 # Formato americano
    assert parse_price("R$ 1234,50") == 1234.50
    assert parse_price("R$ 500.00") == 500.00
    assert parse_price("  Preço: 1500  ") == 1500.0
    
    # Casos de erro
    with pytest.raises(ValueError):
        parse_price("Grátis")
    with pytest.raises(ValueError):
        parse_price("")
