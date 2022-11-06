from tvDatafeed import TvDatafeed, Interval
import numpy as np
import pandas as pd
import pandas_ta as ta
import streamlit as st

def FEMUR():
    Forex_Pairs_List = ["EURUSD","USDJPY","GBPUSD","AUDUSD","USDCHF","NZDUSD","USDCAD",
                       "EURJPY","EURGBP","EURAUD","EURCHF","EURNZD","EURCAD",
                       "GBPJPY","CHFJPY","NZDJPY","AUDJPY","CADJPY",
                       "GBPAUD","AUDCHF","AUDNZD","AUDCAD",
                       "GBPCHF","NZDCHF","CADCHF",
                       "GBPNZD","GBPCAD",
                       "NZDCAD"]

    Final_df = pd.DataFrame()

    username = 'Azreal1'
    password = 'Mynameisdhruv123!@#'

    tv = TvDatafeed(username, password)

    for Currency_Pair in Forex_Pairs_List:
        Symbol_String = Currency_Pair
        Currency_Pair = tv.get_hist(symbol = 'FX:{}'.format(Currency_Pair), exchange = 'FXCM',
                                    interval = Interval.in_1_hour, n_bars = 100)
        #Stochastic
        Stoch = round(ta.stoch(high = Currency_Pair["high"], low = Currency_Pair["low"], 
                               close = Currency_Pair["close"], window = 14, smooth_window = 3),2)
        Currency_Pair["Stochastic %K"] = Stoch["STOCHk_14_3_3"]
        Currency_Pair["Stochastic %D"] = Stoch["STOCHd_14_3_3"]
        #Heiken Ashi
        if Symbol_String[-3:] == "JPY":
            Rounding = 3
        else:
            Rounding = 5
        Heiken_Ashi = round(ta.ha(Currency_Pair["open"], high = Currency_Pair["high"], 
                                  low = Currency_Pair["low"], close = Currency_Pair["close"]),Rounding)
        Currency_Pair["Heiken Ashi Open"] = Heiken_Ashi["HA_open"]
        Currency_Pair["Heiken Ashi High"] = Heiken_Ashi["HA_high"]
        Currency_Pair["Heiken Ashi Low"] = Heiken_Ashi["HA_low"]
        Currency_Pair["Heiken Ashi Close"] = Heiken_Ashi["HA_close"]

        #Heiken Ashi Bool
        Heiken_Ashi_Boolean = []

        i = 0
        while i < Currency_Pair.shape[0]:
            if (Currency_Pair["Heiken Ashi Close"][i] - Currency_Pair["Heiken Ashi Open"][i]) >= 0:
                Heiken_Ashi_Boolean.append(1)
            elif(Currency_Pair["Heiken Ashi Close"][i] - Currency_Pair["Heiken Ashi Open"][i]) < 0:
                Heiken_Ashi_Boolean.append(0)
            i+=1
        Currency_Pair["Heiken Ashi Boolean"] = Heiken_Ashi_Boolean
        Currency_Pair = Currency_Pair.iloc[15:,:]
        
        # Peak swing high and low calculations
        Peak_Value = []
        Peak_Stochastic_Value = []
        Peak_Value_List = list()
        Peak_Stochastic_Value_List = list()
        Peak_Value_List = [np.nan]*Currency_Pair.shape[0]
        Peak_Stochastic_Value_List = [np.nan]*Currency_Pair.shape[0]

        i = 0

        while i < Currency_Pair.shape[0] - 1:
            if Currency_Pair["Heiken Ashi Boolean"][i] == 1 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 0:
                Peak_Value.append(Currency_Pair["close"][i])
                Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][i])
                j = i
                while Currency_Pair["Heiken Ashi Boolean"][j] == 1:
                    Peak_Value.append(Currency_Pair["close"][j])
                    Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][j])
                    j-=1
                Max_Value = max(Peak_Value)
                Max_Stochastic_Value = max(Peak_Stochastic_Value)
                Peak_Value = []
                Peak_Stochastic_Value = []
                Peak_Value_List[i+1] = Max_Value
                Peak_Stochastic_Value_List[i+1] = Max_Stochastic_Value
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 0 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 1:
                Peak_Value.append(Currency_Pair["close"][i])
                Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][i])
                j = i
                while Currency_Pair["Heiken Ashi Boolean"][j] == 0:
                    Peak_Value.append(Currency_Pair["close"][j])
                    Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][j])
                    j-=1
                Min_Value = min(Peak_Value)
                Min_Stochastic_Value = min(Peak_Stochastic_Value)
                Peak_Value = []
                Peak_Stochastic_Value = []
                Peak_Value_List[i+1] = Min_Value
                Peak_Stochastic_Value_List[i+1] = Min_Stochastic_Value
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 1 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 1:
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 0 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 0:
                i+=1

        Currency_Pair["Peak Value"] = Peak_Value_List
        Currency_Pair["Stochastic Peak Value"] = Peak_Stochastic_Value_List

        Swing_High_Recent = np.nan
        Stochastic_High_Recent = np.nan
        Swing_Low_Recent = np.nan
        Stochastic_Low_Recent = np.nan

        Looking_For_Shorts = np.nan
        Looking_For_Longs = np.nan

        Divergence_List = list()
        Divergence_List = [np.nan]*Currency_Pair.shape[0]

        i = 0

        while i < Currency_Pair.shape[0] - 1:
          if (pd.isna(Currency_Pair["Peak Value"][i]) == False and Currency_Pair["Heiken Ashi Boolean"][i] == 1):
              Swing_Low_Recent = Currency_Pair["Peak Value"][i]
              Stochastic_Low_Recent = Currency_Pair["Stochastic Peak Value"][i]
              Looking_For_Shorts = True
              Looking_For_Longs = False
              i+=1
          elif (pd.isna(Currency_Pair["Peak Value"][i]) == False and Currency_Pair["Heiken Ashi Boolean"][i] == 0):
              Swing_High_Recent = Currency_Pair["Peak Value"][i]
              Stochastic_High_Recent = Currency_Pair["Stochastic Peak Value"][i]
              Looking_For_Shorts = False
              Looking_For_Longs = True
              i+=1
          if (pd.isna(Swing_High_Recent) == False and pd.isna(Swing_Low_Recent) == False):
            if (Looking_For_Shorts == True):
              if(Currency_Pair["close"][i] >= Swing_High_Recent and Currency_Pair["Stochastic %K"][i] <= Stochastic_High_Recent):
                Divergence_List[i] = "Regular Divergence Short"
                i+=1
              elif(Currency_Pair["close"][i] <= Swing_High_Recent and Currency_Pair["Stochastic %K"][i] >= Stochastic_High_Recent):
                Divergence_List[i] = "Hidden Divergence Short"
                i+=1
              else:
                i+=1
            elif (Looking_For_Longs == True):
                if(Currency_Pair["close"][i] <= Swing_Low_Recent and Currency_Pair["Stochastic %K"][i] >= Stochastic_Low_Recent):
                  Divergence_List[i] = "Regular Divergence Long"
                  i+=1
                elif(Currency_Pair["close"][i] >= Swing_Low_Recent and Currency_Pair["Stochastic %K"][i] <= Stochastic_Low_Recent):
                  Divergence_List[i] = "Hidden Divergence Long"
                  i+=1
                else:
                  i+=1
          else:
            i+=1

        Currency_Pair["Divergence"] = Divergence_List

        Final_df = pd.concat([Final_df , Currency_Pair.iloc[[-2]]])
    Final_df = Final_df.drop(["open","high","low","close","volume","Heiken Ashi Open","Heiken Ashi High","Heiken Ashi Low","Heiken Ashi Close"
    ,"Heiken Ashi Boolean","Stochastic %K","Stochastic %D","Peak Value","Stochastic Peak Value"], axis = 1)
    return Final_df

st.title("Welcome to Azreal")

st.header("What is Azreal?")
st.markdown("Azreal is a Web based application created by Dhruv Suresh which helps users make better investment decisions. Azreal has 2 constituents to it namely the Forex Matrix and the Mutual Fund Matrix. They will be explained in detail in the descriptions down below.")

st.header("About the Forex Matrix")
st.markdown("The Forex Matrix is a screener in which currency data from all 28 majorly traded spot currencies and crosses is extracted on an hourly time frame. It then uses various technical analysis methods employed from my own personal trading strategy involving Heiken Ashi, Stochastic and Divergence indicators to provide alerts and notifies the user when there is a potential setup being formed.")
st.markdown("Once the Generate button is clicked, the last 1000 bars of data for each pair are pulled and the result is given in the Divergence column whether to look for shorts or longs. All setups are not treated the same and it is upto the discretion of the trader for the timing of the entries.")
st.markdown("Explained simply, the strategy uses Heiken Ashi to identify major swing highs and lows and tries to find scenarios where the Stochastic indicator and the swing high/low points are in disagreement or in divergence from each other.")
st.markdown("Detailed examples of Divergence setups can be found on babypips.com. Divergence is mainly a reversal as well as continuation indicator and hence must be used sparingly especially in their respective market conditions. It is my suggestion to filter out entries using a trend filter such as the 100/200 EMA to develop a directional bias and trade only in that direction.")

if st.button("Generate Forex Matrix"):
  Output = FEMUR()
  st.dataframe(Output,height = 1050,width = 500)

st.header("About the Mutual Fund Matrix")

st.markdown("Mutual Funds are deemed to be one of the most safe investments based on popular opinion. A consistent monthly investment strategy devoting 10-20% of monthly income (varies from person to person) parked in a good performing mutual fund could yield very promising returns in the long run.")
st.markdown("However with the advent and advancement of the finance and technology domain, there is a huge influx of funds and a plethora to choose from which can be very daunting to the consumer. Azreal's Mutual Fund Matrix aims to tackle this issue and recommend the best funds based off of histoical performance.")
st.markdown("Azreal's Mutual Fund matrix pulls all existing historical data for every mutual fund listed by the The Association of Mutual Funds in India (AMFI). It then calculates various parameters such as the 3 and 5 year return, standard deviation of yearly returns etc. Now having these various parameters Azreal determines which fund has provided the most consistent returns with the least amount of risk.")
st.markdown("Since the data extraction process is very time consuming, I have saved the final findings as of September 2022 in a google sheet document which can be accessed by clicking on the Generate Link button below. The Rank sheet contains the final ranking having best to worst ranked top to down in that order. Kindly go into the Data tab to see more details about the funds historical performance.")
st.markdown("** Historical performance does not guarantee future performance. Please read all scheme related documents carefully before investing.")

if st.button("Mutual Fund Matrix Link"):
  url = 'https://docs.google.com/spreadsheets/d/1tUmm4rh-BH53wd8d5xCug9OSYMxqd6CB/edit?usp=sharing&ouid=102568847951223378739&rtpof=true&sd=true'
  st.markdown(f'''<{url}></button>''',unsafe_allow_html=True)

st.markdown("** Please do your own due diligence before investing. This is not financial advice.")
