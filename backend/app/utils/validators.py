"""
Utility functions for validation
"""
import re


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro
    
    Args:
        cpf: String com CPF (pode conter pontos e traço)
    
    Returns:
        True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    
    if digito1 != int(cpf[9]):
        return False
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    
    if digito2 != int(cpf[10]):
        return False
    
    return True


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro
    
    Args:
        cnpj: String com CNPJ (pode conter pontos, traço e barra)
    
    Returns:
        True se o CNPJ é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Valida primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0
    
    if digito1 != int(cnpj[12]):
        return False
    
    # Valida segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0
    
    if digito2 != int(cnpj[13]):
        return False
    
    return True


def validate_cpf_cnpj(cpf_cnpj: str) -> bool:
    """
    Valida CPF ou CNPJ automaticamente baseado no tamanho
    
    Args:
        cpf_cnpj: String com CPF ou CNPJ
    
    Returns:
        True se o documento é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    documento = re.sub(r'\D', '', cpf_cnpj)
    
    if len(documento) == 11:
        return validate_cpf(cpf_cnpj)
    elif len(documento) == 14:
        return validate_cnpj(cpf_cnpj)
    else:
        return False
