from game_calculations import GameCalculations
from events.events import updateGlobalMultEvent, tumbleBoardEvent, winInfoEvent, setWinEvent, setTotalWinEvent
from game_events import updateTumbleBoardBanner, sendBoardMultInfo
class GameExecutables(GameCalculations):

    def evaluateScatterPaysAndTumble(self):
        self.winData = self.getScatterPayWinData()
        revealWin = self.winData['totalWin']
        if revealWin > 0:
            self.updateWinInformation(self.winData)
            winInfoEvent(self)
            updateTumbleBoardBanner(self)
            self.tumbleBoard()
            tumbleBoardEvent(self)

    def tumbleBoardAndSendEvent(self):
        self.tumbleBoard()
        tumbleBoardEvent(self)

    def setEndOfTumbleWins(self):
        boardMult, multInfo = self.getBoardMultipliers()
        self.spinWin *= boardMult
        self.runningBetWin += self.spinWin 
        if len(multInfo) > 0:
            sendBoardMultInfo(self, boardMult, multInfo)
        self.updateGameModeWins(self.spinWin)
        setWinEvent(self)
        if self.spinWin > 0:
            setTotalWinEvent(self)






