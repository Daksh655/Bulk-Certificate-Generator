import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.main import app
from app.database import Base, get_db
import app.database.database as database_module
import app.services.job_processor as job_processor_module
import app.services.certificate_generator as cert_gen_module

@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    """
    Ensure all tests use a temporary database and temporary file storage.
    No development data is touched.
    """
    # 1. Isolate file storage
    generated_dir = tmp_path / "generated"
    generated_dir.mkdir()
    monkeypatch.setattr(cert_gen_module, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(cert_gen_module, "PROJECT_ROOT", tmp_path)

    # 2. Isolate database
    db_path = tmp_path / "test.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    Base.metadata.create_all(bind=test_engine)

    # Patch global SessionLocal references so background tasks use the test DB
    monkeypatch.setattr(database_module, "engine", test_engine)
    monkeypatch.setattr(database_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(job_processor_module, "SessionLocal", TestingSessionLocal)

    # Patch FastAPI dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture
def client():
    # Use TestClient with raise_server_exceptions=False if needed, 
    # but by default it raises exceptions which is good for debugging.
    # Note: TestClient raises a deprecation warning about httpx which we ignore.
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db_session():
    """Yield a database session for test assertions/setup."""
    session = job_processor_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()
