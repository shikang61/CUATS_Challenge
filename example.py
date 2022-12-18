# example algorithm for the CUATS coding challenge
# this is a very simple EMA strategy that you will have seen before in our workshops
# you can build your algorithm out from this example, but make sure to check template.py to see the parameters you can/cannot change

from AlgorithmImports import *

class MovingAverageCrossAlgorithm(QCAlgorithm):
    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end 
        dates for your algorithm. All algorithms must initialized.'''
        self.SetStartDate(2010, 1, 1)    #Set Start Date
        self.SetEndDate(2021, 11, 27)    #Set End Date
        self.SetCash(100000)             #Set Strategy Cash

        # add SPY to our portfolio
        self.AddEquity("SPY")
        # create a 50 day exponential moving average
        self.fast = self.EMA("SPY", 50, Resolution.Daily)
        # create a 200 day exponential moving average
        self.slow = self.EMA("SPY", 200, Resolution.Daily)
        # warm up the indicator (i.e. give it previous data)
        self.SetWarmUp(200)
        self.previous = None
    
    def OnSecuritiesChanged(self, changes):
        for security in changes.AddedSecurities:
            security.SetLeverage(10)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. 
        Each new data point will be pumped in here.'''
        # a couple things to notice in this method:
        #  1. We never need to 'update' our indicators with the data, the engine takes care of this for us
        #  2. We can use indicators directly in math expressions
        #  3. We can easily plot many indicators at the same time
        
        # Docs: https://www.quantconnect.com/docs/algorithm-reference/indicators
        
        # wait for our indicators to fully initialize
        if not self.slow.IsReady and not self.IsWarmingUp:
            return
        
        # only once per day
        if self.previous is not None and self.previous.date() == self.Time.date():
            return 
        
        # plot our indicators
        self.Plot("EMA", self.slow, self.fast)
        
        # define a small tolerance on our checks to avoid bouncing
        tolerance = 0.00015
        holdings = self.Portfolio["SPY"].Quantity
        
        # we only want to go long if we're currently short or flat
        if holdings <= 0:
            # if the fast is greater than the slow, we'll go long
            if self.fast.Current.Value > self.slow.Current.Value * (1 + tolerance):
                self.SetHoldings("SPY", 1.0)

        # we only want to liquidate if we're currently long
        # if the fast is less than the slow we'll liquidate our long
        if holdings > 0 and self.fast.Current.Value < self.slow.Current.Value:
            self.Liquidate("SPY")

        self.previous = self.Time
