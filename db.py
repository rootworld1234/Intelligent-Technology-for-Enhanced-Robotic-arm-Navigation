from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{BASE_DIR}/lab.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Chemical(Base):
    __tablename__ = "chemicals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    iupac = Column(String)
    formula = Column(String)
    barcode = Column(String, unique=True)

class Scientist(Base):
    __tablename__ = "scientists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)

class Robot(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="idle")
    position = Column(String, default="home")

class Storage(Base):
    __tablename__ = "storage"
    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer, default=1)
    occupied = Column(Integer, default=0)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"))
    storage_id = Column(Integer, ForeignKey("storage.id"))
    chemical_id = Column(Integer, ForeignKey("chemicals.id"))
    scientist_id = Column(Integer, ForeignKey("scientists.id"))
    status = Column(String, default="pending")
    start_time = Column(String)
    end_time = Column(String)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("lab.db created successfully")
