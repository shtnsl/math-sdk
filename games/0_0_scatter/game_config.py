from src.config.config import Config
from src.config.distributions import Distribution, DistributionConditions
from src.write_data.force import *
from src.config.bet_mode import BetMode

class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.gameId = "0_0_scatter"
        self.providerNumber = int(self.gameId.split("_")[0])
        self.workingName = "Sample scatter pay (pay anywhere)"
        self.winCap = 5000.0
        self.winType = "scatter"
        self.rtp = 0.9700
        self.constructFilePaths(self.gameId)
        
        # Game Dimensions
        self.numReels = 6
        self.numRows = [5]*self.numReels #Optionally include variable number of rows per reel
        #Board and Symbol Properties
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 36)
        payGroup = {
            (t1, 'H1'): 3.0, (t2, 'H1'): 7.5, (t3, 'H1'): 15.0, (t4, 'H1'): 60.0,
            (t1, 'H2'): 2.0, (t2, 'H2'): 5.0, (t3, 'H2'): 10.0, (t4, 'H2'): 40.0,
            (t1, 'H3'): 1.3, (t2, 'H3'): 3.2, (t3, 'H3'): 7.0, (t4, 'H3'): 30.0,
            (t1, 'H4'): 1.0, (t2, 'H4'): 2.5, (t3, 'H4'): 6.0, (t4, 'H4'): 20.0,
            (t1, 'L1'): 0.6, (t2, 'L1'): 1.5, (t3, 'L1'): 4.0, (t4, 'L1'): 10.0,
            (t1, 'L2'): 0.4, (t2, 'L2'): 1.2, (t3, 'L2'): 3.5, (t4, 'L2'): 8.0,
            (t1, 'L3'): 0.2, (t2, 'L3'): 0.8, (t3, 'L3'): 2.5, (t4, 'L3'): 5.0,
            (t1, 'L4'): 0.1, (t2, 'L4'): 0.5, (t3, 'L4'): 1.5, (t4, 'L4'): 4.0,
        }   
        self.payTable = self.convertWinRangeToPayTable(payGroup)
    
        self.includePadding = True
        self.specialSymbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["M"]
        }

        self.freeSpinTriggers = {
           self.baseGameType : {3: 8, 4: 12, 5: 15},
           self.freeGameType: {2: 3, 3:5, 4: 8, 5: 12}
        }
        self.anticipationTriggers = {
            self.baseGameType : min(self.freeSpinTriggers[self.baseGameType ].keys())-1,
            self.freeGameType: min(self.freeSpinTriggers[self.freeGameType].keys())-1
        }
        #Reels
        reels = {
            "BR0": "BR0.csv",
            "FR0": "FR0.csv"
        }
        self.reels = {}
        for r,f in reels.items():
            self.reels[r] = self.readReelsFromCSV(str.join("/",[self.reelsPath,"BR0.csv"]))

        self.betModes = [
            BetMode(
                name = "base",
                title= "standard game entry",
                description = "default game entry type",
                cost = 1.0,
                rtp = self.rtp,
                maxWin = self.winCap,
                autoCloseDisabled = False,
                isFeature = True,
                isEnhancedMode = False,
                isBuyBonus = False,
                distributions = [
                    Distribution(
                        criteria="winCap", 
                        quota=0.001, 
                        winCriteria=self.winCap, 
                        conditions = {
                            "reelWeights": {self.baseGameType : {"BR0":1}, self.freeGameType: {"FR0":1}},
                            "multiplierValues": {self.baseGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.freeGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "scatterTriggers": {4:1, 5:2},
                            "forceWinCap": True,
                            "forceFreeSpins": True
                        }),
                    Distribution(
                        criteria="freeGame", 
                        quota=0.1, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}, self.freeGameType: {"FR0":1}},
                            "scatterTriggers": {3:20, 4:5, 5:1},
                            "multiplierValues": {self.baseGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.freeGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "forceWinCap": False,
                            "forceFreeSpins": True
                        }),
                    Distribution(
                        criteria="0", 
                        quota=0.4, 
                        winCriteria=0.0, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}},
                            "multiplierValues": {self.baseGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.freeGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "forceWinCap": False,
                            "forceFreeSpins": False
                        }),
                    Distribution(
                        criteria="baseGame", 
                        quota=0.5, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}},
                            "multiplierValues": {self.baseGameType: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "forceWinCap": False,
                            "forceFreeSpins": False
                    })
                ]
            ),
        ]
        
        # Optimisation(rtp, avgWin, hit-rate, recordConditions)