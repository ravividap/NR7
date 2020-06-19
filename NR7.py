import re
import json
import time
import requests
from datetime import datetime, date, timedelta
from firebase import firebase
from nsepy import get_history
import tweepy
import config
import schedule
import time
from datetime import datetime, timedelta

print('Started..')

insideBarList = []
nr7List = []
prevInsideBars = []
fakeyList = []

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
        print('getting history finish')
        revdata = data.sort_values(by=['Date'], inplace=False, ascending=False)
        print(revdata)
        isInsideBar = float(revdata['High'][0]) < float(revdata['High'][1]) and float(revdata['Low'][0]) > float(revdata['Low'][1])
        
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
        for i in range(1, 8):
            diff = float(revdata['High'][i]) - float(revdata['Low'][i])
            if(min_diff>diff):
                isNR7=False
                break
        
        if(isInsideBar and isNR7):
            nr7List.append(stockname)
    except Exception:
        print('error in check')
    return
  
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
            time.sleep(35)
    formatAndTweet()

def formatAndTweet():
    print('formatting tweet')
    insideBarListString = ', '.join(insideBarList)
    nr7ListString = ', '.join(nr7List)
    fakeyListString = ', '.join(fakeyList)
    tweet_stocks('#InsideBar stocks for tommorow:' + insideBarListString)
    tweet_stocks('#NR7 + #InsideBar stocks for tommorow:' + nr7ListString)
    tweet_stocks('#InsideBar #Fakey stocks for tommorow:' + fakeyListString)


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

symbolslist=["M&M","PVR","SUNPHARMA","HEROMOTOCO","RELIANCE","CIPLA","CUMMINSIND","Voltas","BPCL","ACC","ADANITRANS","AMBUJACEM","ASIANPAINT","ASHOKLEY","AUROPHARMA","DMART","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BERGEPAINT","BIOCON","BOSCHLTD","CADILAHC","COLPAL","CONCOR","DLF","DABUR","DIVISLAB","GICRE","GODREJCP","HDFCAMC","HDFCLIFE","HAVELLS","HINDPETRO","HINDZINC","ICICIGI","ICICIPRULI","IBULHSGFIN","INDIGO","L&TFH","LUPIN","MARICO","MOTHERSUMI","NHPC","NMDC","OFSS","PAGEIND","PETRONET","PIDILITIND","PEL","PFC","PGHH","SBILIFE","SRTRANSFIN","SIEMENS", "TORNTPHARM", "NIACL","UBL","MCDOWELL-N"]
 
prevInsideBars = getFromFirebase(firebasePath, firebaseSnapName)

getNR7()

combinedList = nr7List + insideBarList

postToFirebase(firebasePath, firebaseSnapName, combinedList)

# schedule.every().day.at("01:30").do(getNR7)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
