from collections import defaultdict
from src.calculations.board import Board


class ScatterWins(Board):
    """
    Scatter (pay-anywhere) class for handling wins win calculations and recording.
    """

    def recordScatterWins(
        self, num_winning_syms: int, symbol: int, total_multiplier: int, gametype: str
    ) -> None:
        """Force-file description key generator."""
        self.record(
            {
                "win_size": num_winning_syms,
                "symbol": symbol,
                "totalMult": total_multiplier,
                "gametype": gametype,
            }
        )

    def get_scatterpay_wins(
        self,
        record_wins: bool = True,
        wild_key: str = "wild",
        multiplier_key: str = "multiplier",
    ) -> dict:
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        exploding_symbols = []
        symbols_on_board = defaultdict(list)
        wild_positions = []
        total_win = 0.0
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name not in self.config.special_symbols[wild_key]:
                    symbols_on_board[symbol.name].append(
                        {"reel": reel_idx, "row": row_idx}
                    )
                else:
                    wild_positions.append({"reel": reel_idx, "row": row_idx})

        # Update all symbol positons with wilds, as this symbol is shared
        for sym in symbols_on_board:
            if len(wild_positions) > 0:
                symbols_on_board[sym].append(wild_positions)
            win_size = len(symbols_on_board[sym])
            if (win_size, sym) in self.config.paytable:
                symbol_mult = 0
                for positions in symbols_on_board[sym]:
                    if self.board[positions["reel"]][positions["row"]].check_attribute(
                        multiplier_key
                    ):
                        symbol_mult += self.board[positions["reel"]][
                            positions["row"]
                        ].get_attribute(multiplier_key)
                    symbol_mult = max(symbol_mult, 1)

                    self.board[positions["reel"]][positions["row"]].assign_attribute(
                        {"explode": True}
                    )
                    # Account for special symbols, such as wilds which can apply to multiple groups
                    if positions not in exploding_symbols:
                        exploding_symbols.append(positions)

                if record_wins:
                    self.recordScatterWins(
                        win_size,
                        sym,
                        symbol_mult * self.global_multiplier,
                        self.gametype,
                    )
                symbol_win_data = {
                    "symbol": sym,
                    "win": self.config.paytable[(win_size, sym)]
                    * self.global_multiplier
                    * symbol_mult,
                    "positions": symbols_on_board[sym],
                    "meta": {
                        "globalMult": self.global_multiplier,
                        "symbolMult": symbol_mult,
                        "winWithoutMult": self.config.paytable[(win_size, sym)],
                    },
                }
                total_win += symbol_win_data["win"]
                return_data["wins"].append(symbol_win_data)

        return_data["totalWin"] = total_win
        self.win_manager.tumble_win = total_win
        self.exploding_symbols = exploding_symbols

        return return_data
