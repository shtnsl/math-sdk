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

            self.drawBoard()
            self.calculateWins(winType="clusterWins")
            while self.tumbleWin > 0:
                self.tumbleBoard()
                tumbleBoardEvent(self)
                self.calculateWins(winType="clusterWins") 
            
            if self.spinWin > 0: 
                setTotalWinEvent(self) #Only called at end of spin action
    
            if self.checkFreespinCondition():
                self.runFreeSpinFromBaseGame()

            self.evaluateFinalWin()

        self.imprintWins()

    def runFreeSpin(self):
        self.resetFsSpin()
        while self.fs < self.totFs:
            self.updateFreeSpin()
            self.drawBoard()

            self.calculateWins(winType="clusterWins")
            while self.tumbleWin > 0 and not(self.winCapTriggered):
                self.tumbleBoard()
                tumbleBoardEvent(self)
                self.calculateWins(winType="clusterWins")
            
            if self.spinWin > 0 and not(self.winCapTriggered):
                #Update and apply global multiplier to tumble win
                self.applyAndUpdateGlobalMult()
                setWinEvent(self)

            setTotalWinEvent(self)