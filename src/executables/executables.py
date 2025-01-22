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
    
    def evaluateClusterWins(self):
        self.getClusterWins()
        self.evaluateWinCap()
        'For tumbling games, do not send setTotalWin until all tumble events have concluded'
        winInfoEvent(self)
        setTumbleWinEvent(self)
        if not self.winCapTriggered:
            setWinEvent(self)

    def evaluateLineWins(self, recordWins: bool = False):
        self.calculateLineWins(recordWins= recordWins)
        self.evaluateWinCap()
        winInfoEvent(self)
        if not self.winCapTriggered:
            setWinEvent(self)
        setTotalWinEvent(self)

    def evaluateScatterWins(self, emitWinEvent:bool = False):
        self.winData = self.getScatterPayWinData()
        if emitWinEvent:
            winInfoEvent(self)
            if not self.winCapTriggered:
                setTumbleWinEvent(self)


    def calculateWins(self, winType:str = None, recordWinInfo:bool = False) -> ModuleNotFoundError:
        match winType:
            case "lineWins":
                self.evaluateLineWins(recordWins = recordWinInfo)
            case "scatterWins":
                self.evaluateScatterWins()
                raise NotImplementedError
            case "clusterWins":
                self.evaluateClusterWins()
            case "waysWins":
                raise NotImplementedError
            case None:
                raise NotImplementedError (f"must define a valid winTyp ({winType}) when calling 'calculateWins()' function")
            
    def emitWinInformation(self):
        'setWin - cumulative win amount for a given individual spin'
        'setTotalWin - running bet win, including all previous freeSpin and baseGame wins in feature games'
        'winInfo - winning symbol information'
        winInfoEvent(self)
        if not self.winCapTriggered:
            setWinEvent(self)
        setTotalWinEvent(self)

    def evaluateWinCap(self):
        if self.runningBetWin >= self.config.winCap and not(self.winCapTriggered):
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
    
    
    def runFreeSpinFromBaseGame(self, scatterKey:str = 'scatter'):
        self.record({"kind": self.countSpecialSymbols(scatterKey), "symbol": scatterKey, "gameType": self.gameType})
        self.updateTotalFreeSpinAmount()
        self.runFreeSpin()
        
    def updateTotalFreeSpinAmount(self, scatterKey:str = 'scatter'):
        self.totFs = self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols(scatterKey)]
        if self.gameType == self.config.baseGameType:
            baseGameTrigger, freeGameTrigger = True, False 
        else:
            baseGameTrigger, freeGameTrigger = False, True
        freeSpinsTriggerEvent(self, baseGameTrigger=baseGameTrigger, freeGameTrigger=freeGameTrigger)

    def updateFreeSpinRetriggerAmount(self, scatterKey:str = 'scatter'):
        self.totFs += self.config.freeSpinTriggers[self.gameType][self.countSpecialSymbols(scatterKey)]
        freeSpinsTriggerEvent(self, freeGameTrigger=True, baseGameTrigger=False)

    def updateFreeSpin(self):
        updateFreeSpinEvent(self)
        self.spinWin = 0
        self.tumbleWinMultiplier = 0
        self.winData = {}
        self.fs += 1 
        self.globalMultiplier = 1

    def endFreeSpin(self):
        freeSpinEndEvent(self)

    def enforceCriteriaConditions(self):
        """
        Define custom criteria conditions. By default no conditions are enforced and all simulated results are recorded
        """
        self.repeat = False

    def evaluateFinalWin(self):
        self.updateFinalWin()
        finalWinEvent(self)