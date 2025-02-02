from game_calculations import GameCalculations
from src.events.events import updateGlobalMultEvent, tumbleBoardEvent, winInfoEvent, setWinEvent, setTotalWinEvent, freeSpinsTriggerEvent
from game_events import updateTumbleWinEvent, sendBoardMultInfoEvent
from copy import copy

class GameExecutables(GameCalculations):

    def setEndOfTumbleWins(self):
        if self.gameType == self.config.freeGameType: #Only multipliers in freeSpins
            boardMult, multInfo = self.getBoardMultipliers()
            baseTumbleWin = copy(self.winManager.spinWin)
            self.winManager.setSpinWin(baseTumbleWin * boardMult)
            if self.winManager.spinWin > 0 and len(multInfo)>0:
                sendBoardMultInfoEvent(self, boardMult, multInfo, baseTumbleWin, self.winManager.spinWin)
                updateTumbleWinEvent(self)
            
        if self.winManager.spinWin > 0:
            setWinEvent(self)
        setTotalWinEvent(self)

    def updateGlobalMult(self):
        self.globalMultiplier += 1
        updateGlobalMultEvent(self)

    def updateTotalFreeSpinAmount(self, scatterKey:str = 'scatter'):
        self.totFs = self.countSpecialSymbols(scatterKey) * 2
        if self.gameType == self.config.baseGameType:
            baseGameTrigger, freeGameTrigger = True, False 
        else:
            baseGameTrigger, freeGameTrigger = False, True
        freeSpinsTriggerEvent(self, baseGameTrigger=baseGameTrigger, freeGameTrigger=freeGameTrigger)
