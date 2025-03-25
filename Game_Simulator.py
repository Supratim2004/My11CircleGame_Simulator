from Tourney import *
from Rules import *
from Player_Agents import *
from Payoff_Structure import *
import itertools
import random
from tqdm import tqdm
import time
def say(msg = "Error", voice = "Samantha"):
    os.system(f'say -v {voice} {msg}')
class Simulator:
    def __init__(self,squad_folder,L_strat,match_folder=None,n_players=None):
        self.n_players=n_players
        self.squad_folder=squad_folder
        self.match_folder=match_folder
        self.tournament=Tournament(squad_folder)
        self.strat=L_strat
    def Start_Game_Single_Match(self,match,Player_list=None):
        
        (team1,team2)=self.tournament.Get_Match_Team_Names(match)
        if (team1,team2)!=("Match Abandoned","Match Abandoned"):
            Players=self.tournament.Get_Match_Player_IDs(match)
            self.tournament.Current_Game_Card=Game_Card(self.tournament.Squads_dir[team1],self.tournament.Squads_dir[team2],Players)
            if Player_list is None:
                Player_list=Player_Pool.Get_Agent_List(self.n_players)#Declare Player Agents
            Contest=Large_Spread_Payoff_Contest (Player_list)
            #player_list_with_squads=Player_Pool.Choose_Squads(Player_list,self.tournament)
            Contest.Agents_Squad=Player_Pool.Choose_Squads(Player_list,self.tournament)
            Agent.Topsis_shannon_team=None
            Agent.Topsis_AHP_team=None
            Agent.Topsis_synthesised_team=None
            Agent.MA1_team=None
            Agent.allrounder_more_team=None
            Agent.Mean_Variance_selection_team=None
            Agent.MA5_team=None
            Agent.Career_points_team=None
            #Make them select players.Make them select captain and vice captain
            #Each member of player_list_with_squads is a dictionary of 4 elements: {Player_type_name:,Player_type:,Player_squad:,Player_score->initially 0}
            #Each member of Player_squad is {"Teamplayer":stats_dict,'Multiplier'} here
            match_play=self.tournament.Match(match_file=match,Team_tuple=(team1,team2))
            for match_player in match_play[0].keys():
                match_play[0][match_player]["My_11_Circle_Score"]=Scorer.calculate_score((match_play[0])[match_player])
            for match_player in match_play[1].keys():
                match_play[1][match_player]["My_11_Circle_Score"]=Scorer.calculate_score(match_play[1][match_player])
            Team_access={team1:match_play[0],team2:match_play[1]}
            Contest.calculate_points(Team_access)
            Contest.CalculatePayoff()
            self.tournament.Update(match_play)
            Ranked_df,Agents_details=(Contest.Agents_Ranked_with_Points),(Contest.Agents_Squad)
            
            return Ranked_df,Agents_details
        else:
            return (pd.DataFrame(columns=["Agent Type", "Score"]),[])
    def Play_Tournament(self,match_folder):
        Player_list=Player_Pool.Get_Agent_List(self.strat,self.n_players)#Declare Player Agents
        L=[]
        Json_output=[]
        l=0
        Agent_output_logs=[]
        for i in os.listdir(match_folder):
            if (match_folder+"/"+i).endswith(".json"):
                l+=1
        for i in tqdm(range(1,l+1), desc="Progress", ncols=100):
            if (match_folder+"/"+str(i)+".json").endswith(".json"):
                #say(f"Match {i} started")
                L.append(self.Start_Game_Single_Match(match_folder+"/"+str(i)+".json",Player_list))
            """Copy=copy.deepcopy(Player_list)
            
            for j in range(len(Copy)):
                del Copy[j]["Agent Type"]
                for k in range(len(Copy[j]["Agent Squad"])):
                    Copy[j]["Agent Squad"][k]["Match_Player_Stats"].pop("Player Stats",None)
                for k in range(len(Copy[j]['Historical Squad Selection'])):
                    for l in range(len(Copy[j]['Historical Squad Selection'][k])):
                        Copy[j]['Historical Squad Selection'][k][l]["Match_Player_Stats"].pop("Player Stats",None)"""
        #formulate a log file   
        #print(Json_output)
        say(f"Tournament ended")
        Agent.Topsis_shannon_team=None
        Agent.Topsis_AHP_team=None
        Agent.Topsis_synthesised_team=None
        Agent.MA1_team=None
        Agent.allrounder_more_team=None
        Agent.Mean_Variance_selection_team=None
        Agent.MA5_team=None
        Agent.Career_points_team=None
        return L,Json_output
