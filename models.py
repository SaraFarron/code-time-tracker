from sqlalchemy import (
    Column, ForeignKey, String, Integer,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ItemBase(Base):
    id = Column(Integer, primary_key=True)
    editors = relationship('editors', back_populates=Base.__tablename__)
    grand_total = relationship('grand_total', back_populates=Base.__tablename__)
    languages = relationship('languages', back_populates=Base.__tablename__)
    machines = relationship('machines', back_populates=Base.__tablename__)
    operating_systems = relationship('operating_systems', back_populates=Base.__tablename__)
    projects = relationship('projects', back_populates=Base.__tablename__)


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


class Total(Base, ItemBase):
    __tablename__ = 'total'
