# We have in essence two payoff structures here
# One is the payoff structure where a large number of people get significant rewards.
# While in the other structure, the top person gets 50-60 times the reward of the next prizes.
#Defing such payoffs are needed to analyse behaviours of agents and to make them play in various contests.
# We could also see whether people could switch between contest types to get consistent or large rewards.
import pandas as pd
import numpy as np
class Contest():
    def __init__(self,Agents_data):
        self.Agents_data=Agents_data
        self.Agents_Squad=None
        self.Agents_Ranked_with_Points=None
        #self.Agents_with_Payoff=None
        #self.Agents_Squad_With_My11Circle_Score=None
    def calculate_points(self,Team_access):
        for i in range(len(self.Agents_Squad)):
                self.Agents_Squad[i]["Score"]=0
                for team_player in self.Agents_Squad[i]["Agent Squad"]:
                    self.Agents_Squad[i]["Score"]+=Team_access[team_player["Match_Player_Stats"]["Team Name"]][team_player["Match_Player_Stats"]["Player Id"]]["My_11_Circle_Score"]*team_player["Multiplier"]   
        columns = ["My11Circle Agent ID","Agent Type Name", "Score"]
        mod = [{"My11Circle Agent ID":entry["My11Circle Agent ID"],"Agent Type Name":entry["Agent Type Name"],"Score": entry["Score"]} for entry in self.Agents_Squad]
        Player_df=pd.DataFrame(mod,columns=columns)
        Player_df["Rank"]=Player_df.rank(axis=0,method="first",ascending=False)["Score"]
        self.Agents_Ranked_with_Points=Player_df
class Large_Spread_Payoff_Contest (Contest):
    def __init__(self,Agents_data):
        super().__init__(Agents_data)
    EntryFee=500
    
    Prizes= {
    tuple([1]): [50000],   # 1st place gets ₹50,000
    tuple([2]): [10000],   # 2nd place gets ₹10,000
    tuple([3]): [5000],    # 3rd place gets ₹5,000
    tuple([4]): [2000],    # 4th place gets ₹2,000
    tuple([5]): [1000],    # 5th place gets ₹1,000
    tuple(range(6, 11)): [800] * 5,    # 6-10 get ₹800 each
    tuple(range(11, 26)): [625] * 15,  # 11-25 get ₹625 each
    tuple(range(26, 51)): [575] * 25,  # 26-50 get ₹575 each
    tuple(range(51, 101)): [540] * 50, # 51-100 get ₹540 each
    tuple(range(101, 301)): [515] * 200, # 101-300 get ₹515 each
    tuple(range(301, 600)): [505] * 299, # 301-599 get ₹505 each
    tuple(range(600, 901)): [500] * 300, # 600-900 get ₹500 each
    tuple(range(901, 1501)): [0] * 600  # 901-1500 get ₹0 each
}
    prize_distribution = [0] * 1500  # Initialize all ranks with ₹0

# Assigning prizes based on rank
    prize_distribution[0] = 50000  # 1st place
    prize_distribution[1] = 10000  # 2nd place
    prize_distribution[2] = 5000   # 3rd place
    prize_distribution[3] = 2000   # 4th place
    prize_distribution[4] = 1000   # 5th place

    prize_distribution[5:10] = [800] * 5    # 6th-10th place
    prize_distribution[10:25] = [625] * 15  # 11th-25th place
    prize_distribution[25:50] = [575] * 25  # 26th-50th place
    prize_distribution[50:100] = [540] * 50  # 51st-100th place
    prize_distribution[100:300] = [515] * 200  # 101st-300th place
    prize_distribution[300:599] = [505] * 299  # 301st-599th place
    prize_distribution[599:900] = [500] * 301  # 600th-900th place
    Prizes=prize_distribution

# 901-1500 remain 0
    def CalculatePayoff(self):
        Payment=[]
        for i in range(0,1500):
            search_value = int(self.Agents_Ranked_with_Points.loc[i,"Rank"])  # Value to search in keys
            #print(search_value)
        # Find the first matching key and get the corresponding index in the value list
            prize = Large_Spread_Payoff_Contest.Prizes[search_value-1]
            self.Agents_Squad[i]["Agent Payoff Sequence"].append(prize-Large_Spread_Payoff_Contest.EntryFee)
            Payment.append(prize-Large_Spread_Payoff_Contest.EntryFee)
        self.Agents_Ranked_with_Points["Payoff"]=Payment
class Concentrated_Payoff_Contest ():
    def __init__(self,Agents_data):
        super().__init__(Agents_data)
    EntryFee=100
    Prizes={tuple(range(1,301)):list(400*np.ones(300)),tuple(range(301,1501)):list(0*np.ones(1200))}
    def CalculatePayoff(self):
        Payment=[]
        for i in range(0,1500):
            search_value = self.Agents_Ranked_with_Points.loc[i,"Rank"]  # Value to search in keys
        # Find the first matching key and get the corresponding index in the value list
            prize = next(
                (value_list[key.index(search_value)] for key, value_list in Concentrated_Payoff_Contest.Prizes.items() if search_value in key),
                None  # Default if not found
            )
            self.Agents_Squad[i]["Agent Payoff Sequence"].append(prize-Concentrated_Payoff_Contest.EntryFee)
            Payment.append(prize-Concentrated_Payoff_Contest.EntryFee)
        self.Agents_Ranked_with_Points["Payoff"]=Payment
    pass