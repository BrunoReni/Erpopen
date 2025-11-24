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


def obter_saldo_por_local(material_id: int, local_id: int, db: Session) -> float:
    """
    Obtém o saldo de um material em um local específico
    """
    from app.models_modules import EstoquePorLocal
    
    estoque = db.query(EstoquePorLocal).filter(
        EstoquePorLocal.material_id == material_id,
        EstoquePorLocal.local_id == local_id
    ).first()
    
    return estoque.quantidade if estoque else 0.0


def criar_ou_atualizar_estoque_local(
    material_id: int, 
    local_id: int, 
    quantidade: float,
    db: Session
) -> None:
    """
    Cria ou atualiza o registro de estoque por local
    """
    from app.models_modules import EstoquePorLocal
    from datetime import datetime
    
    estoque = db.query(EstoquePorLocal).filter(
        EstoquePorLocal.material_id == material_id,
        EstoquePorLocal.local_id == local_id
    ).first()
    
    if estoque:
        estoque.quantidade = quantidade
        estoque.updated_at = datetime.utcnow()
    else:
        estoque = EstoquePorLocal(
            material_id=material_id,
            local_id=local_id,
            quantidade=quantidade
        )
        db.add(estoque)
    
    db.flush()  # Garante que foi salvo sem commitar


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


def processar_movimentacao_estoque(
    material_id: int,
    tipo_movimento: str,
    quantidade: float,
    local_origem_id: int = None,
    local_destino_id: int = None,
    db: Session = None,
    permitir_negativo: bool = False
) -> dict:
    """
    Processa uma movimentação de estoque e atualiza os saldos
    
    Tipos de movimento:
    - ENTRADA: adiciona ao local_destino
    - SAIDA: remove do local_origem
    - TRANSFERENCIA: remove de origem e adiciona em destino
    - AJUSTE: ajusta para a quantidade especificada
    
    Retorna dict com sucesso e mensagem
    """
    from app.models_modules import Material, EstoquePorLocal, TipoMovimento
    
    if quantidade <= 0:
        return {"sucesso": False, "mensagem": "Quantidade deve ser maior que zero"}
    
    # Buscar material
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        return {"sucesso": False, "mensagem": "Material não encontrado"}
    
    try:
        if tipo_movimento == "ENTRADA":
            if not local_destino_id:
                return {"sucesso": False, "mensagem": "Local de destino obrigatório para entrada"}
            
            # Adiciona ao estoque do local
            saldo_atual = obter_saldo_por_local(material_id, local_destino_id, db)
            novo_saldo = saldo_atual + quantidade
            criar_ou_atualizar_estoque_local(material_id, local_destino_id, novo_saldo, db)
            
        elif tipo_movimento == "SAIDA":
            if not local_origem_id:
                return {"sucesso": False, "mensagem": "Local de origem obrigatório para saída"}
            
            # Remove do estoque do local
            saldo_atual = obter_saldo_por_local(material_id, local_origem_id, db)
            novo_saldo = saldo_atual - quantidade
            
            if novo_saldo < 0 and not permitir_negativo:
                return {
                    "sucesso": False, 
                    "mensagem": f"Estoque insuficiente. Disponível: {saldo_atual}, Solicitado: {quantidade}"
                }
            
            criar_ou_atualizar_estoque_local(material_id, local_origem_id, novo_saldo, db)
            
        elif tipo_movimento == "TRANSFERENCIA":
            if not local_origem_id or not local_destino_id:
                return {"sucesso": False, "mensagem": "Local de origem e destino obrigatórios para transferência"}
            
            if local_origem_id == local_destino_id:
                return {"sucesso": False, "mensagem": "Local de origem e destino não podem ser iguais"}
            
            # Remove da origem
            saldo_origem = obter_saldo_por_local(material_id, local_origem_id, db)
            novo_saldo_origem = saldo_origem - quantidade
            
            if novo_saldo_origem < 0 and not permitir_negativo:
                return {
                    "sucesso": False, 
                    "mensagem": f"Estoque insuficiente na origem. Disponível: {saldo_origem}, Solicitado: {quantidade}"
                }
            
            criar_ou_atualizar_estoque_local(material_id, local_origem_id, novo_saldo_origem, db)
            
            # Adiciona ao destino
            saldo_destino = obter_saldo_por_local(material_id, local_destino_id, db)
            novo_saldo_destino = saldo_destino + quantidade
            criar_ou_atualizar_estoque_local(material_id, local_destino_id, novo_saldo_destino, db)
            
        elif tipo_movimento == "AJUSTE":
            if not local_destino_id:
                return {"sucesso": False, "mensagem": "Local obrigatório para ajuste"}
            
            # Define a quantidade absoluta
            criar_ou_atualizar_estoque_local(material_id, local_destino_id, quantidade, db)
        
        else:
            return {"sucesso": False, "mensagem": f"Tipo de movimento inválido: {tipo_movimento}"}
        
        # Atualiza estoque total do material
        total = calcular_estoque_total(material_id, db)
        material.estoque_atual = total
        
        db.flush()
        
        return {
            "sucesso": True, 
            "mensagem": "Movimentação processada com sucesso",
            "estoque_total": total
        }
        
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao processar movimentação: {str(e)}"}


def obter_historico_movimentacoes(
    material_id: int = None,
    local_id: int = None,
    tipo_movimento: str = None,
    limit: int = 100,
    db: Session = None
) -> list:
    """
    Retorna histórico de movimentações com filtros opcionais
    """
    from app.models_modules import MovimentoEstoque
    
    query = db.query(MovimentoEstoque)
    
    if material_id:
        query = query.filter(MovimentoEstoque.material_id == material_id)
    
    if local_id:
        query = query.filter(
            (MovimentoEstoque.local_origem_id == local_id) |
            (MovimentoEstoque.local_destino_id == local_id)
        )
    
    if tipo_movimento:
        query = query.filter(MovimentoEstoque.tipo_movimento == tipo_movimento)
    
    movimentos = query.order_by(MovimentoEstoque.data_movimento.desc()).limit(limit).all()
    
    return movimentos
