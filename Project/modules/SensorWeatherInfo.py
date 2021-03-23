from modules import SensorInfo as sinf
from modules import WeatherInfo as winf
import numpy as np


def merged_dataframes(sensor_info, weather_info):
    merged = sensor_info.merge(weather_info, left_on="date_time", right_on="date_time", how="left")
    merged.drop_duplicates(keep="first", inplace=True)
    return merged


# if we don't have dataset
def get_dataset(sensor_dict):
    # get all sensor info
    new_sensor_info = sinf.get_sensor_info(sensor_dict)
    # get period of data (need to get weather info)
    new_weather_info = winf.get_weather_info_period(new_sensor_info.index[0], new_sensor_info.tail(1).index[0])
    return merged_dataframes(new_sensor_info, new_weather_info)


# if we already have dataset, we need to update it to now
def update_dataset(sensor_dict, origin_df):
    if origin_df.index.dtype != np.dtype('datetime64[ns]'):
        print('The Dataframe does not have datatime indexes, returned origin Dataframe')
        return origin_df
    # get new sensor info since last uploaded time
    new_sensor_info = sinf.get_sensor_info(sensor_dict, origin_df.tail(1).index[0])
    # get period of data (need to get weather info)
    new_weather_info = winf.get_weather_info_period(new_sensor_info.index[0], new_sensor_info.tail(1).index[0])
    return origin_df.append(merged_dataframes(new_sensor_info, new_weather_info))
