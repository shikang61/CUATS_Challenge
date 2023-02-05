#region imports
from AlgorithmImports import *
#endregion

import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

def find_cointegrated_pairs(data: pd.DataFrame):
    # Input: DataFrame containing time series of symbols
    # Output: pvalues of each pair
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.05:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs
def OLS(S1: pd.Series, S2: pd.Series):
    # Ordinary least squares to calculate a hedge ratio b in order to calculate the spread
    name1 = S1.name
    name2 = S2.name
    keys = [name1,name2]
    #Removing na data
    df = pd.concat([S1,S2], axis=1, keys=keys).dropna(axis=0, how='any')
    S1 = df[name1]
    S2 = df[name2]

    S1 = sm.add_constant(S1)
    model = sm.OLS(S2,S1)
    results = model.fit()
    S1 = S1[name1]
    b = results.params[name1]
    spread = S2 - b*S1
    return spread
