from copy import copy
from src.events.events import set_win_event, set_total_event

class Tumble:
    def tumbleBoard(self) -> None:
        self.tumbles += 1
        self.boardBeforeTumble = copy(self.board)
        staticBoard = copy(self.board)
        self.new_symbols_from_tumble = [[] for _ in range(len(staticBoard))]

        for reel in range(len(staticBoard)):
            explodingSymbols = 0
            copyReel = staticBoard[reel]
            for row in range(len(staticBoard[reel])):
                if staticBoard[reel][-1-row].check_attribute('explode'):
                    explodingSymbols += 1
            
            for i in range(explodingSymbols):
                newReelPos = (self.reel_positions[reel]-1)%len(self.reelstrip[reel])
                self.reel_positions[reel] = newReelPos
                if i == 0 and self.config.include_padding:
                    insertSym = self.top_symbols[reel]
                else:
                    insertSym = self.create_symbol(str(self.reelstrip[reel][(newReelPos) % len(self.reelstrip[reel])]))
                copyReel.insert(0, insertSym)
                self.new_symbols_from_tumble[reel].append(insertSym)
        
            copyReel = [copy(sym) for sym in copyReel if not sym.check_attribute('explode')]
            if len(copyReel) != self.config.num_rows[reel]:
                raise RuntimeError(f"new reel length must match expected board size:\n expected: {self.config.num_rows[reel]} \n actual: {len(copyReel)}")
            staticBoard[reel] = copyReel

        #update topSymbol positions
        if self.config.include_padding:
            self.top_symbols = [[] for _ in range(self.config.num_reels)]
            for reel in range(self.config.num_reels):
                self.top_symbols[reel] = self.create_symbol(str(self.reelstrip[reel][(self.reel_positions[reel] - 1)%len(self.reelstrip[reel])]))

        self.get_special_symbols_on_board()
        self.board = staticBoard

    def set_end_tumble_event(self) -> None:
        if self.win_manager.spinWin > 0:
            set_win_event(self)
        set_total_event(self)