from dotenv import load_dotenv
from os import getenv
from requests import get, post


load_dotenv()
API_KEY = getenv('API_KEY')

response = post('https://wakatime.com/oauth/token', headers={'Authorization': 'Bearer ' + API_KEY})
print(response.text)
