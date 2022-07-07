from pathlib import Path
from requests import get
from datetime import timedelta, datetime
from aiogram.utils.markdown import bold, pre
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models import (
    Editor, Language, Machine,
    OperatingSystem, Project, Day,
    User,
)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATE_FORMAT = '%Y-%m-%d'


# i18n
I18N_DOMAIN = 'time_tracker'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext

WELCOME = _('Hello! This bot can memorise your Wakatime stats and send you weekly reports! Click Start and bot '
            'will register you!')
DESCRIPTION = _('This bot stores your Wakatime stats in db and sends weekly reports, just like Wakatime itself '
                'but in Telegram! In order to work, bot needs your Wakatime API key, there is a button in /menu '
                'for that!')
MENU_ACTION = _('Please choose an action')
SEND_KEY = _('Send me your new Wakatime key')
ERROR = _('error')
API_KEY_SUCCESS = _('credentials updated successfully!')
API_KEY_FAILURE = _('Please send a valid api key, you can get it from your Wakatime profile page')


def get_info(period: str, api_key) -> dict:
    url = 'https://wakatime.com/api/v1/users/current/summaries'
    params = {
        'api_key': api_key,
        'range': period,
    }
    response = get(url, params=params)
    assert response.status_code == 200, response.text

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


def update_user_tracking_info(session: Session, period: str, user: User) -> None:
    tracker_data = get_info(period, user.api_key)['data']
    existing_dates = session.query(Day.date).all()
    existing_dates = [d[0] for d in existing_dates]

    for day in tracker_data:
        sql_objects = []
        date = datetime.strptime(day['range']['date'], DATE_FORMAT).date()
        if date in existing_dates:
            continue
        day_obj = Day(user_id=user.id, date=date)
        session.add(day_obj)
        session.commit()
        day_obj = session.query(Day).filter(Day.user_id == user.id & Day.date == date).first()

        for k, v in day.items():
            match k:
                case 'editors':
                    objects = add_base_objects(Editor, v, day_obj.id)
                    day_obj.editors.extend(objects)
                case 'grand_total':
                    day_obj.total = v['total_seconds']
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


def get_entry_stats(session: Session, klass, days) -> list:
    return session.query(
        klass.name, func.sum(klass.time)
    ).filter(klass.day_id.in_(days)).group_by(klass.name).all()


def get_user_stats(session: Session, start_date: datetime) -> dict:
    days = session.query(Day).filter(start_date <= Day.date).all()
    days = [day.id for day in days]
    stats = {
        _('projects'): get_entry_stats(session, Project, days),
        _('languages'): get_entry_stats(session, Language, days),
        _('machines'): get_entry_stats(session, Machine, days),
        _('operating systems'): get_entry_stats(session, OperatingSystem, days),
        'total': session.query(func.sum(Day.total)).filter(Day.id.in_(days)).all()
    }
    stats['total'] = stats['total'][0][0]

    return stats


def hours(seconds: float | int) -> str:
    h = int(seconds / 3600)
    m = round(seconds / 60 - h * 60)
    return _('%d hrs %d mins') % (h, m) if h >= 1 else _('%d mins') % m


def text_from_stats(name: str, stat: list, total_time: float | int) -> str:
    string = bold(f'{name}\n\n')
    stat_dict = {}
    stat = sorted(stat, key=lambda x: x[1], reverse=True)
    for record in stat:
        title, value = record[0], record[1]
        if title in stat_dict.keys():
            stat_dict[title] += value
        else:
            stat_dict[title] = value
    for k, v in stat_dict.items():
        percent = round(v / total_time * 100, 1)
        if percent >= 1:
            string += pre('%s %s %d' % (k, hours(v), percent) + '%')
    return string + '\n'


def stats_message(user_id: int, engine: MockConnection, time_period: str) -> str:
    with Session(engine) as session:
        user = session.query(User).filter(User.telegram_id == user_id).one()
        if not user.api_key:
            return 'You need to tell the bot your API key first'

        update_user_tracking_info(session, time_period, user)
        if '7' in time_period:
            start_date = datetime.today() - timedelta(days=7)
        else:
            start_date = datetime.strptime('2020-01-01T00:00:00Z', DATETIME_FORMAT)
        user_stats = get_user_stats(session, start_date)

    total = user_stats['total']
    message = bold(_("Time spent coding ") + hours(total)) + '\n\n'
    for k, stat in user_stats.items():
        if k != 'total':
            message += text_from_stats(k, stat, total)

    return message


def update_user_credentials(key: str, user_id: int, engine: MockConnection) -> str:
    url = 'https://wakatime.com/api/v1/users/current/all_time_since_today'
    response = get(url, params={'api_key': key})
    if response.status_code == 200 or response.status_code == 202:
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_id == user_id).one()
            user.api_key = key
            session.add(user)
            session.commit()
        return API_KEY_SUCCESS
    return API_KEY_FAILURE
