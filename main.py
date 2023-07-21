import json

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Date, Float, Time
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

engine = create_engine("sqlite:///db.sqlite3")
session = sessionmaker(bind=engine)
meta = MetaData()

class Base(DeclarativeBase):
    pass


class Data(Base):
    id = Column(Integer, primary_key=True, index=True)
    
    decimal = Column(Float)
    digital = Column(Time)
    hours = Column(Integer)
    minutes = Column(Integer)
    name = Column(String)
    percent = Column(Float)
    seconds = Column(Integer)
    text = Column(String)
    total_seconds = Column(Float)


class Categories(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("Days", back_populates="categories")


class Editors(Base):
    __tablename__ = "editors"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("Days", back_populates="editors")


class Machines(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("Days", back_populates="machines")


class Languages(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("Days", back_populates="languages")


class OperatingSystems(Base):
    __tablename__ = "operating_systems"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("Days", back_populates="operating_systems")


class Projects(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    data = Column(Integer, ForeignKey("data.id"))
    days = relationship("User", back_populates="projects")


class Days(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    categories_id = Column(Integer, ForeignKey("categories.id"))
    categories = relationship("Categories", back_populates="days")
    projects = relationship("Projects", back_populates="days")
    operating_systems = relationship("OperatingSystems", back_populates="days")
    languages = relationship("Languages", back_populates="days")
    machines = relationship("Machines", back_populates="days")
    editors = relationship("Editors", back_populates="days")



def import_json_data(path: str):
    data = json.load(path)["days"]
    days = Table(
        "days", meta,
        Column("id", Integer, primary_key=True),
        Column("date", Date),
        Column("categories", ForeignKey),
    )
    for day in data:
        
