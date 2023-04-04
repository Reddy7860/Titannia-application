import pandas as pd
from datetime import datetime,timedelta
from pandasql import sqldf
import numpy as np
import time
import datetime as dt
from pytz import timezone
from urllib.request import urlopen



def get_display_data(client_id,date_inpt,db):

    # client_id = "M591295"
    # date_inpt = "2023-01-19"

    client_details = db["client_details"].find({'client_id':{'$in' :['J95213','S1604557','G304915','K256027','M591295','M181705']}})
    final_open_data = pd.DataFrame()
    final_stoploss_data = pd.DataFrame()
    final_position_data = pd.DataFrame()
    final_completed_orders = pd.DataFrame()
    final_closed_positions = pd.DataFrame()

    if client_id != "All":
        order_data = db["Order_Data"].find({'Client_id':str(client_id),'execution_date':str(date_inpt)}).sort("updatetime", -1)
        position_data = db["Position_Data"].find({'Client_id':str(client_id),'execution_date':str(date_inpt)})
    else:
        order_data = db["Order_Data"].find({}).sort("updatetime", -1)
        position_data = db["Position_Data"].find({})

    
    order_data =  pd.DataFrame(list(order_data))
    position_data =  pd.DataFrame(list(position_data))

    pysqldf = lambda q: sqldf(q, globals())

    if len(order_data) > 0:
        open_positions = order_data.loc[order_data['status'] == "open",]
        stoploss_pending = order_data.loc[order_data['status'] == "trigger pending",]
        completed_orders = order_data.loc[order_data['status'] == "complete",]

        if len(open_positions) > 0 :
            open_positions.reset_index(inplace=True,drop=True)
            open_positions['Client_id'] = str(client_id)
            final_open_data = final_open_data.append(open_positions)
        
        if len(stoploss_pending) > 0 :
            stoploss_pending.reset_index(inplace=True,drop=True)
            stoploss_pending['Client_id'] = str(client_id)
            final_stoploss_data = final_stoploss_data.append(stoploss_pending)
            
        if len(completed_orders) > 0 :
            print(completed_orders.columns)
            completed_orders.reset_index(inplace=True,drop=True)
            completed_orders['Client_id'] = str(client_id)
            final_completed_orders = final_completed_orders.append(completed_orders)
            
    if len(position_data) > 0:
        position_data['Client_id'] = str(client_id)
        
        closed_orders = position_data.loc[position_data['netprice'] == '0.00',]
        pending_positions = position_data.loc[position_data['netprice'] != '0.00',]
        
        if len(closed_orders) > 0:
            final_closed_positions = final_closed_positions.append(closed_orders)
            
        if len(pending_positions) > 0:
            final_position_data = final_position_data.append(pending_positions)


    print(final_position_data)
    print(final_open_data)
    print(final_stoploss_data)
    print(final_completed_orders)
    print(final_closed_positions)

    if len(final_position_data) > 0:
    	final_position_data = final_position_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close','execution_date']]
    else:
    	final_position_data = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close','execution_date'])

    if len(final_open_data) > 0:
    	final_open_data = final_open_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date']]
    else:
    	final_open_data = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date'])

    if len(final_stoploss_data) > 0 :
    	final_stoploss_data = final_stoploss_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date']]
    else:
    	final_stoploss_data = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date'])

    # if len(final_position_data) > 0:
    # 	final_position_data=final_position_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
    # else:
    # 	final_position_data = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close'])

    if len(final_completed_orders) > 0:
    	final_completed_orders = final_completed_orders[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date']]
    else:
    	final_completed_orders = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid','execution_date'])

    if len(final_closed_positions) > 0:
    	final_closed_positions = final_closed_positions[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close','execution_date']]
    else:
    	final_closed_positions = pd.DataFrame(columns=['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close','execution_date'])

    return final_position_data,final_open_data,final_stoploss_data,final_completed_orders,final_closed_positions


