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