from src.config.config import *
from src.write_data.write_data import *
from src.calculations.symbol import Symbol
import random 

class GeneralGameState:
    def __init__(self, config):
        self.config = config
        self.library = {}
        self.recordedEvents = {}
        self.cumulativeBaseWins = 0
        self.cumulativeFreeWins = 0
        self.totalCumulativeWins = 0
        self.tempWins = []  
        self.createSymbolHashMap()
        self.assignSpecialSymbolFuncions()

    def createSymbolHashMap(self):
        symbolClasses = {}
        payingSymbolMap = {}
        for key,value in self.config.payTable.items():
            if payingSymbolMap.get(key[1]) != None:
                payingSymbolMap[key[1]].append({'kind': key[0], 'value': value})
            else:
                payingSymbolMap[key[1]] = [{'kind': key[0], 'value': value}]

        specialSymbolArgs = {}
        for key in self.config.specialSymbols:
            for sym in self.config.specialSymbols[key]:
                if specialSymbolArgs.get(sym) is not None:
                    specialSymbolArgs[sym].append(key)
                else:
                    specialSymbolArgs[sym] = [key]
        
        for sym in payingSymbolMap.keys():
            if sym in specialSymbolArgs:
                symbolClasses[sym] = Symbol(name=sym, payTable=payingSymbolMap[sym], specials=specialSymbolArgs[sym])
            else:
                symbolClasses[sym] = Symbol(name=sym, payTable=payingSymbolMap[sym])
        for sym in specialSymbolArgs.keys():
            if sym not in payingSymbolMap.keys():
                symbolClasses[sym] = Symbol(name=sym, specials=specialSymbolArgs[sym])

        self.validSymbols = symbolClasses

    def assignSpecialSymbolFuncions(self):
        warn("No special sybmol functionality implmented! ")


    def resetBook(self) -> None:
        """
        Reset global simulation variables
        """
        self.board = [[[] for _ in range(self.config.numRows[x])] for x in range(self.config.numReels)]
        self.bookId = self.sim + 1
        self.book = {
            "id": self.bookId,
            "payoutMultiplier": 0.0,
            "events": [],
            "criteria": self.criteria
        }
        self.globalMultiplier = 1
        self.runningBetWin = 0 #total 
        self.spinWin = 0 
        self.baseGameWins = 0
        self.freeGameWins = 0
        self.totalWins = 0
        self.totFs = 0
        self.fs = 0
        self.winCapTriggered = False
        self.gameType = self.config.baseGameType
        self.repeat = False
        self.anticipation = [0]*self.config.numReels
        
    def resetSeed(self,sim) -> None:
        random.seed(sim+1)
        self.sim = sim
    
    def resetFsSpin(self) -> None:
        self.freeGameWins = 0
        self.fs = 0
        self.gameType = self.config.freeGameType
        
    def verifyWinAmounts(self) -> None:
        assert (min(round(self.baseGameWins + self.freeGameWins,1), self.config.winCap)) == min(round(self.totalWins,1), self.config.winCap), "Ensure sum of basegame and freespin wins equal total amount"
        
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

    def record(self, description: dict):
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
                
    def combine(self, modes, betModeName):
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
        self.library[self.sim+1] = deepcopy(self.book)
        self.totalCumulativeWins += self.runningBetWin
        self.cumulativeBaseWins += self.baseGameWins
        self.cumulativeFreeWins += self.freeGameWins

    def updateFinalWin(self):
        self.finalWin = round(min(self.runningBetWin, self.config.winCap),2)
        self.book["payoutMultiplier"] = self.finalWin
        self.book["baseGameWins"] = float(round(min(self.baseGameWins,self.config.winCap),2))
        self.book["freeGameWins"] = float(round(min(self.freeGameWins,self.config.winCap),2))

        assert min(round(self.book["baseGameWins"]  + self.book["freeGameWins"] ,1),self.config.winCap) == round(self.book["payoutMultiplier"],1), "Base + Free game payout mismatch!"
  
    def checkRepeat(self):
        if self.repeat == False:
            winCriteria = self.getCurrentBetModeDistribution().getWinCriteria()
            if winCriteria is not None and self.finalWin != winCriteria:
                self.repeat = True 

    def runSpin(self, sim):
        print("Base Game is not implemented in this game. We are currently passing when calling runSpin.")
        pass

    def runFreeSpin(self):
        print("gameState requires def runFreeSpin(), currently passing when calling runFreeSpin")
        pass

    def runSims(self, betModesCopyList, betMode, simToCriteria, totalThreads, totalRepeats, numSims, threadIndex, repeatCount, compress=True, writeEventList=False):
        self.betMode = betMode
        self.numSims = numSims
        for sim in range(threadIndex*numSims + (totalThreads*numSims)*repeatCount, (threadIndex+1)*numSims+(totalThreads*numSims)*repeatCount):
            self.criteria = simToCriteria[sim]
            self.runSpin(sim)
        modeCost = self.getCurrentBetMode().getCost()
        print("Thread "+str(threadIndex), "finished with", round(self.totalCumulativeWins/(numSims*modeCost), 3), "RTP.",
              f"[baseGame: {round(self.cumulativeBaseWins/(numSims*modeCost), 3)}, freeGame: {round(self.cumulativeFreeWins/(numSims*modeCost), 3)}]",
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