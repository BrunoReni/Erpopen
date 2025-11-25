"""Tests for authentication module"""
import pytest


def test_root_endpoint(client):
    """Test root endpoint returns service info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ERP Open Backend"
    assert "modules" in data


def test_login_success(client, admin_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, admin_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@test.com", "password": "password"}
    )
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test get current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["full_name"] == "Admin Test"
    assert data["is_active"] is True


def test_get_current_user_unauthorized(client):
    """Test get current user without authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test get current user with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
