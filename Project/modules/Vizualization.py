import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


#HeatMap
def show_corr_heat_map (df, size=(7,5),name = ""):
  f,ax = plt.subplots(figsize=size)
  plt.title(name)
  sns.heatmap(df.corr().abs(), annot=True, fmt= '.1f',ax=ax)
  plt.show()

  
# Получение индекса колонки батарей и стен
# Необходим для следующего метода
def get_index_wall_and_bat(df):
  for item in df.columns:
    if 'bat_temp' in item:
      bat_temp = item
    if 'wall_temp' in item: 
      wall_temp = item 
  return bat_temp,wall_temp  
  
# Разбиение на сезоны
# Необходим для следующего метода
def divine_split(df):
  bat_temp,wall_temp = get_index_wall_and_bat(df)
  # cold - нет батарей, heating - батареи есть    
  cold_season = df[df[bat_temp]-df[wall_temp]<4]  
  heating_season = df[df[bat_temp]-df[wall_temp]>=4]
  #Надо будет нормально сделать (я не знаю как) 
  cold_season = cold_season["2020-04":"2020-10"]
  return cold_season.drop(bat_temp,axis = 1), heating_season

#Heatmap по сезонам
def show_df_per_season(df):
  summer_time, winter_time  = divine_split(df.dropna())
  show_corr_heat_map(summer_time,name = "batery Off")
  show_corr_heat_map(winter_time,name ="batery On")

#Старый граффик для анализа солнца
def show_df_per_season_plot(df,period1,period2):
  summer_time, winter_time  = divine_split(df.dropna())
  bat_temp,wall_temp = get_index_wall_and_bat(df)
  summer_time[period1][[wall_temp,"altitude","T","COA"]].plot(figsize = (20,8))
  winter_time[period2][[wall_temp,"altitude","T","COA"]].plot(figsize = (20,8))

