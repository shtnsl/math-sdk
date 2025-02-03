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
        self.game_id = "0_0_0"
        self.provider_name = "sample_provider"
        self.provider_numer = int(self.game_id.split("_")[0])
        self.game_name = "sample_lines"
        
        #Win information
        self.min_denomination = 0.1
        self.wincap = 5000
        
        #Game details
        self.reels = 5
        self.row = 3
        self.paytable = {} #Symbol information assumes ('kind','name) format
        
        #Define special Symbols properties - list all possible symbol states during gameplay
        self.base_game_type = "baseGame"
        self.free_game_type = "freeSpins"
        
        self.include_padding = True
 
        #Define the number of scatter-symbols required to award free-spins
        self.freespin_triggers = {
        }
        
        #Static game files
        self.reel_location = ""
        self.reels = {
            
        }
        self.padding_reels = { #symbol configuration desplayed before the board reveal
            
        }
        
        self.write_event_list = True
        
        #Define win-levels for each game-mode, returned during win information events
        self.win_levels = {
            "standard":{
                1: (0,0.1),
                2: (0.1,1.0),
                3: (1.0, 2.0),
                4: (2.0, 5.0),
                5: (5.0, 15.0),
                6: (15.0, 30.0),
                7: (30.0, 50.0),
                8: (50.0, 100.0),
                9: (100.0, self.wincap),
                10: (self.wincap, float('inf'))            
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
                9: (200.0, self.wincap),
                10: (self.wincap, float('inf'))            
            }
        }

    def get_win_level(self, winAmount:float, winLevelKey:str) -> int:
        levels = self.win_levels[winLevelKey]
        for idx, pair in levels.items():
            if winAmount >= pair[0] and winAmount < pair[1]:
                return idx 
        return RuntimeError(f"winLevel not found: {winAmount}")
        
    def get_special_symbol_names(self) -> None:
        self.specalSymbolNames = set()
        for key in list(self.special_symbols.keys()):
            for sym in self.special_symbols[key]:
                self.specalSymbolNames.add(sym)
        self.specalSymbolNames = list(self.specalSymbolNames)
    
    def getPayingSymbolNames(self) -> None:
        self.payingSymbolNames = set()
        for tup in self.paytable:
            assert type(tup[1]) == str, "symbol name must be a string"
            self.payingSymbolNames.add(tup[1])
        self.payingSymbolnames = list(self.payingSymbolNames)
        
    def getSpecialProperties(self, sym: str) -> None:
        self.symbols = []
        for sym in self.all_valid_sym_names:
            #Assign specal properties
            special_properties = self.special_attributes
            for s,prop in self.special_properties:
                if s == sym:
                    special_properties[prop] = self.special_properties[sym][prop]
                    
            #Get symbol payouts (if applicable)
            if sym in self.payingSymbolNames:
                symbolPayouts = []
                for kind,pay in self.paytable:
                    if s == sym:
                        symbolPayouts.append((kind,pay))
            
            symObject = Symbol(sym, symbolPayouts, special_properties)
            self.symbols.append(symObject)
        
    def validateSymbolsOnReels(self, reel_strip: str) -> None:
        #Verify that all symbols on the reelstrip are valid
        uniqueSymbols = set()
        for reel in reel_strip:
            for row in reel:
                uniqueSymbols.add(row)
                
        isSubset = uniqueSymbols.issubset(set(self.all_valid_sym_names))
        if not isSubset:
            raise RuntimeError(
            f"Symbol identified in reel that does not exist in valid symbol names. \n"
            f"Valid Symbols: {self.all_valid_sym_names}\n"
            f"Detected Symbols: {list(uniqueSymbols)}"
        )
        
    def read_reels_csv(self, filePath):
        reelStrips = []
        count = 0
        with open(os.path.abspath(filePath), "r") as file:
            for line in file:
                split_line = line.strip().split(",")
                for reelIndex in range(len(split_line)):
                    if count == 0:
                        reelStrips.append(["".join([ch for ch in split_line[reelIndex] if ch.isalnum()])])
                    else:
                        reelStrips[reelIndex].append("".join([ch for ch in split_line[reelIndex] if ch.isalnum()]))

                count += 1

        return reelStrips
    
    def construct_paths(self, game_id:str) -> None:
        assert len(game_id.split("_"))==3, "provider_gameNumber_rtp"
        self.library_path = str.join("/", ["games",self.game_id, "library"])
        self.check_folder_exists(self.library_path)
        
        self.bookPath = str.join("/", [self.library_path, "books"])
        self.check_folder_exists(self.bookPath)
        
        self.compressedBookPath = str.join("/", [self.library_path, "books_compressed"])
        self.check_folder_exists(self.compressedBookPath)
        
        self.lookUpPath = str.join("/", [self.library_path, "lookup_tables"])
        self.check_folder_exists(self.lookUpPath)
        
        self.configPath = str.join("/", [self.library_path, "configs"])
        self.check_folder_exists(self.configPath)
        
        self.forcePath = str.join("/", [self.library_path, "forces"])
        self.check_folder_exists(self.forcePath)
        
        self.reelsPath = str.join("/", ["games", self.game_id, "reels"])   
        self.check_folder_exists(self.reelsPath)
        
        self.temp_path = str.join("/", [self.library_path, "temp_multi_threaded_files"])  
        self.check_folder_exists(self.temp_path)
        

    def check_folder_exists(self, folder_path:str) -> None:
        if not(os.path.exists(folder_path)):
            os.makedirs(folder_path)

    def convert_range_table(self, pay_group: dict) -> dict:
        """
        requires self.pay_group to be defined
        for each symbol, define a pay-range dict stucture: self.pay_group = {(x-y, 's'): z}
        where x-y defines the paying cluster size on the closed interval [x,y].
        e.g (5-5,'L1'): 0.1 will pay 0.1x for clusters of exactly 5 elements

        Function returns RuntimeError if there are overlapping ranges
        """
        paytable = {}
        for symDetails, payout in pay_group.items():
            min_connections, max_connections = symDetails[0][0], symDetails[0][1]
            symbol = symDetails[1]
            for i in range(min_connections, max_connections+1):
                paytable[(i,symbol)] = payout

        #Todo: return runtime error

        return paytable
