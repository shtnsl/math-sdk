import random
from typing import List 
import numpy as np 

from src.state.state_conditions import Conditions
from src.calculations.board import Board
from src.calculations.lines import LineWins
from src.calculations.cluster import ClusterWins
from src.calculations.scatter import ScatterWins
from src.calculations.tumble import Tumble
from src.calculations.statistics import getRandomOutcome
from src.events.events import *

class Executables(Conditions, Board, LineWins, ClusterWins, ScatterWins, Tumble):
    """
    The purpose of this Class is to group together common actions which are likely to be reused between games.
    These can be overridden in the GameExecuatables or GameCalculations if game-specific alterations are required
    """

    def drawBoard(self, emitEvent:bool = True) -> None:
        if self.getCurrentDistributionConditions()["forceFreeSpins"] and self.gameType == self.config.baseGameType:
            numScatters = getRandomOutcome(self.getCurrentDistributionConditions()["scatterTriggers"])
            self.forceSpecialBoard('scatter', numScatters)
        else:
            self.createBoardFromReelStrips()
            while self.countSpecialSymbols('scatter') >= min(self.config.freeSpinTriggers[self.gameType].keys()):
                self.createBoardFromReelStrips()
        if emitEvent:
            revealBoardEvent(self)

    def forceSpecialBoard(self, forceCriteria: str, numForceSymbols: int) -> None:
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


    #Line pays game logic and events
    def emitLineWinEvents(self) -> None:
        if self.winManager.spinWin > 0:
            winInfoEvent(self)
            self.evaluateWinCap()
            setWinEvent(self)
        setTotalWinEvent(self)

    #Tumble (scatter/cluster) game logic and events
    def emitTumbleWinEvents(self, tumbleAfterWins: bool = True) -> None:
        if self.winData['totalWin'] >0:
            winInfoEvent(self)
            updateTumbleWinEvent(self)
            self.evaluateWinCap()
            if tumbleAfterWins:
                self.tumbleBoard()
                tumbleBoardEvent(self)

    def evaluateWinCap(self) -> None:
        if self.winManager.runningBetWin >= self.config.winCap and not(self.winCapTriggered):
            self.winCapTriggered = True
            winCapEvent(self)
            return True
        return False

    def countSpecialSymbols(self, specialSymbolCriteria:str) -> bool:
        return len(self.specialSymbolsOnBoard[specialSymbolCriteria])

    def checkFreespinCondition(self, scatterKey:str = 'scatter') -> bool:
        if self.countSpecialSymbols(scatterKey) >= min(self.config.freeSpinTriggers[self.gameType].keys()) and not(self.repeat):
            return True 
        return False
    
    def runFreeSpinFromBaseGame(self, scatterKey:str = 'scatter') -> None:
        self.record({"kind": self.countSpecialSymbols(scatterKey), "symbol": scatterKey, "gameType": self.gameType})
        self.updateTotalFreeSpinAmount()
        self.runFreeSpin()
        
    def updateTotalFreeSpinAmount(self, scatterKey:str = 'scatter') -> None:
        self.totFs = self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols(scatterKey)]
        if self.gameType == self.config.baseGameType:
            baseGameTrigger, freeGameTrigger = True, False 
        else:
            baseGameTrigger, freeGameTrigger = False, True
        freeSpinsTriggerEvent(self, baseGameTrigger=baseGameTrigger, freeGameTrigger=freeGameTrigger)

    def updateFreeSpinRetriggerAmount(self, scatterKey:str = 'scatter') -> None:
        self.totFs += self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols(scatterKey)]
        freeSpinsTriggerEvent(self, freeGameTrigger=True, baseGameTrigger=False)

    def updateFreeSpin(self) -> None:
        updateFreeSpinEvent(self)
        self.winManager.resetSpinWin()
        self.tumbleWinMultiplier = 0
        self.winData = {}
        self.fs += 1 
        self.globalMultiplier = 1

    def endFreeSpin(self) -> None:
        freeSpinEndEvent(self)

    def enforceCriteriaConditions(self) -> None:
        """
        Define custom criteria conditions. By default no conditions are enforced and all simulated results are recorded
        """
        self.repeat = False

    def evaluateFinalWin(self) -> None:
        self.updateFinalWin()
        finalWinEvent(self)