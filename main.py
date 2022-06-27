import json
from itertools import groupby

from dotenv import load_dotenv
from os import getenv
from requests import get
from datetime import date, timedelta, datetime
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session

# from models import Base, User, Total, ItemBase, Week

load_dotenv()

# db initialisation
# engine = create_engine('sqlite://sqlite.db', echo=True, future=True)
# Base.metadata.create_all(engine)

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
            'editors': [],
            'grand_total': 0,
            'languages': [],
            'machines': [],
            'operating_systems': [],
            'projects': [],
        })
        shift = shift + timedelta(days=days)

    print('Time periods created')
    return weekly_data


def get_week_info(start: datetime, end: datetime, api_key) -> dict:
    params = {
        'api_key': api_key,
        'start': start.strftime(DATE_FORMAT),
        'end': end.strftime(DATE_FORMAT)
    }
    response = get('https://wakatime.com/api/v1/users/current/summaries', params=params)
    assert response.status_code == 200

    return response.json()


def update_tracking_info(start: datetime, end: datetime) -> None:
    weeks = create_week_periods(start, end)
    sql_weeks = []

    for week in weeks:
        week_data = get_week_info(week['start'], week['end'], getenv('API_KEY'))['data']
        for k, v in week_data.items():
            pass  # here sql_weeks.append(sql_alchemy_object)

# for k, v in data.items():
#     # case k every type, then send args to function, that creates sqlalchemy objects (queries?)
#     if k in ['editors', 'grand_total', 'languages', 'operating_systems', 'projects', 'range']:
#         time = v['digital']
#         name = v['name']
#         percent = v['percent']
#     elif k == 'machines':
#         pass
#     elif k == 'grand_total':
#         pass
#     else:
#         continue


def main():
    start = (date.today() - timedelta(days=120)).strftime('%Y-%m-%d')
    end = date.today().strftime('%Y-%m-%d')
    params = {
        'api_key': getenv('API_KEY'),
        'start': start.strip(),
        'end': end.strip()
    }

    response = get('https://wakatime.com/api/v1/users/current/summaries', params=params)
    with open('response.json', 'w') as file:
        file.write(response.text)


with open('response.json', 'r') as f:
    data = json.load(f)
    # update_tracking_info(data)
