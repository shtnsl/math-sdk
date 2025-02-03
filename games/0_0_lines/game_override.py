from game_executables import *
from src.calculations.statistics import get_random_outcome

class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset 
    """

    def reset_book(self):
        #Reset global values used across multiple projects
        super().reset_book()
        #Reset parameters relevant to local game only
        self.emit_win_event = True
        self.cumulativePrize = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            'M': [self.assign_mult_property],
            'W': [self.assign_mult_property]
        }

    def assign_mult_property(self, symbol):
        if self.gametype == self.config.free_game_type:
            multiplier_value = get_random_outcome(self.get_current_distribution_conditions()["multiplierValues"][self.gametype])
            symbol.assign_attribute({'multiplier': multiplier_value})
        elif self.gametype == self.config.base_game_type:
            symbol.assign_attribute({'multiplier': 1})

    
    def check_repeat(self):
        super().check_repeat()
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True 
                return 
            if win_criteria == None and self.final_win == 0:
                self.repeat = True 
                return 
            
