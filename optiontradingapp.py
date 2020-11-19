
import logging
import os.path
import schedule
import datetime 
import sys

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import pandas as pd

class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = {}
        self.pos = {}
        self.df = pd.DataFrame(columns = ['Date', 'Ticker', 'Open', 'High','Low','Close','Volume']) 
        self.cashBalance = 0
        self.placedOrder = {}

    def historicalData(self, reqId, bar):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)
    
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    @staticmethod
    def bracketOrder(parentOrderId:int, action:str, quantity:float, limitPrice:float, stopLossPrice:float):
   
        #This will be our main or "parent" order
        parent = Order()
        parent.orderId = parentOrderId
        parent.action = action
        parent.orderType = "STP LMT"
        parent.totalQuantity = quantity
        parent.lmtPrice = limitPrice
        parent.auxPrice = limitPrice
        #The parent and children orders will need this attribute set to False to prevent accidental executions.
        #The LAST CHILD will have it set to True, 
        parent.transmit = False


        stopLoss = Order()
        stopLoss.orderId = parent.orderId + 2
        stopLoss.action = "SELL" if action == "BUY" else "BUY"
        stopLoss.orderType = "STP"
        #Stop trigger price
        stopLoss.auxPrice = stopLossPrice
        stopLoss.totalQuantity = quantity
        stopLoss.parentId = parentOrderId
        #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
        #to activate all its predecessors
        stopLoss.transmit = True
        bracketOrder = [parent, stopLoss]
        return bracketOrder

    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        if contract.symbol not in self.pos:
            self.pos[contract.symbol]=position
        print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:",
            contract.secType, "Currency:", contract.currency,
            "Position:", position, "Avg cost:", avgCost)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        if(tag=="CashBalance"):
            self.cashBalance = float(value)
            logger.info("Cash available:%s",value)
    
    def realtimeBar(self, reqId: int, time:int, open_: float, high: float, low: float, close: float, volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)

    
        
def marketOrder(direction,quantity):
        order = Order()
        order.action = direction
        order.orderType = "MKT"
        order.totalQuantity = quantity
        return order

def websocket_con():
    app.run()

def dataDataframe(TradeApp_obj,symbols, symbol):
    "returns extracted historical data in dataframe format"
    df = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
    df.set_index("Date",inplace=True)
    return df

#creating object of the Contract class - will be used as a parameter for other function calls
def createStk(symbol,sec_type="STK",currency="INR",exchange="NSE"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def createCallOpt(symbol,strike,contractMonth,sec_type="OPT",currency="INR",exchange="NSE"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.right = "C"
    contract.strike = strike
    contract.multiplier = 1
    contract.tradingClass = 'BANKNIFTY'
    contract.lastTradeDateOrContractMonth = contractMonth
    return contract 

def histData(req_num,contract,duration,candle_size, queryTime):
    app.reqHistoricalData(reqId=req_num, 
                          contract=contract,
                          endDateTime=queryTime,
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='TRADES',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[])	 

def setupLogger():
    logger = logging.getLogger('tradingapp')
    hdlr = logging.FileHandler('{:%Y-%m-%d}.log'.format(datetime.datetime.now()))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    return logger

def calculatePivots(DF):
    df = DF.copy()
    df['Pivot'] = (df['High']+df['Low']+df['Close'])/3
    df['R1'] = 2*df['Pivot'] - df['Low']
    df['S1'] = 2*df['Pivot'] - df['High']
    return df

def checkStocks():
    logger.info('Checking stocks ')
    if(datetime.datetime.now().time() > datetime.time(14,0)):
        logger.info('stop checking its 2 already')
        return

    for ticker in tickers:
        app.data = {}
        app.df = pd.DataFrame(columns = ['Date', 'Ticker', 'Open', 'High','Low','Close','Volume'])
        histData(tickers.index(ticker),createStk(ticker),'600 S', '5 mins','')
        while(len(app.df.index) < 2):
            continue
        app.df.set_index('Date', inplace=True)
        if(app.df.iloc[1]['Close'] > historicalDF.iloc[tickers.index(ticker)]['R1']):
            if(ticker not in takenPositions):
                takenPositions[ticker] = True
                logger.info("Ticker %s satified R1 condition, SL :%s, Entry:%s",ticker,app.df.iloc[0]['Low'],app.df.iloc[1]['High']) 
                cashForEachTicker = app.cashBalance/len(tickers)
                buyingPower = round(cashForEachTicker/app.df.iloc[1]['High'])-1
                qtyPerRisk = round((app.cashBalance*0.01) / (app.df.iloc[1]['High'] - app.df.iloc[0]['Low']))
                qty = (buyingPower < qtyPerRisk and buyingPower) or qtyPerRisk
                app.reqIds(-1)
                logger.info("cash for ticker %s, buyingPower %s, qtyPerrisk %s", cashForEachTicker, buyingPower, qtyPerRisk)
                order_id = app.nextValidOrderId 
                bracket = TradingApp.bracketOrder(order_id, "BUY", qty, app.df.iloc[1]['High'], app.df.iloc[0]['Low'])
                for o in bracket:
                    app.placeOrder(o.orderId, createStk(ticker), o)

def checkStocksEveryTenMin():
    logger.info("Scheduling method checkstocks")
    schedule.every(10).minutes.do(checkStocks)

def getNearestRoundNumber(base,number):
    return (base * round(number/base))
    
def liquidatePosition():
    logger.info("Liquidating positions")
    try:
        app.reqGlobalCancel()
        time.sleep(5)
    except Exception as ex:
        logger.error("Error cancelling pending order: %s", ex)
    try:
        app.reqPositions()
        time.sleep(5)
    except Exception as ex:
        logger.error("Error getting open positions: %s",ex)
    for po in app.pos:  
        try:
            if(app.pos[po] > 0):
                order_id = app.nextValidOrderId
                app.placeOrder(order_id,createStk(po),marketOrder("SELL",app.pos[po]))
        except Exception as ex:
            logger.error("Error placing liquidation orders :%s",ex)

def exitProgram():
    sys.exit()


logger = setupLogger()

########### Connect to TWS Start ##############
try:
    app = TradingApp()      
    app.connect("127.0.0.1", 4001, clientId=2)
    # starting a separate daemon thread to execute the websocket connection
    con_thread = threading.Thread(target=websocket_con, daemon=True)
    con_thread.start()
    time.sleep(1) # some latency added to ensure that the connection is established
except Exception as ex:
    logger.error("Error connecting gateway %s", ex)
###########  Connect to TWS End ##############

########### Get available cash balance #########
histData(4,createCallOpt('BANKNIFTY IND',29000,'20201119'),'1 D', '1 day','')

# app.reqAccountSummary(9002, "All", "$LEDGER")
# time.sleep(3)
########### Get available cash balance end #########

###########  Prepare Historical Data Start ##############
ticker = 'BANKNIFTY'
queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
    # try:
    #     histData(tickers.index(ticker),createStk(ticker),'1 D', '1 day','')
    # except Exception as ex:
    #     logger.error("Error getting historical data for %s", ticker)
    #     logger.error(ex)

    
app.df.set_index('Date', inplace=True)
historicalDF = calculatePivots(app.df)
logger.info('historical df length %d',len(historicalDF))
###########  Prepare Historical Data End ##############
app.reqRealTimeBars(3001, createCallOpt('BANKNIFTY IND',29000,'20201119'), 5, "TRADES", True, [])
#app.reqRealTimeBars(3001, createStk('TCS'), 5, "MIDPOINT", True, [])

takenPositions = {}
schedule.every().day.at("09:15").do(checkStocksEveryTenMin)
schedule.every().day.at("15:20").do(liquidatePosition)
schedule.every().day.at("15:35").do(exitProgram)

#check error while liquidating ..take logs from rremote server


while True:
    schedule.run_pending()
    time.sleep(1)
