import json
from itertools import groupby
from dotenv import load_dotenv
from os import getenv
from requests import get
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from models import (
    Total, Editor, Language, Machine,
    OperatingSystem, Project, Base, Day,
    User
)

load_dotenv()

# db initialisation
engine = create_engine('sqlite:///sqlite.db', echo=True, future=True)
Base.metadata.create_all(engine)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATE_FORMAT = '%Y-%m-%d'


def create_week_periods(start: datetime, end: datetime) -> list:
    week_day = start.weekday()
    if week_day != 0:
        start = start - timedelta(days=week_day)  # Every week starts with monday

    weekly_data = []
    shift = start
    for v, g in groupby(
            ((start + timedelta(days=i)).weekday() for i in range(1, (end - start).days + 1))
    ):
        days = sum(7 for _ in g)
        weekly_data.append({
            'start': shift,
            'end': shift + timedelta(days=days),
        })
        shift = shift + timedelta(days=days)

    print('Time periods created')
    return weekly_data


def get_info(start: datetime, end: datetime, api_key) -> dict:
    params = {
        'api_key': api_key,
        'start': start.strftime(DATE_FORMAT),
        'end': end.strftime(DATE_FORMAT)
    }
    response = get('https://wakatime.com/api/v1/users/current/summaries', params=params)
    assert response.status_code == 200

    print('successfully retrieved weekly data')
    return response.json()


def add_base_objects(klass, object_dict: dict, day_id: int) -> list:
    base_objects = []
    for o in object_dict:
        obj = klass(
            name=o['name'],
            time=o['total_seconds'],
            percent=o['percent'],
            day_id=day_id,
        )
        base_objects.append(obj)

    return base_objects


def update_tracking_info(session: Session, start: datetime, end: datetime, user: User) -> None:
    # weeks = create_week_periods(start, end)
    tracker_data = get_info(start, end, getenv('API_KEY'))['data']

    for day in tracker_data:
        sql_objects = []
        date = datetime.strptime(day['range']['date'], DATE_FORMAT)
        day_obj = Day(user_id=user.id, date=date)
        session.add(day_obj)
        session.commit()
        day_obj = session.query(Day).filter(Day.user_id == user.id).first()  # Might need to order by date

        for k, v in day.items():
            match k:
                case 'editors':
                    objects = add_base_objects(Editor, v, day_obj.id)
                    day_obj.editors.extend(objects)
                case 'grand_total':
                    ttl_obj = Total(
                        time=v['total_seconds'],
                        day=day_obj,
                        day_id=day_obj.id,
                    )
                    objects = [ttl_obj, ]
                    day_obj.total = ttl_obj
                case 'languages':
                    objects = add_base_objects(Language, v, day_obj.id)
                    day_obj.languages.extend(objects)
                case 'machines':
                    objects = add_base_objects(Machine, v, day_obj.id)
                    day_obj.machines.extend(objects)
                case 'operating_systems':
                    objects = add_base_objects(OperatingSystem, v, day_obj.id)
                    day_obj.operating_systems.extend(objects)
                case 'projects':
                    objects = add_base_objects(Project, v, day_obj.id)
                    day_obj.projects.extend(objects)
                case _: continue
            sql_objects += objects
            session.add_all(sql_objects)
            session.commit()

    print('tracking info updated')


def main():
    start = (datetime.today() - timedelta(days=120))
    end = datetime.today()
    with Session(engine) as session:
        user = User(name='testuser')
        session.add(user)
        session.commit()
        user = session.query(User).get(1)
        update_tracking_info(session, start, end, user)


if __name__ == '__main__':
    main()
