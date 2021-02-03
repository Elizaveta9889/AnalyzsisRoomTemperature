from datetime import datetime, date, time, timedelta


def str_to_date(date, format="%Y-%m-%d"):
    if type(date) == str:
        date = datetime.strptime(date, format)
    return date


def str_to_time(time, format="%H:%M:%S"):
    if type(time) == str:
        time = datetime.strptime(time, format).time()
    return time


def str_to_date_time(date, format="%Y-%m-%d %H:%M:%S"):
    if type(date) == str:
        date = datetime.strptime(date, format)
    return date


def get_datetime(date, time, dateformat="%Y-%m-%d", timeformat="%H:%M:%S"):
    return datetime.combine(str_to_date(date, dateformat), str_to_time(time, timeformat))


# the same for df columns
def df_str_to_date(df, column, format="%Y-%m-%d"):
    df[column] = df[column].apply(lambda x: str_to_date(x, format))


def df_str_to_time(df, column, format="%H:%M:%S"):
    df[column] = df[column].apply(lambda x: str_to_time(x, format))


def df_add_datetime(df, date="date", time="time", column_name="date_time", dateformat="%Y-%m-%d", timeformat="%H:%M:%S"):
    df[column_name] = df.apply(lambda x: get_datetime(x[date], x[time], dateformat, timeformat), axis=1)
