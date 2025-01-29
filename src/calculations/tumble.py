from copy import deepcopy
from src.events.events import setWinEvent, setTotalWinEvent

class Tumble:
    
    def tumbleBoard(self) -> None:
        self.tumbles += 1
        self.boardBeforeTumble = deepcopy(self.board)
        staticBoard = deepcopy(self.board)
        self.newSymbolsFromTumble = [[] for _ in range(len(staticBoard))]

        for reel in range(len(staticBoard)):
            explodingSymbols = 0
            copyReel = staticBoard[reel]
            for row in range(len(staticBoard[reel])):
                if staticBoard[reel][-1-row].checkAttribute('explode'):
                    explodingSymbols += 1
            
            for i in range(explodingSymbols):
                newReelPos = (self.reelPositions[reel]-1)%len(self.reelStrip[reel])
                self.reelPositions[reel] = newReelPos
                if i == 0 and self.config.includePadding:
                    insertSym = self.topSymbols[reel]
                else:
                    insertSym = self.createSymbol(str(self.reelStrip[reel][(newReelPos) % len(self.reelStrip[reel])]))
                copyReel.insert(0, insertSym)
                self.newSymbolsFromTumble[reel].append(insertSym)
        
            copyReel = [sym for sym in copyReel if not sym.checkAttribute('explode')]
            if len(copyReel) != self.config.numRows[reel]:
                raise RuntimeError(f"new reel length must match expected board size:\n expected: {self.config.numRows[reel]} \n actual: {len(copyReel)}")
            staticBoard[reel] = copyReel

        #update topSymbol positions
        if self.config.includePadding:
            self.topSymbols = [[] for _ in range(self.config.numReels)]
            for reel in range(self.config.numReels):
                self.topSymbols[reel] = self.createSymbol(str(self.reelStrip[reel][(self.reelPositions[reel] - 1)%len(self.reelStrip[reel])]))

        for reel in range(len(staticBoard)):
            for row in range(len(staticBoard[reel])):
                if staticBoard[reel][row].checkAttribute('explode'):
                    print('here')
        self.getSpecialSymbolsOnBoard()
        self.board = staticBoard

    def setEndOfTumbleWins(self) -> None:
        if self.winManager.spinWin > 0:
            setWinEvent(self)
        setTotalWinEvent(self)