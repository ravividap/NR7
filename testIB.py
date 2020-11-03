from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from datetime import datetime

class St(bt.Strategy):

    def __init__(self):
        self.ema5high = bt.indicators.EMA(self.data.high,period=5)
        self.ema5low = bt.indicators.EMA(self.data.low,period=5)
        self._df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self._s = pd.Series()

    def logdata(self):
        txt = []
        txt.append('{}'.format())
        txt.append('{:.5f}'.format(self.data.open[0]))
        txt.append('{:.5f}'.format(self.data.high[0]))
        txt.append('{:.5f}'.format(self.data.low[0]))
        txt.append('{:.5f}'.format(self.data.close[0]))
        txt.append('{:.5f}'.format(self.data.volume[0]))
        print(','.join(txt))
        self._s = ([self.data.datetime.datetime(0).isoformat(),
                            self.data.open[0], self.data.high[0], self.data.low[0], self.data.close[0], self.data.volume[0]])
    data_live = False

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        if status == data.LIVE:
            self.data_live = True

    def notify_order(self, order):
        date = self.data.datetime.datetime(0).isoformat()
        if order.status == order.Accepted:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Accepted')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}' \
            .format(date, order.status, order.ref, order.size,
                    'NA' if not order.price else round(order.price,5)))

        if order.status == order.Completed:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Completed')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}' \
            .format(date, order.status, order.ref, order.size,
                    'NA' if not order.price else round(order.price,5)))
            print('Created: {} Price: {} Size: {}' \
            .format(bt.num2date(order.created.dt),
                                order.created.price,order.created.size))
            print('-'*80)

        if order.status == order.Canceled:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('Order Canceled')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}' \
            .format(date, order.status, order.ref, order.size,
                    'NA' if not order.price else round(order.price,5)))

        if order.status == order.Rejected:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('WARNING! Order Rejected')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}' \
            .format(date, order.status, order.ref, order.size,
                    'NA' if not order.price else round(order.price,5)))
            print('-'*80)

    def notify_trade(self, trade):
        date = self.data.datetime.datetime()
        if trade.isclosed:
            print('-'*32,' NOTIFY TRADE ','-'*32)
            print('{}, Close Price: {}, Profit, Gross {}, Net {}' \
            .format(date, trade.price, round(trade.pnl,2),
                    round(trade.pnlcomm,2)))
            print('-'*80)

    def next(self):
        self.logdata()
        if not self.data_live:
            return

        close = self.data.close[0]

        if not self.position:
            # look to enter
            if close < self.ema5low[0]:
                # we have closed below the ema5low and are entering
                # a long position via a bracket order
                long_tp = close + 0.0006
                long_stop = close - 0.0008
                self.buy_bracket(size=1, limitprice=long_tp,
                                 stopprice=long_stop,
                                 exectype=bt.Order.Market)

            elif close > self.ema5high[0]:
                short_tp = close - 0.0006
                short_stop = close + 0.0008
                self.sell_bracket(size=1, stopprice=short_stop,
                                  limitprice=short_tp,
                                  exectype=bt.Order.Market)

def run(args=None):
    cerebro = bt.Cerebro(stdstats=False)
    store = bt.stores.IBStore(port=7496, host='127.0.0.1')

    stockkwargs = dict(
        historical=True,
        fromdate=datetime(2019, 9, 9),  # get data from
        timeframe=bt.TimeFrame.Minutes,
        tz="Asia/Kolkata"
    )

    smalldata = store.getdata(dataname='TCS-STK-NSE-INR', **stockkwargs)
  
    #cerebro.resampledata(smalldata, timeframe=bt.TimeFrame.Minutes, compression=30)
    cerebro.resampledata(smalldata, timeframe=bt.TimeFrame.Minutes, compression=30)

    cerebro.broker = store.getbroker()

    cerebro.addstrategy(St)
    cerebro.run()


if __name__ == '__main__':
    run()