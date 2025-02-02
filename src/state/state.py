from src.config.config import *
from src.write_data.write_data import *
from src.calculations.symbol import Symbol
from src.wins.win_manager import WinManager
from src.calculations.symbol import SymbolStorage

from copy import copy
from abc import ABC, abstractmethod
import random 

class GeneralGameState(ABC):
    def __init__(self, config):
        self.config = config
        self.library = {}
        self.recordedEvents = {}
        self.tempWins = []  
        self.createSymbolHashMap()
        self.assignSpecialSymbolFunctions()
        self.setWinManager()

    def createSymbolHashMap(self) -> None:
        allSymbolsList = set()
        for key,_ in self.config.payTable.items():
            allSymbolsList.add(key[1])

        for key in self.config.specialSymbols:
            for sym in self.config.specialSymbols[key]:
                allSymbolsList.add(sym)
        
        allSymbolsList = list(allSymbolsList)
        self.symbolStorage = SymbolStorage(self.config, allSymbolsList)   

    @abstractmethod
    def assignSpecialSymbolFunctions(self):
        warn("No special symbol functions are defined")

    def setWinManager(self):
        self.winManager = WinManager(self.config.baseGameType, self.config.freeGameType)

    def resetBook(self) -> None:
        """
        Reset global simulation variables
        """
        self.board = [[[] for _ in range(self.config.numRows[x])] for x in range(self.config.numReels)]
        self.topSymbols = None 
        self.bottomSymbols = None
        self.bookId = self.sim + 1
        self.book = {
            "id": self.bookId,
            "payoutMultiplier": 0.0,
            "events": [],
            "criteria": self.criteria
        }
        self.winManager.resetEndOfRoundWins()
        self.globalMultiplier = 1
        self.totFs = 0
        self.fs = 0
        self.winCapTriggered = False
        self.triggeredFreeSpins = False
        self.gameType = self.config.baseGameType
        self.repeat = False
        self.anticipation = [0]*self.config.numReels
        
    def resetSeed(self,sim) -> None:
        random.seed(sim+1)
        self.sim = sim
    
    def resetFsSpin(self) -> None:
        self.triggeredFreeSpins = True
        self.fs = 0
        self.gameType = self.config.freeGameType
        self.winManager.resetSpinWin()
        
    def getBetMode(self, modeNameToSelect) -> BetMode:
        for betMode in self.config.betModes:
            if betMode.getName() == modeNameToSelect:
                return betMode
        print("\nWarning: betmode couldn't be retrieved\n")

    def getCurrentBetMode(self) -> object:
        for betMode in self.config.betModes:
            if betMode.getName() == self.betMode:
                return betMode
            
    def getCurrentBetModeDistribution(self) -> object:
        dist = self.getCurrentBetMode().getDistributions()
        for c in dist:
            if c._criteria == self.criteria:
                return c 
        raise RuntimeError("could not locate criteria distribtuion")
        
    def getCurrentDistributionConditions(self) -> dict:
        for d in self.getBetMode(self.betMode).getDistributions():
            if d._criteria == self.criteria:
                return d._conditions
        return RuntimeError ("could not locate betMode conditions")
    
    #State verifications/checks
    def getWinCapTriggered(self) -> bool:
        if self.winCapTriggered:
            return True
        return False 
    
    def inCriteria(self, *args) -> bool:
        for arg in args:
            if self.criteria == arg:
                return True 
        return False 

    def record(self, description: dict) -> None:
        """
        Record functions must be used for distribtion conditions.
        Freespin triggers are most commonly used, i.e {"kind": X, "symbol": "S", "gameType": "baseGame"}
        It is recomended to otherwise record rare events with several keys in order to reduce the overall file-size containing many duplicate ids
        """
        self.tempWins.append(description)
        self.tempWins.append(self.bookId)

    def checkForceKeys(self, description) -> None:
        """
        Check and append unique force-key paramaters
        """
        currentModeForceKeys = self.getCurrentBetMode().getForceKeys()  # type:ignore
        for keyValue in description:
            if keyValue[0] not in currentModeForceKeys:
                self.getCurrentBetMode().addForceKey(keyValue[0])  # type:ignore
                
    def combine(self, modes, betModeName) -> None:
        for modeConfig in modes:
            for betMode in modeConfig:
                if betMode.getName() == betModeName:
                    break
            forceKeys = betMode.getForceKeys()  # type:ignore
            for key in forceKeys:
                if key not in self.getBetMode(betModeName).getForceKeys():  # type:ignore
                    self.getBetMode(betModeName).addForceKey(key)  # type:ignore

    def imprintWins(self) -> None:
        for tempWinIndex in range(int(len(self.tempWins)/2)):
            description = tuple(sorted(self.tempWins[2*tempWinIndex].items()))
            bookId = self.tempWins[2*tempWinIndex+1]
            try:
                if bookId not in self.recordedEvents[description]["bookIds"]:
                    self.recordedEvents[description]["timesTriggered"] += 1
                    self.recordedEvents[description]["bookIds"] += [bookId]
            except:
                self.checkForceKeys(description)
                self.recordedEvents[description] = {
                    "timesTriggered": 1,
                    "bookIds": [bookId]
                }

        # for event in list(self.book['events']):
        #     if event['type'] not in self.uniqueEventTypes:
        #         self.uniqueEventTypes.add(event['type'])
        # print("TODO: get unique wins")
        self.tempWins = []
        self.library[self.sim+1] = copy(self.book)
        self.winManager.updateEndRoundWins()

    def updateFinalWin(self) -> None:
        self.finalWin = round(min(self.winManager.runningBetWin, self.config.winCap),2)
        self.book["payoutMultiplier"] = self.finalWin
        self.book["baseGameWins"] = float(round(min(self.winManager.baseGameWins,self.config.winCap),2))
        self.book["freeGameWins"] = float(round(min(self.winManager.freeGameWins,self.config.winCap),2))

        assert min(round(self.winManager.baseGameWins + self.winManager.freeGameWins ,2),self.config.winCap) == round(self.winManager.runningBetWin, 2), "Base + Free game payout mismatch!"
        assert min(round(self.book["baseGameWins"]  + self.book["freeGameWins"] ,2),self.config.winCap) == round(self.book["payoutMultiplier"],2), "Base + Free game payout mismatch!"
  
    def updateGameModeWins(self, winAmount: float) -> None:
        if winAmount > 0:
            if self.gameType == self.config.baseGameType:
                self.baseGameWins += winAmount
            elif self.gameType == self.config.freeGameType:
                self.freeGameWins += winAmount
            else:
                raise RuntimeError(f"{self.gameType} not a reconised game-type")
            
    def checkRepeat(self) -> None:
        if self.repeat == False:
            winCriteria = self.getCurrentBetModeDistribution().getWinCriteria()
            if winCriteria is not None and self.finalWin != winCriteria:
                self.repeat = True 
            
            if (self.getCurrentDistributionConditions()['forceFreeSpins'] and not(self.triggeredFreeSpins)):
                self.repeat = True

    @abstractmethod
    def runSpin(self, sim):
        print("Base Game is not implemented in this game. Currently passing when calling runSpin.")
        pass

    @abstractmethod
    def runFreeSpin(self):
        print("gameState requires def runFreeSpin(), currently passing when calling runFreeSpin")
        pass

    def runSims(self, betModesCopyList, betMode, simToCriteria, totalThreads, totalRepeats, numSims, threadIndex, repeatCount, compress=True, writeEventList=False) -> None:
        self.betMode = betMode
        self.numSims = numSims
        for sim in range(threadIndex*numSims + (totalThreads*numSims)*repeatCount, (threadIndex+1)*numSims+(totalThreads*numSims)*repeatCount):
            self.criteria = simToCriteria[sim]
            self.runSpin(sim)
        modeCost = self.getCurrentBetMode().getCost()
        print("Thread "+str(threadIndex), "finished with", round(self.winManager.totalCumulativeWins/(numSims*modeCost), 3), "RTP.",
              f"[baseGame: {round(self.winManager.cumulativeBaseWins/(numSims*modeCost), 3)}, freeGame: {round(self.winManager.cumulativeFreeWins/(numSims*modeCost), 3)}]",
              flush=True)
        lastFileWrite = threadIndex == totalThreads-1 and repeatCount == totalRepeats - 1
        firstFileWrite = threadIndex == 0 and repeatCount == 0

        writeJsonFile(self, list(self.library.values()), "temp_multi_threaded_files/books_"+betMode+"_"+str(threadIndex)+"_"+str(repeatCount)+".json", firstFileWrite, lastFileWrite, compress)
        printRecordedWins(self, betMode+"_"+str(threadIndex)+"_"+str(repeatCount))
        makeLookUpTable(self, "lookUpTable_"+betMode+"_"+str(threadIndex)+"_"+str(repeatCount))
        makeLookUpTableIdToCriteria(self, "lookUpTableIdToCriteria_"+betMode+"_"+str(threadIndex)+"_"+str(repeatCount))
        makeLookUpTablePaySplit(self, "lookUpTableSegmented"+"_"+str(betMode)+"_"+str(threadIndex)+"_"+str(repeatCount))
        if writeEventList == True:
            writeLibraryEvents(self, list(self.library.values()), betMode)
        betModesCopyList.append(self.config.betModes)