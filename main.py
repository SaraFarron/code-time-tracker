import json

from sqlalchemy import (
    create_engine,
    MetaData,
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Float,
    Time,
)

engine = create_engine("sqlite:///db.sqlite3")
session = sessionmaker(bind=engine)
meta = MetaData()


class Base(DeclarativeBase):
    pass


class Data(Base):
    decimal = Column(Float)
    digital = Column(Time)
    hours = Column(Integer)
    minutes = Column(Integer)
    percent = Column(Float)
    seconds = Column(Integer)
    text = Column(String)
    total_seconds = Column(Float)


class Categories(Data):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Editors(Data):
    __tablename__ = "editors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Machines(Data):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Languages(Data):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class OperatingSystems(Data):
    __tablename__ = "operating_systems"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Projects(Data):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Days(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    categories_id = Column(
        Integer, ForeignKey("categories.id", ondelete="SET_NULL"), nullable=True
    )
    projects_id = Column(
        Integer, ForeignKey("projects.id", ondelete="SET_NULL"), nullable=True
    )
    operating_systems_id = Column(
        Integer, ForeignKey("operating_systems.id", ondelete="SET_NULL"), nullable=True
    )
    languages_id = Column(
        Integer, ForeignKey("languages.id", ondelete="SET_NULL"), nullable=True
    )
    machines_id = Column(
        Integer, ForeignKey("machines.id", ondelete="SET_NULL"), nullable=True
    )
    editors_id = Column(
        Integer, ForeignKey("editors.id", ondelete="SET_NULL"), nullable=True
    )


def create_generic_table(data: list, day: dict, name: str, table: Base):
    table_data = day.get(name, {})
    if table_data:
        for item in table_data:
            data.append(table(**item))


def import_json_data(path: str):
    data_types = {
        "categories": Categories,
        "editors": Editors,
        "machines": Machines,
        "languages": Languages,
        "operating_systems": OperatingSystems,
    }
    json_data = json.load(path)["days"]
    data = []
    for day in json_data:
        for data_type, table in data_types.items():
            create_generic_table(data, day, data_type, table)
        projects = day.get("projects", {})
        if projects:
            for project in projects:
                data.append(
                    Projects(
                        name=project["name"],
                        **project["grand_total"],
                    )
                )
    meta.create_all(engine)
