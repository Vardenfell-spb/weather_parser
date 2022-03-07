# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime
import logging
from db_manager import DataBaseUpdater
from weather_parser import WeatherMaker
from image_maker import ImageMaker
import argparse

log = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log.addHandler(stream_handler)
log.setLevel(logging.INFO)
stream_handler.setLevel(logging.DEBUG)


class WeatherManager:
    def __init__(self):
        self.weather = None
        self.database = None
        self.today_date = date.today()
        self.data = None

    def run(self):
        self.weather = WeatherMaker()
        self.weather.run()
        self.database = DataBaseUpdater(data=self.weather.weather)
        self.data = self.database.load_base(self.today_date - timedelta(days=6), self.today_date)
        print('Прогноз за прошедшую неделю:')
        self.print_data()

        parser = argparse.ArgumentParser()
        #   Добавление прогнозов за диапазон дат в базу данных
        #   Получение прогнозов за диапазон дат из базы
        #   Создание открыток из полученных прогнозов
        #   Выведение полученных прогнозов на консоль
        parser.add_argument('command', type=str, help='update/load/image')
        parser.add_argument('-f', '--from_', type=str, help='Начальная дата (-f ДД.ММ.ГГГГ)')
        parser.add_argument('-t', '--to', type=str, help='Конечная дата (-t ДД.ММ.ГГГГ)')

        args = parser.parse_args()

        if args.from_:
            from_ = datetime.strptime(args.from_, '%d.%m.%Y').date()
        else:
            from_ = None
        if args.to:
            to = datetime.strptime(args.to, '%d.%m.%Y').date()
        else:
            to = None

        if args.command == 'update':
            self.update_base(from_=from_, to=to)
        elif args.command == 'load':
            self.print_from_base(from_=from_, to=to)
        elif args.command == 'image':
            self.make_image(from_=from_, to=to)
        else:
            print("Нет команд для выполнения")

    def print_data(self):
        for day in self.data:
            day_condition = self.data[day]['condition']
            day_temp_night = self.data[day]['temp_night']
            day_temp_day = self.data[day]['temp_day']
            print(f'{day.day}.{day.month}.{day.year}: {day_condition}, днём {day_temp_day}, ночью {day_temp_night}')

    def update_base(self, from_, to):
        self.database.update_base(from_=from_, to=to)

    def print_from_base(self, from_, to):
        self.data = self.database.load_base(from_=from_, to=to)
        print('Загруженые прогнозы из базы данных:')
        self.print_data()

    def make_image(self, from_, to):
        self.data = self.database.load_base(from_=from_, to=to)
        image_maker = ImageMaker(data=self.data, from_=from_, to=to)
        image_maker.run()
