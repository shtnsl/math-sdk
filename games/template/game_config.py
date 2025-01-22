from src.config.config import Config
from src.config.distributions import Distribution, DistributionConditions
from src.write_data.force import *
from src.config.bet_mode import BetMode

class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.gameId = ""
        self.providerNumber = 0
        self.workingName = ""
        self.winCap = 0
        self.winType = ""
        self.rtp = 0
        self.constructFilePaths(self.gameId)
        
        # Game Dimensions
        self.numReels = 0
        self.numRows = [0]*self.numReels #Optionally include variable number of rows per reel
        #Board and Symbol Properties
        self.payTable = {}
    
        self.includePadding = True
        self.specialSymbols = {
            "wild": [],
            "scatter": [],
            "multiplier": []
        }

        self.freeSpinTriggers = {
           self.baseGameType : {},
           self.freeGameType: {}
        }
        self.anticipationTriggers = {
            self.baseGameType : 0,
            self.freeGameType:0
        }
        #Reels
        reels = {
            "BR0": "BR0.csv",
            "FR0": "FR0.csv"
        }
        self.reels = {}
        for r,f in reels.items():
            self.reels[r] = self.readReelsFromCSV(str.join("/",[self.reelsPath,f]))

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
                            "scatterTriggers": {},
                            "forceWinCap": True,
                            "forceFreeSpins": True
                        }),
                    Distribution(
                        criteria="freeGame", 
                        quota=0.1, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}, self.freeGameType: {"FR0":1}},
                            "scatterTriggers": {},
                            "forceWinCap": False,
                            "forceFreeSpins": True
                        }),
                    Distribution(
                        criteria="0", 
                        quota=0.4, 
                        winCriteria=0.0, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}},
                            "forceWinCap": False,
                            "forceFreeSpins": False
                        }),
                    Distribution(
                        criteria="baseGame", 
                        quota=0.5, 
                        conditions= {
                            "reelWeights": {self.baseGameType: {"BR0": 1}},
                            "forceWinCap": False,
                            "forceFreeSpins": False
                    })
                ]
            ),
        ]
        