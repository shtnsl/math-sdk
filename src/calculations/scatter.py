from collections import defaultdict

class ScatterWins:

    def recordScatterWins(self, numWinningSyms:int, symbol:int, totalMultiplier:int, gameType:str) -> None:
        self.record({
            "winSize": numWinningSyms,
            "symbol": symbol,
            "totalMult": totalMultiplier,
            "gameType": gameType
        })
    
    def getScatterPayWinData(self, recordWins: bool = True, wild_key:str = "wild", multiplier_key:str = "multiplier") -> dict:
        returnData = {
            "totalWin": 0,
            "wins": [],
        }
        explodingSymbols = []
        symbolsOnBoard = defaultdict(list)
        wildPositions = []
        totalWin = 0.0
        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                if self.board[reel][row].name not in self.config.special_symbols[wild_key]:
                    symbolsOnBoard[self.board[reel][row].name].append({'reel': reel, 'row': row})
                else:
                    wildPositions.append({'reel': reel, 'row': row})

        #Update all symbol positons with wilds, as this symbol is shared
        for sym in symbolsOnBoard.keys():
            if len(wildPositions) > 0:
                symbolsOnBoard[sym].append(wildPositions)
            winSize = len(symbolsOnBoard[sym])
            if (winSize, sym) in self.config.paytable:
                symbolMultiplier = 0
                for positions in symbolsOnBoard[sym]:
                    if self.board[positions['reel']][positions['row']].check_attribute(multiplier_key):
                        symbolMultiplier += self.board[positions['reel']][positions['row']].get_attribute(multiplier_key)
                    symbolMultiplier = max(symbolMultiplier, 1)

                    self.board[positions['reel']][positions['row']].assign_attribute({'explode': True})
                    #Account for special symbols, such as wilds which can apply to multiple groups
                    if positions not in explodingSymbols:
                        explodingSymbols.append(positions)

                if recordWins:
                    self.recordScatterWins(winSize, sym, symbolMultiplier*self.global_multiplier, self.gametype)
                symbolWinData = {
                    'symbol': sym, 
                    'win': self.config.paytable[(winSize, sym)]*self.global_multiplier*symbolMultiplier,
                    'positions': symbolsOnBoard[sym],
                    'meta': {'globalMultiplier': self.global_multiplier, 
                             'symbolMultiplier': symbolMultiplier,
                             'winWithoutMult': self.config.paytable[(winSize, sym)]}
                }
                totalWin += symbolWinData['win']
                returnData['wins'].append(symbolWinData)

        returnData['totalWin'] = totalWin
        self.win_manager.tumble_win = totalWin
        self.explodingSymbols = explodingSymbols

        return returnData
