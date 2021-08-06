import pandas as pd
import yfinance as yf
import numpy as np
from functions import start_of_month
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal

# Define Variables
start = '2005-01-01'
end = '2021-05-31'
ticker = ['QQQ', 'SPY']

# Import data
prices = yf.download(tickers=ticker, start=start, end=end)['Adj Close'].dropna()  # Primary asset
INDPRO = pd.read_csv('INDPRO.csv', index_col=0).dropna()  # Industrial Production: Total Index
RRSFS = pd.read_csv('RRSFS.csv', index_col=0).dropna()  # Advance Real Retail and Food Services Sales
UNRATE = pd.read_csv('UNRATE.csv', index_col=0).dropna()  # Unemployment Rate

# Standardise data across datasets
# Price data
month_start = []
month_end = pd.date_range(start, end, freq='M').strftime('%Y-%m-%d').tolist()
for x in month_end:
    month_start.append(start_of_month(x))
date_range = list(zip(month_start, month_end))
trading_month_start = []
trading_month_end = []
nyse = mcal.get_calendar('NYSE')
for k, v in date_range:
    nyse_trading_date_range = nyse.schedule(k, v)
    nyse_trading_date_range_index = mcal.date_range(nyse_trading_date_range, frequency='1D') \
        .strftime('%Y-%m-%d') \
        .tolist()
    trading_month_start.append(nyse_trading_date_range_index[0])
    trading_month_end.append(nyse_trading_date_range_index[-1])

# FRED data
INDPRO = INDPRO.loc[start:start_of_month(end), :]
RRSFS = RRSFS.loc[start:start_of_month(end), :]
UNRATE = UNRATE.loc[start:start_of_month(end), :]

# Calculate indicators
# Recession indicators
dataset = pd.DataFrame()
# Original GTT Model
conditions_original = [(INDPRO['INDPRO'].shift(1) < INDPRO['INDPRO'].shift(12)) &
                       (RRSFS['RRSFS'].shift(1) < RRSFS['RRSFS'].shift(12))]
choices_original = [1]
dataset['original'] = np.select(conditions_original, choices_original)
# Unemployment GTT Model
UNRATE['UnemploymentMA'] = UNRATE['UNRATE'].rolling(12).mean()
dataset['unemployment'] = np.where(UNRATE['UNRATE'] >= UNRATE['UnemploymentMA'], 1, 0)
dataset.index = trading_month_start

# Price indicators
prices['210MA'] = prices['SPY'].rolling(210).mean()
prices['indicator2'] = np.where(prices['SPY'] >= prices['210MA'], 1, 0)
prices_index = prices.index.to_list()
prices_index_dataset = []
for idx, val in enumerate(prices_index):
    for x in trading_month_start:
        if val.strftime('%Y-%m-%d') == x:
            prices_index_dataset.append(prices.iloc[[idx], [-1]])
result = np.reshape(prices_index_dataset, (np.shape(prices_index_dataset)[0], np.shape(prices_index_dataset)[1]))
result_df = pd.DataFrame(result, columns=['indicator2'])
result_df.index = trading_month_start
final_df = pd.concat([dataset, result_df], axis=1)

# Trading signals
# Signals for the Orginal GTT Model
conditions_signal1 = [(final_df['original'] == 1) & (final_df['indicator2'] == 1)]
conditions_signal2 = [(final_df['original'] == 1) & (final_df['indicator2'] == 0)]
final_df['signal_original'] = np.select(conditions_signal1, ['True'])
final_df['signal_original'] = np.select(conditions_signal2, ['False'])
final_df['signal_original'] = np.where(final_df['original'] == 0, 'True', 'False')
prices['signal_original'] = 0

# Signals for the Unemployment GTT Model
conditions_signal3 = [(final_df['unemployment'] == 1) & (final_df['indicator2'] == 1)]
conditions_signal4 = [(final_df['unemployment'] == 1) & (final_df['indicator2'] == 0)]
final_df['signal_unemployment'] = np.select(conditions_signal3, ['True'])
final_df['signal_unemployment'] = np.select(conditions_signal4, ['False'])
final_df['signal_unemployment'] = np.where(final_df['unemployment'] == 0, 'True', 'False')
prices['signal_unemployment'] = 0

# Signals dataset: final touches
nyse_trading_date_range = nyse.schedule(trading_month_start[0], trading_month_end[-1])
nyse_trading_date_range_index = mcal.date_range(nyse_trading_date_range, frequency='1D') \
    .strftime('%Y-%m-%d') \
    .tolist()
prices.drop(index=prices.index[0], axis=0, inplace=True)
final_df = final_df.reindex(nyse_trading_date_range_index, method='ffill')

# Strategy
prices['Tomorrows Returns'] = 0.
prices['Tomorrows Returns'] = np.log(prices['QQQ']/prices['QQQ'].shift(1))
prices['Tomorrows Returns'] = prices['Tomorrows Returns'].shift(-1)
prices['Market Returns'] = 0.
prices['Market Returns'] = np.log(prices['SPY']/prices['SPY'].shift(1))
prices['Market Returns'] = prices['Market Returns'].shift(-1)
prices['Original GTT Returns'] = 0.
prices['Original GTT Returns'] = np.where(final_df['signal_original'] == 'True', prices['Tomorrows Returns'], 0)
prices['Unemployment GTT Returns'] = 0.
prices['Unemployment GTT Returns'] = np.where(final_df['signal_unemployment'] == 'True', prices['Tomorrows Returns'], 0)
prices['Cumulative Market Returns'] = np.cumsum(prices['Market Returns'])
prices['Cumulative Original Strategy Returns'] = np.cumsum(prices['Original GTT Returns'])
prices['Cumulative Unemployment Strategy Returns'] = np.cumsum(prices['Unemployment GTT Returns'])
plt.figure(figsize=(10, 5))
plt.plot(prices['Cumulative Market Returns'], color='r', label='Market Returns')
plt.plot(prices['Cumulative Original Strategy Returns'], color='g', label='Original GTT Model Returns')
plt.plot(prices['Cumulative Unemployment Strategy Returns'], color='b', label='Unemployment GTT Model Returns')
plt.legend()
plt.show()

