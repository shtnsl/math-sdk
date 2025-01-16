from copy import deepcopy
from src.calculations.board import Board

class Tumble:
    
    def tumbleBoard(self):
        self.tumbles += 1
        self.boardBeforeTumble = deepcopy(self.board)
        staticBoard = deepcopy(self.board)
        self.newSymbolsFromTumble = [[] for _ in range(len(staticBoard))]

        for reel in range(len(staticBoard)):
            explodingSymbols = 0
            copyReel = deepcopy(staticBoard[reel])
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

            symsToRemove = []
            for sym in range(len(copyReel)):
                if copyReel[sym].checkAttribute('explode'):
                    symsToRemove.append(copyReel[sym])
            for sym in symsToRemove:
                copyReel.remove(sym)
            
            if len(copyReel) != len(self.board[reel]):
                raise RuntimeError("Incorect Reel Lengths")
        
            staticBoard[reel] = copyReel

        #update topSymbol positions
        if self.config.includePadding:
            self.topSymbols = [[] for _ in range(self.config.numReels)]
            for reel in range(self.config.numReels):
                self.topSymbols[reel] = self.createSymbol(str(self.reelStrip[reel][(self.reelPositions[reel] - 1)%len(self.reelStrip[reel])]))

        self.getSpecialSymbolsOnBoard()
        self.board = deepcopy(staticBoard)