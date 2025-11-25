"""
Script para popular dados de teste de cotações
"""
from app.db import SessionLocal, init_db
from app.models_modules import (
    Cotacao, ItemCotacao, RespostaFornecedor, ItemRespostaFornecedor,
    Fornecedor, Material, StatusCotacao
)
from datetime import datetime, timedelta


def seed_cotacoes():
    """Popula banco com dados de teste de cotações"""
    init_db()
    session = SessionLocal()
    
    try:
        # Verificar se já existem cotações
        existing = session.query(Cotacao).first()
        if existing:
            print("⚠️  Cotações já existem no banco. Pulando seed.")
            return
        
        # Buscar fornecedores e materiais existentes
        fornecedores = session.query(Fornecedor).limit(3).all()
        materiais = session.query(Material).limit(3).all()
        
        if not fornecedores:
            print("❌ Nenhum fornecedor encontrado. Execute seed_data.py primeiro.")
            return
        
        if not materiais:
            print("❌ Nenhum material encontrado. Execute seed_data.py primeiro.")
            return
        
        print("📝 Criando cotações de teste...")
        
        # =====================================================================
        # COTAÇÃO 1 - Materiais de Escritório
        # =====================================================================
        cotacao1 = Cotacao(
            numero="COT-0001",
            descricao="Materiais de Escritório - Q1 2025",
            data_solicitacao=datetime.utcnow(),
            data_limite_resposta=datetime.utcnow() + timedelta(days=7),
            status=StatusCotacao.RESPONDIDA,
            observacoes="Cotação urgente para reposição de estoque"
        )
        session.add(cotacao1)
        session.flush()
        
        # Itens da cotação 1
        item1_cot1 = ItemCotacao(
            cotacao_id=cotacao1.id,
            material_id=materiais[0].id if len(materiais) > 0 else None,
            descricao="Caneta Esferográfica Azul",
            quantidade=100,
            unidade="UN",
            observacoes="Preferência por marca conhecida"
        )
        session.add(item1_cot1)
        
        item2_cot1 = ItemCotacao(
            cotacao_id=cotacao1.id,
            material_id=materiais[1].id if len(materiais) > 1 else None,
            descricao="Papel A4 Sulfite 75g",
            quantidade=50,
            unidade="RESMA",
            observacoes="Papel branco, boa qualidade"
        )
        session.add(item2_cot1)
        session.flush()
        
        # Resposta Fornecedor 1 para Cotação 1
        resposta1_f1 = RespostaFornecedor(
            cotacao_id=cotacao1.id,
            fornecedor_id=fornecedores[0].id,
            prazo_entrega_dias=5,
            condicao_pagamento="30 dias",
            observacoes="Preços especiais para compra acima de R$ 1000",
            selecionada=1
        )
        session.add(resposta1_f1)
        session.flush()
        
        item_resp1_1 = ItemRespostaFornecedor(
            resposta_id=resposta1_f1.id,
            item_cotacao_id=item1_cot1.id,
            preco_unitario=2.50,
            preco_total=250.00,
            marca="BIC"
        )
        session.add(item_resp1_1)
        
        item_resp1_2 = ItemRespostaFornecedor(
            resposta_id=resposta1_f1.id,
            item_cotacao_id=item2_cot1.id,
            preco_unitario=18.50,
            preco_total=925.00,
            marca="Chamex"
        )
        session.add(item_resp1_2)
        
        resposta1_f1.valor_total = 1175.00
        cotacao1.melhor_fornecedor_id = fornecedores[0].id
        
        # Resposta Fornecedor 2 para Cotação 1
        if len(fornecedores) > 1:
            resposta1_f2 = RespostaFornecedor(
                cotacao_id=cotacao1.id,
                fornecedor_id=fornecedores[1].id,
                prazo_entrega_dias=7,
                condicao_pagamento="45 dias",
                observacoes="Frete grátis para compras acima de R$ 1500"
            )
            session.add(resposta1_f2)
            session.flush()
            
            ItemRespostaFornecedor(
                resposta_id=resposta1_f2.id,
                item_cotacao_id=item1_cot1.id,
                preco_unitario=2.80,
                preco_total=280.00,
                marca="Faber Castell"
            )
            session.add(item_resp1_1)
            
            ItemRespostaFornecedor(
                resposta_id=resposta1_f2.id,
                item_cotacao_id=item2_cot1.id,
                preco_unitario=19.00,
                preco_total=950.00,
                marca="Report"
            )
            session.add(item_resp1_2)
            
            resposta1_f2.valor_total = 1230.00
        
        # =====================================================================
        # COTAÇÃO 2 - Equipamentos de Informática
        # =====================================================================
        cotacao2 = Cotacao(
            numero="COT-0002",
            descricao="Equipamentos de TI - Expansão",
            data_solicitacao=datetime.utcnow() - timedelta(days=2),
            data_limite_resposta=datetime.utcnow() + timedelta(days=5),
            status=StatusCotacao.ENVIADA,
            observacoes="Orçamento para expansão do parque tecnológico"
        )
        session.add(cotacao2)
        session.flush()
        
        # Itens da cotação 2
        item1_cot2 = ItemCotacao(
            cotacao_id=cotacao2.id,
            descricao="Mouse Óptico USB",
            quantidade=20,
            unidade="UN",
            observacoes="Ergonômico, com scroll"
        )
        session.add(item1_cot2)
        
        item2_cot2 = ItemCotacao(
            cotacao_id=cotacao2.id,
            descricao="Teclado USB ABNT2",
            quantidade=20,
            unidade="UN",
            observacoes="Resistente a respingos"
        )
        session.add(item2_cot2)
        session.flush()
        
        # =====================================================================
        # COTAÇÃO 3 - Materiais de Limpeza
        # =====================================================================
        cotacao3 = Cotacao(
            numero="COT-0003",
            descricao="Materiais de Limpeza - Trimestre",
            data_solicitacao=datetime.utcnow() - timedelta(days=5),
            data_limite_resposta=datetime.utcnow() - timedelta(days=1),
            status=StatusCotacao.RASCUNHO,
            observacoes="Cotação para fechamento no final do mês"
        )
        session.add(cotacao3)
        session.flush()
        
        item1_cot3 = ItemCotacao(
            cotacao_id=cotacao3.id,
            descricao="Detergente Líquido 500ml",
            quantidade=50,
            unidade="UN"
        )
        session.add(item1_cot3)
        
        item2_cot3 = ItemCotacao(
            cotacao_id=cotacao3.id,
            descricao="Álcool 70% - 1 Litro",
            quantidade=30,
            unidade="UN"
        )
        session.add(item2_cot3)
        
        session.commit()
        
        print("✅ Seed de cotações concluído!")
        print(f"   - {session.query(Cotacao).count()} cotações criadas")
        print(f"   - {session.query(ItemCotacao).count()} itens de cotação criados")
        print(f"   - {session.query(RespostaFornecedor).count()} respostas de fornecedores criadas")
        print(f"   - {session.query(ItemRespostaFornecedor).count()} itens de resposta criados")
        
    except Exception as e:
        print(f"❌ Erro ao popular cotações: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_cotacoes()
