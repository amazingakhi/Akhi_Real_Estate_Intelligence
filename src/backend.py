from __future__ import annotations

import json
import hashlib
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
LEADS_FILE = DATA_DIR / "buyer_leads.json"
USERS_FILE = DATA_DIR / "registered_users.json"
DATABASE_FILE = DATA_DIR / "akhi_properties.db"
PASSWORD_SCHEME = "pbkdf2_sha256"

try:
    from security.sanitizer import sanitize_lead_payload, sanitize_text
except ImportError:
    try:
        from src.security.sanitizer import sanitize_lead_payload, sanitize_text
    except ImportError:
        def sanitize_lead_payload(lead): return lead
        def sanitize_text(text, max_length=500): return str(text or "")[:max_length]


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 240_000
    ).hex()
    return f"{PASSWORD_SCHEME}${salt}${digest}"


def verify_password(password: str, stored_password: str) -> bool:
    if stored_password.startswith(f"{PASSWORD_SCHEME}$"):
        _, salt, expected_digest = stored_password.split("$", 2)
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 240_000
        ).hex()
        return secrets.compare_digest(actual_digest, expected_digest)
    return secrets.compare_digest(password, stored_password)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    return connection


def _initialize_database() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                budget REAL NOT NULL,
                interest TEXT NOT NULL,
                message TEXT NOT NULL,
                property TEXT NOT NULL,
                service TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS shortlist (
                user_email TEXT NOT NULL,
                property_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (user_email, property_id)
            );
            """
        )

        if connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is None:
            legacy_users = load_json(USERS_FILE, {})
            for user in legacy_users.values():
                password = user.get("password", "")
                if password and not password.startswith(f"{PASSWORD_SCHEME}$"):
                    password = hash_password(password)
                if password:
                    connection.execute(
                        "INSERT OR IGNORE INTO users(email, name, phone, password, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (user.get("email", ""), user.get("name", ""), user.get("phone", ""), password, int(bool(user.get("is_admin")))),
                    )

        if connection.execute("SELECT 1 FROM leads LIMIT 1").fetchone() is None:
            legacy_leads = load_json(LEADS_FILE, [])
            for lead in legacy_leads:
                connection.execute(
                    """INSERT INTO leads(name, phone, email, budget, interest, message, property, service, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (lead.get("name", ""), lead.get("phone", ""), lead.get("email", "N/A"), float(lead.get("budget", 0) or 0), lead.get("interest", ""), lead.get("message", ""), lead.get("property", "N/A"), lead.get("service", "General Consultation"), lead.get("timestamp", "")),
                )


def load_json(file_path: Path, default: Any):
    if not file_path.exists():
        return default
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return default


def save_json(file_path: Path, payload: Any):
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


_initialize_database()


def load_leads() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT name, phone, email, budget, interest, message, property, service, timestamp FROM leads ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def save_lead(lead: dict[str, Any]):
    sanitized = sanitize_lead_payload(lead)
    with _connect() as connection:
        connection.execute(
            """INSERT INTO leads(name, phone, email, budget, interest, message, property, service, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                sanitized["name"],
                sanitized["phone"],
                sanitized["email"],
                float(sanitized["budget"]),
                sanitized["interest"],
                sanitized["message"],
                sanitized["property"],
                sanitized["service"],
                sanitized["timestamp"],
            ),
        )


def load_users() -> dict[str, dict[str, str]]:
    with _connect() as connection:
        rows = connection.execute("SELECT email, name, phone, password, is_admin FROM users").fetchall()
    return {
        row["email"]: {"name": row["name"], "email": row["email"], "phone": row["phone"], "password": row["password"], "is_admin": bool(row["is_admin"])}
        for row in rows
    }


def save_user(user: dict[str, str]):
    with _connect() as connection:
        connection.execute(
            """INSERT INTO users(email, name, phone, password, is_admin) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET name=excluded.name, phone=excluded.phone, password=excluded.password, is_admin=excluded.is_admin""",
            (user["email"], user["name"], user["phone"], user["password"], int(bool(user.get("is_admin")))),
        )


def get_total_leads() -> int:
    return len(load_leads())


def load_shortlist(user_email: str) -> list[dict[str, Any]]:
    if not user_email:
        return []
    with _connect() as connection:
        rows = connection.execute(
            "SELECT payload FROM shortlist WHERE user_email = ? ORDER BY rowid",
            (user_email,),
        ).fetchall()
    return [json.loads(row["payload"]) for row in rows]


def save_shortlist_item(user_email: str, property_id: str, property_data: dict[str, Any]) -> None:
    if not user_email:
        return
    with _connect() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO shortlist(user_email, property_id, payload) VALUES (?, ?, ?)",
            (
                user_email,
                property_id,
                json.dumps(
                    property_data,
                    default=lambda value: value.item() if hasattr(value, "item") else str(value),
                ),
            ),
        )


def remove_shortlist_item(user_email: str, property_id: str) -> None:
    if not user_email:
        return
    with _connect() as connection:
        connection.execute(
            "DELETE FROM shortlist WHERE user_email = ? AND property_id = ?",
            (user_email, property_id),
        )


def ensure_admin_account():
    """Migrate legacy passwords and optionally bootstrap an admin from secrets."""
    try:
        from config.settings import ADMIN_EMAIL, ADMIN_PASSWORD, CONTACT_NUMBER
    except ImportError:
        ADMIN_EMAIL = os.getenv("AKHI_ADMIN_EMAIL", "iamakv01@gmail.com")
        ADMIN_PASSWORD = os.getenv("AKHI_ADMIN_PASSWORD", "")
        CONTACT_NUMBER = os.getenv("CONTACT_NUMBER", "")

    admin_email = ADMIN_EMAIL
    admin_password = ADMIN_PASSWORD
    
    users = load_users()
    if admin_email not in users and admin_password:
        admin_user = {
            "name": "Akhi Admin",
            "email": admin_email,
            "phone": CONTACT_NUMBER or "0000000000",
            "password": hash_password(admin_password),
            "is_admin": True
        }
        users[admin_email] = admin_user
        save_user(admin_user)
    
    return users
