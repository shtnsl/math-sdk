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
            while self.tumbleWin > 0:
                self.evaluateScatterPaysAndTumble()
                self.calculateWins(winType="scatterWins", emitWinEvent=True) 

            if self.spinWin > 0: 
                self.setEndOfTumbleWins()
    
            if self.checkFreespinCondition():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            self.updateFreeSpin()
            self.drawBoard()
            self.calculateWins(winType="scatterWins", emitWinEvent=True)
            
            while self.tumbleWin > 0:
                self.evaluateScatterPaysAndTumble()
                self.calculateWins(winType="scatterWins", emitWinEvent=True) 

            if self.spinWin > 0: 
                self.setEndOfTumbleWins()
    
            if self.checkFreespinCondition():
                self.runFreeSpinFromBaseGame()