
import argparse
import getpass
import sys

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Agasaro administrator account")
    parser.add_argument("--username", required=True, help="Admin login username")
    args = parser.parse_args()

    username = args.username.strip()
    if len(username) < 3 or len(username) > 100:
        print("Username must contain between 3 and 100 characters.", file=sys.stderr)
        return 2

    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Repeat admin password: ")
    if len(password) < 8:
        print("Password must contain at least 8 characters.", file=sys.stderr)
        return 2
    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 2

    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first() is not None:
            print(f"Username '{username}' already exists. No changes made.", file=sys.stderr)
            return 1

        db.add(User(username=username, hashed_password=hash_password(password), role="admin", mfa_enabled=False))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print(f"Username '{username}' already exists. No changes made.", file=sys.stderr)
            return 1
    finally:
        db.close()

    print(f"Admin '{username}' created successfully.")
    print("Next step: log in and enable MFA through POST /auth/mfa/setup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
