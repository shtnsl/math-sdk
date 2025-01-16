from game_calculations import GameCalculations
from game_events import ApplyMutToTumbleWinEvent
from src.events.events import updateGlobalMultEvent

class GameExecutables(GameCalculations):

    def applyAndUpdateGlobalMult(self):
        """
        In freepsins, we want to apply a multiplier if there is a multiplier and a winning combination on the board
        """
        boardMult = 0
        for reel in range(len(self.board)):
            for row in range(len(self.board)):
                if self.board[reel][row].name == "M":
                    boardMult += self.board[reel][row].multiplier

        boardMult = max(boardMult, 1)
        if boardMult > 1:
            if self.globalMult == 1:
                self.globalMult = boardMult
            else:
                self.globalMult += boardMult

            finalSpinWin = self.spinWin * self.globalMult
            self.runningBetWin += finalSpinWin
            self.spinWin  = finalSpinWin 
            if self.gameType == self.config.baseGameType:
                self.baseGameWins += finalSpinWin 
            elif self.gameType == self.config.freeGameType:
                self.freeGameWins += finalSpinWin

            self.tumbleWinMultiplier = self.globalMult
            ApplyMutToTumbleWinEvent(self)
            updateGlobalMultEvent(self)
            self.evaluateWinCap()