class WinManager:
    def __init__(self, baseGameMode, freeGameMode):
        self.baseGameMode = baseGameMode
        self.freeGameMode = freeGameMode

        #Updates win amounts across all simulations
        self.total_cumulative_wins = 0
        self.cumulative_base_wins = 0
        self.cumulative_free_wins = 0

        #Base-game and free-game wins for a specific simulation
        self.running_bet_win = 0.0

        #Controls wins for a specific simulation number
        self.base_game_wins = 0.0
        self.freegame_wins = 0.0

        #Controls wins for all actions within a 'Reveal' event
        self.spinWin = 0.0
        self.tumble_win = 0.0 

    def updateSpinWin(self, winAmount:float):
        self.spinWin += winAmount 
        self.running_bet_win += winAmount

    def set_spin_win(self, winAmount:float):
        runningDiff = (winAmount - self.spinWin)
        self.spinWin = winAmount
        self.running_bet_win += runningDiff

    def reset_spin_win(self):
        self.spinWin = 0.0

    def updateGameTypeWins(self, gameType: str):
        if self.baseGameMode.lower() == gameType.lower():
            self.base_game_wins += self.spinWin 
        elif self.freeGameMode.lower() == gameType.lower():
            self.freegame_wins += self.spinWin 
        else:
            raise RuntimeError("Must define a valid gameType")

    def update_end_round_wins(self):
        self.total_cumulative_wins += (self.base_game_wins + self.freegame_wins)
        self.cumulative_base_wins += self.base_game_wins 
        self.cumulative_free_wins += self.freegame_wins  

    def reset_end_round_wins(self):
        self.base_game_wins = 0.0
        self.freegame_wins = 0.0
       
        self.running_bet_win = 0.0
        self.spinWin = 0.0 
        self.tumble_win = 0.0 

    def resetEndOfSpinWin(self):
        self.spinWin = 0.0 
    
    def resetTumbleWin(self):
        self.tumble_win = 0.0
