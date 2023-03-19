import pandas_gbq
import plotly.graph_objects as go
from google.oauth2 import service_account
import pandas as pd

def get_vix_data(start_date,end_date):
    credentials = service_account.Credentials.from_service_account_file('static/ferrous-module-376519-7e08f583402d.json')
    sql = f"select * from `ferrous-module-376519.Titania.vix_data` where Date>='{start_date}' and Date<= '{end_date}'"
    print(sql)
    vix_data = pandas_gbq.read_gbq(sql, project_id='ferrous-module-376519',credentials=credentials)

    print(vix_data)

    vix_data['Date'] = pd.to_datetime(vix_data['Date'], format='%Y-%m-%d')

    vix_data.sort_values(by='Date', ascending=False, inplace=True)

    vix_data.reset_index(inplace=True,drop=True)

    print(vix_data)

    sid = "VIX Data"

    # make sure everything is json serializable, plus use  ISO 8601 for dates
    trace = go.Candlestick(
        x=vix_data['Date'].tolist(),
        open=vix_data['Open'].tolist(),
        high=vix_data['High'].tolist(),
        low=vix_data['Low'].tolist(),
        close=vix_data['Close'].tolist(),
        name="sid",
    )

    data = [trace]

    layout = {"title": sid,'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}

    figure = go.Figure(data=data, layout=layout)

    return figure

if __name__ == '__main__':
    print(get_vix_data(start_date,end_date))