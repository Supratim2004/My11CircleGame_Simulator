from PlayerCard import *
import os,json,re,copy,random
from pathlib import Path
def say(msg = "Error", voice = "Samantha"):
    os.system(f'say -v {voice} {msg}')
Tournament_keys={"Name":"","My_11_Circle_Score":0,"Role":None,"Played":False,"Batting":{"Batted":False,"Runs":0,"BF":0,"Fours":0,"Sixes":0,"SR":"NA"},
       "Bowling":{"Bowled":False,"Overs bowled":0,"Runs conceded":0,"Maidens":0,"Wickets":0,"LBW/Bowled":0,"Economy":"NA"},
       "Fielding":{"Fielded":False,"Catch":0,"Stumping":0,"Run out(direct)":0,"Run out(indirect)":0}}
class Tournament:
    def __init__(self,squad_folder):
        self.top_runs=pd.DataFrame(columns=["Team Name","Player Name","Player Card","Runs"])
        self.top_wickets=pd.DataFrame(columns=["Team Name","Player Name","Player Card","Wickets"])
        self.top_catches=None
        self.player_id_name_mapping=dict()
        self.squad_folder=squad_folder
        self.Squads_dir=dict()
        self.Current_Game_Card=None
        folder_path = Path(self.squad_folder)
        for subfolder in folder_path.iterdir():
            if str(subfolder).endswith(".json"):
                k=Squad(str(subfolder))
                self.Squads_dir[k.Squad_name]=k
                self.player_id_name_mapping.update(k.player_id_name_mapping)
    def Get_Match_Team_Names(self,match_file):
        with open(match_file, 'r') as file:
            data = json.load(file)
        if data["isMatchComplete"]==True:
            Team1=data["scoreCard"][0]["batTeamDetails"]["batTeamName"]
            Team2=data["scoreCard"][1]["batTeamDetails"]["batTeamName"]
            return Team1,Team2
        else:
            return "Match Abandoned","Match Abandoned"
    def Get_Match_Player_IDs(self,match_file):
        with open(match_file, 'r') as file:
            data = json.load(file)
        Players=set()
        for innings_no in [1,2]:
            for bat in data["scoreCard"][innings_no-1]['batTeamDetails']['batsmenData'].keys():
                l=data["scoreCard"][innings_no-1]['batTeamDetails']['batsmenData'][bat]
                Batsman=l['batId']
                Players.add(Batsman)
        return Players
    def Match(self,match_file,Team_tuple):
        if Team_tuple!=("Match Abandoned","Match Abandoned"):
            with open(match_file, 'r') as file:
                data = json.load(file)
            Team1=Team_tuple[0]
            Team2=Team_tuple[1]    
            Name1=list(self.Squads_dir[Team1].Squad.keys())#list of ids of team 1 
            Name2=list(self.Squads_dir[Team2].Squad.keys())#list of ids of team 2
            Team1_dict=dict()
            for i in Name1:
                Team1_dict[i]=copy.deepcopy(Tournament_keys)
                Team1_dict[i]["Name"]=self.Squads_dir[Team1].Squad[i].name
                Team1_dict[i]["Role"]=self.Squads_dir[Team1].Squad[i].Type
            Team2_dict=dict()
            for i in Name2:
                
                Team2_dict[i]=copy.deepcopy(Tournament_keys)
                Team2_dict[i]["Name"]=self.Squads_dir[Team2].Squad[i].name
                Team2_dict[i]["Role"]=self.Squads_dir[Team2].Squad[i].Type
            z=Process_Scorecard(data,1,Team1_dict,Team2_dict,Name1,Name2)
            Team1_dict,Team2_dict=z[0],z[1]
            z=Process_Scorecard(data,2,Team2_dict,Team1_dict,Name2,Name1)
            Team1_dict,Team2_dict=z[0],z[1]
            return (Team1_dict,Team2_dict,Team_tuple)
        else:
            return "Match Abandoned"
    def Update(self,dictionary_tuple_with_Team):
        Team1_dict=dictionary_tuple_with_Team[0]
        Team2_dict=dictionary_tuple_with_Team[1]
        Team1_Name=dictionary_tuple_with_Team[2][0] 
        Team2_Name=dictionary_tuple_with_Team[2][1]
        self.Squads_dir[Team1_Name].Update(Team1_dict)
        self.Squads_dir[Team2_Name].Update(Team2_dict)
        #Orange Cap Update
        Batting_High_Score=[]
        for i in self.Squads_dir[Team1_Name].Squad.keys():
            if Team1_dict[i]["Batting"]["Batted"]==True:
                Batting_High_Score.append({"Team Name":Team1_Name,"Player Name":self.Squads_dir[Team1_Name].Squad[i].name,"Player Card":self.Squads_dir[Team1_Name].Squad[i],"Runs":self.Squads_dir[Team1_Name].Squad[i].tournament_performance.batting.Runs})
        for i in self.Squads_dir[Team2_Name].Squad.keys():
            if Team2_dict[i]["Batting"]["Batted"]==True:
                Batting_High_Score.append({"Team Name":Team2_Name,"Player Name":self.Squads_dir[Team2_Name].Squad[i].name,"Player Card":self.Squads_dir[Team2_Name].Squad[i],"Runs":self.Squads_dir[Team2_Name].Squad[i].tournament_performance.batting.Runs})
        Batting_Score=pd.DataFrame(Batting_High_Score)
        K=self.top_runs
        if K.empty!=True :
            K=pd.concat([K,Batting_Score],ignore_index=True)
        else:
            K=Batting_Score
        df_no_duplicates = K[~K.duplicated(subset=["Team Name", "Player Name"], keep="last")]
        self.top_runs=df_no_duplicates.sort_values(by="Runs",ascending=False).head(5).reset_index(drop=True)
        
        Bowling_High_Wicket=[]
        for i in self.Squads_dir[Team1_Name].Squad.keys():
            if Team1_dict[i]["Bowling"]["Bowled"]==True:
                Bowling_High_Wicket.append({"Team Name":Team1_Name,"Player Name":self.Squads_dir[Team1_Name].Squad[i].name,"Player Card":self.Squads_dir[Team1_Name].Squad[i],"Wickets":self.Squads_dir[Team1_Name].Squad[i].tournament_performance.bowling.Wickets})
        for i in self.Squads_dir[Team2_Name].Squad.keys():
            if Team2_dict[i]["Bowling"]["Bowled"]==True:
                Bowling_High_Wicket.append({"Team Name":Team2_Name,"Player Name":self.Squads_dir[Team2_Name].Squad[i].name,"Player Card":self.Squads_dir[Team2_Name].Squad[i],"Wickets":self.Squads_dir[Team2_Name].Squad[i].tournament_performance.bowling.Wickets})
        Bowling_Wicket=pd.DataFrame(Bowling_High_Wicket)
        Z=self.top_wickets
        if Z.empty!=True :
            Z=pd.concat([Z,Bowling_Wicket],ignore_index=True)
        else:
            Z=Bowling_Wicket
        df_no_duplicates = Z[~Z.duplicated(subset=["Team Name", "Player Name"], keep="last")]
        self.top_wickets=df_no_duplicates.sort_values(by="Wickets",ascending=False).head(5).reset_index(drop=True)
class Squad:
    def __init__(self,Squad_Location):
        self.Squad_ID=(Squad_Location.removesuffix(".json").split("/")[-1]).split("_")[1]
        self.Squad_name=(Squad_Location.split("/")[-1]).split("_")[0]
        self.player_id_name_mapping=dict()
        self.Squad_json_file=Squad_Location
        self.Squad=self.Extraction()
        
        
    def Extraction(self):
        with open("Paths.json","r") as path_file:
            path=json.load(path_file)
        with open(self.Squad_json_file, 'r') as file:
            Squad_x = json.load(file)
        L=dict()
        for i in Squad_x["player"]:
            Player_name=i["name"]
            Player_cricbuzz_id=i["id"]
            Player_espn_id =i["ESPN ID"]
            Path=((path['_'.join([self.Squad_name,self.Squad_ID])])[Player_name])[1]
            data=pd.read_excel(Path,sheet_name=None)
            z=Tournament_Player(data,"21-03-2024")
            z.name=Player_name
            z.Type=i["role"]
            if re.search("WK",z.Type, re.IGNORECASE):
                z.Type="Wicketkeeper"
            elif re.search('Allrounder',z.Type ,re.IGNORECASE):
                z.Type= "Allrounder"
            elif re.search("Bowler",z.Type,re.IGNORECASE):
                z.Type="Bowler"
            elif re.search("Batter",z.Type,re.IGNORECASE):
                z.Type="Batter"
            else:
                say(msg=f"{z.name}")
                print(z.Type)
            z.Cricbuzz_id=int(Player_cricbuzz_id)
            #z.My_11_Circle_points_list=[ random.randint(0, 10)]
            z.ESPN_id=  Player_espn_id
            self.player_id_name_mapping.update({z.name:z.Cricbuzz_id})
            batting_cols=[i for i in Tournament_keys["Batting"].keys() if i!="Batted"]
            bowling_cols=[i for i in Tournament_keys["Bowling"].keys() if i!="Bowled"]
            fielding_cols=[i for i in Tournament_keys["Fielding"].keys() if i!="Fielded"]
            z.tournament_performance.batting.Batting_Stats=pd.DataFrame(columns=batting_cols)
            z.tournament_performance.bowling.Bowling_Stats=pd.DataFrame(columns=bowling_cols)
            z.tournament_performance.fielding.Fielding_Stats=pd.DataFrame(columns=fielding_cols)
            L[z.Cricbuzz_id]=z
        return L
    
    def Update(self,Dictionary_match):
        for i in self.Squad:
            if Dictionary_match[i]["Played"]==True:
                #Batting update
                self.Squad[i].My_11_Circle_points_list.append(Dictionary_match[i]["My_11_Circle_Score"])
                if Dictionary_match[i]["Batting"]["Batted"]==True:
                    filtered_data = {k: v for k, v in Dictionary_match[i]["Batting"].items() if k != 'Batted'}
                    if not (self.Squad)[i].tournament_performance.batting.Batting_Stats.empty:
                        (self.Squad)[i].tournament_performance.batting.Batting_Stats = pd.concat(
                            [(self.Squad)[i].tournament_performance.batting.Batting_Stats, pd.DataFrame([filtered_data])], 
                        ignore_index=True   
                        )
                    else:
                        # Directly assign if it's empty
                        (self.Squad)[i].tournament_performance.batting.Batting_Stats = pd.DataFrame([filtered_data])
                    (self.Squad)[i].tournament_performance.batting.Runs+=Dictionary_match[i]["Batting"]["Runs"]
                    
                    (self.Squad)[i].tournament_performance.batting.BF+=Dictionary_match[i]["Batting"]["BF"]
                    (self.Squad)[i].tournament_performance.batting.Fours+=Dictionary_match[i]["Batting"]["Fours"]
                    (self.Squad)[i].tournament_performance.batting.Sixes+=Dictionary_match[i]["Batting"]["Sixes"]
                    (self.Squad)[i].tournament_performance.batting.Bat_SR=round((self.Squad)[i].tournament_performance.batting.Runs/(self.Squad)[i].tournament_performance.batting.BF*100,2) if (self.Squad)[i].tournament_performance.batting.BF!=0 else "NA"
                    (self.Squad)[i].tournament_performance.batting.MatchesBatted+=1
                    (self.Squad)[i].tournament_performance.batting.Bat_Average=round(self.Squad[i].tournament_performance.batting.Runs/self.Squad[i].tournament_performance.batting.MatchesBatted,2) if self.Squad[i].tournament_performance.batting.MatchesBatted!=0 else "NA"
                    (self.Squad)[i].tournament_performance.batting.Thirties+=1 if Dictionary_match[i]["Batting"]["Runs"]>=30  else 0
                    (self.Squad)[i].tournament_performance.batting.Fifties+=1 if Dictionary_match[i]["Batting"]["Runs"]>=50  else 0
                    (self.Squad)[i].tournament_performance.batting.Hundreds+=1 if Dictionary_match[i]["Batting"]["Runs"]>=100  else 0
                    (self.Squad)[i].tournament_performance.batting.Thirties+=1 if Dictionary_match[i]["Batting"]["Runs"]>=30  else 0
                    (self.Squad)[i].tournament_performance.batting.Highest_Score=max((self.Squad)[i].tournament_performance.batting.Highest_Score, Dictionary_match[i]["Batting"]["Runs"])
                if Dictionary_match[i]["Bowling"]["Bowled"]==True:
                    filtered_data = {k: v for k, v in Dictionary_match[i]["Bowling"].items() if k != 'Bowled'}
                    if not (self.Squad)[i].tournament_performance.bowling.Bowling_Stats.empty:
                        (self.Squad)[i].tournament_performance.bowling.Bowling_Stats = pd.concat(
                            [(self.Squad)[i].tournament_performance.bowling.Bowling_Stats, pd.DataFrame([filtered_data])], 
                            ignore_index=True
                        )
                    else:
                        # Directly assign if it's empty
                        (self.Squad)[i].tournament_performance.bowling.Bowling_Stats = pd.DataFrame([filtered_data])
                    (self.Squad)[i].tournament_performance.bowling.Matches_Bowled+=1
                    (self.Squad)[i].tournament_performance.bowling.Wickets+=Dictionary_match[i]["Bowling"]["Wickets"]
                    (self.Squad)[i].tournament_performance.bowling.Maidens+=Dictionary_match[i]["Bowling"]["Maidens"]
                    (self.Squad)[i].tournament_performance.bowling.Runs_conceded+=Dictionary_match[i]["Bowling"]["Runs conceded"]
                    balls=str(float(Dictionary_match[i]["Bowling"]["Overs bowled"])).split(".")
                    Balls=int(balls[0])*6+int(balls[1])
                    (self.Squad)[i].tournament_performance.bowling.Balls+=Balls
                    (self.Squad)[i].tournament_performance.bowling.Bowl_SR=round((self.Squad)[i].tournament_performance.bowling.Balls/(self.Squad)[i].tournament_performance.bowling.Wickets,2)if self.Squad[i].tournament_performance.bowling.Wickets!=0 else "NA"
                    self.Squad[i].tournament_performance.bowling.Bowl_Average=round(self.Squad[i].tournament_performance.bowling.Runs_conceded/self.Squad[i].tournament_performance.bowling.Wickets,2) if self.Squad[i].tournament_performance.bowling.Wickets!=0 else "NA"
                    self.Squad[i].tournament_performance.bowling.Bowling_Economy=round(self.Squad[i].tournament_performance.bowling.Runs_conceded/Balls,2) if Balls!=0 else "NA"
                    self.Squad[i].tournament_performance.bowling.BowledorLBW+=Dictionary_match[i]["Bowling"]["LBW/Bowled"]
                #Fielding update
                if Dictionary_match[i]["Fielding"]["Fielded"]==True:
                    filtered_data = {k: v for k, v in Dictionary_match[i]["Fielding"].items() if k != 'Fielded'}
                    if not (self.Squad)[i].tournament_performance.fielding.Fielding_Stats.empty:
                        (self.Squad)[i].tournament_performance.fielding.Fielding_Stats = pd.concat(
                            [(self.Squad)[i].tournament_performance.fielding.Fielding_Stats, pd.DataFrame([filtered_data])], 
                            ignore_index=True
                        )
                    else:
                        # Directly assign if it's empty
                        (self.Squad)[i].tournament_performance.fielding.Fielding_Stats = pd.DataFrame([filtered_data])
                    self.Squad[i].tournament_performance.fielding.Catches+=Dictionary_match[i]["Fielding"]["Catch"]
                    self.Squad[i].tournament_performance.fielding.Stumpings+=Dictionary_match[i]["Fielding"]["Stumping"]
                    self.Squad[i].tournament_performance.fielding.Run_out_direct+=Dictionary_match[i]["Fielding"]["Run out(direct)"]
                    self.Squad[i].tournament_performance.fielding.Run_out_indirect+=Dictionary_match[i]["Fielding"]["Run out(indirect)"]
                    self.Squad[i].tournament_performance.fielding.Dismissals+=Dictionary_match[i]["Fielding"]["Catch"]+Dictionary_match[i]["Fielding"]["Stumping"]+Dictionary_match[i]["Fielding"]["Run out(direct)"]+Dictionary_match[i]["Fielding"]["Run out(indirect)"]
                                   
def Process_Scorecard(data,innings_no,Team1_dict,Team2_dict,Name1,Name2):
    for bat in data["scoreCard"][innings_no-1]['batTeamDetails']['batsmenData'].keys():
        l=data["scoreCard"][innings_no-1]['batTeamDetails']['batsmenData'][bat]
        Batsman=l['batId']
        z=Batsman# id of batsman
        k=0
        Team1_dict[Batsman]["Played"]=True
        if l['outDesc']!= '':
            Team1_dict[Batsman]["Batting"]["Batted"]=True
            Team1_dict[Batsman]["Batting"]["Runs"]=l["runs"]
            Team1_dict[Batsman]["Batting"]["BF"]=l["balls"]
            Team1_dict[Batsman]["Batting"]["Fours"]=l["fours"]
            Team1_dict[Batsman]["Batting"]["Sixes"]=l["sixes"]
            Team1_dict[Batsman]["Batting"]["SR"]=l["strikeRate"]
            if l["wicketCode"]=="BOWLED":
                Bowler=l["bowlerId"]
                if Bowler in Team2_dict.keys():
                    Team2_dict[Bowler]["Played"]=True
                    Team2_dict[Bowler]["Bowling"]["Bowled"]=True
                    Team2_dict[Bowler]["Bowling"]["Wickets"]=Team2_dict[Bowler]["Bowling"]["Wickets"]+1
                    Team2_dict[Bowler]["Bowling"]["LBW/Bowled"]=Team2_dict[Bowler]["Bowling"]["LBW/Bowled"]+1
                else:
                    print("Something is wrong...",l["outDesc"]) 
                    k+=1
            elif l["wicketCode"]=="LBW":
                #Bowler=(l["outDesc"].removeprefix("lbw b").strip())
                Bowler=l["bowlerId"]
                #Bowler=Name_Processing(process.extractOne(Bowler,Name2)[0])
                if Bowler in Team2_dict.keys():
                    Team2_dict[Bowler]["Played"]=True
                    Team2_dict[Bowler]["Bowling"]["Bowled"]=True
                    Team2_dict[Bowler]["Bowling"]["Wickets"]=Team2_dict[Bowler]["Bowling"]["Wickets"]+1
                    Team2_dict[Bowler]["Bowling"]["LBW/Bowled"]=Team2_dict[Bowler]["Bowling"]["LBW/Bowled"]+1
                else:
                    print("Something is wrong...",l["outDesc"]) 
                    k+=1
            elif l["wicketCode"]=="CAUGHT":
                Bowler=l["bowlerId"]
                if Bowler in Team2_dict.keys():
                    Team2_dict[Bowler]["Played"]=True
                    Team2_dict[Bowler]["Bowling"]["Bowled"]=True
                    Team2_dict[Bowler]["Bowling"]["Wickets"]=Team2_dict[Bowler]["Bowling"]["Wickets"]+1
                else:
                    print("Something is wrong...",l["outDesc"])  
                    k+=1 
                Fielder=l["fielderId1"]
                if Fielder in Team2_dict.keys():
                    Team2_dict[Fielder]["Played"]=True
                    Team2_dict[Fielder]["Fielding"]["Fielded"]=True
                    Team2_dict[Fielder]["Fielding"]["Catch"]=Team2_dict[Fielder]["Fielding"]["Catch"]+1
                else:
                    print("Something is wrong...",l["outDesc"])
                    k+=1
                
            elif l["wicketCode"]=="CAUGHTBOWLED":
                Bowler=l["bowlerId"]
                if Bowler in Team2_dict.keys():
                    Team2_dict[Bowler]["Played"]=True
                    Team2_dict[Bowler]["Bowling"]["Bowled"]=True
                    Team2_dict[Bowler]["Bowling"]["Wickets"]=Team2_dict[Bowler]["Bowling"]["Wickets"]+1
                    Team2_dict[Bowler]["Fielding"]["Fielded"]=True
                    Team2_dict[Bowler]["Fielding"]["Catch"]=Team2_dict[Bowler]["Fielding"]["Catch"]+1
                else:
                    print("Something is wrong...",l["outDesc"])
                    k+=1 
            elif l["wicketCode"]=="STUMPED":
                Bowler=l["bowlerId"]
                if Bowler in Team2_dict.keys():
                    
                    Team2_dict[Bowler]["Played"]=True
                    Team2_dict[Bowler]["Bowling"]["Bowled"]=True
                    Team2_dict[Bowler]["Bowling"]["Wickets"]=Team2_dict[Bowler]["Bowling"]["Wickets"]+1
                else:
                    print("Something is wrong...",l["outDesc"]) 
                    k+=1
                Stumper=l["fielderId1"]
                if Stumper in Team2_dict.keys():
                    Team2_dict[Stumper]["Played"]=True
                    Team2_dict[Stumper]["Fielding"]["Fielded"]=True
                    Team2_dict[Stumper]["Fielding"]["Stumping"]=Team2_dict[Stumper]["Fielding"]["Stumping"]+1
                else:
                    print("Something is wrong...",l["outDesc"]) 
                    k+=1
            elif l["wicketCode"]=="RUNOUT":
                z=[l["fielderId1"],l["fielderId2"],l["fielderId2"]]
                if z[1]==0:
                    Fielder=z[0]
                    if Fielder in Team2_dict.keys():
                        Team2_dict[Fielder]["Played"]=True
                        Team2_dict[Fielder]["Fielding"]["Fielded"]=True
                        Team2_dict[Fielder]["Fielding"]["Run out(direct)"]=Team2_dict[Fielder]["Fielding"]["Run out(direct)"]+1
                    else:
                        print("Something is wrong...",l["outDesc"])
                        k+=1 
                else:
                    for fielder in z:
                        if fielder!=0:
                            Fielder=fielder
                            if Fielder in Team2_dict.keys():
                                Team2_dict[Fielder]["Played"]=True
                                Team2_dict[Fielder]["Fielding"]["Fielded"]=True
                                Team2_dict[Fielder]["Fielding"]["Run out(indirect)"]=Team2_dict[Fielder]["Fielding"]["Run out(indirect)"]+1
                            else:
                                print("Something is wrong...",l["outDesc"]) 
                                k+=1
                    
    for bowl in data["scoreCard"][innings_no-1]['bowlTeamDetails']['bowlersData'].keys():
        l=data["scoreCard"][innings_no-1]['bowlTeamDetails']['bowlersData'][bowl]
        Bowler=l['bowlerId']
        if Bowler in Team2_dict.keys():
            Team2_dict[Bowler]["Played"]=True
            Team2_dict[Bowler]["Bowling"]["Bowled"]=True
            Team2_dict[Bowler]["Bowling"]["Overs bowled"]=l["overs"]
            Team2_dict[Bowler]["Bowling"]["Runs conceded"]=l["runs"]
            Team2_dict[Bowler]["Bowling"]["Maidens"]=l["maidens"]
            Team2_dict[Bowler]["Bowling"]["Economy"]=l["economy"]
        else:
            print("Something is wrong...") 
            k+=1
    if k>=1:
        say()
    if innings_no==1:
        return Team1_dict,Team2_dict
    else:
        return Team2_dict,Team1_dict