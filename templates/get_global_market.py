import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from flask_pymongo import PyMongo
import yfinance as yf


def get_global_market(start_date,end_date,db):

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Define the indices you want to fetch data for
    indices = ['^DJI','^IXIC', '^GSPC', '000001.SS', '399001.SZ', '^FTSE', '^FCHI','^N225','^HSI']
    index_names = ['Dow Jones','Nasdaq', 'S&P 500', 'Shanghai Composite', 'Shenzhen Composite', 'FTSE 100', 'CAC 40','Nikkei 225','Hang Seng']
    index_market = ['USA','USA', 'USA', 'China', 'China', 'Europe', 'Europe','Japan','Hong Kong']

    main_data = pd.DataFrame()

    for ind in range(0,len(indices)):
        # Fetch the data using the yfinance library
        data = yf.download(indices[ind], start=start_date, end=end_date)
        data = pd.DataFrame(data)
        data['Index'] = str(index_names[ind])
        data['Market'] = str(index_market[ind])

        main_data = main_data.append(data)
    
    main_data['Date'] = main_data.index
    main_data.reset_index(inplace=True,drop=True)
    


    # print(main_data.head())


    # global_markets = db["global_markets"].find({})
    # global_markets = pd.DataFrame(list(global_markets))

    # global_markets['Date'] = pd.to_datetime(global_markets['Date'])

    # filtered_df = global_markets.loc[(global_markets['Date'].dt.date >= start_date) & (global_markets['Date'].dt.date <= end_date)]

    # print(filtered_df.head())

    

    return main_data