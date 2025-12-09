-- Migration: Add Compensacao and Historico Liquidacao tables
-- Date: 2024-12-09

-- Create compensacoes_contas table
CREATE TABLE IF NOT EXISTS compensacoes_contas (
    id SERIAL PRIMARY KEY,
    data_compensacao DATE NOT NULL,
    valor_compensado FLOAT NOT NULL,
    conta_pagar_id INTEGER NOT NULL REFERENCES contas_pagar(id),
    conta_receber_id INTEGER NOT NULL REFERENCES contas_receber(id),
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_compensacoes_data ON compensacoes_contas(data_compensacao);
CREATE INDEX IF NOT EXISTS idx_compensacoes_conta_pagar ON compensacoes_contas(conta_pagar_id);
CREATE INDEX IF NOT EXISTS idx_compensacoes_conta_receber ON compensacoes_contas(conta_receber_id);

-- Create historico_liquidacao table
CREATE TABLE IF NOT EXISTS historico_liquidacao (
    id SERIAL PRIMARY KEY,
    tipo_operacao VARCHAR(50) NOT NULL,
    data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total FLOAT NOT NULL,
    conta_origem_id INTEGER NOT NULL,
    tipo_conta_origem VARCHAR(20) NOT NULL,
    contas_geradas_ids JSONB,
    movimentacao_bancaria_id INTEGER REFERENCES movimentacoes_bancarias(id),
    observacao TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_historico_liquidacao_tipo ON historico_liquidacao(tipo_operacao);
CREATE INDEX IF NOT EXISTS idx_historico_liquidacao_data ON historico_liquidacao(data_operacao);
CREATE INDEX IF NOT EXISTS idx_historico_liquidacao_conta_origem ON historico_liquidacao(conta_origem_id);

-- Add comments
COMMENT ON TABLE compensacoes_contas IS 'Registro de compensações entre contas a pagar e receber';
COMMENT ON TABLE historico_liquidacao IS 'Histórico de operações de liquidação (compensação, baixa múltipla, etc)';
