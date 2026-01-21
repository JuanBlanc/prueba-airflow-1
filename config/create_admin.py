"""
Create or update the admin user for the FAB auth manager using env credentials.

Airflow 3 removed the legacy ``airflow users`` CLI, so we manage the user directly
in the metadata database. The user information (username, password, etc.) comes
from the environment variables defined in ``.env``.
"""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable must be set")
    return value


def main() -> None:
    username = os.environ.get("AIRFLOW_ADMIN_USERNAME") or os.environ.get("_AIRFLOW_WWW_USER_USERNAME")
    password = os.environ.get("AIRFLOW_ADMIN_PASSWORD") or os.environ.get("_AIRFLOW_WWW_USER_PASSWORD")
    first_name = os.environ.get("AIRFLOW_ADMIN_FIRSTNAME") or "Admin"
    last_name = os.environ.get("AIRFLOW_ADMIN_LASTNAME") or "User"
    email = os.environ.get("AIRFLOW_ADMIN_EMAIL") or "admin@example.com"
    if not username or not password:
        raise RuntimeError("Admin username/password env vars must be set")

    database_uri = _required_env("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN")
    hashed_password = generate_password_hash(password)

    engine = create_engine(database_uri)

    with engine.begin() as conn:
        # Ensure the Admin role exists.
        role_id = conn.execute(
            text("SELECT id FROM ab_role WHERE name = :name"),
            {"name": "Admin"},
        ).scalar()
        if role_id is None:
            role_id = conn.execute(
                text("INSERT INTO ab_role (name) VALUES (:name) RETURNING id"),
                {"name": "Admin"},
            ).scalar_one()

        user_row = conn.execute(
            text("SELECT id FROM ab_user WHERE username = :username"),
            {"username": username},
        ).fetchone()

        params: dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": hashed_password,
            "email": email,
        }

        if user_row:
            user_id = user_row[0]
            conn.execute(
                text(
                    """
                    UPDATE ab_user
                    SET first_name = :first_name,
                        last_name = :last_name,
                        email = :email,
                        password = :password,
                        active = true
                    WHERE id = :user_id
                    """
                ),
                {**params, "user_id": user_id},
            )
        else:
            user_id = conn.execute(
                text(
                    """
                    INSERT INTO ab_user (first_name, last_name, username, password, email, active)
                    VALUES (:first_name, :last_name, :username, :password, :email, true)
                    RETURNING id
                    """
                ),
                params,
            ).scalar_one()

        conn.execute(
            text("DELETE FROM ab_user_role WHERE user_id = :user_id"),
            {"user_id": user_id},
        )
        assoc_id = conn.execute(
            text("SELECT to_regclass('ab_user_role_id_seq')")
        ).scalar()
        if assoc_id:
            new_id = conn.execute(
                text("SELECT nextval('ab_user_role_id_seq')")
            ).scalar_one()
        else:
            new_id = conn.execute(
                text("SELECT COALESCE(MAX(id), 0) + 1 FROM ab_user_role")
            ).scalar_one()
        conn.execute(
            text(
                """
                INSERT INTO ab_user_role (id, user_id, role_id)
                VALUES (:id, :user_id, :role_id)
                """
            ),
            {"id": new_id, "user_id": user_id, "role_id": role_id},
        )

    print(f"Stored admin user '{username}' in metadata database.")


if __name__ == "__main__":
    main()
