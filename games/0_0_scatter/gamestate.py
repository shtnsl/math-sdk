import os, sys 
from game_override import *
from src.state.state import *
from src.events.events import setTotalWinEvent, tumbleBoardEvent
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

            self.drawBoard()
            self.evaluateScatterPaysAndTumble()
            #Cumulative wins in tumble banner (with globalmult applied at each update)
            while self.tumbleWin > 0:
                self.evaluateScatterPaysAndTumble()

            if self.spinWin > 0: 
                self.setEndOfTumbleWins()
    
            if self.checkFreespinCondition() and self.checkFreeSpinEntry():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()
            self.checkRepeat()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            #Resets global multiplier at each spin
            self.updateFreeSpin()
            self.drawBoard()
            self.evaluateScatterPaysAndTumble()
            
            while self.tumbleWin > 0:
                self.updateGlobalMult()
                self.evaluateScatterPaysAndTumble()
            
            if self.spinWin > 0: 
                self.setEndOfTumbleWins()
    
            if self.checkFreespinCondition():
                pass #send retriggers
                # self.runFreeSpinFromBaseGame()