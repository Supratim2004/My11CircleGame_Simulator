import copy
class GameRules:
    """Class to define the game-wide rules."""
    MAX_PLAYERS = 11
    CREDIT_CAP = 100

class PlayerRoles:

    """Class to define rules for player roles in the team."""
    ROLES = {
        "Batter": {"min": 1, "max": 8},
        "Bowler": {"min": 1, "max": 8},
        "Allrounder": {"min": 1, "max": 8},
        "Wicketkeeper": {"min": 1, "max": 8},
    }
    Team_Quota={"Team":{"Max":10}}
class ScoringRules:
    """Class to define scoring rules."""
    SCORING = {
        "Played":4,
        "Batting": {
            "Runs": 1,
            "Fours": 1,
            "Sixes": 2,
            "Thirties": 4,
            "Fifties": 8,
            "Hundreds": 16,
            "StrikeRate(20 runs or 10 balls)":{
                "<50": -6,
                "50-59.99": -4,
                "60-69.99": -2,
                "70-129.99": 0,
                "130-149.99": 2,
                "150-169.99": 4,
                "170+": 6
            },
            "Punishment(ExcludingBowlers)":{"Duck": -2}
        },
        "Bowling": {
            "Wickets": 25,
            "Maidens": 12,
            "LBW/Bowled": 8,
            "3Wickets": 4,
            "4Wickets": 8,
            "5Wickets": 16,
            "EconomyRate(>=2overs)":{
                "<5": 6,
                "5-5.99": 4,
                "6-6.99": 2,
                "7-9.99": 0,
                "10-10.99": -2,
                "11-11.99": -4,
                "12+": -6        
            }},
         "Fielding" :{
            "Catch": 8,
            "3CatchBonus": 4,
            "Stumping": 12,
            "Run out(Direct)": 12,
            "Run out(Multiple players involved)": 6
         }  
        
    }
class Scorer:
    """Class to calculate scores of each player."""
    @staticmethod
    def Strike_Rate_Bonus(strike_rate):  
        strike_rate_rules = ScoringRules.SCORING["Batting"]["StrikeRate(20 runs or 10 balls)"]
        if strike_rate < 50:
            return strike_rate_rules["<50"]
        elif 50 <= strike_rate < 60:
            return strike_rate_rules["50-59.99"]
        elif 60 <= strike_rate < 70:
            return strike_rate_rules["60-69.99"]
        elif 70 <= strike_rate < 130:
            return strike_rate_rules["70-129.99"]
        elif 130 <= strike_rate < 150:
            return strike_rate_rules["130-149.99"]
        elif 150 <= strike_rate < 170:
            return strike_rate_rules["150-169.99"]
        else:
            return strike_rate_rules["170+"]
    @staticmethod
    def calculate_economy_rate_bonus(economy_rate):
        economy_rate_rules = ScoringRules.SCORING["Bowling"]["EconomyRate(>=2overs)"]
        if economy_rate < 5:
            return economy_rate_rules["<5"]
        elif 5 <= economy_rate < 6:
            return economy_rate_rules["5-5.99"]
        elif 6 <= economy_rate < 7:
            return economy_rate_rules["6-6.99"]
        elif 7 <= economy_rate < 10:
            return economy_rate_rules["7-9.99"]
        elif 10 <= economy_rate < 11:
            return economy_rate_rules["10-10.99"]
        elif 11 <= economy_rate < 12:
            return economy_rate_rules["11-11.99"]
        else:
            return economy_rate_rules["12+"]
    @staticmethod
    def calculate_career_points(player_obj):
        Stats=player_obj.stats
        Career_points=0
        Points=0
        # Calculate batting score
        Points+=Stats.batting.Runs*ScoringRules.SCORING["Batting"]["Runs"]
        Points+=Stats.batting.Fours*ScoringRules.SCORING["Batting"]["Fours"]
        Points+=Stats.batting.Sixes*ScoringRules.SCORING["Batting"]["Sixes"]
        Points+=Stats.batting.Thirties*ScoringRules.SCORING["Batting"]["Thirties"]
        Points+=Stats.batting.Fifties*ScoringRules.SCORING["Batting"]["Fifties"]
        Points+=Stats.batting.Hundreds*ScoringRules.SCORING["Batting"]["Hundreds"]
        """if Stats.batting.BF>=10 or Stats.batting.Runs>=20:
                    Points += Scorer.Strike_Rate_Bonus(Stats.batting.Bat_SR)"""
        if player_obj.Type!="Bowler":
            Points += Stats.batting.Ducks*ScoringRules.SCORING["Batting"]["Punishment(ExcludingBowlers)"]["Duck"]
        Career_points+=Points/max(Stats.batting.MatchesBatted,1) 
        Points=0
        Points += Stats.bowling.Wickets * ScoringRules.SCORING["Bowling"]["Wickets"]
        Points += Stats.bowling.Maidens * ScoringRules.SCORING["Bowling"]["Maidens"]
        #score += Stats.bowling.["LBW/Bowled"] * ScoringRules.SCORING["Bowling"]["LBW/Bowled"]
        Points += Stats.bowling.Three_Wicket_haul * ScoringRules.SCORING["Bowling"]["3Wickets"]
        Points += Stats.bowling.Four_Wicket_haul * ScoringRules.SCORING["Bowling"]["4Wickets"]
        Points += Stats.bowling.Five_Wicket_haul* ScoringRules.SCORING["Bowling"]["5Wickets"]
        Career_points+=Points/max(Stats.bowling.Matches_Bowled,1) 
        Points=0
        Points += Stats.fielding.Catches * ScoringRules.SCORING["Fielding"]["Catch"]
        Points += Stats.fielding.Three_Catches * ScoringRules.SCORING["Fielding"]["3CatchBonus"]
        Points += Stats.fielding.Stumpings * ScoringRules.SCORING["Fielding"]["Stumping"]
        Career_points+=Points/max(max(Stats.batting.MatchesBatted,Stats.bowling.Matches_Bowled),1)
        return Career_points
        """if float(Stats.bowling.Overs)>=2:
            score +=Scorer.calculate_economy_rate_bonus (dict_player["Bowling"]["Economy"])"""
    @staticmethod
    def calculate_score(dict_player):#Passed as dictionary of performance of player
        score = 0
        # Calculate batting score
        if dict_player["Played"]==True:
            score += ScoringRules.SCORING["Played"]
            
            if dict_player["Batting"]["Batted"]==True:
                score += dict_player["Batting"]["Runs"] * ScoringRules.SCORING["Batting"]["Runs"]
                
                score += dict_player["Batting"]["Fours"] * ScoringRules.SCORING["Batting"]["Fours"]
                
                score += dict_player["Batting"]["Sixes"] * ScoringRules.SCORING["Batting"]["Sixes"]
                
                score += (30<=dict_player["Batting"]["Runs"]<50) * ScoringRules.SCORING["Batting"]["Thirties"]
                
                score += (50<=dict_player["Batting"]["Runs"]<100) * ScoringRules.SCORING["Batting"]["Fifties"]
                
                score += (dict_player["Batting"]["Runs"]>=100) * ScoringRules.SCORING["Batting"]["Hundreds"]
                
                if dict_player["Batting"]["BF"]>=10 or dict_player["Batting"]["Runs"]>=20:
                    score += Scorer.Strike_Rate_Bonus(dict_player["Batting"]["SR"])
                    
                if dict_player["Batting"]["Runs"]==0 and dict_player["Role"]!="Bowler":
                    score += ScoringRules.SCORING["Batting"]["Punishment(ExcludingBowlers)"]["Duck"]
                    
            if dict_player["Bowling"]["Bowled"]==True:
                score += dict_player["Bowling"]["Wickets"] * ScoringRules.SCORING["Bowling"]["Wickets"]
                score += dict_player["Bowling"]["Maidens"] * ScoringRules.SCORING["Bowling"]["Maidens"]
                score += dict_player["Bowling"]["LBW/Bowled"] * ScoringRules.SCORING["Bowling"]["LBW/Bowled"]
                score += (dict_player["Bowling"]["Wickets"]==3) * ScoringRules.SCORING["Bowling"]["3Wickets"]
                score += (dict_player["Bowling"]["Wickets"]==4) * ScoringRules.SCORING["Bowling"]["4Wickets"]
                score += (dict_player["Bowling"]["Wickets"]>=5) * ScoringRules.SCORING["Bowling"]["5Wickets"]
                if float(dict_player["Bowling"]["Overs bowled"])>=2:
                    score +=Scorer.calculate_economy_rate_bonus (dict_player["Bowling"]["Economy"])
            if dict_player["Fielding"]["Fielded"]==True:
                score += dict_player["Fielding"]["Catch"] * ScoringRules.SCORING["Fielding"]["Catch"]
                score += (dict_player["Fielding"]["Catch"]>=3) * ScoringRules.SCORING["Fielding"]["3CatchBonus"]
                score += dict_player["Fielding"]["Stumping"] * ScoringRules.SCORING["Fielding"]["Stumping"]
                score += dict_player["Fielding"]["Run out(direct)"] * ScoringRules.SCORING["Fielding"]["Run out(Direct)"]
                score += dict_player["Fielding"]["Run out(indirect)"] * ScoringRules.SCORING["Fielding"]["Run out(Multiple players involved)"]
        return score
class TeamValidator:
    """Class to validate a team based on rules."""
    def __init__(self, team,credits=None):#Take input as output from Agent.Random()
        """
        Initialize the validator with a team and total credits.

        Args:
        team (dict): Dictionary with player roles and counts.
                     Example: {"Batsman": 4, "Bowler": 3, "All-rounder": 2, "Wicketkeeper": 1}
        credits (int): Total credits used by the team.
        """
        self.team = team
        self.credits = credits
    def validate_team(self):
        """Validate the team composition based on game rules."""
        errors = []

        # Check total players
        total_players = len(self.team)
        if total_players != GameRules.MAX_PLAYERS:
            errors.append(f"Total players must be {GameRules.MAX_PLAYERS}, but found {total_players}.")
        
        # Check credits
        if self.credits is not None:
            if self.credits > GameRules.CREDIT_CAP:
                errors.append(f"Total credits exceed the cap of {GameRules.CREDIT_CAP}. Current: {self.credits}")
        #Get team-wise mapping
        team_count=dict()
        for z in self.team:
            #print(z)
            k=z["Match_Player_Stats"]["Team Name"]
            if k not in team_count:
                team_count[k] = 0
            team_count[k]+=1
        for team, count in team_count.items():
            if count > PlayerRoles.Team_Quota["Team"]["Max"]:
                errors.append(f"Too many players from {team}. Maximum allowed: {PlayerRoles.Team_Quota["Team"]["Max"]}. Found: {count}.")
        #Get role-wise mapping
        role_count=copy.deepcopy(PlayerRoles.ROLES)
        for z in role_count.keys():
            role_count[z]=0
        for z in self.team:
            l=z["Match_Player_Stats"]["Player Stats"].Type
            role_count[l]+=1
        # Check role-specific rules
        for role, count in role_count.items():
            role_rules = PlayerRoles.ROLES.get(role)
            if not role_rules:
                errors.append(f"Invalid role: {role}")
                continue
            if count < role_rules["min"]:
                errors.append(f"Not enough {role}s. Minimum required: {role_rules['min']}. Found: {count}.")
            if count > role_rules["max"]:
                errors.append(f"Too many {role}s. Maximum allowed: {role_rules['max']}. Found: {count}.")

        return errors