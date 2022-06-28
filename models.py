from sqlalchemy import (
    Column, ForeignKey, String, Integer, Float, DateTime
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Item(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time = Column(Float)
    percent = Column(Float)
    week_id = Column(Integer, ForeignKey('week.id'))


class Stats(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    editors = relationship('Editor')
    total = relationship('Total', back_populates='week', uselist=False)
    languages = relationship('Language')
    machines = relationship('Machine')
    operating_systems = relationship('OperatingSystem')
    projects = relationship('Project')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    # total = relationship('total', back_populates="user", uselist=False)
    week = relationship('Week')


class Week(Base, Stats):
    __tablename__ = 'week'

    start = Column(DateTime)
    end = Column(DateTime)


class TotalStats(Base, Stats):
    __tablename__ = 'total_stats'


class Total(Base):
    __tablename__ = 'total'

    id = Column(Integer, primary_key=True)
    time = Column(Float)
    week_id = Column(Integer, ForeignKey('week.id'))
    week = relationship('Week', back_populates='week')


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
