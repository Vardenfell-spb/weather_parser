# -*- coding: utf-8 -*-
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import logging

log = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log.addHandler(stream_handler)
log.setLevel(logging.INFO)
stream_handler.setLevel(logging.DEBUG)


class WeatherMaker:
    def __init__(self):
        self.weather = {}
        self.data = None

    def run(self):
        self.get_data()
        self.parsing_weather()

    def get_data(self):
        self.data = requests.get('https://yandex.ru/pogoda/saint-petersburg')

    def parsing_weather(self):
        if self.data.status_code == 200:

            html_doc = BeautifulSoup(self.data.text, features='html.parser')
            list_of_dates = html_doc.find_all('time', {'class': 'time forecast-briefly__date'})
            list_of_temp_day = html_doc.find_all('div',
                                                 {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'})
            list_of_temp_night = html_doc.find_all('div',
                                                   {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'
                                                    })
            list_of_condition = html_doc.find_all('div',
                                                  {'class': 'forecast-briefly__condition'})
            for dates, temp_night, temp_day, condition in zip(list_of_dates, list_of_temp_night,
                                                              list_of_temp_day, list_of_condition):
                dict_date = datetime.fromisoformat(dates['datetime'][0:10])
                dict_temp_night = temp_night.find('span', {'class': 'temp__value'}).text
                dict_temp_day = temp_day.find('span', {'class': 'temp__value'}).text
                dict_condition = condition.text
                self.weather[dict_date.date()] = {'temp_night': dict_temp_night,
                                                  'temp_day': dict_temp_day,
                                                  'condition': dict_condition
                                                  }


if __name__ == '__main__':
    test_parsing = WeatherMaker()
    test_parsing.run()
    for day in test_parsing.weather:
        print(day, test_parsing.weather[day]['temp_night'],
              test_parsing.weather[day]['temp_day'],
              test_parsing.weather[day]['condition'])
