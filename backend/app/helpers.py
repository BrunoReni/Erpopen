"""Funções auxiliares para o sistema"""

from sqlalchemy.orm import Session
from app.models_modules import Fornecedor, Cliente, Material


def gerar_codigo_fornecedor(db: Session) -> str:
    """
    Gera código automático sequencial para fornecedor
    Formato: FOR-0001, FOR-0002, etc
    """
    ultimo = db.query(Fornecedor).filter(
        Fornecedor.codigo.isnot(None)
    ).order_by(Fornecedor.id.desc()).first()
    
    if ultimo and ultimo.codigo:
        try:
            # Extrai o número do último código (FOR-0001 -> 1)
            num = int(ultimo.codigo.split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    
    return f"FOR-{num:04d}"


def gerar_codigo_cliente(db: Session) -> str:
    """
    Gera código automático sequencial para cliente
    Formato: CLI-0001, CLI-0002, etc
    """
    ultimo = db.query(Cliente).filter(
        Cliente.codigo.isnot(None)
    ).order_by(Cliente.id.desc()).first()
    
    if ultimo and ultimo.codigo:
        try:
            num = int(ultimo.codigo.split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    
    return f"CLI-{num:04d}"


def gerar_codigo_material(db: Session) -> str:
    """
    Gera código automático sequencial para material
    Formato: MAT-0001, MAT-0002, etc
    """
    ultimo = db.query(Material).filter(
        Material.codigo.isnot(None)
    ).order_by(Material.id.desc()).first()
    
    if ultimo and ultimo.codigo:
        try:
            # Se o código já segue o padrão MAT-XXXX
            if ultimo.codigo.startswith('MAT-'):
                num = int(ultimo.codigo.split('-')[1]) + 1
            else:
                # Se é um código antigo, começa do 1
                num = 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    
    return f"MAT-{num:04d}"


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # CPF deve ter 11 dígitos
    if len(cpf) != 11:
        return False
    
    # CPF não pode ter todos os dígitos iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro
    """
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    # CNPJ deve ter 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # CNPJ não pode ter todos os dígitos iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Valida primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        return False
    
    # Valida segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cnpj[13]) == digito2


def calcular_estoque_total(material_id: int, db: Session) -> float:
    """
    Calcula o estoque total de um material somando todos os locais
    """
    from app.models_modules import EstoquePorLocal
    from sqlalchemy import func
    
    total = db.query(
        func.sum(EstoquePorLocal.quantidade)
    ).filter(
        EstoquePorLocal.material_id == material_id
    ).scalar()
    
    return total or 0.0


def atualizar_estoque_material(material_id: int, db: Session):
    """
    Atualiza o estoque_atual do material somando todos os locais
    """
    total = calcular_estoque_total(material_id, db)
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if material:
        material.estoque_atual = total
        db.commit()
        db.refresh(material)
    
    return total
