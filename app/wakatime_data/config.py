from pydantic import BaseModel
import requests


class WakatimeAPI(BaseModel):
    token: str

    _dump_url = "https://wakatime.com/api/v1/users/current/data_dumps"

    def get_dump(self):
        response = requests.get(
            self._dump_url,
            headers={"Authorization": "Basic " + self.token}
        )
        if response.status_code != 200:
            return response.text
        data = response.json()["data"]
        return data["download_url"]

    def create_dump(self):
        response = requests.post(
            self._dump_url,
            headers={"Authorization": "Basic " + self.token}
        )
        if response.status_code != 201:
            return response.text
        return None
