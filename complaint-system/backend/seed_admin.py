import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base

import models

from auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if not db.query(models.User).filter(models.User.email == "admin@demo.com").first():
        admin = models.User(
            name="Admin User",

            email="admin@demo.com",

            hashed_password=hash_password("admin123"),

            role="admin",

        )

        db.add(admin)

        db.commit()

        print("✅ Admin created: admin@demo.com / admin123")

    else:
        print("ℹ️  Admin already exists")

finally:
    db.close()
