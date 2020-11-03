from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
from time import time, strftime
from datetime import datetime
import pandas as pd


class IBDataCache(object):

    def _reset_data(self, host='127.0.0.1', port=7496):
        self._df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self._s = pd.Series()

        #Initialize connection as long as it's not already connected:
        if (not hasattr(self, '_conn')) or (not self._conn.isConnected()):
            self._conn = ibConnection(host, port, client_id)
            self._conn.enableLogging()
            # Register the response callback function and type of data to be returned
            self._conn.register(self._error_handler, message.Error)
            self._conn.register(self._historical_data_handler, message.historicalData)
            self._conn.register(self._save_order_id, 'NextValidId')
            self._conn.register(self._nextValidId_handler, message.nextValidId)
            self._conn.connect()



    def _save_order_id(self, msg):
        self._next_valid_id = msg.orderId
        print('save order id',msg.orderId)

    def _nextValidId_handler(self, msg):
        print("nextValidId_handler: ", msg)
        self.inner(sec_type=self.req.m_secType, symbol=self.req.m_symbol, currency=self.req.m_currency, exchange=self.req.m_exchange, \
                   primaryExchange=self.req.m_primaryExch, endtime=self.req.endtime, duration=self.req.duration, \
                   bar_size=self.req.bar_size, what_to_show=self.req.what_to_show, use_rth=self.req.use_rth)

    def _error_handler(self, msg):
        print("error: ", msg)
        if not msg:
            print('disconnecting', self._conn.disconnect())



    def __init__(self, data_path='/docker_stocks/data', date_format='%Y%m%d %H:%M:%S', host='127.0.0.1', port=7694, client_id=None):
        self._data_path = data_path
        self._date_format = date_format
        self._next_valid_id = 1

        self._host = host
        self._port = port
        self._client_id = client_id






    def _historical_data_handler(self, msg):
        """
            Define historical data handler for IB - this will populate our pandas data frame
        """

        # print (msg.reqId, msg.date, msg.open, msg.close, msg.high, msg.low)
        if not 'finished' in str(msg.date):
            #print ("historical_data_handler: ", msg)
            try:
                self._s = ([datetime.strptime(msg.date, self._date_format),
                            msg.open, msg.high, msg.low, msg.close, msg.volume, 0])
            except:
                #for dates only with no time to str:
                self._s = ([datetime.strptime(msg.date, "%Y%m%d"),
                            msg.open, msg.high, msg.low, msg.close, msg.volume, 0])
            self._df.loc[len(self._df)] = self._s

        else:
            self._df.set_index('Date', inplace=True)



    def setAllWithKwArgs(self, **kwargs):
        #set all attributes to the kwargs to pass along
        for key, value in kwargs.items():
            setattr(self, key, value)

    def inner(self, sec_type, symbol, currency, exchange, primaryExchange, endtime, duration, bar_size, what_to_show, use_rth):
        print ("calling inner... setting up req.")
        self.req = Contract()
        self.req.m_secType = sec_type
        self.req.m_symbol = symbol
        self.req.m_currency = currency
        self.req.m_exchange = exchange
        self.primaryExch = primaryExchange
        self.req.endtime = endtime
        self.req.duration = duration
        self.req.bar_size = bar_size
        self.req.what_to_show = what_to_show
        self.req.use_rth = use_rth


        self._conn.reqHistoricalData(self._next_valid_id, self.req, endtime, duration,
                                     bar_size, what_to_show, use_rth, 1)


    def get_dataframe(self, sec_type, symbol, currency, exchange, primaryExchange, endtime, duration, bar_size, what_to_show, use_rth, timeoutsecs):



        # build filename
        self.filename = symbol + '_' + sec_type + '_' + exchange + '_' + currency + '_' + \
            endtime.replace(' ', '') + '_' + duration.replace(' ', '') + '_' + bar_size.replace(' ', '') + '_' + \
            what_to_show + '_' + str(use_rth) + '.csv'
        self.filename = self.filename.replace('/', '.')
        self.filename = self._data_path + '/' + self.filename
        print ("filename:  ", self.filename)


        try:

            # check if we have this cached
            self._df = pd.read_csv(self.filename,
                         parse_dates=True,
                         index_col=0)
            self._df.index = pd.to_datetime(self._df.index, format='%Y-%m-%d %H:%M:%S')
        except IOError:
            #set up connection:
            self._reset_data(self._host, self._port, self._client_id)

            # Not cached. Download it.
            # Establish a Contract object and the params for the request
            self.inner(sec_type, symbol, currency, exchange,
                  primaryExchange, endtime, duration, bar_size,
                  what_to_show, use_rth)

            # Make sure the connection doesn't get disconnected prior the response data return
            timeout = time() + timeoutsecs
            while self._conn.isConnected() and time() < timeout:
                #print(".", end="", flush=True)
                pass
            self._conn.disconnect()
            self._df.to_csv(self.filename)


        return self._df





if __name__ == '__main__':

    date_format = '%Y%m%d %H:%M:%S'

    downloader_kwargs = dict(
        data_path='../data',
        date_format=date_format,
        host='127.0.0.1',
        port=7496,
        client_id=5
    )
    downloader = IBDataCache(**downloader_kwargs)

    stock_kwargs = dict(
        sec_type='STK',
        symbol='TCS',
        currency='INR',
        primaryExchange='NSE',
        endtime=datetime(2017, 10, 26, 15, 59).strftime(date_format),
        duration='2 D',
        bar_size='30 mins',
        what_to_show='TRADES',
        use_rth=1
    )

    df = downloader.get_dataframe(**stock_kwargs)
    print(df)


    stock_kwargs = dict(
        sec_type='STK',
        symbol='MSFT',
        currency='USD',
        exchange='SMART',
        primaryExchange='NASDAQ',
        endtime=datetime(2018, 10, 26, 15, 59).strftime(date_format),
        duration='1 D',
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=1
    )

    df = downloader.get_dataframe(**stock_kwargs)

    print ("IBCacheData")

    print(df)
