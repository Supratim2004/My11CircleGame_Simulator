import pandas as pd
from Rules import *
class Batting:
    def __init__ (self,data,end_date):
        self.Keys=["Bat1","Runs","BF","SR","4s","6s","Opposition","Ground","Start Date"]
        self.end_date=end_date
        self.data=(self.Data_process_Date_time(data)).Bat_Normal()
        self.Runs=self.data["Runs"].sum() if self.data.empty==False else 0
        self.BF=self.data["BF"].sum()if self.data.empty==False else 0
        self.Bat_SR=round(100*self.Runs/self.BF,2) if self.BF!=0 else "NA"
        self.Dismissals_bat=self.data[ (self.data["Bat_Status"]=="Out") ]["Bat_Status"].count()if self.data.empty==False else 0
        self.Not_out=self.data[(self.data["Bat_Status"]=="Not Out") ]["Bat_Status"].count()if self.data.empty==False else 0
        self.MatchesBatted=self.Not_out+self.Dismissals_bat if self.data.empty==False else 0
        self.Highest_Score={"Score":self.data["Runs"][self.data["Runs"].idxmax()],"Dismissal Status":self.data["Bat_Status"][self.data["Runs"].idxmax()]}if self.data.empty==False else {"Score":"NA","Dismissal Status":"NA"}
        self.Bat_Average=round(self.Average(),2) if self.MatchesBatted!=0 else "NA"
        self.Thirties=self.data[(self.data["Runs"] >= 30) & (self.data["Runs"] < 50)]["Runs"].count() if self.data.empty==False else 0
        self.Fifties=self.data[(self.data["Runs"] >= 50) & (self.data["Runs"] < 100)]["Runs"].count() if self.data.empty==False else 0
        self.Hundreds=self.data[self.data["Runs"]>=100]["Runs"].count() if self.data.empty==False else 0
        self.Fours=self.data["4s"].sum()if self.data.empty==False else 0
        self.Sixes=self.data["6s"].sum()if self.data.empty==False else 0
        self.Ducks=self.data[self.data["Runs"]==0]["Runs"].count() if self.data.empty==False else 0
        self.Batting_Stats=self.data
    def Bat_status(self,value):
        match value:
            case "DNB":
                return "DNB"
            case "TDNB":
                return "TDNB"
            case "sub":
                return "sub"
            case z if ([*z])[-1]=="*":
                z.removesuffix("*")
                return "Not Out"
            case _:
                return "Out"
    def Average(self):
            if self.MatchesBatted!=0:
                return self.Runs/self.MatchesBatted
            else:
                return "NA"
    def Bat_Normal(self):
        self.data["Bat_Status"]=[self.Bat_status(z) for z in self.data["Bat1"]]
        z=self.Keys.copy()
        z[0]="Bat_Status"
        for z in ["Runs","BF","4s","6s"]:
            self.data[z]=[int(k.replace("-","0")) if isinstance(k,str) else int(k) for k in self.data[z]]   
        self.data["SR"]=[k.replace("-","NA") if isinstance(k,str) else float(k) for k in self.data["SR"]]
        return self.data
    def Data_process_Date_time(self,Data):    
        if Data.empty==False and "Start Date" in Data.columns:
                Data["Start Date"] = pd.to_datetime(Data["Start Date"], format='%d %b %Y')
                #end_date = "21-03-2024"
                Data = Data[ (Data['Start Date'] <= self.end_date)]
                Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        else:
            Data=pd.DataFrame(columns=self.Keys)
            Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        self.data=Data
        return self
    def Update(self,data):
        if data.empty==True:
            return self
        else:
            pass
class Bowling:
    def __init__ (self,data,end_date):
        self.Keys=["Overs",	"Mdns",	"Runs"	,"Wkts"	,"Econ"	,"Ave"	,"SR"	,"Opposition"	,"Ground"	,"Start Date"]
        self.end_date=end_date
        self.data=self.Data_process_Date_time(data).Bowl_Normal()
        self.Matches_Bowled=self.data[self.data["Balls"]!=0]["Balls"].count() if self.data.empty==False else 0
        self.Maidens=self.data["Mdns"].sum() if self.data.empty==False else 0
        self.Wickets=self.data["Wkts"].sum() if self.data.empty==False else 0
        self.BowledorLBW=None
        self.Balls=self.data["Balls"].sum() if self.data.empty==False else 0
        self.Overs=".".join([str(int(self.Balls//6)),str(int(self.Balls%6))]) if self.data.empty==False else 0
        self.Runs_conceded=self.data["Runs"].sum() if self.data.empty==False else 0
        self.Bowling_Economy=round(6*self.Runs_conceded/self.Balls,2) if self.Balls!=0 else "NA"
        self.Bowl_SR=round(self.Balls/self.Wickets,2) if self.Wickets!=0 else "NA"
        z = self.data["Wkts"].idxmax() if self.data.empty==False else "NA"
        self.Best_Figures={"Wickets":data.loc[z,"Wkts"],"Runs":data.loc[z,"Runs"],"Overs":data.loc[z,"Overs"]} if self.data.empty==False else {"Wickets":0,"Runs":0,"Overs":0}
        self.Bowl_Average=round(self.Runs_conceded/self.Wickets,2) if self.Wickets!=0 else "NA"
        self.Three_Wicket_haul=self.data[self.data["Wkts"]==3]["Wkts"].count() if self.data.empty==False else 0
        self.Four_Wicket_haul=self.data[self.data["Wkts"]==4]["Wkts"].count() if self.data.empty==False else 0
        self.Five_Wicket_haul=self.data[self.data["Wkts"]==5]["Wkts"].count() if self.data.empty==False else 0
        self.Bowling_Stats=self.data
    def Bowl_Normal(self):
        for z in ["Mdns","Runs","Wkts"]:
            self.data[z]=[int(k.replace("-","0")) if isinstance(k,str) else int(k)for k in self.data[z]]   
        for z in ["Econ","Ave","SR"]:
            self.data[z]=[(k.replace("-","NA")) if isinstance(k,str) else float(k) for k in self.data[z]] 
        self.data["Overs"]=[float(k.replace("-","0")) if isinstance(k,str) else float(k) for k in self.data["Overs"]] 
        self.data["Balls"]=[int(b[0])*6+int(b[1]) for b in ([str(r).split(".") for r in self.data["Overs"]])]
        z=self.Keys.copy()
        z.insert(1,"Balls")
        self.data=pd.DataFrame(self.data[z])
        return self.data
    def Data_process_Date_time(self,Data):    
        if Data.empty==False and "Start Date" in Data.columns:
            Data["Start Date"] = pd.to_datetime(Data["Start Date"], format='%d %b %Y')
            #end_date = "21-03-2024"
            Data = Data[ (Data['Start Date'] <= self.end_date)]
            Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        else:
            Data=pd.DataFrame(columns=self.Keys)
            Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        self.data=Data
        return self
class Fielding:
    def __init__(self,data,end_date):#end_date = "21-03-2024"
        self.Keys=["Dis",	"Ct"	,"St"	,"Ct Wk",	"Ct Fi",	"Opposition",	"Ground",	"Start Date"] 
        self.end_date=end_date
        self.data=self.Data_process_Date_time(data).Field_Normal()
        self.Run_out_direct=None
        self.Run_out_indirect=None
        self.Dismissals=self.data["Dis"].sum() if self.data.empty==False else 0
        self.Catches=self.data["Ct"].sum() if self.data.empty==False else 0
        self.Three_Catches=self.data[self.data["Ct"]>=3]["Ct"].count() if self.data.empty==False else 0
        self.Stumpings=self.data["St"].sum() if self.data.empty==False else 0
        self.Wicketkeeper_catch=self.data["Ct Wk"].sum() if self.data.empty==False else 0
        self.Field_Catches=self.data["Ct Fi"].sum() if self.data.empty==False else 0
        z = self.data["Dis"].idxmax() if self.data.empty==False else "NA"
        self.Most_Dismissals={"Wickets":self.data.loc[z,"Dis"],
                              "Catches":{"Fielding":self.data.loc[z,"Ct Fi"],
                                         "Wicketkeeper":self.data.loc[z,"Ct Wk"]},
                              "Stumpings":self.data.loc[z,"St"]}if self.data.empty==False else {"Most Dismissals":0,
                                                "Catches":{"Fielding":0,
                                                "Wicketkeeper":0},
                                    "Stumpings":0}
        self.Fielding_Stats=self.data
    def Field_Normal(self):
        for z in self.Keys[:-3]:
            self.data[z]=([int(k.replace("-","0")) if isinstance(k,str) else int(k) for k in self.data[z]] )
        return self.data
    def Data_process_Date_time(self,Data):    
        if Data.empty==False and "Start Date" in Data.columns:
            Data["Start Date"] = pd.to_datetime(Data["Start Date"], format='%d %b %Y')
            #end_date = "21-03-2024"
            Data = Data[ (Data['Start Date'] <= self.end_date)]
            Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        else:
            Data=pd.DataFrame(columns=self.Keys)
            Data = Data.loc[:, ~Data.columns.str.contains('^Unnamed')]
        self.data=Data
        return self
class Player_stats:
    def __init__(self,data,end_date):
        self.end_date=end_date
        self.batting=Batting(data["Batting"],self.end_date)
        self.bowling=Bowling(data["Bowling"],self.end_date)
        self.fielding=Fielding(data["Fielding"],self.end_date)
class Tournament_Player:
    def __init__(self,data,end_date):
        self.end_date=end_date
        self.name=None
        self.Type=None #Batter,Bowler
        self.My_11_Circle_points_list=[]
        self.Cricbuzz_id=None
        self.ESPN_id=  None
        l={"Batting":pd.DataFrame(),"Bowling":pd.DataFrame(),"Fielding":pd.DataFrame()}
        self.tournament_performance=Player_stats(l,end_date)
        self.tournament_performance.bowling.BowledorLBW=0
        self.tournament_performance.fielding.Run_out_direct=0
        self.tournament_performance.fielding.Run_out_indirect=0 
        self.tournament_performance.batting.Highest_Score=0
        self.stats=Player_stats(data,end_date)
        self.career_points=Scorer.calculate_career_points(self)