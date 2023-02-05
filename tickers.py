#region imports
from AlgorithmImports import *
#endregion
def ExtractTickersFromIndustry(sr, industry):
    return list(sr[sr.Industry == industry].Symbol.values)

def FilterByIndustrySize(sr, size=(25,50)):
    industries_series = sr.value_counts("Industry")
    industries = list(industries_series.keys())

    selected_industries = industries_series[(industries_series >= size[0]) & (industries_series <= size[1])]

    bar = {} # Mapping of industry to tickers in that industry
    for industry in selected_industries.keys():
        bar[industry] = ExtractTickersFromIndustry(sr, industry)
    return bar
