import random
from state.state import *
from copy import deepcopy
from calculations.statistics import getRandomOutcome
from calculations.symbol import Symbol
from typing import List

class Board(GeneralGameState):
    def createBoardFromReelStrips(self) -> None:
        if self.config.includePaddingSymbols:
            topSymbols = []
            bottomSymbols = []
        self.refreshSpecalSymbolsOnBoard()
        if type(self.getCurrentDistributionConditions()['reelWeights'][self.gameType]) != dict:
            print('here')
        self.reelStripId = getRandomOutcome(self.getCurrentDistributionConditions()['reelWeights'][self.gameType])
        self.reelStrip = self.config.reels[self.reelStripId]
        anticipation = [0]*self.config.numReels
        board = [[]]*self.config.numReels
        for i in range(self.config.numReels):
            board[i] = [0]*self.config.numRows[i]
        reelPositions = [random.randrange(0, len(self.reelStrip[reel])) for reel in range(self.config.numReels)]
        paddingPositions = [0]*self.config.numReels
        firstScatterReel = -1
        for reel in range(self.config.numReels):
            reelPos = reelPositions[reel]
            if self.config.includePaddingSymbols:
                topSymbols.append(self.createSymbol(self.reelStrip[reel][(reelPos-1) % len(self.reelStrip[reel])]))
                bottomSymbols.append(self.createSymbol(self.reelStrip[reel][(reelPos+len(board[reel])) % len(self.reelStrip[reel])]))
            for row in range(self.config.numRows[reel]):
                symbolID = self.reelStrip[reel][(reelPos+row) % len(self.reelStrip[reel])]
                sym = self.createSymbol(symbolID)
                board[reel][row] = sym

                for specialSymbol in self.specialSymbolsOnBoard:
                    if sym.special:
                        self.specialSymbolsOnBoard[specialSymbol] += [{"reel": reel, "row": row}]
                        if hasattr(sym, 'scatter') and len(self.specialSymbolsOnBoard[specialSymbol]) >= self.config.anticipationTriggers[self.gameType] and firstScatterReel == -1:
                                firstScatterReel = reel+1
            paddingPositions[reel] = (reelPositions[reel]+len(board[reel])+1) % len(self.reelStrip[reel])

        if firstScatterReel > -1:
            count = 1
            for reel in range(firstScatterReel, self.config.numReels):
                if reel != len(self.board) - 1:
                    anticipation[reel] = count
                    count += 1

        self.board = board
        self.reelPositions = reelPositions
        self.paddingPosition = paddingPositions
        self.anticipation = anticipation
        if self.config.includePaddingSymbols:
            self.topSymbols = topSymbols
            self.bottomSymbols = bottomSymbols

    def forceBoardFromReelStrips(self, reelStripId:str, forceStopPositions:List[List]) -> None:
        if self.config.includePaddingSymbols:
            topSymbols = []
            bottomSymbols = []
        self.refreshSpecalSymbolsOnBoard()
        self.reelStripId = reelStripId
        self.reelStrip = self.config.reels[self.reelStripId]
        anticipation = [0]*self.config.numReels
        board = [[]]*self.config.numReels
        for i in range(self.config.numReels):
            board[i] = [0]*self.config.numRows[i]
        
        reelPositions = [None]*self.config.numReels
        for r,s in forceStopPositions.items():
            reelPositions[r] = s - random.randint(0, self.config.numRows[r]-1)
        for r in range(len(reelPositions)):
            if reelPositions[r] == None:
                reelPositions[r] = random.randrange(0, len(self.reelStrip[r]))

        paddingPositions = [0]*self.config.numReels
        firstScatterReel = -1
        for reel in range(self.config.numReels):
            reelPos = reelPositions[reel]
            if self.config.includePaddingSymbols:
                topSymbols.append(self.createSymbol(self.reelStrip[reel][(reelPos-1) % len(self.reelStrip[reel])]))
                bottomSymbols.append(self.createSymbol(self.reelStrip[reel][(reelPos+len(board[reel])) % len(self.reelStrip[reel])]))
            for row in range(self.config.numRows[reel]):
                symbolID = self.reelStrip[reel][(reelPos+row) % len(self.reelStrip[reel])]
                sym = self.createSymbol(symbolID)
                board[reel][row] = sym

                if sym.special:
                    for specialSymbol in self.specialSymbolsOnBoard:
                        for s in self.config.specialSymbols[specialSymbol]:
                            if board[reel][row].name == s:
                                self.specialSymbolsOnBoard[specialSymbol] += [{"reel": reel, "row": row}]
                                if hasattr(sym, 'scatter') and len(self.specialSymbolsOnBoard[specialSymbol]) >= self.config.anticipationTriggers[self.gameType] and firstScatterReel == -1:
                                        firstScatterReel = reel+1
                paddingPositions[reel] = (reelPositions[reel]+len(board[reel])+1) % len(self.reelStrip[reel])

        if firstScatterReel > -1:
            count = 1
            for reel in range(firstScatterReel, self.config.numReels):
                anticipation[reel] = count 
                count += 1
                if reel == self.config.numReels - 1 and anticipation[reel-2] == 0:
                    anticipation[reel] = 0

        self.board = board
        self.reelPositions = reelPositions
        self.paddingPosition = paddingPositions
        self.anticipation = anticipation
        if self.config.includePaddingSymbols:
            self.topSymbols = topSymbols
            self.bottomSymbols = bottomSymbols

    def createSymbol(self, name) -> object:
        if name not in self.validSymbols:
            raise ValueError(f"Symbol '{name}' is not registered.")
        "Leave valid symbol registery unaltered"
        symObject = deepcopy(self.validSymbols[name])
        symObject.applySpecialFunction()  
        return symObject
    
    def refreshSpecalSymbolsOnBoard(self) -> None:
        self.specialSymbolsOnBoard = {}
        for s in self.config.specialSymbols:
            self.specialSymbolsOnBoard[s] = []
            
    def getSpecialSymbolsOnBoard(self) -> None:
        self.refreshSpecalSymbolsOnBoard()
        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                if self.board[reel][row].special:
                    for specialType in list(self.specialSymbolsOnBoard.keys()):
                           if self.board[reel][row].specialType:
                               self.specialSymbolsOnBoard[specialType].append({'reel': reel, 'row': row})

    def transposeBoardString(self, boardString: List[List[str]]) -> List[List[str]]:
        return [list(row) for row in zip(*boardString)]

    def printBoard(self, board: List[List[object]]) -> List[List[str]]:
        stringBoard = []
        maxSymLength = max(len(sym.name) for row in board for sym in row) + 1
        boardString = [[sym.name.ljust(maxSymLength) for sym in reel] for reel in board]
        transposedBoard = self.transposeBoardString(boardString)
        for row in transposedBoard:
            stringBoard.append("".join(row))
            print("".join(row))
        return stringBoard
    
    def boardString(self, board:List[List[object]]):
        boardStr = []*self.config.numReels
        for reel in range(len(board)):
            boardStr.append([x.name for x in board[reel]])
        return boardStr

    def __str__(self):
        return self.printBoard(self.board)