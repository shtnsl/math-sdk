from src.config.config import Config
from src.config.distributions import Distribution, DistributionConditions
from src.write_data.force import *
from src.config.bet_mode import BetMode

class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.gameId = "0_0_lines"
        self.providerNumber = int(self.gameId.split("_")[0])
        self.workingName = "Sample Lines Game"
        self.winCap = 5000.0
        self.winType = "lines"
        self.rtp = 0.9700
        self.constructFilePaths(self.gameId)
        
        # Game Dimensions
        self.numReels = 5
        self.numRows = [3]*self.numReels
        #Board and Symbol Properties
        self.payTable = {
            (5, 'W'): 20, (4, 'W'): 10,	(3, 'W'): 5,
            (5, 'H1'): 20, (4, 'H1'): 10,	(3, 'H1'): 5,
            (5, 'H2'): 15,	(4, 'H2'): 5,	(3, 'H2'): 3,
            (5, 'H3'): 10,	(4, 'H3'): 3,	(3, 'H3'): 2,
            (5, 'H4'): 8,	(4, 'H4'): 2,	(3, 'H4'): 1,
            (5, 'L1'): 5,	(4, 'L1'): 1,	(3, 'L1'): 0.5,
            (5, 'L2'): 3,	(4, 'L2'): 0.7,	(3, 'L2'): 0.3,
            (5, 'L3'): 3,	(4, 'L3'): 0.7,	(3, 'L3'): 0.3,
            (5, 'L4'): 2,	(4, 'L4'): 0.5,	(3, 'L4'): 0.2,
            (5, 'L5'): 1,	(4, 'L5'): 0.3,	(3, 'L5'): 0.1
        }

        self.payLines = {
            1:	[	0,	0,	0,	0,	0,	],
            2:	[	1,	1,	1,	1,	1,	],
            3:	[	2,	2,	2,	2,	2,	],
            4:	[	0,	1,	2,	1,	0,	],
            5:	[	2,	1,	0,	1,	2,	],
            6:	[	0,	0,	1,	2,	2,	],
            7:	[	2,	2,	1,	0,	0,	],
            8:	[	1,	0,	1,	2,	1,	],
            9:	[	1,	2,	1,	0,	1,	],
            10:	[	0,	1,	1,	1,	2,	],
            11:	[	2,	1,	1,	1,	0,	],
            12:	[	0,	1,	0,	1,	2,	],
            13:	[	2,	1,	2,	1,	0,	],
            14:	[	1,	1,	0,	1,	1,	],
            15:	[	1,	1,	2,	1,	1,	],
            16:	[	0,	2,	1,	0,	2,	],
            17:	[	2,	0,	1,	2,	0,	],
            18:	[	0,	0,	2,	0,	0,	],
            19:	[	2,	2,	0,	2,	2,	],
            20:	[	1,	0,	0,	0,	1,	],

        }
    
        self.includePadding = True
        self.specialSymbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["M", "W"]
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
                        # winCriteria=self.winCap, 
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