from pyephem_sunpath.sunpath import sunpos
import numpy as np
import requests
from bs4 import BeautifulSoup
from modules import DateConvertor as dc
import pandas as pd
from datetime import datetime, date, time, timedelta


# get position of the sun by datetime, latitude, longitude (Tyumen State University by default)
def df_set_sun_position(df, date_time="date_time", lon=65.52226, lat=57.15897, tz=5):
    sun_position = df.apply(lambda x: sunpos(x[date_time], lat, lon, tz, dst=False), axis=1)
    df["altitude"] = sun_position.apply(lambda x: np.round(x[0], 2))
    df["azimuth"] = sun_position.apply(lambda x: np.round(x[1], 2))
    return df


def km_to_m(value):
    if type(value) == str:
        splitted_value = value.split()
        value = int(splitted_value[0])
        unit = splitted_value[1]
        if unit == "км":
            value *= 1000
    return value


# split cloudiness information into 4 values: overall_amount(COA), under_lower_amount(CULA), lower_bound(CLB), type(CT).
# 0/0 = Небо видно(облаков нет или почти нет)
# 10/10 = Мы не видим неба (много облаков или туман)
def cloudiness_split(cloudiness):
    if type(cloudiness) == str:
        if cloudiness == "нет сущ. обл.":
            return 0, 0, -1, ""
        if cloudiness == "ясно":
            return 0, 0, 0, ""
        splitted = cloudiness.split()
        if splitted[0] == "?/?":
            return 10, 10, splitted[3], "не видно из-за явлений"
        amount = splitted[0].split('/')
        if len(splitted) == 1:
            return int(amount[0]), int(amount[1]), 0, ""
        if len(splitted) >= 4:
            return int(amount[0]), int(amount[1]), splitted[1], splitted[3]
        else:
            if splitted[1].isdigit():
                return int(amount[0]), int(amount[1]), splitted[1], ""
            else:
                return int(amount[0]), int(amount[1]), np.nan, ""
        return cloudiness


# convert wind speed to int ('нст' and 'тихо')
def direction_to_int(direction):
    if direction == 'тихо' or direction == 'нст':
        return 0
    return int(direction)


# convert wind speed to int (' ' and intervals)
def speed_to_int(speed):
    if type(speed) == str:
        if speed == '':
            return 0
        splitted = speed.split('-')
        if len(splitted) == 1:
            return int(speed)
        else:
            return (int(splitted[0]) + int(splitted[1])) / 2
    return speed


# convert some columns of DataFrame to int
def columns_to_int(df, columns):
    df[columns] = df[columns].astype(int)


# convert all columns of weather info to appropriate type
def weather_columns_to_digit(df):
    # wind to int
    df['wind_dir'] = df['wind_dir'].apply(lambda x: direction_to_int(x))
    df['wind_speed'] = df['wind_speed'].apply(lambda x: speed_to_int(x))

    # visibility to int
    df['visibility'] = df['visibility'].apply(lambda x: km_to_m(x))

    # cloudiness to int
    cloudiness = df['cloudiness'].apply(lambda x: cloudiness_split(x))
    # cloudiness_overall_amount
    df["COA"] = cloudiness.apply(lambda x: x[0])
    # cloudiness_under_lower_amount
    df["CULA"] = cloudiness.apply(lambda x: x[1])
    # cloudiness_lower_bound
    df["CLB"] = cloudiness.apply(lambda x: x[2])
    # cloud_type
    df["CT"] = cloudiness.apply(lambda x: x[3])
    df = df.drop('cloudiness', axis=1)

    # all digit columns to int
    columns_to_int(df, ['T', 'Td', 'f', 'Te', 'QNH', 'Po'])

    return df


# convert data to request format
def date_to_object(date):
    date = dc.str_to_date(date)
    myobj = {'Date[0]': number_to_str(date.day), 'Date[1]': number_to_str(date.month), 'Date[2]': str(date.year),
             'CSV': 'on', 'ICAO': 'USTR'}
    return myobj


# convert a number to request format
def number_to_str(number):
    if number > 9:
        return str(number)
    else:
        return "0" + str(number)


# preprocessing weather info
def format_weather_info(weather):
    weather.dropna(inplace=True)
    weather = weather.rename(
        columns={'Время': 'time', 'Дата': 'date', 'Напр.ветра': 'wind_dir', 'Ск.ветра': 'wind_speed',
                 'Видим.': 'visibility', 'Явл.': 'atm_phenomena', 'Обл.': 'cloudiness', 'Т': 'T', 'Тd': 'Td',
                 'Тe': 'Te'})
    dc.df_add_datetime(weather, dateformat="%d.%m.%y", timeformat="%H%M")
    weather = weather.drop(['', 'date', 'time'], axis=1)
    weather = weather_columns_to_digit(weather)
    return weather


# get weather data from the meteocenter.net
def get_weather_info_date(date):
    # get html from the weather source
    url = 'http://meteocenter.net/forecast/all.php'
    html = requests.post(url, data=date_to_object(date)).text
    # parse html and get weather info
    soup = BeautifulSoup(html, 'html.parser')
    weather_info = soup.find('pre').text
    splitted_data = weather_info.split('\r\n')
    # get columns name
    header = splitted_data[1].split(';')
    # get data
    weather_info = splitted_data[2:]
    # to dataframe
    weather = pd.DataFrame([x.split(';') for x in weather_info], columns=header)
    weather = format_weather_info(weather)
    weather['date_time'] = weather['date_time'].apply(lambda x: x + timedelta(hours=5))
    # add sun position
    weather = df_set_sun_position(weather)
    weather = weather.set_index('date_time')
    return weather  # .resample("H").mean()


def get_weather_info_period(start, end):
    weather_info = pd.DataFrame()
    while start < end:
        df_weather = get_weather_info_date(start)
        print(start)
        weather_info = weather_info.append(df_weather)
        new_start = weather_info.index[-1]
        if new_start == start:
          break
        else:
          start = new_start
    return weather_info
