"""Tests for helper functions"""
import pytest
from app.helpers import (
    gerar_codigo_fornecedor,
    gerar_codigo_cliente,
    gerar_codigo_material,
    validar_cpf,
    validar_cnpj
)


def test_gerar_codigo_fornecedor(db_session):
    """Test generating fornecedor code"""
    codigo = gerar_codigo_fornecedor(db_session)
    assert codigo.startswith("FOR-")
    assert len(codigo) == 8  # FOR-XXXX


def test_gerar_codigo_cliente(db_session):
    """Test generating cliente code"""
    codigo = gerar_codigo_cliente(db_session)
    assert codigo.startswith("CLI-")
    assert len(codigo) == 8  # CLI-XXXX


def test_gerar_codigo_material(db_session):
    """Test generating material code"""
    codigo = gerar_codigo_material(db_session)
    assert codigo.startswith("MAT-")
    assert len(codigo) == 8  # MAT-XXXX


def test_validar_cpf_valido():
    """Test validating valid CPF"""
    assert validar_cpf("12345678909") is True


def test_validar_cpf_invalido():
    """Test validating invalid CPF"""
    assert validar_cpf("12345678900") is False
    assert validar_cpf("00000000000") is False
    assert validar_cpf("11111111111") is False


def test_validar_cpf_formato_invalido():
    """Test validating CPF with invalid format"""
    assert validar_cpf("123") is False
    assert validar_cpf("abc") is False


def test_validar_cnpj_valido():
    """Test validating valid CNPJ"""
    assert validar_cnpj("11222333000181") is True


def test_validar_cnpj_invalido():
    """Test validating invalid CNPJ"""
    assert validar_cnpj("11222333000180") is False
    assert validar_cnpj("00000000000000") is False


def test_validar_cnpj_formato_invalido():
    """Test validating CNPJ with invalid format"""
    assert validar_cnpj("123") is False
    assert validar_cnpj("abc") is False
