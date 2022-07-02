from itertools import groupby
from requests import get
from datetime import timedelta, datetime

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models import (
    Total, Editor, Language, Machine,
    OperatingSystem, Project, Day,
    User,
)

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
    url = 'https://wakatime.com/api/v1/users/current/summaries'
    params = {
        'api_key': api_key,
        'start': start.strftime(DATE_FORMAT),
        'end': end.strftime(DATE_FORMAT)
    }
    response = get(url, params=params)
    assert response.status_code == 200

    print('successfully retrieved data')
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


def update_user_tracking_info(session: Session, start: datetime, end: datetime, user: User) -> None:
    tracker_data = get_info(start, end, user.api_key)['data']

    for day in tracker_data:
        sql_objects = []
        date = datetime.strptime(day['range']['date'], DATE_FORMAT)
        day_obj = Day(user_id=user.id, date=date)
        session.add(day_obj)
        session.commit()
        day_obj = session.query(Day).filter(Day.user_id == user.id).order_by(-Day.id).first()

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
                case _:
                    continue
            sql_objects += objects
            session.add_all(sql_objects)
            session.commit()

    print('tracking info updated')


def get_user_key_or_404(user_id: int, engine: MockConnection):
    with Session(engine) as session:
        user = session.query(User).filter(User.telegram_id == user_id)
    if not user.api_key:
        raise 'No api key'
    return user.api_key


def all_data(user_id: int, engine: MockConnection) -> str:
    with Session(engine) as session:
        user = session.query(User).filter(User.telegram_id == user_id)
        start_date = datetime.strptime('2010-01-01T00:00:00Z', DATETIME_FORMAT)
        end_date = datetime.now()
        update_user_tracking_info(session, start_date, end_date, user)
        total_time = session.query(
            func.sum(Day.total.time)).filter(start_date <= Day.date & Day.user_id == user.id
                                             )
    #     todo make sql requests for projects, languages, etc.
    return 'TODO all data ' + str(user_id)


def add_entries_text(day: dict, text: str, total: dict):
    entries = ['projects', 'languages', 'editors', 'operating_systems', 'machines']
    for entry in entries:
        total_entry = total[entry]
        total_time = 0
        for e in day[entry]:
            entry_name = e['name']
            entry_seconds = e['total_seconds']
            total_time += entry_seconds

            text += f"""
            * {entry} distribution:
              * {entry_name} - {e['text']}, {e['percent']}%
            """

            total['grand_total_sum'] += day['grand_total']['total_seconds']
            if entry_name in total_entry.keys():
                total_entry[entry_name]['total_seconds'] += entry_seconds
            else:
                total_entry[entry_name] = {
                    'total_seconds': entry_seconds,
                }
        total_entry['percent'] = round(total_entry['total_seconds'] / total_time)


def last_week_data(user_id: int, engine: MockConnection) -> str:
    key = get_user_key_or_404(user_id, engine)
    start = datetime.today() - timedelta(days=7)
    end = datetime.today()
    summaries = get_info(start, end, key)['date']
    totals = {
        'grand_total_sum': 0,
        'projects': {},
        'languages': {},
        'operation_systems': {},
        'machines': {},
    }

    summaries_text = '<h2> Your week summaries </h2>\n'
    for day in summaries:
        summaries_text += f"""
        ###{day['range']['date']}
        * total time spent <em>{day['grand_total']['text']}</em>
        * projects distribution:
        """
        add_entries_text(day, summaries_text, totals)

    summaries_text += f"""
    ## Total time spent
    {totals['grand_total_sum']}
    * projects distribution:
      * {totals['projects']}
    * languages distribution:
      * {totals['languages']}
    * OS distribution:
      * {totals['oss']}
    * machines distribution
      * {totals['machines']}
    """

    return 'TODO last week stats ' + str(user_id)


def update_user_credentials(key: str, user_id: int, engine: MockConnection) -> str:
    url = 'https://wakatime.com/api/v1/users/current/all_time_since_today'
    response = get(url, params={'api_key': key})
    if response.status_code == 200:
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_id == user_id)
            user.api_key = key
            session.commit()
        return 'credentials updated successfully!'
    print(response.text)
    return 'Please send a valid api key, you can get it from your Wakatime profile page'
