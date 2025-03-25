from Game_Simulator import *
class Strategy_Set_Summary():
    def __init__(self,Match_play,Strategies=None):
        self.Match_set=Match_play
        self.Current_Strategy_list=Strategies
        self.Current_match_list=None
    def Filter_Strategies(self,strats):
        self.Current_Strategy_list=strats
        k=[]
        for data in self.Match_set:
            if data.empty==False:
                l=data[data["Player Type Name"].isin(strats)]
                l=l.reset_index(0, drop=True)
                l["Rank"]=l.rank(axis=0,method="min",ascending=False)["Score"]
                k.append(l)
        self.Current_match_list=k
    def Do(self):
        strat_list=self.Current_Strategy_list
        l=self.Current_match_list
        Wins_best_Match_no={key: set() for key in strat_list}
        #print(Wins_best_Match_no)
        Wins_best_Rank = {key: 0 for key in strat_list}
        Matches_played=0
        #Wins_best_Rank=defaultdict(int)
        for i in range(len(l)):
            #print(i)
            if l[i].empty==False:
                Matches_played+=1
                h=l[i][l[i]["Rank"]==1]["Player Type Name"].unique()
                for j in h:
                    Wins_best_Match_no[j].add(i+1)
                    Wins_best_Rank[j]+=1
        for i in Wins_best_Rank.keys():
            Wins_best_Rank[i]=round(100*Wins_best_Rank[i]/Matches_played,3)
        Wins_best_Match_no
        df_AverageRank=pd.DataFrame(columns=strat_list)
        for i in range(len(l)):
            Match_no=i+1
            if l[i].empty==False:
                Rank=dict()
                Rank["Match No."]=[Match_no]
                for g in strat_list:
                    d=l[i][l[i]["Player Type Name"]==g]["Rank"].mean()
                    Rank[g]=[d]
                
                if df_AverageRank.empty==True:
                    df_AverageRank=pd.DataFrame(Rank)
                else:
                    df_AverageRank=pd.concat([df_AverageRank,pd.DataFrame(Rank)], ignore_index=True)
                    #df_AverageRank.reset_index()
        df_AverageRank
        Win_per=pd.DataFrame(columns=list(df_AverageRank.columns)[1:])
        Wins_average_Rank = {key: set() for key in strat_list}
        for i in range(71):
            Win_per.loc[i]=df_AverageRank.iloc[i,1:].rank(method="min",ascending=True)
            row = Win_per.loc[i]
            argmins = row[row == 1].index.tolist()
            #print(argmins)
            for j in argmins:
                Wins_average_Rank[j].add(i+1)
        #Win_per
        Win_percentage_Average_Rank=dict()
        for i in list(Win_per.columns):
            Win_percentage_Average_Rank[i]=round((100*len(Win_per[Win_per[i]==1][i])/71),3)
        Win_percentage_Average_Rank
        df_AveragePoints=pd.DataFrame(columns=strat_list)
        for i in range(len(l)):
            Match_no=i+1
            if l[i].empty==False:
                Rank=dict()
                Rank["Match No."]=[Match_no]
                for g in strat_list:
                    d=l[i][l[i]["Player Type Name"]==g]["Score"].mean()
                    Rank[g]=[d]
                
                if df_AveragePoints.empty==True:
                    df_AveragePoints=pd.DataFrame(Rank)
                else:
                    df_AveragePoints=pd.concat([df_AveragePoints,pd.DataFrame(Rank)], ignore_index=True)
                    #df_AverageRank.reset_index()
        df_AverageRank=pd.DataFrame(columns=strat_list)
        for i in range(len(l)):
            Match_no=i+1
            if l[i].empty==False:
                Rank=dict()
                Rank["Match No."]=[Match_no]
                for g in strat_list:
                    d=l[i][l[i]["Player Type Name"]==g]["Rank"].mean()
                    Rank[g]=[d]
                
                if df_AverageRank.empty==True:
                    df_AverageRank=pd.DataFrame(Rank)
                else:
                    df_AverageRank=pd.concat([df_AverageRank,pd.DataFrame(Rank)], ignore_index=True)
                    #df_AverageRank.reset_index()
        df_Best_Rank=pd.DataFrame(columns=["Match No."]+strat_list)
        for i in range(len(l)):
            Match_no=i+1
            if l[i].empty==False:
                Rank=dict()
                Rank["Match No."]=[Match_no]
                for g in strat_list:
                    d=l[i][l[i]["Player Type Name"]==g]["Rank"].min()
                    Rank[g]=[d]
                
                if df_Best_Rank.empty==True:
                    df_Best_Rank=pd.DataFrame(Rank)
                else:
                    df_Best_Rank=pd.concat([df_Best_Rank,pd.DataFrame(Rank)], ignore_index=True)
                    #df_AverageRank.reset_index()
        ex=df_Best_Rank.iloc[:,1:]
        g=df_AverageRank.iloc[:,1:]
        o=df_AveragePoints.iloc[:,1:]
        
        Stats=o.describe()
        Stats2=g.describe()
        Stats3=ex.describe()
        Stats=Stats.loc[["mean","25%","50%","75%"],:].to_dict()
        Stats2=Stats2.loc[["mean","25%","50%","75%"],:].to_dict()
        Stats3=Stats3.loc[["mean","25%","50%","75%"],:].to_dict()
        for i in Stats.keys():
            Stats[i]={"Win% (Best Rank)":Wins_best_Rank[i],"Win% (Average Rank)":Win_percentage_Average_Rank[i]}|Stats[i]
        Stats
        df_AverageRank
        df = pd.DataFrame(Stats)
        df1=pd.DataFrame(Stats2)
        df2=pd.DataFrame(Stats3)
        columns = pd.MultiIndex.from_tuples(
            [
                ('Win% (Best Rank)', ""),
                ('Win% (Average Rank)', ""),
                ("Average Points","mean"),
                ("Average Points","25%"),
                ("Average Points","50%"),
                ("Average Points",'75%')
            ],
            names=["", ""]
        )
        columns1=pd.MultiIndex.from_tuples(
                [
                    ("Average Rank","mean"),
                    ("Average Rank","25%"),
                    ("Average Rank","50%"),
                    ("Average Rank",'75%')
                ],
                names=["",""]
        )
        columns2=pd.MultiIndex.from_tuples(
                [
                    ("Best Rank","mean"),
                    ("Best Rank","25%"),
                    ("Best Rank","50%"),
                    ("Best Rank",'75%')
                ],
                names=["",""]
        )
        # Transpose to make keys (Random1, Random2) rows
        df = df.T
        df1=df1.T
        df2=df2.T
        df.columns=columns
        df1.columns=columns1
        df2.columns=columns2
        df=pd.concat([df,df1,df2],axis=1)
        return df
