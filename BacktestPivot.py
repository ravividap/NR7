# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 20:35:20 2020

@author: ravi
"""
import numpy as np
import pandas as pd
import copy
import matplotlib 

df = pd.read_csv('TCS1.csv')

df['date'] = pd.to_datetime(df['date'])
df= df.set_index('date')
#df =df.dropna()

mindf = (df.resample('10min', base=5)
               .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume':'mean'}))

mindf=mindf.dropna()

dailydf = (df.resample('1 D')
               .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume':'mean'}))

dailydf=dailydf.dropna()

dcopy= copy.deepcopy(dailydf)
pivots= (dailydf['high'].shift(1) + dailydf['low'].shift(1) + dailydf['close'].shift(1))/3
r1 = 2*pivots.shift(1) - dailydf['low'].shift(1)

dailydf['pivot'] = pivots
dailydf['r1'] = r1
dailydf = dailydf.dropna()                                            


dailydf['signal']=''
dailydf['ret']=0

dailydf1 = copy.deepcopy(dailydf)
capital = 100000
dailydf1['cap']=100000
returns = dailydf1['cap']

def getReturns(df,r1,capital):
    pos = 0
    entry = 0
    sl = 0
    risk = capital*0.01
    size = 0
    for index, row in df.iterrows():
        if(row['close']>r1 and pos==0 and entry==0): 
            entry=row['high']
            sl = row['low']
            size = round(risk/(entry-sl))
        if(row['high']>entry and pos==0 and entry!=0):
            pos = 1
        if(row['low']<sl and pos==1):
            return size*(sl-entry)
        if(index.time() == pd.to_datetime('15:05').time() and pos==1):
            return size*(row['close'] - entry)
    return 0  
    


for index, row in dailydf.iterrows():
    dailyr = 0
    dailyr = getReturns(mindf.loc[index.strftime('%Y-%m-%d')], row.r1, capital)
    capital = capital + dailyr
    dailydf1.at[index.strftime('%Y-%m-%d'), 'ret']= dailyr
    returns.at[index.strftime('%Y-%m-%d')] = capital

dailydf1['dailyr']=returns
dailydf1.plot(y='dailyr')
    
    