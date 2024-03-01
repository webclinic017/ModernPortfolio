# -*- coding: utf-8 -*-


"""

 ________  ___  ___  ________  ________  ___  ________  _______   ________  ___  _________  ________
 |\   ____\|\  \|\  \|\   ____\|\   ____\|\  \|\   __  \|\  ___ \ |\   __  \|\  \|\___   ___\\   __  \
 \ \  \___|\ \  \\\  \ \  \___|\ \  \___|\ \  \ \  \|\  \ \   __/|\ \  \|\  \ \  \|___ \  \_\ \  \|\  \
  \ \  \  __\ \  \\\  \ \  \    \ \  \    \ \  \ \   ____\ \  \_|/_\ \   ____\ \  \   \ \  \ \ \  \\\  \
   \ \  \|\  \ \  \\\  \ \  \____\ \  \____\ \  \ \  \___|\ \  \_|\ \ \  \___|\ \  \   \ \  \ \ \  \\\  \
    \ \_______\ \_______\ \_______\ \_______\ \__\ \__\    \ \_______\ \__\    \ \__\   \ \__\ \ \_______\
     \|_______|\|_______|\|_______|\|_______|\|__|\|__|     \|_______|\|__|     \|__|    \|__|  \|_______|

"""



# import librairies
from pypfopt import EfficientFrontier # pip install pyportfolioopt
from pypfopt import risk_models 
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import pandas as pd # pip install pandas
import numpy as np # pip install numpy
import yfinance as yf # pip install yfinance
import matplotlib.pyplot as plt # pip install matplotlib


# importatation des data
tickers = ['ENB', 'BABA', 'MSFT', 'NFLX', 'JPM', 'SQSP', 'ATD.TO']
start = '2018-12-31'
end = '2023-12-31' # exemple est des données sur 5 ans
prices_df= yf.download(' '.join(tickers), start, end)['Adj Close']
returns_df = prices_df.pct_change()[1:]

# Parameters for plotting by default
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)
fig.savefig('test2png.png', dpi=100)

#-- Visually show the stock/portfolio
title = 'Stocks Performance'
#-- Get the stocks
my_stocks = prices_df
#-- Create and plot the graph
for c in my_stocks.columns.values:
    plt.plot(my_stocks[c], label = c)

plt.title(title)
plt.xlabel('Date (Years)', fontsize = 10)
plt.ylabel('Price USD(Adj Close)', fontsize = 10)
plt.legend(my_stocks.columns.values, loc='upper left')
plt.grid(axis = 'y')
plt.show()

plt.figure(figsize=(18.5, 10.5))
for i in returns_df.columns.values:
    plt.plot(returns_df.index, returns_df[i], lw=2, alpha=0.8,label=i)
plt.legend(loc='lower center', fontsize=10)
plt.ylabel('daily returns')
plt.title('Performance per Stock')
plt.xlabel('Date (Years)', fontsize = 10)
plt.ylabel('Change (%)', fontsize = 10)
plt.grid(axis = 'y')
plt.legend()

# return vector & covariance matrix
r = ((1+returns_df).prod( ))**(252/len(returns_df)) - 1 # annuel returns
cov = returns_df.cov()*252 # covariance matrix
e = np.ones(len(r)) # vector of one equal to the number of stocks
mu = expected_returns.mean_historical_return(prices_df)
S = risk_models.sample_cov(prices_df)
ef = EfficientFrontier(mu, S)
raw_weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
latest_prices = get_latest_prices(prices_df)

weights = cleaned_weights
da = DiscreteAllocation(weights, latest_prices, total_portfolio_value = 10000) #portfolio_value
allocation, leftover = da.greedy_portfolio()

# define investable universe & risk return optimazation facets of efficient portfolio tm and modern portfolio theory
icov = np.linalg.inv(cov) # inverse covariance matrix
h = np.matmul(e, icov) # h vector
g = np.matmul(r, icov) # g vector
a = np.sum(e*h)
b = np.sum(r*h)
c = np.sum(r*g)
d = a*c - b**2

# minimum tagency portfolio and variance
mvp = h/a
mvp_returns = b/a
mvp_risk = (1/a)**(1/2)

tagency = g/b
tagency_returns = c/b
tagency_risk = c**(1/2)/b

# plotting efficient frontiere
exp_returns = np.arange(-0.001, 0.801,0.001)
risk = ((a*exp_returns**2 - 2*b*exp_returns + c)/d)**(1/2)

plt.plot(risk, exp_returns, linestyle = 'dotted', color = 'b')
plt.scatter(mvp_risk, mvp_returns, marker = '*', color = 'r')
plt.scatter(tagency_risk, tagency_returns, marker = '*', color = 'g')
plt.title("Efficient Frontiere")
plt.xlabel("Standar Deviation")
plt.ylabel("Expected Return")
plt.grid(axis = 'y')
plt.legend(["Efficient Frontiere", "Efficient portfolio with minimum volatility", "Optimal risky portfolion"], loc ="lower right")

# ploting securities market line
SML_slope = 1/c**(1/2)
SML_risk = exp_returns*SML_slope
plt.plot(risk, exp_returns, color = 'b', linestyle = 'dotted')
plt.plot(SML_risk, exp_returns, color ='r', linestyle = 'dashdot')
plt.scatter(mvp_risk, mvp_returns, marker = '*', color = 'r')
plt.scatter(tagency_risk, tagency_returns, marker = '*', color = 'g')
plt.title("Efficient Frontiere & Securities Market Line")
plt.xlabel("Standar Deviation")
plt.ylabel("Expected Return")
plt.grid(axis = 'y')
plt.legend(["Efficient Frontiere", "Securities Market Line (SML)", "Efficient portfolio with minimum volatility", "Optimal risky portfolio"], loc ="lower right")

# solving the target return problem
target_return = 0.5
if target_return < mvp_returns:
  optimal_portfolio = mvp
  optimal_return = mvp_returns
  optimal_risk = mvp_risk
else:
  l = (c - b*target_return)/d
  m = (a * target_return - b)/d
  optimal_portfolio = l*h + m*g
  optimal_return =  np.sum(optimal_portfolio*r)
  optimal_risk = ((a*optimal_return**2 - 2*b*optimal_return + c)/d)**(1/2)

print(optimal_portfolio, optimal_return, optimal_risk)

ef.portfolio_performance(verbose = True)

print("Cleaned Weights:",cleaned_weights)
print("Discrete allocation:", allocation)
print("Funds remaining: ${:.2f}".format(leftover),"CAD")

'''
Usually, any Sharpe ratio greater than 1.0 is considered acceptable to good by investors.
A ratio higher than 2.0 is rated as very good.
A ratio of 3.0 or higher is considered excellent.
A ratio under 1.0 is considered sub-optimal.
'''

# ------------------------------------------------------------------------------------------------------------------#
