from sqlalchemy import (
    Column, ForeignKey, String, Integer, Float,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Item(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time = Column(Float)
    percent = Column(Float)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    total = relationship('total', back_populates="user", uselist=False)
    week = relationship('week', back_populates="user", uselist=False)


class Week(Base):
    __tablename__ = 'week'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('user', back_populates='week', uselist=False)


class Total(Base):
    __tablename__ = 'total'

    id = Column(Integer, primary_key=True)
    time = Column(Float)


class Editor(Base, Item):
    __tablename__ = 'editor'


class Language(Base, Item):
    __tablename__ = 'language'


class Machine(Base, Item):
    __tablename__ = 'machine'


class OperatingSystem(Base, Item):
    __tablename__ = 'operating_system'
