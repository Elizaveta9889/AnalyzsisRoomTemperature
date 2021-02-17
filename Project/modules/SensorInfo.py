import pandas as pd
from modules import DateConvertor as dc


def get_sensor_info_from_url(url, sep=" "):
    return pd.read_csv(url, sep=sep, header=None, names=["date", "time", "temp"])


# get all sensor data
def get_sensor_info(sensor_info, sep=" ", first_date_time=None):
    # data_count needs to check that all data was added
    data_count = 0
    # get dataframes from the URL
    for sensor in sensor_info.keys():
        sensor_info[sensor] = get_sensor_info_from_url(sensor_info[sensor], sep)
        data_count += sensor_info[sensor].shape[0]
        # rename temp column for every sensor
        sensor_info[sensor] = sensor_info[sensor].rename(columns={"temp": sensor + "_temp"})
    # create summary df
    sensor_info_val = sensor_info.values()
    # convert values of time column to time
    df = pd.concat(sensor_info_val, sort=True)
    dc.df_add_datetime(df)
    # delete loaded data
    if first_date_time is not None:
        df = df[df['date_time'] >= first_date_time]
    # set index and resample
    df = df.set_index('date_time')
    df = df.resample("1H").mean()
    return df.round(2), data_count
