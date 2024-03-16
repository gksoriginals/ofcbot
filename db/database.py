import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import (
    database_exists, 
    create_database, 
    drop_database
)
from db.models import Base

dotenv.load_dotenv("ops/.env")

database_url = os.environ.get("DATABASE_URL")

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

def generate_database():
    """
    Create the database
    """
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database created")

def delete_database():
    """
    Delete the database
    """
    if database_exists(engine.url):
        drop_database(engine.url)
        print("Database deleted")

def create_tables():
    """
    Create the database schema and tables
    """
    Base.metadata.create_all(engine)
    print("Tables created")


def drop_tables():
    """
    Drop the database tables
    """

    Base.metadata.bind = engine
    Base.metadata.drop_all(engine)