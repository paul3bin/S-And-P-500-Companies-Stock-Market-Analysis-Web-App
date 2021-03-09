import pandas as pd
import streamlit as st
import base64
import yfinance as yf
from datetime import date
from pandas_datareader import DataReader

st.set_page_config(page_title='S&P500 Stock Market Analysis')


@st.cache
def get_SnP_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df


def file_download(df):
    # returns tag for downloading csv of
    csv = df.to_csv(index=False)
    # Strings <-> bytes conversion
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href


def get_year_to_date_data():
    return yf.download(
        tickers=list(df_selected_sector[:10].Symbol),
        period="ytd",
        interval='1d',
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )


def plot_line_chart_close(tickerDf):
    return st.line_chart(tickerDf.Close)


def plot_line_chart_volume(tickerDf):
    return st.line_chart(tickerDf.Volume)


def plot_adjusted_closing_price(tickerDf):
    return st.line_chart(tickerDf['Adj Close'])


def plot_moving_average(tickerDf):
    return st.line_chart(tickerDf[['Adj Close', 'MA for 10 days', 'MA for 20 days', 'MA for 50 days']])


def get_start_and_end_date():
    last = str(date.today()).split('-')
    last[0] = str(int(last[0])-1)
    return [str(date.today()), '-'.join(last)]


def get_ticker_df(ticker_symbol):
    dates = get_start_and_end_date()
    # tickerData = yf.Ticker(ticker_symbol)
    # return tickerData.history(
    #     period='1d', start=dates[1], end=dates[0])
    df = DataReader(ticker_symbol, 'yahoo', dates[1], dates[0])
    add_moving_average(df)
    return df


def add_moving_average(df):
    ma_day = [10, 20, 50]
    for ma in ma_day:
        column_name = "MA for "+str(ma)+" days"
        df[column_name] = df['Adj Close'].rolling(ma).mean()
    return df


if __name__ == '__main__':

    st.set_option('deprecation.showPyplotGlobalUse', False)

    st.title('S&P 500 Stock Market Analysis Web-App')
    st.sidebar.header('User Input Features')

    df = get_SnP_data()
    sector = df.groupby('GICS Sector')

    st.header('S&P500 Companies')
    st.write('Data Dimension: '+str(df.shape[0])+' rows and '+str(
        df.shape[1])+' columns')
    st.dataframe(df)

    # Sidebar - Sector Selection
    sorted_unique_sector = sorted(df['GICS Sector'].unique())
    selected_sector = st.sidebar.multiselect(
        'Sector', sorted_unique_sector, sorted_unique_sector[0])

    # Filtering data
    df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

    # Sidebar - Companies Under Selected Sector
    company_names = sorted(df_selected_sector['Security'])
    selected_company = st.sidebar.multiselect(
        'Company', company_names)

    df_selected_company = df_selected_sector[df_selected_sector['Security'].isin(
        selected_company)]

    # Header
    st.header('Display Companies in Selected Sector')
    st.write('Data Dimension: '+str(df_selected_sector.shape[0])+' rows and '+str(
        df_selected_sector.shape[1])+' columns')

    # Dataframe which is displayed on the page
    st.dataframe(df_selected_sector)

    # link for downloading csv file
    st.markdown(file_download(df_selected_sector), unsafe_allow_html=True)

    data = get_year_to_date_data()

    ticker_symbols = list(df_selected_company['Symbol'])
    company_names = list(df_selected_company['Security'])

    if st.button('Show Plots'):
        i = 0
        for symbol in ticker_symbols:
            df = get_ticker_df(symbol)
            st.markdown(f'### Stock Closing Price {company_names[i]}')
            plot_line_chart_close(df)
            st.markdown(f'### Stock Closing Volume {company_names[i]}')
            plot_line_chart_volume(df)
            st.markdown(f'### Stock Adjusted Closing Price {company_names[i]}')
            plot_adjusted_closing_price(df)
            st.markdown(
                f'### Moving Avergage for 10, 20 and 50 days {company_names[i]}')
            plot_moving_average(df)
            i += 1
