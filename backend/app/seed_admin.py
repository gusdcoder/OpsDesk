#!/usr/bin/env python3
"""
Script to seed initial admin user.
Run: python -m app.seed_admin
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base, User, RoleEnum
from app.utils.auth_utils import hash_password
import os

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def seed_admin():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@opsdesk.local").first()
        if admin:
            print("Admin user already exists.")
            return
        
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@opsdesk.local')
        admin_password = os.getenv('ADMIN_PASSWORD', 'SecurePassword123')
        
        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"Admin user created: {admin_email}")
        print(f"Default password: {admin_password}")
        print("⚠️  IMPORTANT: Change this password in production!")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
