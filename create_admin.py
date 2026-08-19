# it is the first admin bootstrap mechanism. we run it manually once to create the first admin
from getpass import getpass

from database import Base, engine, SessionLocal
from models import User
from security import hash_password


# Make sure the database tables exist
Base.metadata.create_all(bind=engine)


def create_first_admin():

    db = SessionLocal()

    try:
        # Ask for admin credentials through the terminal
        username = input("Enter admin username: ").strip()
        password = getpass("Enter admin password: ")

        # Basic validation
        if not username:
            print("Username cannot be empty.")
            return

        if not password:
            print("Password cannot be empty.")
            return

        # Check whether the username already exists
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            print("Username already exists.")
            return

        # Hash the password before storing it
        hashed_password = hash_password(password)

        # IMPORTANT:
        # The role is decided by this trusted server-side script.
        # The user does NOT send "role": "admin".
        admin = User(
            username=username,
            hashed_password=hashed_password,
            role="admin"
        )

        # Add admin to database
        db.add(admin)

        # Save the transaction
        db.commit()

        # Get the generated ID
        db.refresh(admin)

        print("\nFirst admin created successfully.")
        print(f"Username: {admin.username}")
        print(f"Role: {admin.role}")

    finally:
        # Always close the database session
        db.close()


if __name__ == "__main__":
    create_first_admin()