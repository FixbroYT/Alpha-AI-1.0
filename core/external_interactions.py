import logging

import requests
from bs4 import BeautifulSoup

from config import API_KEY_WEATHER

logger = logging.getLogger(__name__)


class Weather:
    def __init__(self):
        self.api_key = API_KEY_WEATHER

    def get_weather(self, city_name):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={self.api_key}&units=metric"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            filtered_data = {
                "main": data["weather"][0]["main"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }

            return filtered_data
        else:
            logger.error(f"Request failed, response status code: {response.status_code}")
            return None

def get_news(count = 5):
    url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "lxml")

    news_list = soup.find_all("article", class_="IBr9hb")[:count]

    clear_news = ""

    for news in news_list:
        clear_news += news.find("a", class_="gPFEn").get_text() + ". "

    return clear_news