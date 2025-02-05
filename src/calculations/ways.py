class WaysWins:

    def getWaysWinData(self, wild_key: str = "wild"):
        self.currentWaysWin = 0
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.tumble_win = 0
        potentialWins = {}
        wilds = [[] for _ in range(len(self.board))]
        potentialWins = {}

        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                sym = self.board[reel][row].name
                try:
                    potentialWins[sym.name][reel].append({"reel": reel, "row": row})
                except:
                    if reel == 0:
                        potentialWins[sym.name] = [[] for _ in range(len(self.board))]
                        potentialWins[sym.name][0] = [{"reel": reel, "row": row}]

                if sym["name"] in self.config.special_symbols[wild_key]:
                    wilds[reel].append({"reel": reel, "row": row})

        for symbol in potentialWins:
            kind, ways = 0, 1
            for reel in range(len(potentialWins[symbol])):
                if len(potentialWins[symbol][reel]) > 0 or len(wilds[reel]) > 0:
                    kind += 1
                    ways *= len(potentialWins[symbol][reel]) + len(wilds[reel])
                else:
                    break

            if (kind, symbol) in self.config.paytable:
                positions = []
                for reel in range(kind):
                    for pos in potentialWins[symbol][reel]:
                        positions += [pos]
                    for pos in wilds[reel]:
                        positions += [pos]

                win = self.config.paytable[kind, symbol] * ways
                return_data["wins"] += [
                    {
                        "symbol": symbol,
                        "kind": kind,
                        "win": win,
                        "positions": positions,
                        "meta": {"ways": ways, "multiplier": 1},
                    }
                ]
                return_data["totalWin"] += win
                self.record(
                    {
                        "kind": kind,
                        "symbol": symbol,
                        "ways": ways,
                        "gametype": self.gametype,
                    }
                )

        return return_data
