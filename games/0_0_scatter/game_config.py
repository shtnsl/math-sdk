from src.config.config import Config
from src.config.distributions import Distribution, DistributionConditions
from src.write_data.force import *
from src.config.bet_mode import BetMode

class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.game_id = "0_0_scatter"
        self.game_name = "sample_scatter"
        self.provider_numer = int(self.game_id.split("_")[0])
        self.working_name = "Sample scatter pay (pay anywhere)"
        self.wincap = 5000.0
        self.win_type = "scatter"
        self.rtp = 0.9700
        self.construct_paths(self.game_id)
        
        # Game Dimensions
        self.num_reels = 6
        self.num_rows = [5]*self.num_reels #Optionally include variable number of rows per reel
        #Board and Symbol Properties
        t1, t2, t3, t4 =  (8, 9), (9, 10), (10, 12), (13,36)
        pay_group = {
            (t1, 'H1'): 3.0, (t2, 'H1'): 7.5, (t3, 'H1'): 15.0, (t4, 'H1'): 60.0,
            (t1, 'H2'): 2.0, (t2, 'H2'): 5.0, (t3, 'H2'): 10.0, (t4, 'H2'): 40.0,
            (t1, 'H3'): 1.3, (t2, 'H3'): 3.2, (t3, 'H3'): 7.0, (t4, 'H3'): 30.0,
            (t1, 'H4'): 1.0, (t2, 'H4'): 2.5, (t3, 'H4'): 6.0, (t4, 'H4'): 20.0,
            (t1, 'L1'): 0.6, (t2, 'L1'): 1.5, (t3, 'L1'): 4.0, (t4, 'L1'): 10.0,
            (t1, 'L2'): 0.4, (t2, 'L2'): 1.2, (t3, 'L2'): 3.5, (t4, 'L2'): 8.0,
            (t1, 'L3'): 0.2, (t2, 'L3'): 0.8, (t3, 'L3'): 2.5, (t4, 'L3'): 5.0,
            (t1, 'L4'): 0.1, (t2, 'L4'): 0.5, (t3, 'L4'): 1.5, (t4, 'L4'): 4.0,
        }   
        self.paytable = self.convert_range_table(pay_group)
    
        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["M"]
        }

        self.freeSpinTriggers = {
           self.base_game_type : {3: 8, 4: 12, 5: 15},
           self.free_game_type: {2: 3, 3:5, 4: 8, 5: 12}
        }
        self.anticipation_triggers = {
            self.base_game_type : min(self.freeSpinTriggers[self.base_game_type ].keys())-1,
            self.free_game_type: min(self.freeSpinTriggers[self.free_game_type].keys())-1
        }
        #Reels
        reels = {
            "BR0": "BR0.csv",
            "FR0": "FR0.csv"
        }
        self.reels = {}
        for r,f in reels.items():
            self.reels[r] = self.read_reels_csv(str.join("/",[self.reelsPath,f]))

        self.padding_reels[self.base_game_type] = self.reels["BR0"]
        self.padding_reels[self.free_game_type] = self.reels["FR0"]
        self.bet_modes = [
            BetMode(
                name = "base",
                title= "standard game entry",
                description = "default game entry type",
                cost = 1.0,
                rtp = self.rtp,
                max_win = self.wincap,
                auto_close_disables = False,
                is_feature = True,
                is_enhanced_mode = False,
                is_buy_bonus = False,
                distributions = [
                    Distribution(
                        criteria="winCap", 
                        quota=0.001, 
                        # winCriteria=self.wincap, 
                        conditions = {
                            "reel_weights": {self.base_game_type : {"BR0":1}, self.free_game_type: {"FR0":1}},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.free_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "scatterTriggers": {4:1, 5:2},
                            "force_wincap": True,
                            "force_freespins": True
                        }),
                    Distribution(
                        criteria="freeGame", 
                        quota=0.1, 
                        conditions= {
                            "reel_weights": {self.base_game_type: {"BR0": 1}, self.free_game_type: {"FR0":1}},
                            "scatterTriggers": {3:20, 4:5, 5:1},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.free_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "force_wincap": False,
                            "force_freespins": True
                        }),
                    Distribution(
                        criteria="0", 
                        quota=0.4, 
                        winCriteria=0.0, 
                        conditions= {
                            "reel_weights": {self.base_game_type: {"BR0": 1}},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.free_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "force_wincap": False,
                            "force_freespins": False
                        }),
                    Distribution(
                        criteria="baseGame", 
                        quota=0.5, 
                        conditions= {
                            "reel_weights": {self.base_game_type: {"BR0": 1}},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "force_wincap": False,
                            "force_freespins": False
                    })
                ]
            ),
            BetMode(
                name = "bonus",
                title= "buy bonus game entry",
                description = "by bonus 1",
                cost = 200,
                rtp = self.rtp,
                max_win = self.wincap,
                auto_close_disables = False,
                is_feature = False,
                is_enhanced_mode = False,
                is_buy_bonus = True,
                distributions = [
                    Distribution(
                        criteria="winCap", 
                        quota=0.001, 
                        # winCriteria=self.wincap, 
                        conditions = {
                            "reel_weights": {self.base_game_type : {"BR0":1}, self.free_game_type: {"FR0":1}},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.free_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "scatterTriggers": {4:1, 5:2},
                            "force_wincap": True,
                            "force_freespins": True
                        }),
                    Distribution(
                        criteria="freeGame", 
                        quota=0.1, 
                        conditions= {
                            "reel_weights": {self.base_game_type: {"BR0": 1}, self.free_game_type: {"FR0":1}},
                            "scatterTriggers": {3:20, 4:5, 5:1},
                            "multiplierValues": {self.base_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}, self.free_game_type: {2:100, 3:80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1}},
                            "force_wincap": False,
                            "force_freespins": True
                        }),
                ]
            ),
        ]
        
        # Optimisation(rtp, avgWin, hit-rate, recordConditions)