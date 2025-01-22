import os, sys 
from game_override import *
from src.state.state import *
from src.events.events import setTotalWinEvent, tumbleBoardEvent, setWinEvent, updateGlobalMultEvent
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from game_config import *
from game_executables import *
from game_calculations import *

class GameState(GameStateOverride):

    def runSpin(self, sim):
        self.resetSeed(sim)
        self.repeat = True
        while self.repeat:
            self.resetBook()

            self.evaluateFinalWin()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        pass