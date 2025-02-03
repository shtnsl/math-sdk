from typing import List, Tuple, Dict

class LineWins:
    def addMultipliersInWinningPositions(self, winingPositions:List[Dict], multiplier_key:str = "multiplier"):
        multiplier = 0
        for pos in winingPositions:
            if self.board[pos['reel']][pos['row']].check_attribute(multiplier_key):
                multiplier += self.board[pos['reel']][pos['row']].get_attribute(multiplier_key)
        return max(multiplier, 1)
    
    def getLineWin(self, kind:int, symName:str, multiplier_key:str, positions:list) -> List[type]:
        mult = self.addMultipliersInWinningPositions(positions, multiplier_key)
        win = self.config.paytable[(kind, symName)]*mult
        baseWin = self.config.paytable[(kind, symName)]
        
        return baseWin, win, mult

    def recordLineWin(self, kind:int, symbol:str, mult:int, gameType:str) -> None:
        self.record({
            "kind": kind,
            "symbol": symbol,
            "mult": mult,
            "gameType": gameType
        })
    
    def lineWinInfo(self, symbol: str, kind: int, win: float, positions: list, metaData: dict) -> dict:
        return {
            "symbol": symbol,
            "kind": kind,
            "win": win,
            "positions": positions,
            "meta": metaData
        }

    def getLineWinData(self, wild_key:str = 'wild', multiplier_key:str = 'multiplier', recordWins:bool = None):
        returnData = {
            "totalWin": 0,
            "wins": [],
        }
        for lineIndex in self.config.pay_lines:
            winLine = []
            for reel in range(len(self.board)):
                winLine.append(self.board[reel][self.config.pay_lines[lineIndex][reel]])
            
            matches, wildMatches = 0, 0
            firstSymNotWild = ""
            finishedWildWins = False 
            for sym in winLine:
                if not(sym.check_attribute(wild_key)) or finishedWildWins:
                    if firstSymNotWild == "":
                        firstSymNotWild = sym 
                        finishedWildWins = True
                        matches = 1
                    else:
                        if sym.name == firstSymNotWild.name or sym.check_attribute(wild_key):
                           matches += 1
                        else:
                            break
                elif not(finishedWildWins):
                    wildMatches += 1

            win = 0
            if winLine[0].check_attribute(wild_key) and ((wildMatches, winLine[0].name) in self.config.paytable):
                "check if all wilds, or first non-wild symbol is not paying"
                if firstSymNotWild == "" or not((wildMatches+matches, firstSymNotWild.name) in self.config.paytable):
                    positions = [{"reel": reel_, "row": self.config.pay_lines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                    baseWin, win, mult = self.getLineWin(wildMatches, firstSymNotWild.name, multiplier_key, positions)
                    mult *= self.global_multiplier
                    winDict = self.lineWinInfo(winLine[0].name, 
                                               wildMatches, 
                                               win, 
                                               positions, 
                                               {"lineIndex": lineIndex, 
                                                "multiplier": mult, 
                                                "winWithoutMult": baseWin, 
                                                "globalMultiplier": self.global_multiplier, 
                                                "lineMultiplier": mult/self.global_multiplier})
                    returnData['wins'].append(winDict)
                    returnData['wins'] += [{"symbol": winLine[0].name, "kind": wildMatches, "win": win, "positions": positions, "meta": {"lineIndex": lineIndex, "multiplier": mult, "winWithoutMult": baseWin}}]
                    if recordWins: self.recordLineWin(wildMatches, winLine[0].name, mult, self.gametype)
                else:
                    if self.config.paytable[(wildMatches, winLine[0].name)] > self.config.paytable[wildMatches+matches, firstSymNotWild.name]:
                        positions = [{"reel": reel_, "row": self.config.pay_lines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                        baseWin, win, mult = self.getLineWin(wildMatches, firstSymNotWild.name, multiplier_key, positions)
                        mult *= self.global_multiplier
                        winDict = self.lineWinInfo(winLine[0].name, 
                                                wildMatches, 
                                                win, 
                                                positions, 
                                                {"lineIndex": lineIndex, 
                                                    "multiplier": mult, 
                                                    "winWithoutMult": baseWin, 
                                                    "globalMultiplier": self.global_multiplier, 
                                                    "lineMultiplier": mult/self.global_multiplier})
                        returnData['wins'].append(winDict)
                        if recordWins: self.recordLineWin(wildMatches, winLine[0].name, mult, self.gametype)
                    else:
                        positions = [{"reel": reel_, "row": self.config.pay_lines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                        baseWin, win, mult = self.getLineWin(wildMatches+matches, firstSymNotWild.name, multiplier_key, positions)
                        mult *= self.global_multiplier
                        winDict = self.lineWinInfo(firstSymNotWild.name, 
                                                wildMatches+matches, 
                                                win, 
                                                positions, 
                                                {"lineIndex": lineIndex, 
                                                    "multiplier": mult, 
                                                    "winWithoutMult": baseWin, 
                                                    "globalMultiplier": self.global_multiplier, 
                                                    "lineMultiplier": mult/self.global_multiplier})
                        returnData['wins'].append(winDict)
                        if recordWins: self.recordLineWin(wildMatches+matches,firstSymNotWild.name, mult, self.gametype)
            else:
                if firstSymNotWild != "" and (wildMatches+matches, firstSymNotWild.name) in self.config.paytable:
                    positions = [{"reel": reel_, "row": self.config.pay_lines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                    baseWin, win, mult = self.getLineWin(wildMatches+matches, firstSymNotWild.name, multiplier_key, positions)
                    mult *= self.global_multiplier
                    winDict = self.lineWinInfo(firstSymNotWild.name, 
                                            wildMatches+matches, 
                                            win, 
                                            positions, 
                                            {"lineIndex": lineIndex, 
                                            "multiplier": mult, 
                                            "winWithoutMult": baseWin, 
                                            "globalMultiplier": self.global_multiplier, 
                                            "lineMultiplier": int(mult/self.global_multiplier)})
                    returnData['wins'].append(winDict)
                    if recordWins: self.recordLineWin(wildMatches+matches,firstSymNotWild.name, mult, self.gametype)

            returnData['totalWin'] += win

        return returnData