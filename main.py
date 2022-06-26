from dotenv import load_dotenv
from os import getenv
from base64 import b64encode
from requests import get, post
from datetime import date, timedelta
from sqlalchemy import create_engine

from models import Base

load_dotenv()

# db initialisation
engine = create_engine('sqlite://', echo=True, future=True)
Base.metadata.create_all(engine)

start = (date.today() - timedelta(days=120)).strftime('%Y-%m-%d')
end = date.today().strftime('%Y-%m-%d')

params = {
    'api_key': getenv('API_KEY'),
    'start': start.strip(),
    'end': end.strip()
}

response = get('https://wakatime.com/api/v1/users/current/summaries', params=params)
with open('response.json', 'w') as f:
    f.write(response.text)
