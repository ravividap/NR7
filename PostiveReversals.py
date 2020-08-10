from nsepy import get_history
import time
import numpy as np
import math, ta
from datetime import datetime, date, timedelta

def getData(stockname):
    endd = datetime.today() + timedelta(1)
    stard = datetime.today() - timedelta(130)
    data = get_history(symbol=stockname, start=date(stard.year, stard.month, stard.day), end=date(endd.year,endd.month,endd.day))

    revdata = data.sort_values(by=['Date'], inplace=False, ascending=True)
    rsi = ta.momentum.RSIIndicator(revdata['Close'],14).rsi()
    data['rsi'] = rsi.sort_values(ascending=True)
    data.drop(columns=['VWAP', 'Volume', 'Turnover', 'Trades', 'Deliverable Volume', '%Deliverble'])
    
    return data

def checkReversal(stockname):
    intermediateTroughs = []
    matchedRsi = 111
    data = getData(stockname)
    if(data.empty == True):
        return
    data['rsi_troughs'] = ((data.rsi < data.rsi.shift(-1)) & (data.rsi < data.rsi.shift(1)))
    revdata = data.sort_values(by=['Date'], inplace=False, ascending=False)
    print(revdata)
    for i in range(0, 7):
        if((revdata['rsi_troughs'][i] == True) and (revdata['rsi'][i] > revdata['rsi'][0])) :
            if(revdata['Close'][i] < revdata['Close'][0]):
                rsiStocks.append(revdata['Symbol'][i])
                matchedRsi = revdata['rsi'][i]
                # print(revdata['Symbol'][i])
                break
        elif(revdata['rsi_troughs'][i] == True):
            intermediateTroughs.append(revdata['rsi'][i])

    for irsi in intermediateTroughs:
        if(matchedRsi > irsi and len(rsiStocks) > 0):
            if stockname in rsiStocks: rsiStocks.remove(stockname)

    

symbolslist=["MCX","MARUTI","TATACONSUM","AMARAJABAT","COALINDIA","ESCORTS","JUBLFOOD","IGL","NESTLEIND","NIITTECH","M&M","PVR",
             "SUNPHARMA","HEROMOTOCO","RELIANCE","CIPLA","CUMMINSIND","Voltas","BPCL","ACC","ADANITRANS","AMBUJACEM",
             "ASIANPAINT","ASHOKLEY","AUROPHARMA","DMART","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BERGEPAINT",
             "BIOCON","BOSCHLTD","CADILAHC","COLPAL","CONCOR","DLF","DABUR","DIVISLAB","GICRE","GODREJCP",
             "HDFCAMC","HDFCLIFE","HAVELLS","HINDPETRO","HINDZINC","ICICIGI","ICICIPRULI","IBULHSGFIN","INDIGO",
             "L&TFH","LUPIN","MARICO","MOTHERSUMI","NHPC","NMDC","OFSS","PAGEIND","PETRONET",
             "PIDILITIND","PEL","PFC","PGHH","SBILIFE","SRTRANSFIN","SIEMENS", "TORNTPHARM", "NIACL","UBL","MCDOWELL-N"]

fnoList = ['APOLLOHOSP','AMBUJACEM','BANDHANBNK','BEL','FEDERALBNK','BPCL','CUMMINSIND','EICHERMOT','GAIL','GODREJCP','CADILAHC','GRASIM','HAVELLS','HCLTECH','HDFC','ADANIPORTS','HDFCBANK','HINDALCO',
'BRITANNIA','ADANIENT','INFY','JINDALSTEL','JUBLFOOD','LT','LUPIN','MGL','MINDTREE','ASHOKLEY','MRF','ASIANPAINT','NIITTECH','INDUSINDBK','LICHSGFIN','ONGC','AUROPHARMA','AXISBANK','PETRONET',  
'SHREECEM','BAJAJ-AUTO','BAJAJFINSV','BALKRISIND','SUNTV','BATAINDIA','BERGEPAINT','TATACONSUM','TATAPOWER','TCS','TITAN','UJJIVAN','BHARATFORG','EQUITAS','BHARTIARTL','ICICIBANK','JSWSTEEL',
'AMARAJABAT','ESCORTS','BHEL','BIOCON','NMDC','PEL','CANBK','ACC','CENTURYTEX','CHOLAFIN','CIPLA','COALINDIA','COLPAL','CONCOR','DABUR','HDFCLIFE','DIVISLAB','MARICO','DLF','DRREDDY','EXIDEIND',
'SUNPHARMA','TATASTEEL','GLENMARK','GMRINFRA','APOLLOTYRE','GODREJPROP','MANAPPURAM','UPL','HEROMOTOCO','HINDPETRO','HINDUNILVR','ICICIPRULI','IDFCFIRSTB','INDIGO','INFRATEL','IOC','ITC',
'M&MFIN','MARUTI','BOSCHLTD','MCDOWELL-N','MFSL','IBULHSGFIN','MOTHERSUMI','NAUKRI','NESTLEIND','NTPC','RELIANCE','M&M','SRTRANSFIN','TATACHEM','PAGEIND','PFC','PIDILITIND','PVR','TVSMOTOR','RAMCOCEM',  
'RBLBANK','BANKBARODA','SBILIFE','SBIN','TECHM','SRF','TORNTPOWER','UBL','ULTRACEMCO','VEDL','VOLTAS','WIPRO','ZEEL','L&TFH','NATIONALUM','POWERGRID','BAJFINANCE','RECLTD','SAIL','MUTHOOTFIN','KOTAKBANK', 
'IGL','SIEMENS','TATAMOTORS','TORNTPHARM']

rsiStocks = []

print('started  scan..')
index = 0
timeout = 1
while(index<len(fnoList)):
    checkReversal(fnoList[index])
    index=index+1
    timeout+=1
    if timeout==4:
        timeout=0
        time.sleep(5)

print(rsiStocks)