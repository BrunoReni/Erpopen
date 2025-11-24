#!/usr/bin/env python
"""Script para popular dados iniciais (seed) do banco de dados"""

from app.db import SessionLocal, init_db
from app.models_modules import UnidadeMedida, LocalEstoque

def seed_unidades_medida():
    """Popula tabela de unidades de medida com dados padrão"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem unidades
        count = db.query(UnidadeMedida).count()
        if count > 0:
            print(f"⚠️  Já existem {count} unidades de medida. Pulando seed.")
            return
        
        unidades_padrao = [
            ("UN", "Unidade", "unidade", 0),
            ("PC", "Peça", "unidade", 0),
            ("CX", "Caixa", "unidade", 0),
            ("KG", "Quilograma", "peso", 1),
            ("G", "Grama", "peso", 1),
            ("T", "Tonelada", "peso", 1),
            ("L", "Litro", "volume", 1),
            ("ML", "Mililitro", "volume", 1),
            ("M", "Metro", "comprimento", 1),
            ("CM", "Centímetro", "comprimento", 1),
            ("M2", "Metro Quadrado", "area", 1),
            ("M3", "Metro Cúbico", "volume", 1),
            ("PAR", "Par", "unidade", 0),
            ("DZ", "Dúzia", "unidade", 0),
            ("FD", "Fardo", "unidade", 0),
        ]
        
        print("📦 Criando unidades de medida padrão...")
        
        for sigla, nome, tipo, permite_decimal in unidades_padrao:
            unidade = UnidadeMedida(
                sigla=sigla,
                nome=nome,
                tipo=tipo,
                permite_decimal=permite_decimal,
                ativa=1
            )
            db.add(unidade)
            print(f"  ✅ {sigla} - {nome}")
        
        db.commit()
        print(f"\n✅ {len(unidades_padrao)} unidades de medida criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar unidades: {e}")
        db.rollback()
    finally:
        db.close()


def seed_local_estoque_padrao():
    """Cria local de estoque padrão"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe local
        count = db.query(LocalEstoque).count()
        if count > 0:
            print(f"⚠️  Já existem {count} locais de estoque. Pulando seed.")
            return
        
        print("🏢 Criando local de estoque padrão...")
        
        local_padrao = LocalEstoque(
            codigo="ALM-01",
            nome="Almoxarifado Central",
            tipo="almoxarifado",
            ativo=1,
            padrao=1  # Define como padrão
        )
        
        db.add(local_padrao)
        db.commit()
        
        print("✅ Local de estoque padrão criado: ALM-01 - Almoxarifado Central")
        
    except Exception as e:
        print(f"❌ Erro ao criar local de estoque: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados inicializado!\n")
    
    print("=" * 60)
    print("POPULANDO DADOS INICIAIS (SEED)")
    print("=" * 60)
    
    seed_unidades_medida()
    print()
    seed_local_estoque_padrao()
    
    print("\n" + "=" * 60)
    print("🎉 SEED CONCLUÍDO COM SUCESSO!")
    print("=" * 60)


def seed_materiais_teste():
    """Cria materiais de teste com estoque inicial"""
    from app.models_modules import Material, EstoquePorLocal, LocalEstoque, UnidadeMedida
    from app.helpers import gerar_codigo_material
    
    db = SessionLocal()
    
    print("\n📦 Criando materiais de teste...")
    
    try:
        # Buscar unidades de medida
        un = db.query(UnidadeMedida).filter(UnidadeMedida.sigla == "UN").first()
        kg = db.query(UnidadeMedida).filter(UnidadeMedida.sigla == "KG").first()
        
        # Buscar local padrão
        local_padrao = db.query(LocalEstoque).first()
        
        # Verificar se já existem materiais
        count = db.query(Material).count()
        if count > 0:
            print(f"⚠️  Já existem {count} materiais. Pulando seed.")
            return
        
        # Material 1
        mat1 = Material(
            codigo=gerar_codigo_material(db),
            nome="Caneta Azul",
            descricao="Caneta esferográfica azul",
            unidade_medida="UN",
            unidade_medida_id=un.id if un else None,
            estoque_minimo=10.0,
            estoque_maximo=100.0,
            estoque_atual=0.0,
            preco_medio=1.50,
            preco_venda=2.50,
            ativo=1
        )
        db.add(mat1)
        db.flush()
        
        # Adicionar estoque inicial no local padrão
        if local_padrao:
            estoque1 = EstoquePorLocal(
                material_id=mat1.id,
                local_id=local_padrao.id,
                quantidade=50.0
            )
            db.add(estoque1)
            mat1.estoque_atual = 50.0
        
        print(f"  ✅ {mat1.codigo} - {mat1.nome} (Estoque: 50 UN)")
        
        # Material 2
        mat2 = Material(
            codigo=gerar_codigo_material(db),
            nome="Papel A4",
            descricao="Resma de papel A4 - 500 folhas",
            unidade_medida="UN",
            unidade_medida_id=un.id if un else None,
            estoque_minimo=5.0,
            estoque_maximo=50.0,
            estoque_atual=0.0,
            preco_medio=25.00,
            preco_venda=35.00,
            ativo=1
        )
        db.add(mat2)
        db.flush()
        
        if local_padrao:
            estoque2 = EstoquePorLocal(
                material_id=mat2.id,
                local_id=local_padrao.id,
                quantidade=20.0
            )
            db.add(estoque2)
            mat2.estoque_atual = 20.0
        
        print(f"  ✅ {mat2.codigo} - {mat2.nome} (Estoque: 20 UN)")
        
        # Material 3
        mat3 = Material(
            codigo=gerar_codigo_material(db),
            nome="Café em Pó",
            descricao="Café torrado e moído - pacote 500g",
            unidade_medida="KG",
            unidade_medida_id=kg.id if kg else None,
            estoque_minimo=2.0,
            estoque_maximo=20.0,
            estoque_atual=0.0,
            preco_medio=15.00,
            preco_venda=20.00,
            ativo=1
        )
        db.add(mat3)
        db.flush()
        
        if local_padrao:
            estoque3 = EstoquePorLocal(
                material_id=mat3.id,
                local_id=local_padrao.id,
                quantidade=10.5
            )
            db.add(estoque3)
            mat3.estoque_atual = 10.5
        
        print(f"  ✅ {mat3.codigo} - {mat3.nome} (Estoque: 10.5 KG)")
        
        db.commit()
        print("\n✅ 3 materiais criados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar materiais: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


# Executar seed de materiais se for main
if __name__ == "__main__":
    seed_materiais_teste()
