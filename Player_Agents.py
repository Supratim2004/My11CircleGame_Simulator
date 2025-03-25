import itertools
import random
import numpy as np
from Rules import *
from collections import defaultdict
from statistics import variance
import math
# Importing the required libraries for Linear Programming
from pulp import LpMaximize, LpProblem, LpVariable, lpSum,PULP_CBC_CMD,LpMinimize
class Game_Card:
    def __init__(self,team1,team2,Players):#Passed as Squad objects
        self.team1=team1
        self.team2=team2
        self.Players=Players
        self.Batter=self.Get_Categories("Batter")
        self.Bowler=self.Get_Categories("Bowler")
        self.Allrounder=self.Get_Categories("Allrounder")
        self.Wicketkeeper=self.Get_Categories("Wicketkeeper")
        self.Card={"Batter":self.Batter,"Bowler":self.Bowler,"Allrounder":self.Allrounder,"Wicketkeeper":self.Wicketkeeper}
        self.Sum_Card=self.Batter+self.Bowler+self.Allrounder+self.Wicketkeeper
        self.Card_with_Selection_Stats=self.initialize_stats()
    def Get_Categories(self,type):
        Category_list=[]
        for player in self.team1.Squad.keys():
            if self.team1.Squad[player].Type==type:
                if player in self.Players:
                    Category_list.append({"Team Name":self.team1.Squad_name,"Player Id":player,"Player Stats":self.team1.Squad[player],"player match play type":type})
        for player in self.team2.Squad.keys():      
            if self.team2.Squad[player].Type==type:
                if player in self.Players:
                    Category_list.append({"Team Name":self.team2.Squad_name,"Player Id":player,"Player Stats":self.team2.Squad[player],"player match play type":type})
        return Category_list   
    #Every player is a dictionary of 3 elements: {Player_squad:,Player_id:,Tournament_Player_Card:}
    def initialize_stats(self):
        Count_stat=copy.deepcopy(self.Sum_Card)
        for i in Count_stat:
            i["Selection Percentage"],i["Agents played"],i["Picked"]=0.0,0.0,0
        return Count_stat
    def Update_Selection_Percentage(self,team):
        Team_Player_Ids=set([i["Player Id"] for i in team])
        for player in self.Card_with_Selection_Stats:
            if player["Player Id"] in Team_Player_Ids:
                player["Picked"]+=1
            player["Agents played"]+=1 
            player["Selection Percentage"]=round(100*player["Picked"]/player["Agents played"],3)       

class Agent:
    Topsis_shannon_team=None
    Topsis_AHP_team=None
    Topsis_synthesised_team=None
    MA1_team=None
    allrounder_more_team=None
    Mean_Variance_selection_team=None
    MA5_team=None
    Career_points_team=None
    @staticmethod
    def Popularity_Based_Selection(tournament, k=11):
        game_Card=tournament.Current_Game_Card
        Count=game_Card.Card_with_Selection_Stats
        players = list(copy.deepcopy(Count))  # Avoid deepcopy unless modifying original
        teams = set(player["Team Name"] for player in players)
        roles = set(player["player match play type"] for player in players)

        # LP Problem Definition
        problem = LpProblem("Maximize_Team_Score", LpMaximize)

        # Decision Variables (1 if player is selected, 0 otherwise)
        player_vars = {
            player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players
        }

        # Objective: Maximize total Career Points
        problem += lpSum(player["Selection Percentage"] * player_vars[player["Player Id"]] for player in players), "Total_Score"

        # Constraint: Select Exactly k Players
        problem += lpSum(player_vars[player["Player Id"]] for player in players) == k, "Team_Size"

        # Constraint: Role limits (1 to 8 for each role)
        for role in roles:
            count = lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role)
            problem += count >= 1, f"Min_{role}"  # At least 1 player of each role
            problem += count <= 8, f"Max_{role}"  # At most 8 players per role

        # Constraint: At least one player from each team
        for team in teams:
            problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

        # Solve the problem
        problem.solve(PULP_CBC_CMD(msg=False))

        # Extract selected players
        selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]

        if not selected_players:
            return None  # No valid solution

        # Identify Captain & Vice-Captain by Career Points
        top_two_players = sorted(selected_players, key=lambda x: x["Selection Percentage"], reverse=True)[:2]

        # Assign multipliers
        for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_players[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_players[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
        return "Popularity_Selection",selected_players
    @staticmethod
    def Career_points(tournament):
        if Agent.Career_points_team==None:
            Card=tournament.Current_Game_Card
            players=copy.deepcopy(Card.Sum_Card)
            for i in players:
                i["Career Points"]=i["Player Stats"].career_points
            teams = list(set(player["Team Name"] for player in players))
            roles = list(set(player["player match play type"] for player in players))

            # Define the problem
            problem = LpProblem("Maximize_Team_Score", LpMaximize)

            # Define decision variables
            player_vars = {player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players}

            # Objective function: Maximize total score
            problem += lpSum(player["Career Points"] * player_vars[player["Player Id"]] for player in players), "Total_Score"

            # Constraint: Exactly 11 players selected
            problem += lpSum(player_vars[player["Player Id"]] for player in players) == 11, "Team_Size"

            # Constraints: Role limits (1 to 8 for each role)
            for role in roles:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) >= 1, f"Min_{role}"
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) <= 8, f"Max_{role}"

            # Constraint: At least one player from each team
            for team in teams:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

            # Solve the problem
            problem.solve(PULP_CBC_CMD(msg=False))

            # Extract results
            selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]
            #print(selected_players[0].keys())
            sorted_indices = sorted(range(len(selected_players)), key=lambda i: selected_players[i]["Career Points"], reverse=True)

            # Get the top two indices
            top_two_indices = sorted_indices[:2]

            for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_indices[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_indices[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
            Agent.Career_points_team=("Career_points", selected_players)
            return "Career_points", selected_players
        else:
            return Agent.Career_points_team
    @staticmethod
    def Tournament_figures(tournament):
        Card=tournament.Current_Game_Card
        SumCard=copy.deepcopy(Card.Sum_Card)
        for i in SumCard:
            i["Boundaries"]=i["Player Stats"].tournament_performance.batting.Sixes+i["Player Stats"].tournament_performance.batting.Fours
            i["Runs"]=i["Player Stats"].tournament_performance.batting.Runs
            i["Wickets"]=i["Player Stats"].tournament_performance.bowling.Wickets
        Team_choice=[]
        for j in ["Boundaries","Runs","Wickets"]:
            Team_choice.append(SumCard.pop(SumCard.index(max(SumCard, key=lambda x: x[j]))))
        exit=0
        Team_left=SumCard
        while exit==0:
            Team=copy.deepcopy(Team_choice+random.sample(Team_left,8))
            for i in range(len(Team)):
                Team[i]={"Match_Player_Stats":Team[i],"Multiplier":1}
            if TeamValidator(Team).validate_team()==[]:
                exit=1
        Team[0]["Multiplier"]=2
        Team[1]["Multiplier"]=1.5    
        return "Tournament_stats",Team
    @staticmethod 
    def Career_averages(tournament):
        Card=tournament.Current_Game_Card
        Batters=copy.deepcopy(Card.Batter)
        Bowlers=copy.deepcopy(Card.Bowler)
        Wicketkeepers=copy.deepcopy(Card.Wicketkeeper)
        Allrounders=copy.deepcopy(Card.Allrounder)
        for i in Batters:
            i["Bat_Average"]=i['Player Stats'].stats.batting.Bat_Average if i['Player Stats'].stats.batting.Bat_Average!="NA" else 0
        Choice_batter=[Batters.pop(Batters.index(max(Batters, key=lambda x: x["Bat_Average"])))]
        for i in Wicketkeepers:
            i["Bat_Average"]=i['Player Stats'].stats.batting.Bat_Average if i['Player Stats'].stats.batting.Bat_Average!="NA" else 0
        Choice_batter.append(Wicketkeepers.pop(Wicketkeepers.index(max(Wicketkeepers, key=lambda x: x["Bat_Average"]))))
        for i in Allrounders:
            i["Bat_Average"]=i['Player Stats'].stats.batting.Bat_Average if i['Player Stats'].stats.batting.Bat_Average!="NA" else 0
        Choice_batter.append(Allrounders.pop(Allrounders.index(max(Allrounders, key=lambda x: x["Bat_Average"]))))
        for i in Allrounders:
            i["Wickets"]=i['Player Stats'].stats.bowling.Wickets
        Choice_bowler=[(Allrounders.pop(Allrounders.index(max(Allrounders, key=lambda x: x["Wickets"]))))]
        for i in Bowlers:
            i["Wickets"]=i['Player Stats'].stats.bowling.Wickets
        Choice_bowler.append(Bowlers.pop(Bowlers.index(max(Bowlers, key=lambda x: x["Wickets"]))))
        Players_chosen=Choice_batter+Choice_bowler
        exit=0
        Team_left=Batters+Bowlers+Wicketkeepers+Allrounders
        while exit==0:
            Team=copy.deepcopy(Players_chosen+random.sample(Team_left,6))
            for i in range(len(Team)):
                Team[i]={"Match_Player_Stats":Team[i],"Multiplier":1}
            if TeamValidator(Team).validate_team()==[]:
                exit=1
        Team[0]["Multiplier"]=2
        Team[1]["Multiplier"]=1.5        
        return "Career_averages",Team
    @staticmethod
    def Choose_Fav_Team(tournament):
        Card=tournament.Current_Game_Card
        Teams=(Card.team1.Squad_name,Card.team2.Squad_name)
        Team_choice=random.sample(Teams,1)[0]
        Team_choice_team1=[i for i in Card.Sum_Card if i["Team Name"]==Team_choice]
        Team_choice_team2=[i for i in Card.Sum_Card if i["Team Name"]!=Team_choice]
        #print(len(Team_choice_team1),len(Team_choice_team2))
        exit=0
        while exit==0:
            Team=copy.deepcopy(random.sample(Team_choice_team1,10)+random.sample(Team_choice_team2,1))
            for i in range(len(Team)):
                Team[i]={"Match_Player_Stats":Team[i],"Multiplier":1}
            if TeamValidator(Team).validate_team()==[]:
                exit=1
        Team[0]["Multiplier"]=2
        Team[1]["Multiplier"]=1.5        
        return "Fav_Team",Team
    
    @staticmethod
    def All_rounder_select_all(tournament):
        Card=tournament.Current_Game_Card
        All=Card.Allrounder
        allrounder=random.sample(All,min(len(All),8))
        Rem=Card.Batter+Card.Bowler+Card.Wicketkeeper
        exit=0
        while exit==0:
            Team=copy.deepcopy(allrounder+random.sample(Rem,11-min(len(All),8)))
            for i in range(len(Team)):
                Team[i]={"Match_Player_Stats":Team[i],"Multiplier":1}
            if TeamValidator(Team).validate_team()==[]:
                exit=1
        Team[0]["Multiplier"]=2
        Team[1]["Multiplier"]=1.5    
        return "Allrounder_Select_All",Team
        
    @staticmethod
    def Random1(tournament):
        list1=tournament.Current_Game_Card.Batter
        list2=tournament.Current_Game_Card.Bowler
        list3=tournament.Current_Game_Card.Allrounder
        list4=tournament.Current_Game_Card.Wicketkeeper
        joined_list = list(itertools.chain(list1, list2, list3,list4))
        z=random.sample(joined_list, 11)
        for i in range(len(z)):
            z[i]={"Match_Player_Stats":z[i],"Multiplier":1}
        z[0]["Multiplier"]=2
        z[1]["Multiplier"]=1.5    
        return "Random1",z
    
    def Random2(tournament):
        k=random.sample(tournament.Current_Game_Card.Batter, min(len(tournament.Current_Game_Card.Batter),2))
        list2=tournament.Current_Game_Card.Bowler
        list3=tournament.Current_Game_Card.Allrounder
        list4=tournament.Current_Game_Card.Wicketkeeper
        joined_list = list(itertools.chain( list2, list3,list4))
        L=random.sample(joined_list, 11-len(k))
        z=k+L
        for i in range(len(z)):
            z[i]={"Match_Player_Stats":z[i],"Multiplier":1}
        z[0]["Multiplier"]=2
        z[1]["Multiplier"]=1.5   
        return "Random2",z
    
    def MA5(tournament):
        if Agent.MA5_team==None:
            game_Card=tournament.Current_Game_Card
            players=(game_Card.Sum_Card)
            for i in players:
                i["score"]=i["Player Stats"].My_11_Circle_points_list[-5:] if isinstance(i["Player Stats"].My_11_Circle_points_list, list) else []
                if len(i["score"])>=1:
                    i["score"]=np.mean(i["score"])
                else:
                    i["score"]=0
            # Importing the required libraries for Linear Programming
            # Extract unique teams and roles
            teams = list(set(player["Team Name"] for player in players))
            roles = list(set(player["player match play type"] for player in players))

            # Define the problem
            problem = LpProblem("Maximize_Team_Score", LpMaximize)

            # Define decision variables
            player_vars = {player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players}

            # Objective function: Maximize total score
            problem += lpSum(player["score"] * player_vars[player["Player Id"]] for player in players), "Total_Score"

            # Constraint: Exactly 11 players selected
            problem += lpSum(player_vars[player["Player Id"]] for player in players) == 11, "Team_Size"

            # Constraints: Role limits (1 to 8 for each role)
            for role in roles:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) >= 1, f"Min_{role}"
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) <= 8, f"Max_{role}"

            # Constraint: At least one player from each team
            for team in teams:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

            # Solve the problem
            problem.solve(PULP_CBC_CMD(msg=False))


            # Extract results
            selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]
            sorted_indices = sorted(range(len(selected_players)), key=lambda i: selected_players[i]["score"], reverse=True)

            # Get the top two indices
            top_two_indices = sorted_indices[:2]

            for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_indices[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_indices[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
            Agent.MA5_team=("MA5", selected_players)
            return "MA5", selected_players
        else:
            return Agent.MA5_team
        
    def MA1(tournament):
        if Agent.MA1_team==None:
            game_Card=tournament.Current_Game_Card
            players=(game_Card.Sum_Card)
            for i in players:
                i["score"]=i["Player Stats"].My_11_Circle_points_list[-1] if i["Player Stats"].My_11_Circle_points_list else 0
            # Extract unique teams and roles
            teams = list(set(player["Team Name"] for player in players))
            roles = list(set(player["player match play type"] for player in players))

            # Define the problem
            problem = LpProblem("Maximize_Team_Score", LpMaximize)

            # Define decision variables
            player_vars = {player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players}

            # Objective function: Maximize total score
            problem += lpSum(player["score"] * player_vars[player["Player Id"]] for player in players), "Total_Score"

            # Constraint: Exactly 11 players selected
            problem += lpSum(player_vars[player["Player Id"]] for player in players) == 11, "Team_Size"

            # Constraints: Role limits (1 to 8 for each role)
            for role in roles:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) >= 1, f"Min_{role}"
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) <= 8, f"Max_{role}"

            # Constraint: At least one player from each team
            for team in teams:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

            # Solve the problem
            problem.solve(PULP_CBC_CMD(msg=False))


            # Extract results
            selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]
            sorted_indices = sorted(range(len(selected_players)), key=lambda i: selected_players[i]["score"], reverse=True)

            # Get the top two indices
            top_two_indices = sorted_indices[:2]

            for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_indices[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_indices[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
            Agent.MA1_team=("MA1", selected_players)
            return "MA1", selected_players
        else:
            return Agent.MA1_team
        
    def allrounder_more(tournament):
        if Agent.allrounder_more_team==None:
            game_Card=tournament.Current_Game_Card
            players=(game_Card.Sum_Card)
            for i in players:
                i["score"]=i["Player Stats"].My_11_Circle_points_list[-1] if i["Player Stats"].My_11_Circle_points_list else 0
            # Extract unique teams and roles
            teams = list(set(player["Team Name"] for player in players))
            roles = list(set(player["player match play type"] for player in players))

            # Define the problem
            problem = LpProblem("Maximize_Team_Score", LpMaximize)

            # Define decision variables
            player_vars = {player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players}

            # Objective function: Maximize total score
            problem += lpSum(player["score"] * player_vars[player["Player Id"]] for player in players), "Total_Score"

            # Constraint: Exactly 11 players selected
            problem += lpSum(player_vars[player["Player Id"]] for player in players) == 11, "Team_Size"

            # Constraints: Role limits (1 to 8 for each role)
            for role in ["Batter","Bowler","Wicketkeeper"]:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) >= 1, f"Min_{role}"
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) <= 8, f"Max_{role}"
            problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == "Allrounder") >= 3, f"Min_Allrounder"
            problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == "Allrounder") <= 8, f"Max_Allrounder"
            # Constraint: At least one player from each team
            for team in teams:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

            # Solve the problem
            problem.solve(PULP_CBC_CMD(msg=False))


            # Extract results
            selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]
            sorted_indices = sorted(range(len(selected_players)), key=lambda i: selected_players[i]["score"], reverse=True)

            # Get the top two indices
            top_two_indices = sorted_indices[:2]

            for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_indices[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_indices[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
            Agent.allrounder_more_team=("Allrounder_pref", selected_players)
            return "Allrounder_pref", selected_players
        else:
            return Agent.allrounder_more_team
    def Mean_Variance_selection(tournament):
        if Agent.Mean_Variance_selection_team==None:
            game_Card=tournament.Current_Game_Card
            players=(game_Card.Sum_Card)
            for i in players:
                i["score"]=i["Player Stats"].My_11_Circle_points_list[-3:] if isinstance(i["Player Stats"].My_11_Circle_points_list, list) else []
                if len(i["score"])>=1:
                    i["mean score"]=np.mean(i["score"])
                else:
                    i["mean score"]=-4
                if len(i["score"])>=2:
                    i["SD"]=math.sqrt(variance(i["score"]))
                else:
                    i["SD"]=2000
            lambda_risk=1
            teams = list(set(player["Team Name"] for player in players))
            roles = list(set(player["player match play type"] for player in players))

            # Define the problem
            problem = LpProblem("Maximize_Team_Score", LpMaximize)

            # Define decision variables
            player_vars = {player["Player Id"]: LpVariable(f"Player_{player['Player Id']}", cat="Binary") for player in players}

            # Objective function: Maximize total score
            problem += lpSum((player["mean score"]-lambda_risk*player["SD"]) * player_vars[player["Player Id"]] for player in players), "Total_Score"

            # Constraint: Exactly 11 players selected
            problem += lpSum(player_vars[player["Player Id"]] for player in players) == 11, "Team_Size"
            # Constraints: Role limits (1 to 8 for each role)
            for role in roles:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) >= 1, f"Min_{role}"
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["player match play type"] == role) <= 8, f"Max_{role}"
            # Constraint: At least one player from each team
            for team in teams:
                problem += lpSum(player_vars[player["Player Id"]] for player in players if player["Team Name"] == team) >= 1, f"Team_{team}"

            # Solve the problem
            problem.solve(PULP_CBC_CMD(msg=False))


            # Extract results
            selected_players = [player for player in players if player_vars[player["Player Id"]].value() == 1]
            sorted_indices = sorted(range(len(selected_players)), key=lambda i: selected_players[i]["score"], reverse=True)

            # Get the top two indices
            top_two_indices = sorted_indices[:2]

            for i in range(len(selected_players)):
                selected_players[i] = {"Match_Player_Stats": selected_players[i], "Multiplier": 1}
                if i == top_two_indices[0]:
                    selected_players[i]["Multiplier"] = 2 #captain
                elif i == top_two_indices[1]:
                    selected_players[i]["Multiplier"] = 1.5 #vice-captain
                else:
                    selected_players[i]["Multiplier"] = 1 #normal player
            Agent.Mean_Variance_selection_team=("Mean_var_optimization", selected_players)        
            return "Mean_var_optimization", selected_players
        else:
            return Agent.Mean_Variance_selection_team
    def Topsis_strat_synthesis(tournament):
        if Agent.Topsis_synthesised_team==None:
            game_Card=tournament.Current_Game_Card
            Batters=game_Card.Batter
            Bowlers=game_Card.Bowler
            Wicketkeepers=game_Card.Wicketkeeper
            Allrounders=game_Card.Allrounder
            batting_players = Batters+Wicketkeepers
            batting_performance = np.array([[i["Player Stats"].stats.batting.MatchesBatted,
                                            i["Player Stats"].stats.batting.Bat_Average if i["Player Stats"].stats.batting.Bat_Average!="NA" else 0 ,
                                            i["Player Stats"].stats.batting.Bat_SR if i["Player Stats"].stats.batting.Bat_SR!="NA" else 0,
                                            i["Player Stats"].stats.batting.Fifties]
                                            for i in batting_players])
            batting_weights = np.array(TOPSIS.Synthesis_weights["Batting"])
            bowling_weights = np.array(TOPSIS.Synthesis_weights["Bowling"])
            all_rounder_weights = np.array(TOPSIS.Synthesis_weights["All_rounders"])
            bowling_players=Bowlers
            bowling_performance=np.array([[i["Player Stats"].stats.bowling.Runs_conceded,
                                        i["Player Stats"].stats.bowling.Wickets,
                                        i["Player Stats"].stats.bowling.Bowling_Economy if i["Player Stats"].stats.bowling.Bowling_Economy!="NA" else 20,
                                        i["Player Stats"].stats.bowling.Matches_Bowled]
                                        for i in bowling_players])
            
            all_rounder_players=Allrounders
            all_rounder_performance=np.array([[i["Player Stats"].stats.batting.Runs,
                                            i["Player Stats"].stats.batting.Fifties,
                                            i["Player Stats"].stats.bowling.Runs_conceded,
                                            i["Player Stats"].stats.bowling.Wickets] 
                                            for i in all_rounder_players])
            
            ranked_batting = TOPSIS.topsis_ranking(batting_players, batting_performance, batting_weights)
            ranked_bowling = TOPSIS.topsis_ranking(bowling_players, bowling_performance, bowling_weights)
            ranked_all_rounders = TOPSIS.topsis_ranking(all_rounder_players, all_rounder_performance, all_rounder_weights)
            Selected_bowlers=ranked_bowling[:3]
            Selected_all_rounders=ranked_all_rounders[:3]
            Selected_batters=[]
            ranked_batters=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Batter"]
            ranked_wicketkeepers=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Wicketkeeper"]
            Selected_batters.append(ranked_batters.pop(0))
            Selected_batters.append(ranked_wicketkeepers.pop(0))
            Rem_batters=ranked_batters+ranked_wicketkeepers
            Rem_batters = sorted(Rem_batters, key=lambda x: x[1], reverse=True)
            for i in range(3):
                Selected_batters.append(Rem_batters.pop(0))
            
            # Combine rankings from all categories
            Roster = (
                Selected_batters +  # Top 5 batting players
                Selected_bowlers +  # Top 3 bowling players
                Selected_all_rounders  # Top 3 all-rounders
            )

            # Aggregate and sort by closeness coefficient
            aggregated_rankings = sorted(Roster, key=lambda x: x[1], reverse=True)

            # Select Captain and Vice-Captain
            captain = aggregated_rankings[0]  # Player with the highest CC
            vice_captain = aggregated_rankings[1]  # Player with the second-highest CC
            Team=[]
            for player in Roster:
                l={"Match_Player_Stats":player[0]}
                if player==captain:
                    l["Multiplier"]=2
                elif player==vice_captain:
                    l["Multiplier"]=1.5
                else:
                    l["Multiplier"]=1
                Team.append(l)
            Agent.Topsis_synthesised_team=("TOPSIS_Synthesis",Team)
            return "TOPSIS_Synthesis",Team
        else:
            return Agent.Topsis_synthesised_team
    def Topsis_strat_AHP(tournament):
        if Agent.Topsis_AHP_team==None:
            game_Card=tournament.Current_Game_Card
            Batters=game_Card.Batter
            Bowlers=game_Card.Bowler
            Wicketkeepers=game_Card.Wicketkeeper
            Allrounders=game_Card.Allrounder
            batting_players = Batters+Wicketkeepers
            batting_performance = np.array([[i["Player Stats"].stats.batting.MatchesBatted,
                                            i["Player Stats"].stats.batting.Bat_Average if i["Player Stats"].stats.batting.Bat_Average!="NA" else 0 ,
                                            i["Player Stats"].stats.batting.Bat_SR if i["Player Stats"].stats.batting.Bat_SR!="NA" else 0,
                                            i["Player Stats"].stats.batting.Fifties]
                                            for i in batting_players])
            batting_weights = np.array(TOPSIS.AHP_weights["Batting"])
            bowling_weights = np.array(TOPSIS.AHP_weights["Bowling"])
            all_rounder_weights = np.array(TOPSIS.AHP_weights["All_rounders"])
            bowling_players=Bowlers
            bowling_performance=np.array([[i["Player Stats"].stats.bowling.Runs_conceded,
                                        i["Player Stats"].stats.bowling.Wickets,
                                        i["Player Stats"].stats.bowling.Bowling_Economy if i["Player Stats"].stats.bowling.Bowling_Economy!="NA" else 20,
                                        i["Player Stats"].stats.bowling.Matches_Bowled]
                                        for i in bowling_players])
            
            all_rounder_players=Allrounders
            all_rounder_performance=np.array([[i["Player Stats"].stats.batting.Runs,
                                            i["Player Stats"].stats.batting.Fifties,
                                            i["Player Stats"].stats.bowling.Runs_conceded,
                                            i["Player Stats"].stats.bowling.Wickets] 
                                            for i in all_rounder_players])
            
            ranked_batting = TOPSIS.topsis_ranking(batting_players, batting_performance, batting_weights)
            ranked_bowling = TOPSIS.topsis_ranking(bowling_players, bowling_performance, bowling_weights)
            ranked_all_rounders = TOPSIS.topsis_ranking(all_rounder_players, all_rounder_performance, all_rounder_weights)
            Selected_bowlers=ranked_bowling[:3]
            Selected_all_rounders=ranked_all_rounders[:3]
            Selected_batters=[]
            ranked_batters=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Batter"]
            ranked_wicketkeepers=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Wicketkeeper"]
            Selected_batters.append(ranked_batters.pop(0))
            Selected_batters.append(ranked_wicketkeepers.pop(0))
            Rem_batters=ranked_batters+ranked_wicketkeepers
            Rem_batters = sorted(Rem_batters, key=lambda x: x[1], reverse=True)
            for i in range(3):
                Selected_batters.append(Rem_batters.pop(0))
            
            # Combine rankings from all categories
            Roster = (
                Selected_batters +  # Top 5 batting players
                Selected_bowlers +  # Top 3 bowling players
                Selected_all_rounders  # Top 3 all-rounders
            )

            # Aggregate and sort by closeness coefficient
            aggregated_rankings = sorted(Roster, key=lambda x: x[1], reverse=True)

            # Select Captain and Vice-Captain
            captain = aggregated_rankings[0]  # Player with the highest CC
            vice_captain = aggregated_rankings[1]  # Player with the second-highest CC
            Team=[]
            for player in Roster:
                l={"Match_Player_Stats":player[0]}
                if player==captain:
                    l["Multiplier"]=2
                elif player==vice_captain:
                    l["Multiplier"]=1.5
                else:
                    l["Multiplier"]=1
                Team.append(l)
            Agent.Topsis_AHP_team=("TOPSIS_AHP",Team)
            return "TOPSIS_AHP",Team
        else:
            return Agent.Topsis_AHP_team
    def Topsis_strat_Shannon(tournament):
        if Agent.Topsis_shannon_team==None:
            game_Card=tournament.Current_Game_Card
            Batters=game_Card.Batter
            Bowlers=game_Card.Bowler
            Wicketkeepers=game_Card.Wicketkeeper
            Allrounders=game_Card.Allrounder
            batting_players = Batters+Wicketkeepers
            batting_performance = np.array([[i["Player Stats"].stats.batting.MatchesBatted,
                                            i["Player Stats"].stats.batting.Bat_Average if i["Player Stats"].stats.batting.Bat_Average!="NA" else 0 ,
                                            i["Player Stats"].stats.batting.Bat_SR if i["Player Stats"].stats.batting.Bat_SR!="NA" else 0,
                                            i["Player Stats"].stats.batting.Fifties]
                                            for i in batting_players])
            batting_weights = np.array(TOPSIS.Shannon_weights["Batting"])
            bowling_weights = np.array(TOPSIS.Shannon_weights["Bowling"])
            all_rounder_weights = np.array(TOPSIS.Shannon_weights["All_rounders"])
            bowling_players=Bowlers
            bowling_performance=np.array([[i["Player Stats"].stats.bowling.Runs_conceded,
                                        i["Player Stats"].stats.bowling.Wickets,
                                        i["Player Stats"].stats.bowling.Bowling_Economy if i["Player Stats"].stats.bowling.Bowling_Economy!="NA" else 20,
                                        i["Player Stats"].stats.bowling.Matches_Bowled]
                                        for i in bowling_players])
            
            all_rounder_players=Allrounders
            all_rounder_performance=np.array([[i["Player Stats"].stats.batting.Runs,
                                            i["Player Stats"].stats.batting.Fifties,
                                            i["Player Stats"].stats.bowling.Runs_conceded,
                                            i["Player Stats"].stats.bowling.Wickets] 
                                            for i in all_rounder_players])
            
            ranked_batting = TOPSIS.topsis_ranking(batting_players, batting_performance, batting_weights)
            ranked_bowling = TOPSIS.topsis_ranking(bowling_players, bowling_performance, bowling_weights)
            ranked_all_rounders = TOPSIS.topsis_ranking(all_rounder_players, all_rounder_performance, all_rounder_weights)
            Selected_bowlers=ranked_bowling[:3]
            Selected_all_rounders=ranked_all_rounders[:3]
            Selected_batters=[]
            ranked_batters=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Batter"]
            ranked_wicketkeepers=[i for i in ranked_batting if i[0]["Player Stats"].Type=="Wicketkeeper"]
            Selected_batters.append(ranked_batters.pop(0))
            Selected_batters.append(ranked_wicketkeepers.pop(0))
            Rem_batters=ranked_batters+ranked_wicketkeepers
            Rem_batters = sorted(Rem_batters, key=lambda x: x[1], reverse=True)
            for i in range(3):
                Selected_batters.append(Rem_batters.pop(0))
            
            # Combine rankings from all categories
            Roster = (
                Selected_batters +  # Top 5 batting players
                Selected_bowlers +  # Top 3 bowling players
                Selected_all_rounders  # Top 3 all-rounders
            )

            # Aggregate and sort by closeness coefficient
            aggregated_rankings = sorted(Roster, key=lambda x: x[1], reverse=True)

            # Select Captain and Vice-Captain
            captain = aggregated_rankings[0]  # Player with the highest CC
            vice_captain = aggregated_rankings[1]  # Player with the second-highest CC
            Team=[]
            for player in Roster:
                l={"Match_Player_Stats":player[0]}
                if player==captain:
                    l["Multiplier"]=2
                elif player==vice_captain:
                    l["Multiplier"]=1.5
                else:
                    l["Multiplier"]=1
                Team.append(l)
            Agent.Topsis_shannon_team=("TOPSIS_Shannon",Team)
            return "TOPSIS_Shannon",Team
        else:
            return Agent.Topsis_shannon_team
            
class Player_Pool:
    @staticmethod
    def Get_Agent_List(List_of_strategies,n_players=100):  
        List_of_agents=[]  
        List_of_agents = [
        {"My11Circle Agent ID": f"{i}", "Agent Type Name": "", "Agent Type": k,"Agent Payoff Sequence":[],"Agent Contest Sequence":[],"Historical Squad Selection":[]}
        for i in range(n_players)
        for k in List_of_strategies
        ]
        return List_of_agents
    @staticmethod
    def Choose_Squads(Agent_list,Tournament):
        random.shuffle(Agent_list)
        for i in range(len(Agent_list)):
            k=0
            while (k==0):
                l=copy.deepcopy(Agent_list[i])
                #print(l["Player Type"])
                z=l["Agent Type"](Tournament)
                l["Agent Type Name"]=z[0]
                l["Agent Squad"]=z[1]
                l["Score"]=0
                if TeamValidator(l["Agent Squad"]).validate_team()==[]:
                    k=1
                    Agent_list[i]["Agent Type Name"]=l["Agent Type Name"]
                    Agent_list[i]["Agent Squad"]=l["Agent Squad"]
                    #Agent_list[i]["Historical Squad Selection"].append(l["Agent Squad"])
                    Agent_list[i]["Score"]=0
                #update game card here once
                    team=[i["Match_Player_Stats"] for i in Agent_list[i]["Agent Squad"]]
                    Tournament.Current_Game_Card.Update_Selection_Percentage(team)
                else:
                    #print(l["Player Type Name"],TeamValidator(l["Player Squad"]).validate_team())
                    pass
        return Agent_list
class TOPSIS:
    Shannon_weights={"Batting":[0.252,0.309,0.340,0.098],"Bowling":[0.234,0.195,0.403,0.168],"All_rounders":[0.247,0.227,0.262,0.264]}
    AHP_weights={"Batting":[0.122,0.396,0.086,0.396],"Bowling":[0.243,0.090,0.130,0.537],"All_rounders":[0.332,0.235,0.126,0.308]}
    Synthesis_weights={"Batting":[0.138, 0.553, 0.132, 0.176],"Bowling":[0.262,0.081,0.241,0.416],"All_rounders":[0.328,0.214,0.132,0.326]}
    
    @staticmethod
    def normalize_matrix(matrix):
        """Normalize the decision matrix."""
        return matrix / np.sqrt((matrix ** 2).sum(axis=0))
    @staticmethod
    def weighted_normalized_matrix(norm_matrix, weights):
        """Apply weights to the normalized decision matrix."""
        return norm_matrix * weights
    @staticmethod
    def calculate_ideal_solutions(weighted_matrix):
        """Calculate the positive and negative ideal solutions."""
        PIS = np.max(weighted_matrix, axis=0)  # Positive Ideal Solution
        NIS = np.min(weighted_matrix, axis=0)  # Negative Ideal Solution
        return PIS, NIS
    @staticmethod
    def calculate_closeness_coefficient(weighted_matrix, PIS, NIS):
        """Calculate closeness coefficients for all alternatives."""
        distance_to_PIS = np.sqrt(((weighted_matrix - PIS) ** 2).sum(axis=1))
        distance_to_NIS = np.sqrt(((weighted_matrix - NIS) ** 2).sum(axis=1))
        closeness_coefficients = distance_to_NIS / (distance_to_PIS + distance_to_NIS)
        return closeness_coefficients
    @staticmethod
    def topsis_ranking(players, performance_data, weights):
        """Perform the TOPSIS method and rank players."""
        norm_matrix = TOPSIS.normalize_matrix(performance_data)
        weighted_matrix = TOPSIS.weighted_normalized_matrix(norm_matrix, weights)
        PIS, NIS = TOPSIS.calculate_ideal_solutions(weighted_matrix)
        closeness_coefficients = TOPSIS.calculate_closeness_coefficient(weighted_matrix, PIS, NIS)
        ranked_players = sorted(
            zip(players, closeness_coefficients),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked_players