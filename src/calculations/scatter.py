from collections import defaultdict

class ScatterWins:

    def getScatterPayWinData(self, wildKey:str = "wild") -> dict:
        returnData = {
            "totalWin": 0,
            "wins": [],
        }

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
            symbolsOnBoard[sym].append(wildPositions)
            winSize = len(symbolsOnBoard[sym])
            if (winSize, sym) in self.config.payTable:
                symbolWinData = {
                    'symbol': sym, 
                    'win': self.config.payTable(winSize, sym)*self.globalMultiplier,
                    'positions': symbolsOnBoard[sym],
                    'meta': {'multiplier': self.globalMultiplier, 'winWithoutMult': self.config.payTable(winSize, sym)}

                }
                totalWin += symbolWinData['win']
                returnData['wins'].append(symbolWinData)

        returnData['totalWin'] = totalWin

        return returnData
    
    def updateWinInformation(self, winData:dict):
        winFromTumble = winData['totalWin']
        self.tumbleWin = winFromTumble
        self.spinWin += winFromTumble
        self.runningBetWin += winFromTumble