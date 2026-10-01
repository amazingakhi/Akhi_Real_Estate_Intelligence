from src import backend
from src.backend import hash_password, verify_password


def test_password_hashes_are_verifiable_without_storing_plaintext():
    password = "A-strong-production-password-123!"
    stored = hash_password(password)

    assert stored.startswith("pbkdf2_sha256$")
    assert stored != password
    assert verify_password(password, stored)
    assert not verify_password("wrong-password", stored)


def test_sqlite_storage_persists_users_and_leads(tmp_path, monkeypatch):
    monkeypatch.setattr(backend, "DATABASE_FILE", tmp_path / "test.db")
    backend._initialize_database()

    user = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210",
        "password": hash_password("StrongPass123!"),
        "is_admin": False,
    }
    backend.save_user(user)
    backend.save_lead(
        {
            "name": "Test User",
            "phone": "9876543210",
            "email": "test@example.com",
            "budget": 1.5,
            "interest": "Investment",
            "message": "Looking for a 3 BHK",
            "property": "Sector 79",
            "service": "Investor Edge",
            "timestamp": "2026-09-02T00:00:00",
        }
    )

    assert "test@example.com" in backend.load_users()
    assert backend.load_leads()[0]["service"] == "Investor Edge"