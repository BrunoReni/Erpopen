"""Tests for dev_tools module"""
import pytest
from app.feature_flags import FeatureStatus


def test_list_dev_features_without_auth(client):
    """Test that /dev/features requires authentication"""
    response = client.get("/dev/features")
    assert response.status_code == 401


def test_list_dev_features_with_auth(client, auth_headers):
    """Test listing all features with authentication"""
    response = client.get("/dev/features", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "features" in data
    assert isinstance(data["features"], list)
    assert data["total"] > 0


def test_list_dev_features_filter_by_module(client, auth_headers):
    """Test filtering features by module"""
    response = client.get("/dev/features?module=financeiro", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(f["module"] == "financeiro" for f in data["features"])


def test_list_dev_features_filter_by_status(client, auth_headers):
    """Test filtering features by status"""
    response = client.get("/dev/features?status=backend_only", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(f["status"] == "backend_only" for f in data["features"])


def test_get_feature_gaps(client, auth_headers):
    """Test getting feature gaps"""
    response = client.get("/dev/features/gaps", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "critical_gaps" in data
    assert "total_gaps" in data
    assert "backend_only" in data
    assert "all_incomplete" in data
    assert isinstance(data["backend_only"], list)


def test_get_feature_statistics(client, auth_headers):
    """Test getting feature statistics"""
    response = client.get("/dev/features/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "complete" in data
    assert "backend_only" in data
    assert "incomplete" in data
    assert "average_completeness" in data
    assert "completion_rate" in data
    assert "modules" in data


def test_get_feature_by_id(client, auth_headers):
    """Test getting a specific feature"""
    response = client.get("/dev/features/fin_contas_pagar", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "fin_contas_pagar"
    assert data["module"] == "financeiro"
    assert "has_backend" in data
    assert "has_frontend" in data


def test_get_feature_by_id_not_found(client, auth_headers):
    """Test getting a non-existent feature"""
    response = client.get("/dev/features/nonexistent_feature", headers=auth_headers)
    assert response.status_code == 404


def test_get_module_features(client, auth_headers):
    """Test getting features by module"""
    response = client.get("/dev/features/modules/vendas", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "vendas"
    assert "total" in data
    assert "complete" in data
    assert "completion_rate" in data
    assert all(f["module"] == "vendas" for f in data["features"])


def test_health_check(client):
    """Test health check endpoint (no auth required)"""
    response = client.get("/dev/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "total_features" in data
    assert "complete_features" in data
    assert "critical_gaps" in data


def test_backend_only_feature_exists(client, auth_headers):
    """Test that Issue #16 feature (compensacao) is marked as backend_only"""
    response = client.get("/dev/features/fin_compensacao_liquidacao", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "backend_only"
    assert data["has_backend"] is True
    assert data["has_frontend"] is False
    assert data["issue_number"] == 16
