from src.state.state import GeneralGameState

class Conditions(GeneralGameState):
    def inFence(self, *args):
        for arg in args:
            if self.fence == arg:
                return True 
        return False
    
    def inMode(self, *args):
        for arg in args:
            if self.betMode == arg:
                return True 
        return False 
    
    def isMaxWin(self):
        if self.runningBetWin >= self.config.winCap:
            return True 
        return False
    
    def isInGameType(self, *args):
        for arg in args:
            if self.gameType == arg:
                return True 
        return False
