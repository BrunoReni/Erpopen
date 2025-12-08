"""
Script para popular o banco de dados com dados reais da empresa
CNPJ: 45.439.857/0001-40
"""

from datetime import datetime, timedelta
from app.db import SessionLocal
from app.models_modules import (
    Fornecedor, Cliente, ContaPagar, ContaReceber, 
    ContaBancaria, CentroCusto, LocalEstoque
)

db = SessionLocal()

try:
    print("🏢 Criando dados da empresa...")
    
    # ============================================================================
    # 1. FORNECEDOR: BV FINANCEIRA
    # ============================================================================
    print("\n📦 Criando fornecedor: BV Financeira...")
    bv_financeira = Fornecedor(
        codigo="FOR-0001",
        nome="BV FINANCEIRA S.A.",
        razao_social="BV FINANCEIRA S.A. CREDITO FINANCIAMENTO E INVESTIMENTO",
        cnpj="01.800.019/0001-04",
        telefone="(11) 2847-9280",
        email="atendimento@bvfinanceira.com.br",
        endereco="Av. das Nações Unidas, 14171 - Torre B",
        cidade="São Paulo",
        estado="SP",
        cep="04794-000",
        ativo=1
    )
    db.add(bv_financeira)
    db.flush()
    
    # ============================================================================
    # 2. CLIENTE: ALICE TECNOLOGIA LTDA
    # ============================================================================
    print("👤 Criando cliente: Alice Tecnologia Ltda...")
    alice_tech = Cliente(
        codigo="CLI-0001",
        nome="ALICE TECNOLOGIA LTDA",
        razao_social="ALICE TECNOLOGIA LTDA",
        cpf_cnpj="35.612.503/0001-00",
        tipo_pessoa="PJ",
        email="contato@alicetecnologia.com.br",
        telefone="(11) 3090-1035",
        celular="(11) 98765-4321",
        endereco="Rua Tabapuã, 1123",
        numero="Cj 215",
        complemento="Conjunto 215",
        bairro="Itaim Bibi",
        cidade="São Paulo",
        estado="SP",
        cep="04533-014",
        tipo_cliente="atacado",
        limite_credito=50000.00,
        dias_vencimento=30,
        ativo=1
    )
    db.add(alice_tech)
    db.flush()
    
    # ============================================================================
    # 3. CENTRO DE CUSTO
    # ============================================================================
    print("💰 Criando centros de custo...")
    cc_operacional = CentroCusto(
        codigo="CC-001",
        nome="Despesas Operacionais",
        descricao="Despesas operacionais da empresa",
        ativo=1
    )
    db.add(cc_operacional)
    
    cc_financeiro = CentroCusto(
        codigo="CC-002",
        nome="Despesas Financeiras",
        descricao="Despesas financeiras (juros, tarifas, financiamentos)",
        ativo=1
    )
    db.add(cc_financeiro)
    
    cc_vendas = CentroCusto(
        codigo="CC-003",
        nome="Receitas de Vendas",
        descricao="Receitas de vendas de serviços",
        ativo=1
    )
    db.add(cc_vendas)
    db.flush()
    
    # ============================================================================
    # 4. CONTA BANCÁRIA
    # ============================================================================
    print("🏦 Criando conta bancária...")
    conta_principal = ContaBancaria(
        nome="Conta Corrente Principal",
        banco="001",
        agencia="1234-5",
        conta="56789-0",
        saldo_inicial=10000.00,
        saldo_atual=10000.00,
        ativa=1
    )
    db.add(conta_principal)
    db.flush()
    
    # ============================================================================
    # 5. LOCAL DE ESTOQUE
    # ============================================================================
    print("📦 Criando local de estoque...")
    local_principal = LocalEstoque(
        codigo="LOC-0001",
        nome="Almoxarifado Principal",
        tipo="almoxarifado",
        endereco="Endereço da sua empresa",
        responsavel="Admin",
        padrao=1,
        ativo=1
    )
    db.add(local_principal)
    db.flush()
    
    # ============================================================================
    # 6. CONTA A RECEBER: ALICE TECNOLOGIA
    # ============================================================================
    print("💵 Criando conta a receber da Alice Tecnologia...")
    
    data_emissao = datetime(2024, 12, 1)
    data_vencimento = datetime(2024, 12, 10)
    
    conta_receber_alice = ContaReceber(
        cliente_id=alice_tech.id,
        descricao="Serviços prestados - Desenvolvimento de Software",
        valor_original=18000.00,
        data_emissao=data_emissao,
        data_vencimento=data_vencimento,
        status="pendente",
        observacoes="NF 001 - Desenvolvimento de sistema customizado",
        centro_custo_id=cc_vendas.id
    )
    db.add(conta_receber_alice)
    db.flush()
    
    # ============================================================================
    # 7. CONTAS A PAGAR: BV FINANCEIRA (30 parcelas)
    # ============================================================================
    print("💳 Criando 30 parcelas do financiamento BV Financeira...")
    
    valor_parcela = 1054.00
    data_base = datetime(2024, 12, 10)  # Primeira parcela em 10/12/2024
    
    for i in range(1, 31):  # 30 parcelas
        data_vencimento_parcela = data_base + timedelta(days=30 * (i - 1))
        
        conta_pagar = ContaPagar(
            fornecedor_id=bv_financeira.id,
            descricao=f"Financiamento Veículo - Parcela {i}/30",
            valor_original=valor_parcela,
            data_emissao=datetime(2024, 11, 20),
            data_vencimento=data_vencimento_parcela,
            status="pendente",
            observacoes=f"Parcela {i} de 30 - Financiamento de veículo",
            centro_custo_id=cc_financeiro.id
        )
        db.add(conta_pagar)
    
    db.commit()
    
    # ============================================================================
    # RESUMO
    # ============================================================================
    print("\n" + "="*60)
    print("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
    print("="*60)
    print(f"\n📊 RESUMO:")
    print(f"  👤 Cliente: {alice_tech.nome}")
    print(f"     CNPJ: {alice_tech.cpf_cnpj}")
    print(f"     Código: {alice_tech.codigo}")
    print(f"\n  📦 Fornecedor: BV Financeira")
    print(f"     CNPJ: {bv_financeira.cnpj}")
    print(f"     Código: {bv_financeira.codigo}")
    print(f"\n  💵 Conta a Receber:")
    print(f"     Cliente: Alice Tecnologia")
    print(f"     Valor: R$ 18.000,00")
    print(f"     Emissão: 01/12/2024")
    print(f"     Vencimento: 10/12/2024")
    print(f"     Status: Pendente")
    print(f"\n  💳 Contas a Pagar:")
    print(f"     Fornecedor: BV Financeira")
    print(f"     Parcelas: 30x de R$ 1.054,00")
    print(f"     Total: R$ 31.620,00")
    print(f"     Primeira parcela: 10/12/2024")
    print(f"     Última parcela: {(data_base + timedelta(days=30 * 29)).strftime('%d/%m/%Y')}")
    print(f"\n  💰 Centros de Custo: 3 criados")
    print(f"  🏦 Conta Bancária: Banco do Brasil - Saldo R$ 10.000,00")
    print(f"  📦 Local de Estoque: Almoxarifado Principal")
    print("\n" + "="*60)
    print("🎉 Sistema pronto para uso com dados reais!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Erro ao popular banco: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
