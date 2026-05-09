import pytest
import pytest_asyncio  # Added for E2E support
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient  # Added for E2E support
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from db.models import DcUser, DcCompany, DcPurchase  # Added DcPurchase
from auth.oauth2 import get_current_user
from main import app

# 1. SETUP SQLITE WITH STATICPOOL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    async def override_get_current_user():
        # A. Seed Company
        company = session.query(DcCompany).filter(DcCompany.name == "NeoLocal").first()
        if not company:
            company = DcCompany(name="NeoLocal")
            session.add(company)
            session.commit()
            session.refresh(company)

        # B. Seed Admin User
        user = session.query(DcUser).filter(DcUser.username == "test_admin").first()
        if not user:
            user = DcUser(username="test_admin", email="admin@neo.local", password="hashed_password", company_id=company.id)
            session.add(user)
            session.commit()
            session.refresh(user)

        # C. SEED BUSINESS LOGIC (Usage/Purchase Resources)
        purchase = session.query(DcPurchase).filter(DcPurchase.company_id == company.id).first()
        if not purchase:
            purchase = DcPurchase(dcpower=20000, uspace=100, nport=100, sport=100, company_id=company.id, created_by=user.id)
            session.add(purchase)
            session.commit()

        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "company_id": user.company_id,
            "company_name": company.name,
        }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# --- NEW ADDITION FOR E2E TESTING ---


@pytest_asyncio.fixture
async def async_client():
    """
    Provides an asynchronous client for E2E tests.
    Ensures the in-memory database schema is created and
    the app's DB dependency is correctly overridden.
    """
    # Create schema in the shared in-memory engine
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the DB dependency for the app
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up overrides and drop tables after the E2E test finishes
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
