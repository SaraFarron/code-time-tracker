import bcrypt
from sqlalchemy import (
    Column, ForeignKey, String, Integer, Float, Date,
)
from sqlalchemy.orm import declarative_base, relationship, declared_attr, validates

Base = declarative_base()


class Item:
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time = Column(Float)
    percent = Column(Float)

    @declared_attr
    def day_id(self):
        return Column(Integer, ForeignKey('day.id'))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    day = relationship('Day')
    api_key = Column(String)


class Day(Base):
    __tablename__ = 'day'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    editors = relationship('Editor')
    total = relationship('Total', back_populates='day', uselist=False)
    languages = relationship('Language')
    machines = relationship('Machine')
    operating_systems = relationship('OperatingSystem')
    projects = relationship('Project')
    user_id = Column(Integer, ForeignKey('user.id'))


class Total(Base):
    __tablename__ = 'total'

    id = Column(Integer, primary_key=True)
    time = Column(Float)
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship('Day', back_populates='total')


class Editor(Base, Item):
    __tablename__ = 'editor'


class Language(Base, Item):
    __tablename__ = 'language'


class Machine(Base, Item):
    __tablename__ = 'machine'


class OperatingSystem(Base, Item):
    __tablename__ = 'operating_system'


class Project(Base, Item):
    __tablename__ = 'project'
