from state.state_conditions import Conditions
from calculations.board import Board
from calculations.lines import LineWins
from calculations.statistics import getRandomOutcome
from events.events import *
from typing import List, Dict

class Executables(Conditions, Board, LineWins):
    """
    The purpose of this Class is to group together common actions which are likely to be reused between games.
    These can be overridden in the GameExecuatables or GameCalculations if game-specific alterations are required
    """

    def drawBoard(self) -> None:
        if self.getCurrentDistributionConditions()["forceFreeSpins"]:
            self.forceSpecialBoard('scatter')
            #force specific symbol combination on board
        else:
            while self.countSpecialSymbols('scatter') >= min(self.config.freeSpinTrigger[self.gameType].keys()):
                self.createBoardFromReelStrips()
        
        revealBoardEvent(self)

    def forceSpecialBoard(self, forceCriteria: str):
        reelStripId = getRandomOutcome(self.getCurrentDistributionConditions()['reelWeights'][self.gameType])
        reelStops = self.getSymbolLocationsOnReel(reelStripId, forceCriteria)
        self.forceBoardFromReelStrips(reelStripId, reelStops)


    def getSymbolLocationsOnReel(self, reelId:str, targetSymbol:str) -> List[List]:
        reel = self.config.reels[reelId]
        reelStopPositions = []*[self.config.numReels]
        for r in range(self.config.numReels):
            for s in range(len(reel[r])):
                if reel[r][s] == targetSymbol:
                    reelStopPositions[r].append(s)

        return reelStopPositions
    
    def calculateWins(self, winType:str = "lineWins") -> ModuleNotFoundError:
        match winType:
            case "lineWins":
                self.calculateLineWins()
            case "scatterWins":
                raise NotImplementedError
            case "clusterWins":
                raise NotImplementedError
            case "waysWins":
                raise NotImplementedError
            case "customWins":
                raise NotImplementedError ("must define custom win evaluation")
            
    def countSpecialSymbols(self, specialSymbolCriteria:str) -> bool:
        return len(self.specialSymbolsOnBoard[specialSymbolCriteria])

    def checkFreespinCondition(self) -> bool:
        if self.countSpecialSymbols('scatter') >= min(self.config.freeSpinTriggers[self.gameType].keys()):
            return True 
        return False
    
    
    def runFreeSpinFromBaseGame(self):
        self.record({"kind": self.countSpecialSymbols('scatter'), "symbol": 'scatter', "gameType": self.gameType})
        self.updateTotalFreeSpinAmount()
        self.runFreeSpin()
        
    def updateTotalFreeSpinAmount(self):
        self.totFs = self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols('scatter')]
        freeSpinsTriggerEvent(self, baseGameTrigger=True)

    def updateFreeSpinRetriggerAmount(self):
        self.totFs += self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols('scatter')]
        freeSpinsTriggerEvent(self, freeGameTrigger=True)
