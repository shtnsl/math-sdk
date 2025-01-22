from game_calculations import GameCalculations
from src.events.events import updateGlobalMultEvent, tumbleBoardEvent, winInfoEvent, setWinEvent, setTotalWinEvent, freeSpinsTriggerEvent
from game_events import updateTumbleBoardBannerEvent, sendBoardMultInfoEvent

class GameExecutables(GameCalculations):

    def evaluateScatterPaysAndTumble(self):
        self.winData = self.getScatterPayWinData()
        if self.winData['totalWin'] >0:
            self.updateWinInformation(self.winData)
            winInfoEvent(self)
            updateTumbleBoardBannerEvent(self)
            self.tumbleBoard()
            tumbleBoardEvent(self)

    def tumbleBoardAndSendEvent(self):
        self.tumbleBoard()
        tumbleBoardEvent(self)

    def setEndOfTumbleWins(self):
        boardMult, multInfo = self.getBoardMultipliers()
        self.spinWin *= boardMult
        self.runningBetWin += self.spinWin 
        if self.spinWin> 0 and len(multInfo)>0:
            sendBoardMultInfoEvent(self, boardMult, multInfo)
            updateTumbleBoardBannerEvent(self)
        self.updateGameModeWins(self.spinWin)
        setWinEvent(self)
        if self.spinWin > 0:
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

    def checkFreeSpinEntry(self):
        if not(self.getCurrentDistributionConditions()['forceFreeSpins']):
            self.repeat = True
            return False 
        return True

