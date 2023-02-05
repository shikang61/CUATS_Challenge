#region imports
from AlgorithmImports import *
#endregion
# https://quantpedia.com/Screener/Details/12

import numpy as np
import pandas as pd
import random
from io import StringIO
from helper import *
from tickers import *

def SymbolSelection(algo):
    algo.symbols = []
    for ticker in algo.selected_tickers:
        symbol = algo.AddEquity(ticker, Resolution.Hour).Symbol
        hist = algo.History([ticker], algo.formation_period, Resolution.Daily)
        if hist.empty: # This probably means the ticker hasn't existed yet, banish!
            algo.RemoveSecurity(symbol) 
            algo.Log(f"Excluded {ticker} from algo.symbols")
            continue
        elif len(hist) < algo.formation_period: # History requests truncate trailing NAs, so we need to test for length 252, rather than for NAs present
            algo.RemoveSecurity(symbol)
            algo.Log(f"Excluded {ticker} from algo.symbols")
            continue
        else:
            # The following tickers are complete within the daterange    
            # Populating a dictionary of rolling windows of historical prices from the past 252 days
            algo.symbols.append(symbol)
            algo.history_price[symbol] = RollingWindow[float](algo.formation_period)
            for close_price in hist.close.T:
                algo.history_price[symbol].Add(close_price)
    # Upon return, self.symbols should have no NA data for the given formation period. 
        
    #elif hist.close.isnull().values.any() # this is the code to test for NAs in between, not trailing, but we filled forward

def PairSelection(algo):
    # Input: The algorithm object algo
    # Side effects: Resets algo.sorted_pairs to empty, then mutates and updates the list for the upcoming year
    algo.sorted_pairs = []
    adfullerlist = []   
    history = algo.History(algo.symbols, algo.formation_period, Resolution.Daily) # DataFrame containing all time series of all symbols         
    if not history.empty:
        df = history.close.unstack().T
        score_matrix, pvalue_matrix, pairs = find_cointegrated_pairs(df)  
        for pair in pairs:
            S1 = df[pair[0]]
            S2 = df[pair[1]]
            spread = OLS(S1,S2)        
            pval = adfuller(spread)[1]
            if pval <= 0.05:
                adfullerlist.append((algo.Symbol(S1.name), algo.Symbol(S2.name), pval))
        algo.sorted_pairs = sorted(adfullerlist, key=lambda x: x[2],)[:algo.pair_count] # the pairs with the lowest p-value


class PairsTradingAlgorithm(QCAlgorithm):
    
    def Initialize(self):
        lower = 1998
        a = random.randint(lower,2016)
        self.SetStartDate(a,1,1)
        self.SetEndDate(a+7,1,1)
        # self.SetStartDate(2012,1,1)
        # self.SetEndDate(2019,1,1)
        self.Debug(f"Start Date: {self.StartDate}")
        self.Debug(f"End Date: {self.EndDate}")
        self.SetCash(100000)

        # n_std for position taking/exiting
        self.threshold = float(self.GetParameter("threshold"))
        self.stoploss = float(self.GetParameter("stoploss"))
        self.takeprofit = float(self.GetParameter("takeprofit"))
        self.direction = None # 1 for above mean and 0 for below mean
        
        # Counter for rebalancing
        self.count = 0
        self.rebalance_period = int(self.GetParameter("rebalance_period"))

        # Pair selection
        self.symbols = []
        self.formation_period = int(self.GetParameter("formation_period"))
        self.pair_count = int(self.GetParameter("pair_count"))

        # Rolling windows
        self.history_price = {} #key: symbol, value: rolling window[float](252) containing close prices

        # Tracking orders
        self.orders = {} #key:pair, value: tuple of tickets 

        # Import tickers from NASDAQ Screener and filtering
        content = self.Download(address="https://raw.githubusercontent.com/shikang61/CUATS_Challenge/main/nasdaq_screener_1675228934415.csv", )
        df = pd.read_csv(StringIO(content))

        # 1. Randomized industry
        industries_tickers = FilterByIndustrySize(df)
        selected_industry = random.choice(list(industries_tickers.items()))
        self.Debug(f"Industry: {selected_industry[0]}")
        self.selected_tickers = selected_industry[1]

        # OR 2. Select an particular industry        
        # self.selected_tickers = ExtractTickersFromIndustry(df, "Biotechnology: Electromedical & Electrotherapeutic Apparatus")
        # self.selected_tickers = ExtractTickersFromIndustry(df, 'Farming/Seeds/Milling')
        # industry = 'Air Freight/Delivery Services'
        # self.selected_tickers = ExtractTickersFromIndustry(df, industry)
        # self.Debug(f"Industry: {industry}")
        

        # Do not include any tickers in self.symbols if they contain NaN in the past one year from the start date
        # Later on we will further remove tickers from self.symbols if we encounter a NaN. 
        # This is neccessary as the coint, OLS, adfuller routines cannot handle NaNs. 
        SymbolSelection(self)

        # Populate sorted_pairs initially
        PairSelection(self)

        # Add the benchmark
        self.SetBenchmark("SPY")
        self.Schedule.On(self.DateRules.MonthStart(), self.TimeRules.At(9,30), self.Rebalance)
            

    def OnData(self, data:Slice):
        # Update the price series everyday
        for symbol in self.symbols:
            if symbol in data and symbol in self.history_price:
                if data[symbol]:
                    self.history_price[symbol].Add(float(data[symbol].Close)) 
            else:
                self.history_price[symbol].Add(self.history_price[symbol][0])
        
        if not self.sorted_pairs:
            return

        for i in self.sorted_pairs:
            if not self.history_price[i[0]].IsReady and not self.history_price[i[1]].IsReady:
                return

            # 1. Calculate the spread of each pair
            S1 = pd.Series(self.history_price[i[0]])
            S2 = pd.Series(self.history_price[i[1]])


            S1 = sm.add_constant(S1)
            model = sm.OLS(S2,S1)
            results = model.fit()         
            S1 = S1[0]
            b = results.params[0]
            spread = S2 - b*S1
            spread = list(spread) # So that we can keep the previous syntax below :(
            # for j,k in zip(self.history_price[i[0]], self.history_price[i[1]]):
            #     spread.append(j - k)
            mean = np.mean(spread)
            std = np.std(spread)

            # 2. Entering positions    
            if not self.orders.get(i):
                if spread[-1] > mean + self.threshold * std:
                    self.direction = 1
                    amount0 = self.CalculateOrderQuantity(i[0], 1/(3*len(self.sorted_pairs)))
                    amount1 = self.CalculateOrderQuantity(i[1], 1/(3*len(self.sorted_pairs)))
                    ticket0 = self.MarketOrder(i[0], -amount0)
                    ticket1 = self.MarketOrder(i[1], amount1)
                    self.orders[i] = (ticket0, ticket1)
                
                elif spread[-1] < mean - self.threshold * std:                
                    self.direction = -1
                    amount0 = self.CalculateOrderQuantity(i[0], 1/(3*len(self.sorted_pairs)))
                    amount1 = self.CalculateOrderQuantity(i[1], 1/(3*len(self.sorted_pairs)))
                    ticket1 = self.MarketOrder(i[1], -amount1)
                    ticket0 = self.MarketOrder(i[0], amount0)
                    self.orders[i] = (ticket0, ticket1)

            # 3. Exiting positions        
            else:
                if self.Portfolio[i[0]].Invested and self.Portfolio[i[1]].Invested:
                        # Stop loss
                        if self.direction == 1 and spread[-1] > mean + self.stoploss * std:
                            self.Buy(i[0], self.orders[i][0].Quantity)
                            self.Sell(i[1], self.orders[i][1].Quantity)
                        elif self.direction == -1 and spread[-1] < mean - self.stoploss * std:
                            self.Buy(i[1], self.orders[i][1].Quantity)
                            self.Sell(i[0], self.orders[i][0].Quantity)

                        # Take profit
                        elif self.direction == 1 and spread[-1] < mean + self.takeprofit * std:
                            self.Buy(i[0], self.orders[i][0].Quantity)
                            self.Sell(i[1], self.orders[i][1].Quantity)
                        elif self.direction == -1 and spread[-1] > mean - self.takeprofit * std:
                            self.Buy(i[1], self.orders[i][1].Quantity)
                            self.Sell(i[0], self.orders[i][0].Quantity)     


                    
    def Rebalance(self):
        # Schedule the event to fire every year to first redefine self.symbols, then select pairs
        if self.count % self.rebalance_period == 0:
            self.Log(f"New year: {self.Time.year}")
            self.Log(f"Liquidating all positions...")
            self.Liquidate()
            SymbolSelection(self)            
            PairSelection(self)
        self.count += 1 # Always runs to increment counter
