# Template for the CUATS Coding Challenge
# 
# Start and end date: you may change these. Your algorithm will be tested against a random 7 year period between 1980-present
# Cash: do not change this
# fee and execution models: do not add a fee/execution model. Quantconnect defaults to using their standard fee/execution model
# leverage: you can use up to 10x leverage. You can set leverage globally as in this template with SetLeverage(x) or you can specify it for specific trades with SetHoldings("SPY", x)

# Got questions? Put them on the discussion page of this repo (https://github.com/CUATS/ChallengeCodingCompetition/discussions)


from AlgorithmImports import *

class MyTradingAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2010, 1, 1)    #Set Start Date
        self.SetEndDate(2021, 11, 27)    #Set End Date
        self.SetCash(100000)             #Set Strategy Cash

    def OnSecuritiesChanged(self, changes):
        for security in changes.AddedSecurities:
            security.SetLeverage(10)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. 
        Each new data point will be pumped in here.'''
        pass 
