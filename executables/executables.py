from state.state_conditions import Conditions
from calculations.board import Board
from calculations.lines import LineWins
from calculations.statistics import getRandomOutcome
from events.events import *
from typing import List, Dict
import random 
import numpy as np

class Executables(Conditions, Board, LineWins):
    """
    The purpose of this Class is to group together common actions which are likely to be reused between games.
    These can be overridden in the GameExecuatables or GameCalculations if game-specific alterations are required
    """

    def drawBoard(self, emitEvent:bool = True) -> None:
        self.refreshSpecalSymbolsOnBoard()
        if self.getCurrentDistributionConditions()["forceFreeSpins"]:
            numScatters = getRandomOutcome(self.getCurrentDistributionConditions()["scatterTriggers"])
            self.forceSpecialBoard('scatter', numScatters)
        else:
            self.createBoardFromReelStrips()
            while self.countSpecialSymbols('scatter') >= min(self.config.freeSpinTriggers[self.gameType].keys()):
                self.createBoardFromReelStrips()
        if emitEvent:
            revealBoardEvent(self)

    def forceSpecialBoard(self, forceCriteria: str, numForceSymbols: int):
        reelStripId = getRandomOutcome(self.getCurrentDistributionConditions()['reelWeights'][self.gameType])
        reelStops = self.getSymbolLocationsOnReel(reelStripId, forceCriteria)

        symbolProb = []
        for x in range(self.config.numReels):
            symbolProb.append(len(reelStops[x])/len(self.config.reels[reelStripId][x]))
        forceStopPositions = {}
        while len(forceStopPositions) != numForceSymbols:
            chosenReel = random.choices(list(np.arange(0,self.config.numReels)),symbolProb)[0]
            chosenStop = random.choice(reelStops[chosenReel])
            symbolProb[chosenReel] = 0
            forceStopPositions[int(chosenReel)] = int(chosenStop)
        
        forceStopPositions = dict(sorted(forceStopPositions.items(), key=lambda x: x[0]))
        self.forceBoardFromReelStrips(reelStripId, forceStopPositions)


    def getSymbolLocationsOnReel(self, reelId:str, targetSymbol:str) -> List[List]:
        reel = self.config.reels[reelId]
        reelStopPositions = [[] for _ in range(self.config.numReels)]
        for r in range(self.config.numReels):
            for s in range(len(reel[r])):
                if reel[r][s] in self.config.specialSymbols[targetSymbol]: 
                    reelStopPositions[r].append(s)

        return reelStopPositions
    
    def calculateWins(self, winType:str = None, emitEvent:bool = None, emitWinEvent:bool = False) -> ModuleNotFoundError:
        match winType:
            case "lineWins":
                self.calculateLineWins(recordWins=emitWinEvent)
            case "scatterWins":
                raise NotImplementedError
            case "clusterWins":
                raise NotImplementedError
            case "waysWins":
                raise NotImplementedError
            case "customWins":
                raise NotImplementedError ("must define custom win evaluation")
        if emitEvent:
            winInfoEvent(self)

            
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
        if self.gameType == self.config.baseGameType:
            baseGameTrigger, freeGameTrigger = True, False 
        else:
            baseGameTrigger, freeGameTrigger = False, True
        freeSpinsTriggerEvent(self, baseGameTrigger=baseGameTrigger, freeGameTrigger=freeGameTrigger)

    def updateFreeSpinRetriggerAmount(self):
        self.totFs += self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols('scatter')]
        freeSpinsTriggerEvent(self, freeGameTrigger=True, baseGameTrigger=False)

    def updateFreeSpin(self):
        updateFreeSpinEvent(self)
        self.spinWin = 0
        self.winData = {}
        self.fs += 1 

    def endFreeSpin(self):
        freeSpinEndEvent(self)

    def enforceCriteriaConditions(self):
        """
        Define custom criteria conditions. By default no conditions are enforced and all simulated results are recorded
        """
        self.repeat = False

    def evaluateFinalWin(self):
        self.finalWin = min(self.runningBetWin, self.config.winCap)
        self.updateFinalWin()
        finalWinEvent(self)