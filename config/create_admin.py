"""
Writes the credential file consumed by the SimpleAuthManager.
Airflow 3 removes the legacy `airflow users` CLI in favor of the new auth manager.
We create/update the password store here to keep a deterministic admin login.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    username = os.environ.get("_AIRFLOW_WWW_USER_USERNAME")
    password = os.environ.get("_AIRFLOW_WWW_USER_PASSWORD")
    password_file = os.environ.get("AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE")

    if not username or not password:
        raise RuntimeError("Admin username/password env vars must be set")
    if not password_file:
        raise RuntimeError("AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE must be configured")

    path = Path(password_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON in password file: {path}") from exc
    else:
        data = {}

    data[username] = password
    path.write_text(json.dumps(data))
    print(f"Stored password for '{username}' in {path}")


if __name__ == "__main__":
    main()
