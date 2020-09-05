from nsepy import get_history
import time
import numpy as np
import math, ta
from datetime import datetime, date, timedelta

def getData(stockname):
    endd = datetime.today() + timedelta(1)
    stard = datetime.today() - timedelta(365)
    data = get_history(symbol=stockname, start=date(stard.year, stard.month, stard.day), end=date(endd.year,endd.month,endd.day))

    revdata = data.sort_values(by=['Date'], inplace=False, ascending=True)
    rsi = ta.momentum.RSIIndicator(revdata['Close'],14).rsi()
    ma200 = ta.trend.SMAIndicator(revdata['Close'], 200).sma_indicator()
    ma50 = ta.trend.SMAIndicator(revdata['Close'], 50).sma_indicator()
    ema20 = ta.trend.EMAIndicator(revdata['Close'], 20).ema_indicator()
    ema10 = ta.trend.EMAIndicator(revdata['Close'], 10).ema_indicator()
    ema5 = ta.trend.EMAIndicator(revdata['Close'], 5).ema_indicator()

    data['rsi'] = rsi.sort_values(ascending=True)
    data['ema5'] = ema5.sort_values(ascending=True)
    data['ema10'] = ema10.sort_values(ascending=True)
    data['ema20'] = ema20.sort_values(ascending=True)
    data['ma50'] = ma50.sort_values(ascending=True)
    data['ma200'] = ma200.sort_values(ascending=True)

    data.drop(columns=['VWAP', 'Volume', 'Turnover', 'Trades', 'Deliverable Volume', '%Deliverble'])
    
    return data

def scan(stockname):
    data = getData(stockname)
    if(data.empty == True):
        return
    checkReversal(data)
    checkVolContraction(data)

def checkReversal(data):
    intermediateTroughs = []
    matchedRsi = 111
    data['rsi_troughs'] = ((data.rsi < data.rsi.shift(-1)) & (data.rsi < data.rsi.shift(1)))
    revdata = data.sort_values(by=['Date'], inplace=False, ascending=False)
    print(revdata)
    if(revdata['rsi_troughs'][1] == False):
        return

    for i in range(2, 9):
        if((revdata['rsi_troughs'][i] == True) and (revdata['rsi'][i] > revdata['rsi'][1])) :
            if(revdata['Close'][i] < revdata['Close'][1]):
                rsiStocks.append(revdata['Symbol'][i])
                matchedRsi = revdata['rsi'][i]
                # print(revdata['Symbol'][i])
                break
        elif(revdata['rsi_troughs'][i] == True):
            intermediateTroughs.append(revdata['rsi'][i])

    for irsi in intermediateTroughs:
        if(matchedRsi > irsi and len(rsiStocks) > 0):
            if revdata['Symbol'][0] in rsiStocks: rsiStocks.remove(revdata['Symbol'][0])

def checkVolContraction(data):
    revdata = data.sort_values(by=['Date'], inplace=False, ascending=False)

    # Check NR7
    isNR7 = True
    min_diff=float(revdata['High'][0]) - float(revdata['Low'][0])
    for i in range(1, 7):
        diff = float(revdata['High'][i]) - float(revdata['Low'][i])
        if(min_diff>diff):
            isNR7=False
            break
        
    if(isNR7):
        nr7Stocks.append(revdata['Symbol'][0])
    
    #Check II
    isTodayInsideBar = float(revdata['High'][0]) < float(revdata['High'][1]) and float(revdata['Low'][0]) > float(revdata['Low'][1])
    isYesterdayInsideBar = float(revdata['High'][1]) < float(revdata['High'][2]) and float(revdata['Low'][1]) > float(revdata['Low'][2])
    if(isTodayInsideBar and isYesterdayInsideBar):
        iiStocks.append(revdata['Symbol'][0])

    #Check  IOI
    isTodayInsideBar = float(revdata['High'][0]) < float(revdata['High'][1]) and float(revdata['Low'][0]) > float(revdata['Low'][1])
    isDBYInsideBar = float(revdata['High'][2]) < float(revdata['High'][1]) and float(revdata['Low'][2]) > float(revdata['Low'][1])
    if(isTodayInsideBar and isDBYInsideBar):
        ioiStocks.append(revdata['Symbol'][0])

    #Check Double Doji
    isDoji = float(revdata['Close'][0]) - float(revdata['Open'][0]) < 0.25 * (float(revdata['High'][0]) > float(revdata['Low'][0]))
    isYesterdayDoji = float(revdata['Close'][1]) - float(revdata['Open'][1]) < 0.25 * (float(revdata['High'][1]) > float(revdata['Low'][1]))
    if(isDoji and isYesterdayDoji):
        dDojiStocks.append(revdata['Symbol'][0])

    #breaking200MA 
    cond = (float(revdata['Close'][0]) - float(revdata['Low'][0])) > 0.75 * (float(revdata['High'][0]) - float(revdata['Low'][0]))
    if(float(revdata['Close'][0]) > float(revdata['ma200'][0]) and float(revdata['Close'][1]) < float(revdata['ma200'][1]) and cond):
        breaking200MA.append(revdata['Symbol'][0])
    
    #breaking 50 ma
    cond = (float(revdata['Close'][0]) - float(revdata['Low'][0])) > 0.75 * (float(revdata['High'][0]) - float(revdata['Low'][0]))
    if(float(revdata['Close'][0]) > float(revdata['ma50'][0]) and float(revdata['Close'][1]) < float(revdata['ma50'][1]) and cond):
        breaking200MA.append(revdata['Symbol'][0])

    # pinbar at 200ma
    cond = (float(revdata['Close'][0]) - float(revdata['Low'][0])) > 0.75 * (float(revdata['High'][0]) - float(revdata['Low'][0]))
    cond2 = (float(revdata['Close'][0]) - float(revdata['Open'][0])) <= 0.1 * (float(revdata['High'][0]) - float(revdata['Low'][0]))
    if(float(revdata['High'][0]) > float(revdata['ma200'][0]) and float(revdata['Low'][0]) < float(revdata['ma200'][0]) and cond and cond2):
        pinbarAt200MA.append(revdata['Symbol'][0])

    # top ib
    if((float(revdata['ema5'][0]) > float(revdata['ema10'][0]) > float(revdata['ema20'][0])) and isTodayInsideBar):
        topIB.append(revdata['Symbol'][0])

fnoList = ['APOLLOHOSP','AMBUJACEM','BANDHANBNK','BEL','FEDERALBNK','BPCL','CUMMINSIND','EICHERMOT','GAIL','GODREJCP','CADILAHC','GRASIM','HAVELLS','HCLTECH','HDFC','ADANIPORTS','HDFCBANK','HINDALCO',
'BRITANNIA','ADANIENT','INFY','JINDALSTEL','JUBLFOOD','LT','LUPIN','MGL','MINDTREE','ASHOKLEY','MRF','ASIANPAINT','NIITTECH','INDUSINDBK','LICHSGFIN','ONGC','AUROPHARMA','AXISBANK','PETRONET',  
'SHREECEM','BAJAJ-AUTO','BAJAJFINSV','BALKRISIND','SUNTV','BATAINDIA','BERGEPAINT','TATACONSUM','TATAPOWER','TCS','TITAN','UJJIVAN','BHARATFORG','EQUITAS','BHARTIARTL','ICICIBANK','JSWSTEEL',
'AMARAJABAT','ESCORTS','BHEL','BIOCON','NMDC','PEL','CANBK','ACC','CENTURYTEX','CHOLAFIN','CIPLA','COALINDIA','COLPAL','CONCOR','DABUR','HDFCLIFE','DIVISLAB','MARICO','DLF','DRREDDY','EXIDEIND',
'SUNPHARMA','TATASTEEL','GLENMARK','GMRINFRA','APOLLOTYRE','GODREJPROP','MANAPPURAM','UPL','HEROMOTOCO','HINDPETRO','HINDUNILVR','ICICIPRULI','IDFCFIRSTB','INDIGO','INFRATEL','IOC','ITC',
'M&MFIN','MARUTI','BOSCHLTD','MCDOWELL-N','MFSL','IBULHSGFIN','MOTHERSUMI','NAUKRI','NESTLEIND','NTPC','RELIANCE','M&M','SRTRANSFIN','TATACHEM','PAGEIND','PFC','PIDILITIND','PVR','TVSMOTOR','RAMCOCEM',  
'RBLBANK','BANKBARODA','SBILIFE','SBIN','TECHM','SRF','TORNTPOWER','UBL','ULTRACEMCO','VEDL','VOLTAS','WIPRO','ZEEL','L&TFH','NATIONALUM','POWERGRID','BAJFINANCE','RECLTD','SAIL','MUTHOOTFIN','KOTAKBANK', 
'IGL','SIEMENS','TATAMOTORS','TORNTPHARM']

rsiStocks = []
nr7Stocks = []
ioiStocks = []
iiStocks = []
dDojiStocks = []
newYearlyHighClose = []
breaking200MA = []
breaking50MA = []
pinbarAt200MA = []
topIB = []


print('started  scan..')
index = 0
timeout = 1
while(index<len(fnoList)):
    scan(fnoList[index])
    index=index+1
    timeout+=1
    if timeout==4:
        timeout=0
        time.sleep(5)

print('NR7: ')
print(nr7Stocks)
print('II: ')
print(nr7Stocks)
print('IOI: ')
print(ioiStocks)
print('Double Doji: ')
print(dDojiStocks)
print('Breaking 200 MA: ')
print(breaking200MA)
print('Breaking 50 MA: ')
print(breaking50MA)
print('Pinbar at 200 MA: ')
print(pinbarAt200MA)
print('Top IB: ')
print(topIB)
