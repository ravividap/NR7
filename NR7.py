
import re
import json
import time
import requests
from datetime import datetime
from firebase import firebase

print("NR7 Stocks")

firebase = firebase.FirebaseApplication('https://newtest-a66c7.firebaseio.com/', None)
data =  { 'Name': 'John Doe',
          'RollNo': 3,
          'Percentage': 70.02
          }
result = firebase.post('/python/Students/',data)
print(result)

def check(stockname):
    res = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=NSE:'+stockname+'&apikey=BX73FYAMN2WVYMWO')
    days = res.json()['Time Series (Daily)']
    #today = datetime.today().strftime('%Y-%m-%d')
    #del days[today]
    rever_days=sorted(days.keys(), reverse=True)
    isInsideBar = float(days[rever_days[0]]['2. high']) < float(days[rever_days[1]]['2. high']) and float(days[rever_days[0]]['3. low']) > float(days[rever_days[1]]['3. low'])
    isNR7 = True
    min_diff=float(days[rever_days[0]]['2. high']) - float(days[rever_days[0]]['3. low'])
    for i in range(1, 8):
        day = days[rever_days[i-1]]
        diff = float(day['2. high']) - float(day['3. low'])
        if(min_diff>diff):
            isNR7=False
      
    if(isInsideBar and isNR7):
        print(stockname)
    return;
  

symbolslist=["ACC","ADANITRANS","AMBUJACEM","ASHOKLEY","AUROPHARMA","DMART","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BERGEPAINT","BIOCON","BOSCHLTD","CADILAHC","COLPAL","CONCOR","DLF","DABUR","DIVISLAB","GICRE","GODREJCP","HDFCAMC","HDFCLIFE","HAVELLS","HINDPETRO","HINDZINC","ICICIGI","ICICIPRULI","IBULHSGFIN","INDIGO","L&TFH","LUPIN","MARICO","MOTHERSUMI","NHPC","NMDC","OFSS","PAGEIND","PETRONET","PIDILITIND","PEL","PFC","PGHH","PNB","SBILIFE","SRTRANSFIN","SIEMENS","NIACL","UBL","MCDOWELL-N","IDEA"]
index=0
timeout = 1
while(index<len(symbolslist)):
    check(symbolslist[index])
    index=index+1
    timeout+=1
    if timeout==5:
        timeout=0
        time.sleep(65)
