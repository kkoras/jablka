import pandas as pd
import numpy as np

def pair_wise_spread(df1, df2):
    """ Calculates spread between prices on two different markets"""
    return max(df1.bid-df2.ask, df2.bid-df1.ask)  

def markets_with_highest_spread(list_of_markets):
    """Returns two markets having maximum pair-spread at given moment and correspodning spread"""
    current_max=-200.
    max_market1_idx=0
    max_market2_idx=0
    for i in range(len(list_of_markets)):
        for j in range(len(list_of_markets)):
            current_spread=pair_wise_spread(list_of_markets[i], list_of_markets[j])
            if current_spread>current_max:
                current_max=current_spread
                max_market1_idx=i
                max_market2_idx=j
                
    return max_market1_idx, max_market2_idx, current_max   

def markets_with_best_spread(list_of_markets, X):
    """Searches for two markets that meet the spread treshold"""
    market1_idx = 0
    market2_idx = 0
    for i in range(len(list_of_markets)):
        for j in range(len(list_of_markets)):
            spread=pair_wise_spread(list_of_markets[i], list_of_markets[j])
            if spread>X:
                return i, j, spread
                
    return None

    

def apples_bought_open_long(market, capital):
    """Returns amount of (virtual) apples bought at an opening transaction price (Ask), given invested capital""" 
    return capital/market.ask 

def dollars_earned_opening_short(market, apples):
    """ Returns dollars earned by opening short (selling virtual apples)"""
    return apples*market.bid

def dollars_spent_closing_short(market, apples):
    """Returns money spent on closing (buying) previously opened short position"""
    return apples*market.ask 

def dollars_earned_closing_long(market, apples):
    """Returns money earned by closing (selling) previously opened long position"""
    return apples*market.bid

def search_for_opportunity_open(list_of_markets, X):
    """Searches for arbitrage opportunity to open transactions"""
    max_market1_idx, max_market2_idx, max_spread=markets_with_highest_spread(list_of_markets)
    if max_spread >= X:
        return max_market1_idx, max_market2_idx, max_spread
    else:
        return None  
    
    
def identify_short_and_long_markets(market1_idx, market2_idx, market_list):
    """Given markets with highest spread, returns which market dedicated for long position, and market dedicated
    for short position"""
    if market_list[market1_idx].ask < market_list[market2_idx].bid:
        long_market_idx, short_market_idx = market1_idx, market2_idx
    else:
        long_market_idx, short_market_idx = market2_idx, market1_idx
    return long_market_idx, short_market_idx   

def close_opportunity(long_market_idx, short_market_idx, Y, market_list):
    """Returns True if there is a opportunity to close, False otherwise"""
    close_spread=market_list[long_market_idx].bid - market_list[short_market_idx].ask
    if close_spread >= Y:
        return True
    return False   

    
    
def arbitrage_strategy(market_list, X, Y, time_to_close, long_ratio, start_capital=1000., display_logs=False):
    """Implements arbitrage algorithm"""
    #Initializing variables
    current_capital=start_capital
    moment=0
    look_for_short=True   #Checking if we are during arbitrage
    time_in_arbitrage=0   #Time in which we are in arbitrage, measured in ticks
    while moment < (market_list[0].shape[0] -1):
        #Price data from all markets at given time
        markets_at_moment=[market.iloc[moment, :] for market in market_list]
        
        if look_for_short:
            #Checking if there is an opportunity for opening transactions
            if markets_with_best_spread(markets_at_moment, X):
                if display_logs:
                    print "Opening positions at moment {}".format(moment)
                #If there is, identify the best pair
                max_market1, max_market2, max_spread = markets_with_best_spread(markets_at_moment, X)
                
                #Identyfing long and short markets
                long_market, short_market=identify_short_and_long_markets(max_market1, max_market2, markets_at_moment)
                
                #Capital calculations related to opening positions. Keeping things simple: every transaction (opening and closing, long and
                #short) will be conducted in separate calculation
                money_invested_in_long=current_capital*long_ratio
                
                #Buying (opening long position)
                apples=apples_bought_open_long(markets_at_moment[long_market], money_invested_in_long)
                current_capital = current_capital - money_invested_in_long
                
                #Selling (opening short position)
                dollars_earned_on_short = dollars_earned_opening_short(markets_at_moment[short_market], apples)
                current_capital = current_capital + dollars_earned_on_short
                
                #Now we are done with opening calculations
                look_for_short = False
                time_in_arbitrage=1
                moment+=1   #Advancing time, we assume that we cannot close position in the same moment in which we opened them
                continue    #Skipping rest of the iteration
            else:
                #If we are looking for opening opportunity, but there isn't one good enough
                moment+=1
                continue   #Skipping rest of the iteration
        
        if not look_for_short:    #That means we are during arbitrage
            #Checking is there a good opportunity to close or did we exceed time limit Y
            
            if (close_opportunity(long_market, short_market, Y, markets_at_moment)) or (time_in_arbitrage > time_to_close):
                #Calculations related to closing positions
                if display_logs:
                    print "Closing positions at moment {}".format(moment)
                    print ""
                
                #Closing (buying back) short
                dollars_spent_on_closing_short = dollars_spent_closing_short(markets_at_moment[short_market], apples)
                current_capital = current_capital - dollars_spent_on_closing_short
                
                #Closing (selling) long
                dollars_earned_on_closing_long = dollars_earned_closing_long(markets_at_moment[long_market], apples)
                current_capital = current_capital + dollars_earned_on_closing_long
                
                #If we closed recently opened positions we can look for next opening positions
                time_in_arbitrage = 0
                look_for_short = True
                moment+=1
            
            else:
                #If we did not exceed time limit, but there is no good opportunity at the moment
                time_in_arbitrage+=1
                moment+=1
    
    #Outside the loop; when we reach the final record
    if look_for_short:
        #If we are in open-opportunities mode we do nothing since we will not be able to close any transaction
        pass
    else:
        #If we have currently open positions we close them
        if display_logs:
            print "Closing positions at moment {}".format(moment)
        
        dollars_spent_on_closing_short = dollars_spent_closing_short(markets_at_moment[short_market], apples)
        current_capital = current_capital - dollars_spent_on_closing_short
                
        dollars_earned_on_closing_long = dollars_earned_closing_long(markets_at_moment[long_market], apples)
        current_capital = current_capital + dollars_earned_on_closing_long
    
    #Finally, we return our capital after performing the strategy
    return current_capital

def two_step_strategy(market_list, X, Y, time_to_close, long_ratio, start_capital=1000., display_logs=False):
    """Allows to perform strategy on all given data (using targ6 in the first period as well)"""
    
    #Step one
    market_list_first=[df.iloc[:659, :] for df in market_list]
    capital_after_step1=arbitrage_strategy(market_list_first, X, Y, time_to_close, long_ratio, 
                                           start_capital, display_logs)
    
    #Step two
    market_list_second = [df.iloc[659:, :] for df in market_list if df.shape[0] != 659]
    capital_after_step_two = arbitrage_strategy(market_list_second, X, Y, time_to_close, long_ratio,
                                               capital_after_step1, display_logs)
    
    return capital_after_step_two

def grid_search(param_grid, market_list, start_capital, data_piece=100000, display_progress=False):
    """ Brute force search for best parameters, param_grid is a dictionary in form (parameter: values_to_consider).
    Since we use nested loops, we assume parameters are independent"""
    counter=1
    market_list=[df.iloc[:data_piece, :] for df in market_list]
    current_max_capital=0
    for X in param_grid["X"]:
        for Y in param_grid["Y"]:
            for time_to_close in param_grid["time_to_close"]:
                for long_ratio in param_grid["long_ratio"]:
                    current_end_capital = arbitrage_strategy(market_list, X, Y, time_to_close, long_ratio, 
                                                            start_capital ,display_logs=False)
                    if current_end_capital > current_max_capital:
                        current_max_capital = current_end_capital
                        best_params = (X, Y, time_to_close, long_ratio)
                    if display_progress:
                        print "{} combinations checked".format(counter)
                        print "Best capital so far: {}".format(current_max_capital)
                        print ""
                        counter+=1
                            
                            
    print "Best params: X: {}, Y: {}, time_to_close: {}, long_ratio: {}".format(best_params[0],
                                                                               best_params[1],
                                                                               best_params[2],
                                                                               best_params[3])
    print "Best end capital: {}".format(current_max_capital)
    return best_params, current_max_capital

    
#**************************************************************************
#Execution part

#Loading all seven files
targ1=pd.read_csv("targowisko-1.csv", sep=";", parse_dates=["Datetime"])
targ2=pd.read_csv("targowisko-2.csv", sep=";", parse_dates=["Datetime"])
targ3=pd.read_csv("targowisko-3.csv", sep=";", parse_dates=["Datetime"])
targ4=pd.read_csv("targowisko-4.csv", sep=";", parse_dates=["Datetime"])
targ5=pd.read_csv("targowisko-5.csv", sep=";", parse_dates=["Datetime"])
targ6=pd.read_csv("targowisko-6.csv", sep=";", parse_dates=["Datetime"])
targ7=pd.read_csv("targowisko-7.csv", sep=";", parse_dates=["Datetime"])


search_for_best_params = False     #Change to True if you want to run parameter search
if search_for_best_params:
    market_list=[targ1, targ2, targ3, targ4, targ5, targ7]
    param_grid={"X": [1+20*i for i in range(10)],
               "Y": [-199 +i*20 for i in range(10)],
               "time_to_close": [10000],
               "long_ratio": [0.5]}

    best_params, best_capital=grid_search(param_grid, market_list, 1000., data_piece=10000, display_progress=True)
    print best_params
    print best_capital

#Setting parameters
X = 81.     #Inter-market spread treshold for opening transactions
Y=-75.      #Inter-market spread treshold for closing transactions
time_to_close=10000     #Time after which we close opened transactions, even if there is no good opportunity
long_ratio=0.5         #Ratio of capital invested in long position
    
market_list=[targ1, targ2, targ3, targ4, targ5, targ6, targ7]
end_capital=two_step_strategy(market_list, 81, -75., 10000, 0.5, display_logs=True)

print "Implementing strategy..."
print "Capital after performing the algorithm: {}".format(end_capital)




