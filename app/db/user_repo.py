import hashlib
from typing import Optional
from app.db.database import get_connection


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username: str, password: str) -> Optional[dict]:
    """
    Check username + password.
    Returns user dict {id, username, full_name, role} if valid, else None.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, full_name, role, password_hash "
        "FROM users WHERE username = ?",
        (username.strip(),)
    ).fetchone()
    conn.close()

    if not row:
        return None

    if row["password_hash"] != _hash_password(password):
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"] or "",
        "role": row["role"] or "admin",
    }


def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    """
    Change a user's password after verifying the old one.
    Returns True on success, False if old password is wrong.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if not row or row["password_hash"] != _hash_password(old_password):
        conn.close()
        return False

    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (_hash_password(new_password), user_id)
    )
    conn.commit()
    conn.close()
    return True


def get_all_users() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, full_name, role, created_at FROM users ORDER BY username"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username: str, password: str,
                full_name: str = "", role: str = "admin") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role) "
        "VALUES (?, ?, ?, ?)",
        (username.strip(), _hash_password(password), full_name, role)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id