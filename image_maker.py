# -*- coding: utf-8 -*-
import os
from datetime import timedelta, date
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageColor
from param import GRADIENTS, WEATHER_IMAGES
import logging

log = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log.addHandler(stream_handler)
log.setLevel(logging.INFO)
stream_handler.setLevel(logging.DEBUG)


class ImageMaker:
    def __init__(self, data, from_=None, to=None):
        self.form_ = from_
        self.to = to
        self.data = data
        self.image = None
        self.image_path = 'img/probe.jpg'

    def run(self):
        if not self.to:
            if not self.form_:
                self.form_ = date.today()
                self.to = date.today()
            else:
                self.to = self.form_
        w_date = self.form_
        while w_date <= self.to:
            try:
                self.make_image(w_date)
            except Exception as error:
                weather_date = f'{w_date.day}.{w_date.month}.{w_date.year}'
                log.exception(f'Ошибка генерации изображения ({weather_date}): {error}')
                print(f'Нет данных в базе для {weather_date}')
            w_date += timedelta(days=1)


    def make_image(self, w_date):
        self.draw_background(w_date)
        self.draw_text(w_date)
        self.insert_weather_pic(w_date)

    def show_result(self):
        self.image = cv2.imread(self.image_path)
        cv2.imshow("Weather", self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def insert_weather_pic(self, w_date):
        pic_offset = (100, 78)
        image_name = WEATHER_IMAGES[self.data[w_date]['condition']]
        weather_pic = Image.open(f'img/weather_img/{image_name}.jpg')
        self.image = Image.open(self.image_path)
        self.image.paste(weather_pic, pic_offset)
        if not os.path.exists('images'):
            os.mkdir('images')
        self.image.save(self.image_path)

    def draw_background(self, w_date):
        self.image = cv2.imread(self.image_path)
        weather_condition = self.data[w_date]['condition']
        log.debug(f'Градиент фона: {weather_condition} {GRADIENTS[weather_condition]}')
        color_r = GRADIENTS[weather_condition]['R']
        color_g = GRADIENTS[weather_condition]['G']
        color_b = GRADIENTS[weather_condition]['B']
        for x in range(256):
            r = color_r[0] + (color_r[1] - color_r[0]) / 255 * x
            b = color_b[0] + (color_b[1] - color_b[0]) / 255 * x
            g = color_g[0] + (color_g[1] - color_g[0]) / 255 * x
            cv2.line(self.image, (0, x), (512, x), (b, g, r), 1)
        weather_date = f'{w_date.day}.{w_date.month}.{w_date.year}'
        self.image_path = f'images/{weather_date}.jpg'
        cv2.imwrite(self.image_path, self.image)

    def draw_text(self, w_date):
        self.image = Image.open(self.image_path)
        draw = ImageDraw.Draw(self.image)
        font = ImageFont.truetype('arial.ttf', size=24)
        weather_date = f'{w_date.day}.{w_date.month}.{w_date.year}'
        temp_night = self.data[w_date]['temp_night']
        temp_day = self.data[w_date]['temp_day']
        condition = self.data[w_date]['condition']
        temp_all = f'Днем: {temp_day}  Ночью: {temp_night}'
        log.debug(f'Текст на картинке: дата:{weather_date} погода:{condition} t день:{temp_night} t ночь:{temp_day}')

        draw.text((210, 78), weather_date, font=font, fill=ImageColor.colormap['black'])
        draw.text((210, 116), temp_all, font=font, fill=ImageColor.colormap['black'])
        draw.text((210, 154), condition, font=font, fill=ImageColor.colormap['black'])
        self.image.save(self.image_path)

        self.image = cv2.imread(self.image_path)


if __name__ == '__main__':
    today_date = date.today()
    test_data = {today_date: {'condition': 'Ясно',
                              'temp_night': '+10',
                              'temp_day': '+20'
                              }
                 }
    test_image = ImageMaker(test_data, from_=today_date, to=None)
    test_image.draw_background(today_date)
    test_image.draw_text(today_date)
    test_image.insert_weather_pic(today_date)
    test_image.show_result()
