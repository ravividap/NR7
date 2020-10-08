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

    def __init__(self):
        pass

    def start(self):
        self.counter = 0

    def prenext(self):
        self.counter += 1
        self.log('prenext len %d - counter %d' % (len(self), self.counter))

    def next(self):
        self.counter += 1
        self.log('---next len %d - counter %d' % (len(self), self.counter))


stockkwargs = dict(
        timeframe=bt.TimeFrame.Minutes,
        compression=15,
        historical=True,  # only historical download
        fromdate=datetime.datetime(2020, 9, 1),  # get data from..
        todate=datetime.datetime(2020, 9, 13)  # get data from..
    )

cerebro = bt.Cerebro(stdstats=False)
store = bt.stores.IBStore(port=7496,clientId=5)
data = store.getdata(dataname='TCS-STK-NSE-INR',**stockkwargs)  
cerebro.replaydata(data,timeframe=bt.TimeFrame.Days,compression=1)
cerebro.addstrategy(IntraTrendStrategy)
cerebro.run()