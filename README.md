# CUATS_Challenge

Team name: Wolves of Wall Street 


Challenge statement:
Starting with a cash balance of **$100,000**, develop a trading algorithm that achieves a **positive alpha** with the **highest Sharpe ratio (minimum of 1.00)**, the **maximum profit**, and a **maximum drawdown of 20%**.  The trading strategy should be **backtestable over any 7 year period from 1 January 1980** to the present and benchmarked against the **S&P 500 Index**.  You may use any tradable instrument across all assets of the **US markets** available on QuantConnect in constructing your trading strategy.  (Strategies that use Crypto assets will be benchmarked against Bitcoin)

Note: A template code will be provided on the CUATS GitHub including the default QuantConnect standard execution model and fees structure as well as maximum leverage limit of 10 -  similar to what has been used in our example strategies from the CUATS Coding Sessions. 

**<ins> Competition Details </ins>**

Code Submission Deadline: **Saturday, 28 January 2023, 17:00**

Submission of code and documentation to: _cuats.challenge@gmail.com_

**<ins> Plan </ins>**

Step 1: Start by completing the QuantConnect Bootcamp. https://quantconnect.com/learning This will give you a good handle on the QuantConnect platform and a familiarity with its syntax

Step 2: Then look at the coding strategies on CUATS's GitHub https://github.com/CUATS we have presented in past coding sessions. This will give you an idea of how the algorithms are organised and the logic for implementing algorithms in QuantConnect

Step 3: Conduct (non-exhaustive) research to ascertain what trading types of strategies are being pursued currently and what the key assumptions and challenges are

Step 4: Think about what market anomaly you want to exploit and start testing ideas for trading them using the template QuantConnect code provided. This will give you sense of whether the strategy a) works, and b) is implementable.

Step 5: Backtest the strategy over several 7 year periods from 1980 to the present. Your strategy should not be designed to work only during a specific 7 year period within this timeframe, it should work across all 7 year periods within this time period range. Use Resolution.Daily for the tick size to run backtests quickly and efficiently debug your algorithms.
