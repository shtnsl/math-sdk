import pathlib, os, sys
from src.config.bet_mode import *
from src.config.constants import *
from src.write_data.force import *
import pathlib
from src.events.event_constants import *
from src.write_data.force import *
from src.calculations.symbol import Symbol

class Config:
    """
    Sets the default game-values required by the game-state. 
    Custom values are set in the child class - gameConfig.py - located in the game directory
    """
    def __init__(self):
        self.rtp = 0.97
        self.gameId = "0_0_0"
        self.providerName = "sample_provider"
        self.providerNumber = int(self.gameId.split("_")[0])
        self.gameName = "sample_lines"
        
        #Win information
        self.minDenomination = 0.1
        self.winCap = 5000
        
        #Game details
        self.reels = 5
        self.row = 3
        self.payTable = {} #Symbol information assumes ('kind','name) format
        
        #Define special Symbols properties - list all possible symbol states during gameplay
        self.baseGameType = "baseGame"
        self.freeGameType = "freeSpins"
        
        self.includePaddingSymbols = True
 
        #Define the number of scatter-symbols required to award free-spins
        self.freeSpinTriggers = {
        }
        
        #Static game files
        self.reelLocation = ""
        self.reels = {
            
        }
        self.paddingReels = { #symbol configuration desplayed before the board reveal
            
        }
        
        self.writeEventList = True
        
        #Define win-levels for each game-mode, returned during win information events
        self.winLevels = {
            "standard":{
                1: (0,0.1),
                2: (0.1,1.0),
                3: (1.0, 2.0),
                4: (2.0, 5.0),
                5: (5.0, 15.0),
                6: (15.0, 30.0),
                7: (30.0, 50.0),
                8: (50.0, 100.0),
                9: (100.0, self.winCap),
                10: (self.winCap, float('inf'))            
            },
            "endFeature": {
                1: (0.0,1.0),
                2: (1.0,5.0),
                3: (5.0, 10.0),
                4: (10.0, 20.0),
                5: (20.0, 50.0),
                6: (50.0, 100.0),
                7: (200.0, 500.0),
                8: (500.0, 2000.0),
                9: (200.0, self.winCap),
                10: (self.winCap, float('inf'))            
            }
        }

    def getWinLevel(self, winAmount:float, winLevelKey:str) -> int:
        levels = self.winLevels[winLevelKey]
        for idx, pair in levels.items():
            if winAmount >= pair[0] and winAmount < pair[1]:
                return idx 
        return RuntimeError(f"winLevel not found: {winAmount}")
        
    def getSpecialSymbolNames(self) -> None:
        self.specalSymbolNames = set()
        for key in list(self.specialSymbols.keys()):
            for sym in self.specialSymbols[key]:
                self.specalSymbolNames.add(sym)
        self.specalSymbolNames = list(self.specalSymbolNames)
    
    def getPayingSymbolNames(self) -> None:
        self.payingSymbolNames = set()
        for tup in self.payTable:
            assert type(tup[1]) == str, "symbol name must be a string"
            self.payingSymbolNames.add(tup[1])
        self.payingSymbolnames = list(self.payingSymbolNames)
        
    def getSpecialProperties(self, sym: str) -> None:
        self.symbols = []
        for sym in self.allValidSymbolNames:
            #Assign specal properties
            specialProperties = self.defaultSpecialAttributes
            for s,prop in self.specialProperties:
                if s == sym:
                    specialProperties[prop] = self.specialProperties[sym][prop]
                    
            #Get symbol payouts (if applicable)
            if sym in self.payingSymbolNames:
                symbolPayouts = []
                for kind,pay in self.payTable:
                    if s == sym:
                        symbolPayouts.append((kind,pay))
            
            symObject = Symbol(sym, symbolPayouts, specialProperties)
            self.symbols.append(symObject)
        
    def validateSymbolsOnReels(self, reelStrip: str) -> None:
        #Verify that all symbols on the reelstrip are valid
        uniqueSymbols = set()
        for reel in reelStrip:
            for row in reel:
                uniqueSymbols.addd(row)
                
        isSubset = uniqueSymbols.issubset(set(self.allValidSymbolNames))
        if not isSubset:
            raise RuntimeError(
            f"Symbol identified in reel that does not exist in valid symbol names. \n"
            f"Valid Symbols: {self.allValidSymbolNames}\n"
            f"Detected Symbols: {list(uniqueSymbols)}"
        )
        
    def readReelsFromCSV(self, filePath):
        reelStrips = []
        count = 0
        with open(os.path.abspath(filePath), "r") as file:
            for line in file:
                splitLine = line.strip().split(",")
                for reelIndex in range(len(splitLine)):
                    if count == 0:
                        reelStrips.append(["".join([ch for ch in splitLine[reelIndex] if ch.isalnum()])])
                    else:
                        reelStrips[reelIndex].append("".join([ch for ch in splitLine[reelIndex] if ch.isalnum()]))

                count += 1

        return reelStrips
    
    def constructFilePaths(self, gameId:str) -> None:
        assert len(gameId.split("_"))==3, "provider_gameNumber_rtp"
        self.libraryPath = str.join("/", ["games",self.gameId, "library"])
        self.checkFolderExistance(self.libraryPath)
        
        self.bookPath = str.join("/", [self.libraryPath, "books"])
        self.checkFolderExistance(self.bookPath)
        
        self.compressedBookPath = str.join("/", [self.libraryPath, "books_compressed"])
        self.checkFolderExistance(self.compressedBookPath)
        
        self.lookUpPath = str.join("/", [self.libraryPath, "lookup_tables"])
        self.checkFolderExistance(self.lookUpPath)
        
        self.configPath = str.join("/", [self.libraryPath, "configs"])
        self.checkFolderExistance(self.configPath)
        
        self.forcePath = str.join("/", [self.libraryPath, "forces"])
        self.checkFolderExistance(self.forcePath)
        
        self.reelsPath = str.join("/", ["games", self.gameId, "reels"])   
        self.checkFolderExistance(self.reelsPath)
        
        self.tempPath = str.join("/", [self.libraryPath, "temp_multi_threaded_files"])  
        self.checkFolderExistance(self.tempPath)
        

    def checkFolderExistance(self, folderPath:str) -> None:
        if not(os.path.exists(folderPath)):
            os.makedirs(folderPath)

    def convertWinRangeToPayTable(self, payGroup: dict) -> dict:
        """
        requires self.payGroup to be defined
        for each symbol, define a pay-range dict stucture: self.payGroup = {(x-y, 's'): z}
        where x-y defines the paying cluster size on the closed interval [x,y].
        e.g (5-5,'L1'): 0.1 will pay 0.1x for clusters of exactly 5 elements

        Function returns RuntimeError if there are overlapping ranges
        """
        payTable = {}
        for symDetails, payout in payGroup.items():
            minConnectionSize, maxConnectionSize = symDetails[0][0], symDetails[0][1]
            symbol = symDetails[1]
            for i in range(minConnectionSize, maxConnectionSize+1):
                payTable[(i,symbol)] = payout

        #Todo: return runtime error

        return payTable
