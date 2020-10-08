#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-e

from __future__ import absolute_import, division, print_function, unicode_literals
import backtrader as bt
from backtrader import Order
import matplotlib as plt
import datetime
import pytz
import ta
import backtrader.feeds as btfeeds

class IntraTrendStrategy(bt.Strategy):
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.f.write('%s, %s\n' % (dt.isoformat(), txt))

    def __init__(self):
        self.f = open("log.csv", "w")
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.rsi = bt.ind.RSI(self.data, period=5)
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.sellprice = None
        self.buycomm = None
        self.daylow = None
        self.dayhigh = None
        self.long = None
        self.isgap = False

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.sellprice = order.executed.price

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def start(self):
        self.counter = 0

    def prenext(self):
        self.counter += 1
        self.log('prenext len %d - counter %d' % (len(self), self.counter))

    def next(self):
        self.counter += 1
        # Simply log the closing price of the series from the reference
        self.log('---next len %d - counter %d' % (len(self), self.counter))
        self.log('%d Close, %.2f, RSI, %.2f' % (len(self), self.dataclose[0], self.rsi[0]))

        if(self.data.datetime.time(0) == datetime.time(9,15)):
            #avoid stocks with 2% gap
            if(abs(self.dataopen[0]-self.dataclose[-1]) >= (self.dataclose[-1]*0.02)):
                self.isgap = True
            self.daylow = self.datalow[0]
            self.dayhigh = self.datahigh[0]
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            if(self.data.datetime.time(0) == datetime.time(3,25)):
                self.order = None
            return

        # Check if we are in the market
        if not self.position:
            #add another condition as candle should be bullish
            
            if (not self.isgap and self.data.datetime.time(0) == datetime.time(9,25) and self.rsi[0] < 50 and self.datalow[0] > self.dataopen[-1]):

                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                #self.order = self.buy(exectype=Order.StopLimit, price=self.datahigh[0], valid=self.datas[0].datetime.date(0) + datetime.timedelta(days=3))
                self.order = self.buy(size=1)
                self.long = True
            
            if (not self.isgap and self.data.datetime.time(0) == datetime.time(9,25) and self.rsi[0] > 50 and self.datahigh[0] < self.dataopen[-1]):

                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                #self.order = self.buy(exectype=Order.StopLimit, price=self.datahigh[0], valid=self.datas[0].datetime.date(0) + datetime.timedelta(days=3))
                self.order = self.sell(size=1)
                self.long = False

        else:
            self.isgap = False
            # Already in the market ... we might sell
            if(self.long):
                target = self.buyprice + ((self.buyprice - self.daylow) * 2)
                if (self.data.datetime.time(0) == datetime.time(15,20) or self.dataclose[0]>=target or self.datalow[0] < self.daylow):
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell(size=1)
            else:
                target = self.sellprice - ((self.dayhigh-self.sellprice) * 2)
                if (self.data.datetime.time(0) == datetime.time(15,20) or self.dataclose[0]<=target or self.datahigh[0] > self.dayhigh):
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy(size=1)




# data0 = store.getdata(dataname="TCS-STK-NSE-INR", **stockkwargs)
# cerebro.resampledata(data0, timeframe=bt.TimeFrame.Days, compression=1)

stockkwargs = dict(
        timeframe=bt.TimeFrame.Minutes,
        compression=30,
        historical=True,  # only historical download
        fromdate=datetime.datetime(2020, 9, 1),  # get data from..
        todate=datetime.datetime(2020, 9, 13)  # get data from..
    )

cerebro = bt.Cerebro(stdstats=False)
store = bt.stores.IBStore(port=7496,clientId=5)
data = store.getdata(dataname='TCS-STK-NSE-INR',**stockkwargs)  
#cerebro.adddata(data)
 

cerebro.replaydata(data,timeframe=bt.TimeFrame.Minutes,compression=30)
cerebro.addstrategy(IntraTrendStrategy)
cerebro.run()