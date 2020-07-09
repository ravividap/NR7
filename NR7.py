import re
import json
from datetime import datetime, date, timedelta
from firebase import firebase
from nsepy import get_history
import tweepy
import config
import schedule
import time
import divergence
import numpy as np

print('Started..')

insideBarList = []
nr7List = []
prevInsideBars = []
fakeyList = []
deliveryPercentUp = []

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
key = config.access_key
secret = config.access_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweet_char_limit = 280
tweetId = ''
firebasePath = '/NR7/'
firebaseSnapName = 'insidebar'


firebase = firebase.FirebaseApplication('https://newtest-a66c7.firebaseio.com/', None)

def create_rsi_price_array(rsi,closelist):
    price_rsi = []
 
    prices_close_list = []
 
    prices_close_list = list(closelist.values.flatten())
    
    rsi = rsi.tolist()
    
    #print rsi
    #print prices_close_list
 
    for price,rsi in zip(rsi,prices_close_list):
        price_rsi.append([rsi,price])
    
    #print price_rsi
    return price_rsi

def bullish_divergence(price_rsi,percent_baseline,low):
                get_rsi = []
                get_price = []
                low_vals = []
                trough_vals = []
                #get array of just price
                for rsi in price_rsi:
                                rsi = rsi[1]
                                get_rsi.append(rsi)
 
                #get array of just rsi
                for price in price_rsi:
                                price = price[0]
                                get_price.append(price)
 
 
                for value in get_rsi:
                                if value < low:
                                                low_vals.append(value)
                #filter actual troughs from potentials 
                for item in low_vals:
                    try:
                        if get_rsi[get_rsi.index(item)-1] > item and get_rsi[get_rsi.index(item)+1] > item and get_rsi.index(item) != 0:
 
                            trough_vals.append(item)
                    except:
                        pass
                #check to see if potential pattern. A potential pattern means it is current and RSI is gaining strength (bullish)
                try:
                    if trough_vals[-1] == get_rsi[-2] and trough_vals[-1] > trough_vals[-2]:
 
                        delta = get_rsi[(get_rsi.index(trough_vals[-2])):(get_rsi.index(trough_vals[-1]))]
                        payload = []
                        for item in delta:
                                        if item >  trough_vals[-1] and item > trough_vals[-2]:
                                            difference = item - trough_vals[-2]
                                            percent_dif = difference/trough_vals[-2]
 
                                            if percent_dif >= percent_baseline:
       
                                                trough_vals = trough_vals[-2:]
                                                trough_one_index = (get_rsi.index(trough_vals[-1]))
                                                trough_two_index = (get_rsi.index(trough_vals[-2]))
                                                price_signal = get_price[trough_one_index]
                                                price_setup = get_price[trough_two_index]
                                                #confirm divergence by comparing price action
                                                if price_signal < price_setup:
                                                    payload.append(trough_vals)
                                                    payload.append(len(delta))
                                                    payload.append([price_setup,price_signal])
                                                    break
                    if len(payload) != 0:
                        return payload
                except:
                    pass
                return 

def postToFirebase(path, snapshot, data):
    result = firebase.put(path,snapshot,data)


def getFromFirebase(path, snapshot):
    result = firebase.get(path, snapshot)
    return result

def check(stockname):
    isFakey = False
    isPinBar = False
    print('checking stock '+stockname)
    endd = datetime.today() + timedelta(1)
    stard = datetime.today() - timedelta(15)
    try:
        print('getting history')
        data = get_history(symbol=stockname, start=date(stard.year, stard.month, stard.day), end=date(endd.year,endd.month,endd.day))

        data['3 day Del%'] = (data['Deliverable Volume'].rolling(3).sum()/data['Volume'].rolling(3).sum())*100
        data['5 day Del%'] = (data['Deliverable Volume'].rolling(5).sum()/data['Volume'].rolling(5).sum())*100
        data['10 day Del%'] = (data['Deliverable Volume'].rolling(10).sum()/data['Volume'].rolling(10).sum())*100
        data['15 day Del%'] = (data['Deliverable Volume'].rolling(15).sum()/data['Volume'].rolling(15).sum())*100

        data['Delivery up'] = np.where((data['3 day Del%']>data['5 day Del%']) & (data['5 day Del%'] > data['10 day Del%']) & (data['10 day Del%'] >data['15 day Del%']) , 1, 0)

        print('getting history finish')
        revdata = data.sort_values(by=['Date'], inplace=False, ascending=False)
        print(revdata)
        isInsideBar = float(revdata['High'][0]) < float(revdata['High'][1]) and float(revdata['Low'][0]) > float(revdata['Low'][1])
        
        if(revdata['Delivery up'][0] == 1)
            deliveryPercentUp.append(stockname)


        if((float(revdata['High'][0]) - float(revdata['Low'][0])) > (2*abs(float(revdata['Close'][0]) - float(revdata['Open'][0])))):
            isPinBar = ((float(revdata['High'][0]) - float(revdata['Open'][0])) < 0.3*(float(revdata['High'][0])-float(revdata['Low'][0]))) or ((float(revdata['High'][0]) - float(revdata['Close'][0])) < 0.3*(float(revdata['High'][0])-float(revdata['Low'][0])))
        
        if(stockname in prevInsideBars):
            isFakey = float(revdata['Low'][0]) < float(revdata['Low'][1]) # and float(revdata['High'][0]) < float(revdata['High'][1])

        if(isFakey and isPinBar):
            fakeyList.append(stockname)

        if(isInsideBar):
            insideBarList.append(stockname)
        else:
            return
        
        isNR7 = True
        min_diff=float(revdata['High'][0]) - float(revdata['Low'][0])
        for i in range(1, 7):
            diff = float(revdata['High'][i]) - float(revdata['Low'][i])
            if(min_diff>diff):
                isNR7=False
                break
        
        if(isInsideBar and isNR7):
            nr7List.append(stockname)
    except Exception:
        print('error in check')
    return

def checkDivergence(data):
    data = data.drop(columns=['Series','Last','VWAP','Turnover','Trades','Deliverable Volume','%Deliverble'])
    delta = data.iloc[:, 5].diff()  # 7 the column is close
    #delta = delta[1:] 
    #print(delta)
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    lookback = 14
    roll_up = up.ewm(lookback).mean()
    roll_down = down.abs().ewm(lookback).mean()
    # Calculate the RSI based on SMA
    RS = roll_up / roll_down
    RSI = (100.0 - (100.0 / (1.0 + RS)))
    RSI = np.array(RSI)
    data['rsi'] = RSI
    data = data.sort_values(by=['Date'], inplace=False, ascending=False)
    rsi_prices = create_rsi_price_array(data['rsi'],data['Close']) 
    divergence = bullish_divergence(rsi_prices,0.5,35)


def getNR7():
    print('started nr7 scan..')
    index=0
    timeout = 1
    while(index<len(symbolslist)):
        check(symbolslist[index])
        index=index+1
        timeout+=1
        if timeout==5:
            timeout=0
            time.sleep(5)
    formatAndTweet()

def formatAndTweet():
    print('formatting tweet')
    insideBarListString = ', '.join(insideBarList)
    nr7ListString = ', '.join(nr7List)
    fakeyListString = ', '.join(fakeyList)
    #tweet_stocks('#InsideBar stocks for tommorow:' + insideBarListString)
    #tweet_stocks('#NR7 + #InsideBar stocks for tommorow:' + nr7ListString)
    #tweet_stocks('#InsideBar #Fakey stocks for tommorow:' + fakeyListString)


def tweet_stocks(texttotweet):
    print('started tweeting..')
    try:
        for i in range(0, len(texttotweet), tweet_char_limit):
            if(tweetId == ''):
                tweetObj = api.update_status(texttotweet[i: i + tweet_char_limit])
            else:
                tweetObj = api.update_status(texttotweet[i: i + tweet_char_limit], tweetObj.id)
    except:
        print('error occured')

symbolslist=["MARUTI","TATACONSUM","AMARAJABAT","COALINDIA","ESCORTS","JUBLFOOD","IGL","NESTLEIND","NIITTECH","M&M","PVR","SUNPHARMA","HEROMOTOCO","RELIANCE","CIPLA","CUMMINSIND","Voltas","BPCL","ACC","ADANITRANS","AMBUJACEM","ASIANPAINT","ASHOKLEY","AUROPHARMA","DMART","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BERGEPAINT","BIOCON","BOSCHLTD","CADILAHC","COLPAL","CONCOR","DLF","DABUR","DIVISLAB","GICRE","GODREJCP","HDFCAMC","HDFCLIFE","HAVELLS","HINDPETRO","HINDZINC","ICICIGI","ICICIPRULI","IBULHSGFIN","INDIGO","L&TFH","LUPIN","MARICO","MOTHERSUMI","NHPC","NMDC","OFSS","PAGEIND","PETRONET","PIDILITIND","PEL","PFC","PGHH","SBILIFE","SRTRANSFIN","SIEMENS", "TORNTPHARM", "NIACL","UBL","MCDOWELL-N"]
 
prevInsideBars = getFromFirebase(firebasePath, firebaseSnapName)

getNR7()

combinedList = nr7List + insideBarList


postToFirebase(firebasePath, firebaseSnapName, combinedList)
