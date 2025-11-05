import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    """Test chat endpoint with basic query"""
    response = client.post(
        "/api/v1/chat",
        json={"message": "recommend action movies"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "movies" in data
    assert "intent" in data

def test_search_movies():
    """Test movie search endpoint"""
    response = client.get("/api/v1/movies/search?q=toy")
    assert response.status_code == 200
    assert isinstance(response.json(), list)