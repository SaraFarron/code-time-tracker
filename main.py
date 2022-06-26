import json
from dotenv import load_dotenv
from os import getenv
from requests import get, post
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, User, Total, ItemBase, Week

load_dotenv()

# db initialisation
engine = create_engine('sqlite://', echo=True, future=True)
Base.metadata.create_all(engine)

with open('response.json', 'r') as f:
    data = json.load(f)['data']

for k, v in data.items():
    # case k every type, then send args to function, that creates sqlalchemy objects (queries?)
    if k in ['editors', 'grand_total', 'languages', 'operating_systems', 'projects', 'range']:
        time = v['digital']
        name = v['name']
        percent = v['percent']
    elif k == 'machines':
        pass
    elif k == 'grand_total':
        pass
    else:
        continue

with Session(engine) as session:
    user = User(
        name='test_user',
        total=[Total(
            editors='',
            grand_total='',
            languages='',
            machines='',
            operating_systems='',
            projects='',
        )],
    )
    session.add_all([user, ])
    session.commit()


def create_object(category: str, name: str, time: str, percent: float):
    match category:
        case 'editors':
            pass
        case 'languages':
            pass
        case 'operating_systems':
            pass
        case 'projects':
            pass
    pass


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
