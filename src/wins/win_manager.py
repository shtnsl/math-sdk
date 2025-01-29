class WinManager:
    def __init__(self, baseGameMode, freeGameMode):
        self.baseGameMode = baseGameMode
        self.freeGameMode = freeGameMode

        #Updates win amounts across all simulations
        self.totalCumulativeWins = 0
        self.cumulativeBaseWins = 0
        self.cumulativeFreeWins = 0

        #Base-game and free-game wins for a specific simulation
        self.runningBetWin = 0.0

        #Controls wins for a specific simulation number
        self.baseGameWins = 0.0
        self.freeGameWins = 0.0

        #Controls wins for all actions within a 'Reveal' event
        self.spinWin = 0.0
        self.tumbleWin = 0.0 

    def updateSpinWin(self, winAmount:float):
        self.spinWin += winAmount 
        self.runningBetWin += winAmount

    def setSpinWin(self, winAmount:float):
        runningDiff = (winAmount - self.spinWin)
        self.spinWin = winAmount
        self.runningBetWin += runningDiff

    def resetSpinWin(self):
        self.spinWin = 0.0

    def updateGameTypeWins(self, gameType: str):
        if self.baseGameMode.lower() == gameType.lower():
            self.baseGameWins += self.spinWin 
        elif self.freeGameMode.lower() == gameType.lower():
            self.freeGameWins += self.spinWin 
        else:
            raise RuntimeError("Must define a valid gameType")

    def updateEndRoundWins(self):
        self.totalCumulativeWins += (self.baseGameWins + self.freeGameWins)
        self.cumulativeBaseWins += self.baseGameWins 
        self.cumulativeFreeWins += self.freeGameWins  

    def resetEndOfRoundWins(self):
        self.baseGameWins = 0.0
        self.freeGameWins = 0.0
       
        self.runningBetWin = 0.0
        self.spinWin = 0.0 
        self.tumbleWin = 0.0 

    def resetEndOfSpinWin(self):
        self.spinWin = 0.0 
    
    def resetTumbleWin(self):
        self.tumbleWin = 0.0
