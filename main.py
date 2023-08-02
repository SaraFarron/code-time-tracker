import json
from datetime import timedelta, datetime
from sqlalchemy import (
    create_engine,
    MetaData,
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Float,
    Interval,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from plotly import graph_objects as go

engine = create_engine("sqlite:///db.sqlite3")
Session = sessionmaker(bind=engine)
session = Session()
meta = MetaData()


class Base(DeclarativeBase):
    pass


class Data:
    decimal = Column(Float)
    digital = Column(Interval)
    hours = Column(Integer)
    minutes = Column(Integer)
    percent = Column(Float)
    seconds = Column(Integer)
    text = Column(String)
    total_seconds = Column(Float)


class Categories(Base, Data):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Editors(Base, Data):
    __tablename__ = "editors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Machines(Base, Data):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    machine_name_id = Column(String)
    name = Column(String)


class Languages(Base, Data):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class OperatingSystems(Base, Data):
    __tablename__ = "operating_systems"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Projects(Base, Data):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Days(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    categories_id = Column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    projects_id = Column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    operating_systems_id = Column(
        Integer, ForeignKey("operating_systems.id", ondelete="SET NULL"), nullable=True
    )
    languages_id = Column(
        Integer, ForeignKey("languages.id", ondelete="SET NULL"), nullable=True
    )
    machines_id = Column(
        Integer, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    editors_id = Column(
        Integer, ForeignKey("editors.id", ondelete="SET NULL"), nullable=True
    )


def create_generic_table(day_data: list, day: dict, name: str, table: Base):
    table_data = day.get(name, {})
    if table_data:
        for item in table_data:
            time = datetime.strptime(item["digital"], "%H:%M:%S")
            item["digital"] = timedelta(
                hours=time.hour, minutes=time.minute, seconds=time.second
            )
            row = table(**item)
            day_data[f"{name}_id"] = row.id
            session.add(row)


def import_json_data(path: str):
    data_types = {
        "categories": Categories,
        "editors": Editors,
        "machines": Machines,
        "languages": Languages,
        "operating_systems": OperatingSystems,
    }
    with open(path, "r", encoding="utf-8") as file:
        json_data = json.load(file)["days"]
    for day in json_data:
        day_data = {}
        for data_type, table in data_types.items():
            create_generic_table(day_data, day, data_type, table)
        projects = day.get("projects", {})
        if projects:
            for project in projects:
                project_time = project["grand_total"]["digital"]
                time = datetime.strptime(project_time, "%H:%M").time()
                project["grand_total"]["digital"] = timedelta(
                    hours=time.hour, minutes=time.minute, seconds=time.second
                )
                project_row = Projects(
                    name=project["name"],
                    **project["grand_total"],
                )
                day_data["projects_id"] = project_row.id
                session.add(project_row)
        day_row = Days(date=datetime.strptime(day["date"], "%Y-%m-%d").date(), **day_data)
        session.add(day_row)
    session.commit()


def create_plots():
    fig = go.Figure()
    data = session.query(Days).all()
    


Base.metadata.create_all(engine)
