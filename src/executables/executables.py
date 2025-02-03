import random
import numpy as np 
from typing import List 
from src.state.state_conditions import Conditions
from src.calculations.board import Board
from src.calculations.lines import LineWins
from src.calculations.cluster import ClusterWins
from src.calculations.scatter import ScatterWins
from src.calculations.tumble import Tumble
from src.calculations.statistics import get_random_outcome
from src.events.events import *

class Executables(Conditions, Board, LineWins, ClusterWins, ScatterWins, Tumble):
    """
    The purpose of this Class is to group together common actions which are likely to be reused between games.
    These can be overridden in the GameExecuatables or GameCalculations if game-specific alterations are required
    """

    def drawBoard(self, emitEvent:bool = True) -> None:
        if self.get_current_distribution_conditions()["force_freespins"] and self.gametype == self.config.base_game_type:
            numScatters = get_random_outcome(self.get_current_distribution_conditions()["scatterTriggers"])
            self.forceSpecialBoard('scatter', numScatters)
        else:
            self.create_board_reelstrips()
            while self.count_special_symbols('scatter') >= min(self.config.freeSpinTriggers[self.gametype].keys()):
                self.create_board_reelstrips()
        if emitEvent:
            reveal_event(self)

    def forceSpecialBoard(self, forceCriteria: str, numForceSymbols: int) -> None:
        reelStripId = get_random_outcome(self.get_current_distribution_conditions()['reel_weights'][self.gametype])
        reelStops = self.getSymbolLocationsOnReel(reelStripId, forceCriteria)

        symbolProb = []
        for x in range(self.config.num_reels):
            symbolProb.append(len(reelStops[x])/len(self.config.reels[reelStripId][x]))
        forceStopPositions = {}
        while len(forceStopPositions) != numForceSymbols:
            chosenReel = random.choices(list(np.arange(0,self.config.num_reels)),symbolProb)[0]
            chosenStop = random.choice(reelStops[chosenReel])
            symbolProb[chosenReel] = 0
            forceStopPositions[int(chosenReel)] = int(chosenStop)
        
        forceStopPositions = dict(sorted(forceStopPositions.items(), key=lambda x: x[0]))
        self.forceBoardFromReelStrips(reelStripId, forceStopPositions)


    def getSymbolLocationsOnReel(self, reelId:str, targetSymbol:str) -> List[List]:
        reel = self.config.reels[reelId]
        reelStopPositions = [[] for _ in range(self.config.num_reels)]
        for r in range(self.config.num_reels):
            for s in range(len(reel[r])):
                if reel[r][s] in self.config.special_symbols[targetSymbol]: 
                    reelStopPositions[r].append(s)

        return reelStopPositions


    #Line pays game logic and events
    def emitLineWinEvents(self) -> None:
        if self.win_manager.spinWin > 0:
            win_info_event(self)
            self.evaluateWinCap()
            set_win_event(self)
        set_total_event(self)

    #Tumble (scatter/cluster) game logic and events
    def emitTumbleWinEvents(self, tumbleAfterWins: bool = True) -> None:
        if self.winData['totalWin'] >0:
            win_info_event(self)
            update_tunble_win_event(self)
            self.evaluateWinCap()
            if tumbleAfterWins:
                self.tumbleBoard()
                tumeble_board_event(self)

    def evaluateWinCap(self) -> None:
        if self.win_manager.running_bet_win >= self.config.wincap and not(self.wincap_triggered):
            self.wincap_triggered = True
            wincap_event(self)
            return True
        return False

    def count_special_symbols(self, specialSymbolCriteria:str) -> bool:
        return len(self.special_syms_on_board[specialSymbolCriteria])

    def check_fs_condition(self, scatterKey:str = 'scatter') -> bool:
        if self.count_special_symbols(scatterKey) >= min(self.config.freeSpinTriggers[self.gametype].keys()) and not(self.repeat):
            return True 
        return False
    
    def checkFreeSpinEntry(self, scatterKey:str = "scatter"):
        if not(self.get_current_distribution_conditions()['force_freespins']) and len(self.special_syms_on_board[scatterKey])>=min(self.config.freeSpinTriggers[self.gametype].keys()):
            self.repeat = True
            return False 
        return True
    
    def runFreeSpinFromBaseGame(self, scatterKey:str = 'scatter') -> None:
        self.record({"kind": self.count_special_symbols(scatterKey), "symbol": scatterKey, "gameType": self.gametype})
        self.update_freespin_amount()
        self.run_freespin()
        
    def update_freespin_amount(self, scatterKey:str = 'scatter') -> None:
        self.totFs = self.config.freeSpinTriggers[self.gametype][self.count_special_symbols(scatterKey)]
        if self.gametype == self.config.base_game_type:
            basegame_trigger, freeGameTrigger = True, False 
        else:
            basegame_trigger, freeGameTrigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freeGameTrigger=freeGameTrigger)

    def update_fs_retrigger_amt(self, scatterKey:str = 'scatter') -> None:
        self.totFs += self.config.freeSpinTriggers[self.gametype][self.count_special_symbols(scatterKey)]
        fs_trigger_event(self, freeGameTrigger=True, basegame_trigger=False)

    def updateFreeSpin(self) -> None:
        update_freepsin_event(self)
        self.win_manager.reset_spin_win()
        self.tumbleWinMultiplier = 0
        self.winData = {}
        self.fs += 1 
        self.global_multiplier = 1

    def endFreeSpin(self) -> None:
        freespin_end_event(self)

    def enforceCriteriaConditions(self) -> None:
        """
        Define custom criteria conditions. By default no conditions are enforced and all simulated results are recorded
        """
        self.repeat = False

    def evaluateFinalWin(self) -> None:
        self.update_final_win()
        final_win_event(self)