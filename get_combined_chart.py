import pandas as pd
import plotly
import plotly.graph_objects as go
from datetime import datetime,timedelta
import json

def get_combined_chart(selectedOption,selectedDate,selectedLine,db):

    Stocks_data_5_minutes = db["Stocks_data_5_minutes"].find({'Stock':str(selectedOption),'instrumenttype':"FUTIDX"}).sort([('Datetime', 1)])
    Stocks_data_5_minutes =  pd.DataFrame(list(Stocks_data_5_minutes))

    Stocks_data_1_minutes = db["Stocks_data_1_minutes"].find({'Stock':str(selectedOption),'instrumenttype':"FUTIDX"}).sort([('Datetime', 1)])
    Stocks_data_1_minutes =  pd.DataFrame(list(Stocks_data_1_minutes))

    support_and_resistance = db["support_and_resistance"].find({'Stock':str(selectedOption)}).sort([('Execution_date', 1)])
    support_and_resistance =  pd.DataFrame(list(support_and_resistance))

    Stocks_data_5_minutes = Stocks_data_5_minutes[['Datetime','Open','High','Low','Close','Volume','Execution_Date']]
    Stocks_data_1_minutes = Stocks_data_1_minutes[['Datetime','Open','High','Low','Close','Volume','Execution_Date']]

    print(support_and_resistance.columns)

    # support_and_resistance = support_and_resistance[['Stock','Execution_date','pivot_point','arima_resistance_2','arima_resistance_1','arima_pivot_point','arima_support_2','arima_support_1']]

    print(Stocks_data_5_minutes.columns)
    print(support_and_resistance.columns)

    futures_options_signals = db["futures_options_signals"].find({'Stock':str(selectedOption)}).sort([('Execution_date', 1)])
    futures_options_signals =  pd.DataFrame(list(futures_options_signals))


    futures_options_signals['Combined_Rnk'] = futures_options_signals['fut_volume_rank'] +  futures_options_signals['call_volume_rank'] +  futures_options_signals['put_volume_rank']
    futures_options_signals = futures_options_signals.sort_values(['Combined_Rnk'])
    futures_options_signals.reset_index(inplace=True,drop=True)

    highest_change = futures_options_signals.loc[0,'Datetime']
    Stocks_data_1_minutes['Datetime'] = Stocks_data_1_minutes['Datetime'] + timedelta(hours=5,minutes=30)
    highest_entry = Stocks_data_1_minutes.loc[Stocks_data_1_minutes['Datetime'] == highest_change,]
    highest_entry.reset_index(inplace=True,drop=True)

    oi_low = highest_entry.loc[0,"Low"]
    oi_high = highest_entry.loc[0,"High"]

    modified_stocks_5_data = Stocks_data_5_minutes.merge(support_and_resistance, left_on='Execution_Date', right_on='Execution_date',how="left")
    modified_stocks_5_data['Datetime'] = modified_stocks_5_data['Datetime'] + timedelta(hours=5,minutes=30)
    modified_stocks_5_data['oi_low'] = oi_low
    modified_stocks_5_data['oi_high'] = oi_high

    option_value = ""
    if selectedOption == "Nifty":
        option_value = '%5ENSEI'
    else:
        option_value = '%5ENSEBANK'
    algo_orders_place_data = db["algo_orders_place_data"].find({'Stock':str(option_value),'client_id':"J95213","execution_date":str(selectedDate)})
    algo_orders_place_data =  pd.DataFrame(list(algo_orders_place_data))

    modified_stocks_5_data['Execution_Date'] = pd.to_datetime(modified_stocks_5_data['Execution_Date'])

    algo_orders_place_data = algo_orders_place_data[['Strategy', 'Stock', 'Signal','Datetime', 'Value','buy_probability', 'sell_probability','current_script','Strike_Buy_Price','premium_Target','premium_StopLoss','historic_profit','conclusion']]

    modified_stocks_5_data = modified_stocks_5_data.merge(algo_orders_place_data, left_on='Datetime', right_on='Datetime',how="left")


    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    

    modified_stocks_5_data = modified_stocks_5_data[modified_stocks_5_data['Execution_Date'] == selectedDate]
    modified_stocks_5_data.reset_index(inplace=True,drop=True)

    print(modified_stocks_5_data.columns)


    candlestick_data = [go.Candlestick(
                                        x=modified_stocks_5_data['Datetime'],
                                                    open=modified_stocks_5_data['Open'], high=modified_stocks_5_data['High'],
                                                    low=modified_stocks_5_data['Low'], close=modified_stocks_5_data['Close']
                                    )]

    if selectedLine == "Arima":
        # Create scatter data
        scatter_data1 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['arima_pivot_point'],
                                    name='Arima Pivot Point'
                                )

        scatter_data2 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['arima_resistance_1'],
                                    name = 'Arima Resistance'
                                )

        scatter_data3 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['arima_support_1'],
                                    name = 'Arima Support'
                                )
    elif selectedLine == "Classical":
        # Create scatter data
        scatter_data1 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['pivot_point'],
                                    name='Pivot Point'
                                )

        scatter_data2 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['classical_resistance_1'],
                                    name = 'Classical Resistance'
                                )

        scatter_data3 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['classical_support_1'],
                                    name = 'Classical Support'
                                )
    elif selectedLine == "Fibonnaci":
        # Create scatter data
        scatter_data1 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['pivot_point'],
                                    name='Pivot Point'
                                )

        scatter_data2 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['fibonnaci_resistance_1'],
                                    name = 'Fibonnaci Resistance'
                                )

        scatter_data3 = go.Scatter(mode = "lines",
                                    x=modified_stocks_5_data['Datetime'],
                                    y=modified_stocks_5_data['fibonnaci_support_1'],
                                    name = 'Fibonnaci Support'
                                )

    scatter_data4 = go.Scatter(mode = "lines",
                                x=modified_stocks_5_data['Datetime'],
                                y=modified_stocks_5_data['oi_low'],
                                name = 'Highest OI Low'
                            )

    scatter_data5 = go.Scatter(mode = "lines",
                                x=modified_stocks_5_data['Datetime'],
                                y=modified_stocks_5_data['oi_high'],
                                name = 'Highest OI High'
                            )

    scatter_data6 = go.Scatter(
                                x=algo_orders_place_data['Datetime'],
                                y=algo_orders_place_data['Value'],
                                mode="markers",
                                marker=dict(symbol='star-triangle-down'),
                                marker_size=12,
                                text = "Datetime : "+ algo_orders_place_data['Datetime'].astype(str) + "<br>Value: " + algo_orders_place_data['Value'].astype(str) + "<br>Buy Probability: " + algo_orders_place_data['buy_probability'].astype(str)+ "<br>Sell Probability: " + algo_orders_place_data['sell_probability'].astype(str)+ "<br>Strategy: " + algo_orders_place_data['Strategy'].astype(str)+ "<br>Current Script: " + algo_orders_place_data['current_script'].astype(str)+ "<br>Strike Buy Price : " + algo_orders_place_data['Strike_Buy_Price'].astype(str)  ,
                                hoverinfo='text'

                            )


    data = candlestick_data + [scatter_data1,scatter_data2,scatter_data3,scatter_data4,scatter_data5,scatter_data6]
    layout = {'title': 'Orders Chart', 
              'xaxis': dict(type='category',
                            rangebreaks=[dict(bounds=["sat", "mon"])], # set rangebreaks
                            rangeslider=dict(visible=False) # make rangeslider invisible
                            )}
    figure = go.Figure(data=data, layout=layout)

    return figure


