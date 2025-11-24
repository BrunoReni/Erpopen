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
