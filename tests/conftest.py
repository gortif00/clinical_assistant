# tests/conftest.py
"""
Configuración de pytest para tests
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crea un event loop para tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    """Cliente de test para FastAPI"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_clinical_case() -> dict:
    """Caso clínico de prueba"""
    return {
        "text": "Patient reports feeling anxious and having trouble sleeping for the past two weeks. "
                "Also experiencing loss of appetite and difficulty concentrating at work."
    }


@pytest.fixture
def mock_jwt_token() -> str:
    """Token JWT de prueba"""
    from backend.app.middleware.auth import AuthManager
    return AuthManager.create_access_token(
        data={"sub": "test_user", "tier": "authenticated"}
    )
