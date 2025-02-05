"""Evaluates and records winds for lines games."""

from typing import List, Tuple, Dict
from src.calculations.board import Board


class LineWins(Board):
    """Primary win evaluation and recording."""

    def get_line_mults(
        self, winning_positions: List[Dict], multiplier_key: str = "multiplier"
    ):
        """Searches symbol position for multiplier attributes."""
        multiplier = 0
        for pos in winning_positions:
            if self.board[pos["reel"]][pos["row"]].check_attribute(multiplier_key):
                multiplier += self.board[pos["reel"]][pos["row"]].get_attribute(
                    multiplier_key
                )
        return max(multiplier, 1)

    def get_line_win(
        self, kind: int, sym_name: str, multiplier_key: str, positions: list
    ) -> List[type]:
        """Find line wins and multipliers."""
        mult = self.get_line_mults(positions, multiplier_key)
        win = self.config.paytable[(kind, sym_name)] * mult
        base_win = self.config.paytable[(kind, sym_name)]

        return base_win, win, mult

    def record_line_win(self, kind: int, symbol: str, mult: int, gametype: str) -> None:
        """Force file description for line-win."""
        self.record(
            {"kind": kind, "symbol": symbol, "mult": mult, "gametype": gametype}
        )

    def line_win_info(
        self, symbol: str, kind: int, win: float, positions: list, meta_data: dict
    ) -> dict:
        """Construct line-win event key."""
        return {
            "symbol": symbol,
            "kind": kind,
            "win": win,
            "positions": positions,
            "meta": meta_data,
        }

    def get_line_data(
        self,
        wild_key: str = "wild",
        multiplier_key: str = "multiplier",
        record_wins: bool = None,
    ):
        """Primary function for finding line wins on the active game board."""
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        for line_index in self.config.pay_lines:
            win_line = []
            for reel, _ in enumerate(self.board):
                win_line.append(
                    self.board[reel][self.config.pay_lines[line_index][reel]]
                )

            matches, wild_matches = 0, 0
            first_non_wild = None
            finished_wild_wins = False
            for sym in win_line:
                if not (sym.check_attribute(wild_key)) or finished_wild_wins:
                    if first_non_wild is None:
                        first_non_wild = sym
                        finished_wild_wins = True
                        matches = 1
                    else:
                        if sym.name == first_non_wild.name or sym.check_attribute(
                            wild_key
                        ):
                            matches += 1
                        else:
                            break
                elif not (finished_wild_wins):
                    wild_matches += 1

            win = 0
            if win_line[0].check_attribute(wild_key) and (
                (wild_matches, win_line[0].name) in self.config.paytable
            ):
                if first_non_wild == "" or not (
                    (wild_matches + matches, first_non_wild.name)
                    in self.config.paytable
                ):
                    positions = [
                        {"reel": reel_, "row": self.config.pay_lines[line_index][reel_]}
                        for reel_ in range(wild_matches)
                    ]
                    base_win, win, mult = self.get_line_win(
                        wild_matches, first_non_wild.name, multiplier_key, positions
                    )
                    mult *= self.global_multiplier
                    win_dict = self.line_win_info(
                        win_line[0].name,
                        wild_matches,
                        win,
                        positions,
                        {
                            "lineIndex": line_index,
                            "multiplier": mult,
                            "winWithoutMult": base_win,
                            "globalMult": self.global_multiplier,
                            "lineMultiplier": mult / self.global_multiplier,
                        },
                    )
                    return_data["wins"].append(win_dict)
                    return_data["wins"] += [
                        {
                            "symbol": win_line[0].name,
                            "kind": wild_matches,
                            "win": win,
                            "positions": positions,
                            "meta": {
                                "lineIndex": line_index,
                                "multiplier": mult,
                                "winWithoutMult": base_win,
                            },
                        }
                    ]
                    if record_wins:
                        self.record_line_win(
                            wild_matches, win_line[0].name, mult, self.gametype
                        )
                else:
                    if (
                        self.config.paytable[(wild_matches, win_line[0].name)]
                        > self.config.paytable[
                            wild_matches + matches, first_non_wild.name
                        ]
                    ):
                        positions = [
                            {
                                "reel": reel_,
                                "row": self.config.pay_lines[line_index][reel_],
                            }
                            for reel_ in range(wild_matches)
                        ]
                        base_win, win, mult = self.get_line_win(
                            wild_matches, first_non_wild.name, multiplier_key, positions
                        )
                        mult *= self.global_multiplier
                        win_dict = self.line_win_info(
                            win_line[0].name,
                            wild_matches,
                            win,
                            positions,
                            {
                                "lineIndex": line_index,
                                "multiplier": mult,
                                "winWithoutMult": base_win,
                                "globalMult": self.global_multiplier,
                                "lineMultiplier": mult / self.global_multiplier,
                            },
                        )
                        return_data["wins"].append(win_dict)
                        if record_wins:
                            self.record_line_win(
                                wild_matches, win_line[0].name, mult, self.gametype
                            )
                    else:
                        positions = [
                            {
                                "reel": reel_,
                                "row": self.config.pay_lines[line_index][reel_],
                            }
                            for reel_ in range(wild_matches + matches)
                        ]
                        base_win, win, mult = self.get_line_win(
                            wild_matches + matches,
                            first_non_wild.name,
                            multiplier_key,
                            positions,
                        )
                        mult *= self.global_multiplier
                        win_dict = self.line_win_info(
                            first_non_wild.name,
                            wild_matches + matches,
                            win,
                            positions,
                            {
                                "lineIndex": line_index,
                                "multiplier": mult,
                                "winWithoutMult": base_win,
                                "globalMult": self.global_multiplier,
                                "lineMultiplier": mult / self.global_multiplier,
                            },
                        )
                        return_data["wins"].append(win_dict)
                        if record_wins:
                            self.record_line_win(
                                wild_matches + matches,
                                first_non_wild.name,
                                mult,
                                self.gametype,
                            )
            else:
                if (
                    first_non_wild != ""
                    and (wild_matches + matches, first_non_wild.name)
                    in self.config.paytable
                ):
                    positions = [
                        {"reel": reel_, "row": self.config.pay_lines[line_index][reel_]}
                        for reel_ in range(wild_matches + matches)
                    ]
                    base_win, win, mult = self.get_line_win(
                        wild_matches + matches,
                        first_non_wild.name,
                        multiplier_key,
                        positions,
                    )
                    mult *= self.global_multiplier
                    win_dict = self.line_win_info(
                        first_non_wild.name,
                        wild_matches + matches,
                        win,
                        positions,
                        {
                            "lineIndex": line_index,
                            "multiplier": mult,
                            "winWithoutMult": base_win,
                            "globalMult": self.global_multiplier,
                            "lineMultiplier": int(mult / self.global_multiplier),
                        },
                    )
                    return_data["wins"].append(win_dict)
                    if record_wins:
                        self.record_line_win(
                            wild_matches + matches,
                            first_non_wild.name,
                            mult,
                            self.gametype,
                        )

            return_data["totalWin"] += win

        return return_data
