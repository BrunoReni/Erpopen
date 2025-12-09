"""add_compensacao_and_historico_liquidacao

Revision ID: 683c4ca3ec71
Revises: 
Create Date: 2025-12-09 00:25:27.968901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '683c4ca3ec71'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create compensacoes_contas table
    op.create_table(
        'compensacoes_contas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_compensacao', sa.Date(), nullable=False),
        sa.Column('valor_compensado', sa.Float(), nullable=False),
        sa.Column('conta_pagar_id', sa.Integer(), nullable=False),
        sa.Column('conta_receber_id', sa.Integer(), nullable=False),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['conta_pagar_id'], ['contas_pagar.id'], ),
        sa.ForeignKeyConstraint(['conta_receber_id'], ['contas_receber.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_compensacoes_data', 'compensacoes_contas', ['data_compensacao'])
    op.create_index('idx_compensacoes_conta_pagar', 'compensacoes_contas', ['conta_pagar_id'])
    op.create_index('idx_compensacoes_conta_receber', 'compensacoes_contas', ['conta_receber_id'])

    # Create historico_liquidacao table
    op.create_table(
        'historico_liquidacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_operacao', sa.String(length=50), nullable=False),
        sa.Column('data_operacao', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('valor_total', sa.Float(), nullable=False),
        sa.Column('conta_origem_id', sa.Integer(), nullable=False),
        sa.Column('tipo_conta_origem', sa.String(length=20), nullable=False),
        sa.Column('contas_geradas_ids', sa.Text(), nullable=True),  # JSON stored as text in SQLite
        sa.Column('movimentacao_bancaria_id', sa.Integer(), nullable=True),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['movimentacao_bancaria_id'], ['movimentacoes_bancarias.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_historico_liquidacao_tipo', 'historico_liquidacao', ['tipo_operacao'])
    op.create_index('idx_historico_liquidacao_data', 'historico_liquidacao', ['data_operacao'])
    op.create_index('idx_historico_liquidacao_conta_origem', 'historico_liquidacao', ['conta_origem_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_historico_liquidacao_conta_origem', table_name='historico_liquidacao')
    op.drop_index('idx_historico_liquidacao_data', table_name='historico_liquidacao')
    op.drop_index('idx_historico_liquidacao_tipo', table_name='historico_liquidacao')
    op.drop_table('historico_liquidacao')
    
    op.drop_index('idx_compensacoes_conta_receber', table_name='compensacoes_contas')
    op.drop_index('idx_compensacoes_conta_pagar', table_name='compensacoes_contas')
    op.drop_index('idx_compensacoes_data', table_name='compensacoes_contas')
    op.drop_table('compensacoes_contas')
