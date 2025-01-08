from typing import List, Tuple, Dict

class LineWins:

    def addMultipliersInWinningPositions(self, winingPositions:List[Dict], multiplierKey:str = "multiplier"):
        multiplier = 0
        for pos in winingPositions:
            if self.board[pos['reel']][pos['row']].checkAttribute(multiplierKey):
                multiplier += self.board[pos['reel']][pos['row']].getAttribute(multiplierKey)
        return max(multiplier, 1)

    def calculateLineWins(self, wildKey:str = 'wild', multiplierKey:str = 'multiplier'):
        returnData = {
            "totalWin": 0,
            "wins": [],
        }
        for lineIndex in self.config.payLines:
            winLine = []
            for reel in self.config.payLines[lineIndex]:
                winLine.append(self.board[reel][self.config.payLines[lineIndex][reel]])
            
            matches, wildMatches = 0, 0
            firstSymNotWild = ""
            finishedWildWins = False 

            for sym in winLine:
                if not(sym.checkAttribute(wildKey)):
                    if firstSymNotWild == "":
                        firstSymNotWild = sym 
                        finishedWildWins = True
                        matches = 1
                    else:
                        if sym in self.config.specialSymbols[wildKey]:
                           matches += 1
                        else:
                            break
                elif not(finishedWildWins):
                    wildMatches += 1

            win = 0
            if winLine[0].checkAttribute(wildKey) and ((wildMatches, winLine[0].name) in self.config.payTable):
                "check if all wilds, or first non-wild symbol is not paying"
                if firstSymNotWild == "" or not((wildMatches+matches, firstSymNotWild.name) in self.config.payTable):
                    win = self.config.payTable[(wildMatches, winLine[0].name)]
                    positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                    mult = 1 #TODO: get function to grab multiplier property
                    win = win*mult
                    returnData['wins'] += [{"symbol": winLine[0].name, "kind": wildMatches, "win": win, "positions": positions, "meta": {"lineIndex": lineIndex, "multiplier": mult}}]

                    # self.record({"kind": wildMatches, "symbol": winLine[0]['name'], "hasWild": True, "wildMult": 1, "gameType": self.gameType})
                else:
                    if self.config.payTable[(wildMatches, winLine[0].name)] > self.config.payTable[wildMatches+matches, firstSymNotWild.name]:
                        win = self.config.payTable[(wildMatches, winLine[0]['name'])]
                        positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                        mult = self.addMultipliersInWinningPositions(positions, multiplierKey)
                        mult *= self.globalMultiplier

                        win = win*mult
                        returnData['wins'] += [{"symbol": winLine[0].name, "kind": wildMatches, "win": win, "positions": positions, "meta": {"lineIndex": lineIndex, "multiplier": mult}}]
                        # self.record({"kind": wildMatches, "symbol": winLine[0]['name'], "hasWild": True, "wildMult": 1, "gameType": self.gameType})
                    else:
                        win = self.config.payTable[wildMatches+matches, firstSymNotWild.name]
                        positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                        mult = self.addMultipliersInWinningPositions(positions, multiplierKey)
                        mult *= self.globalMultiplier

                        win = win*mult
                        # self.record({"kind": wildMatches+matches, "symbol": firstSymNotWild.name, "hasWild": True, "wildMult": 1, "gameType": self.gameType})
                        returnData['wins'] += [{"symbol": firstSymNotWild.name, "kind": wildMatches+matches, "win": win, "positions": [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)], "meta": {"lineIndex": lineIndex, "multiplier": mult}}]

            else:
                if firstSymNotWild != "" and (wildMatches+matches, firstSymNotWild.name) in self.config.payTable:
                    win = self.config.payTable[(wildMatches+matches, firstSymNotWild.name)]
                    positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                    mult = self.addMultipliersInWinningPositions(positions, multiplierKey)
                    mult *= self.globalMultiplier

                    win = win*mult
                    # self.record({"kind": wildMatches+matches, "symbol": firstSymNotWild.name, "hasWild": True, "wildMult": 1, "gameType": self.gameType})
                    returnData['wins'] += [{"symbol": firstSymNotWild.name, "kind": wildMatches+matches, "win": win, "positions": positions, "meta": {"lineIndex": lineIndex, "multiplier": mult}}]

            if win > 0:
                print('here')
            returnData['totalWin'] += win