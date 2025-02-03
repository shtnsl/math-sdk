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
        self.recorded_events = {}
        self.tempWins = []  
        self.create_symbol_map()
        self.assign_special_sym_function()
        self.set_win_manager()

    def create_symbol_map(self) -> None:
        allSymbolsList = set()
        for key,_ in self.config.paytable.items():
            allSymbolsList.add(key[1])

        for key in self.config.special_symbols:
            for sym in self.config.special_symbols[key]:
                allSymbolsList.add(sym)
        
        allSymbolsList = list(allSymbolsList)
        self.symbolStorage = SymbolStorage(self.config, allSymbolsList)   

    @abstractmethod
    def assign_special_sym_function(self):
        warn("No special symbol functions are defined")

    def set_win_manager(self):
        self.win_manager = WinManager(self.config.base_game_type, self.config.free_game_type)

    def reset_book(self) -> None:
        """
        Reset global simulation variables
        """
        self.board = [[[] for _ in range(self.config.num_rows[x])] for x in range(self.config.num_reels)]
        self.top_symbols = None 
        self.bottom_symbols = None
        self.bookId = self.sim + 1
        self.book = {
            "id": self.bookId,
            "payoutMultiplier": 0.0,
            "events": [],
            "criteria": self.criteria
        }
        self.win_manager.reset_end_round_wins()
        self.global_multiplier = 1
        self.totFs = 0
        self.fs = 0
        self.wincap_triggered = False
        self.triggered_freespins = False
        self.gametype = self.config.base_game_type
        self.repeat = False
        self.anticipation = [0]*self.config.num_reels
        
    def resetSeed(self,sim) -> None:
        random.seed(sim+1)
        self.sim = sim
    
    def reset_fs_spin(self) -> None:
        self.triggered_freespins = True
        self.fs = 0
        self.gametype = self.config.free_game_type
        self.win_manager.reset_spin_win()
        
    def get_betmode(self, modeNameToSelect) -> BetMode:
        for bet_mode in self.config.bet_modes:
            if bet_mode.getName() == modeNameToSelect:
                return bet_mode
        print("\nWarning: betmode couldn't be retrieved\n")

    def get_current_betmode(self) -> object:
        for bet_mode in self.config.bet_modes:
            if bet_mode.getName() == self.bet_mode:
                return bet_mode
            
    def get_current_betmode_distributions(self) -> object:
        dist = self.get_current_betmode().getDistributions()
        for c in dist:
            if c._criteria == self.criteria:
                return c 
        raise RuntimeError("could not locate criteria distribtuion")
        
    def get_current_distribution_conditions(self) -> dict:
        for d in self.get_betmode(self.bet_mode).getDistributions():
            if d._criteria == self.criteria:
                return d._conditions
        return RuntimeError ("could not locate bet_mode conditions")
    
    #State verifications/checks
    def get_wincap_triggered(self) -> bool:
        if self.wincap_triggered:
            return True
        return False 
    
    def in_criteria(self, *args) -> bool:
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

    def check_force_keys(self, description) -> None:
        """
        Check and append unique force-key paramaters
        """
        currentModeForceKeys = self.get_current_betmode().getForceKeys()  # type:ignore
        for keyValue in description:
            if keyValue[0] not in currentModeForceKeys:
                self.get_current_betmode().addForceKey(keyValue[0])  # type:ignore
                
    def combine(self, modes, betmode_name) -> None:
        for modeConfig in modes:
            for bet_mode in modeConfig:
                if bet_mode.getName() == betmode_name:
                    break
            forceKeys = bet_mode.getForceKeys()  # type:ignore
            for key in forceKeys:
                if key not in self.get_betmode(betmode_name).getForceKeys():  # type:ignore
                    self.get_betmode(betmode_name).addForceKey(key)  # type:ignore

    def imprint_wins(self) -> None:
        for tempWinIndex in range(int(len(self.tempWins)/2)):
            description = tuple(sorted(self.tempWins[2*tempWinIndex].items()))
            bookId = self.tempWins[2*tempWinIndex+1]
            try:
                if bookId not in self.recorded_events[description]["bookIds"]:
                    self.recorded_events[description]["timesTriggered"] += 1
                    self.recorded_events[description]["bookIds"] += [bookId]
            except:
                self.check_force_keys(description)
                self.recorded_events[description] = {
                    "timesTriggered": 1,
                    "bookIds": [bookId]
                }

        # for event in list(self.book['events']):
        #     if event['type'] not in self.uniqueEventTypes:
        #         self.uniqueEventTypes.add(event['type'])
        # print("TODO: get unique wins")
        self.tempWins = []
        self.library[self.sim+1] = copy(self.book)
        self.win_manager.update_end_round_wins()

    def update_final_win(self) -> None:
        self.final_win = round(min(self.win_manager.running_bet_win, self.config.wincap),2)
        self.book["payoutMultiplier"] = self.final_win
        self.book["baseGameWins"] = float(round(min(self.win_manager.base_game_wins,self.config.wincap),2))
        self.book["freeGameWins"] = float(round(min(self.win_manager.freegame_wins,self.config.wincap),2))

        assert min(round(self.win_manager.base_game_wins + self.win_manager.freegame_wins ,2),self.config.wincap) == round(self.win_manager.running_bet_win, 2), "Base + Free game payout mismatch!"
        assert min(round(self.book["baseGameWins"]  + self.book["freeGameWins"] ,2),self.config.wincap) == round(self.book["payoutMultiplier"],2), "Base + Free game payout mismatch!"
  
    def update_mode_wins(self, winAmount: float) -> None:
        if winAmount > 0:
            if self.gametype == self.config.base_game_type:
                self.base_game_wins += winAmount
            elif self.gametype == self.config.free_game_type:
                self.freegame_wins += winAmount
            else:
                raise RuntimeError(f"{self.gametype} not a reconised game-type")
            
    def check_repeat(self) -> None:
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True 
            
            if (self.get_current_distribution_conditions()['force_freespins'] and not(self.triggered_freespins)):
                self.repeat = True

    @abstractmethod
    def run_spin(self, sim):
        print("Base Game is not implemented in this game. Currently passing when calling runSpin.")
        pass

    @abstractmethod
    def run_freespin(self):
        print("gamestate requires def run_freespin(), currently passing when calling runFreeSpin")
        pass

    def run_sims(self, betmode_copy_list, bet_mode, simToCriteria, total_threads, totalRepeats, num_sims, thread_index, repeat_count, compress=True, write_event_list=False) -> None:
        self.bet_mode = bet_mode
        self.num_sims = num_sims
        for sim in range(thread_index*num_sims + (total_threads*num_sims)*repeat_count, (thread_index+1)*num_sims+(total_threads*num_sims)*repeat_count):
            self.criteria = simToCriteria[sim]
            self.run_spin(sim)
        mode_cost = self.get_current_betmode().getCost()
        print("Thread "+str(thread_index), "finished with", round(self.win_manager.total_cumulative_wins/(num_sims*mode_cost), 3), "RTP.",
              f"[baseGame: {round(self.win_manager.cumulative_base_wins/(num_sims*mode_cost), 3)}, freeGame: {round(self.win_manager.cumulative_free_wins/(num_sims*mode_cost), 3)}]",
              flush=True)
        last_file_write = thread_index == total_threads-1 and repeat_count == totalRepeats - 1
        frist_file_write = thread_index == 0 and repeat_count == 0

        write_json(self, list(self.library.values()), "temp_multi_threaded_files/books_"+bet_mode+"_"+str(thread_index)+"_"+str(repeat_count)+".json", frist_file_write, last_file_write, compress)
        print_recorded_wins(self, bet_mode+"_"+str(thread_index)+"_"+str(repeat_count))
        make_lookup_tables(self, "lookUpTable_"+bet_mode+"_"+str(thread_index)+"_"+str(repeat_count))
        make_lookup_to_criteria(self, "lookUpTableIdToCriteria_"+bet_mode+"_"+str(thread_index)+"_"+str(repeat_count))
        make_lookup_pay_split(self, "lookUpTableSegmented"+"_"+str(bet_mode)+"_"+str(thread_index)+"_"+str(repeat_count))
        if write_event_list == True:
            write_library_events(self, list(self.library.values()), bet_mode)
        betmode_copy_list.append(self.config.bet_modes)