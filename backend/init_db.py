import mysql.connector
from database import engine, Base, SQLALCHEMY_DATABASE_URL
from sqlalchemy_utils import database_exists, create_database

def setup():
    print("Checking database connection...")
    
    # Extract connection details from URL for raw mysql-connector
    parts = SQLALCHEMY_DATABASE_URL.split("://")[1].split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    user = user_pass[0]
    password = user_pass[1]
    host = host_db[0]
    db_name = host_db[1]

    try:
        # 1. Create Database if it doesn't exist
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✅ Database '{db_name}' is ready.")
        conn.close()

        # 2. Create Tables using SQLAlchemy
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully.")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    setup()
