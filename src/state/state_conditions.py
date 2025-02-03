from src.state.state import GeneralGameState

class Conditions(GeneralGameState):
    def inFence(self, *args):
        for arg in args:
            if self.fence == arg:
                return True 
        return False
    
    def inMode(self, *args):
        for arg in args:
            if self.bet_mode == arg:
                return True 
        return False 
    
    def isMaxWin(self):
        if self.running_bet_win >= self.config.wincap:
            return True 
        return False
    
    def isInGameType(self, *args):
        for arg in args:
            if self.gametype == arg:
                return True 
        return False
