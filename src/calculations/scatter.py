from collections import defaultdict

class ScatterWins:

    def recordScatterWins(self, numWinningSyms:int, symbol:int, totalMultiplier:int, gameType:str) -> None:
        self.record({
            "winSize": numWinningSyms,
            "symbol": symbol,
            "totalMult": totalMultiplier,
            "gameType": gameType
        })
    
    def getScatterPayWinData(self, recordWins: bool = True, wildKey:str = "wild", multiplierKey:str = "multiplier") -> dict:
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
                if self.board[reel][row].name not in self.config.specialSymbols[wildKey]:
                    symbolsOnBoard[self.board[reel][row].name].append({'reel': reel, 'row': row})
                else:
                    wildPositions.append({'reel': reel, 'row': row})

        #Update all symbol positons with wilds, as this symbol is shared
        for sym in symbolsOnBoard.keys():
            if len(wildPositions) > 0:
                symbolsOnBoard[sym].append(wildPositions)
            winSize = len(symbolsOnBoard[sym])
            if (winSize, sym) in self.config.payTable:
                symbolMultiplier = 0
                for positions in symbolsOnBoard[sym]:
                    if self.board[positions['reel']][positions['row']].checkAttribute(multiplierKey):
                        symbolMultiplier += self.board[positions['reel']][positions['row']].getAttribute(multiplierKey)
                    symbolMultiplier = max(symbolMultiplier, 1)

                    self.board[positions['reel']][positions['row']].explode = True
                    #Account for special symbols, such as wilds which can apply to multiple groups
                    if positions not in explodingSymbols:
                        explodingSymbols.append(positions)

                if recordWins:
                    self.recordScatterWins(winSize, sym, symbolMultiplier*self.globalMultiplier, self.gameType)
                symbolWinData = {
                    'symbol': sym, 
                    'win': self.config.payTable[(winSize, sym)]*self.globalMultiplier*symbolMultiplier,
                    'positions': symbolsOnBoard[sym],
                    'meta': {'globalMultiplier': self.globalMultiplier, 
                             'symbolMultiplier': symbolMultiplier,
                             'winWithoutMult': self.config.payTable[(winSize, sym)]}
                }
                totalWin += symbolWinData['win']
                returnData['wins'].append(symbolWinData)

        returnData['totalWin'] = totalWin
        self.winManager.tumbleWin = totalWin
        self.explodingSymbols = explodingSymbols

        return returnData
