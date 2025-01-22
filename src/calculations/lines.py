from typing import List, Tuple, Dict
from copy import deepcopy

class LineWins:
    def addMultipliersInWinningPositions(self, winingPositions:List[Dict], multiplierKey:str = "multiplier"):
        multiplier = 0
        for pos in winingPositions:
            if self.board[pos['reel']][pos['row']].checkAttribute(multiplierKey):
                multiplier += self.board[pos['reel']][pos['row']].getAttribute(multiplierKey)
        return max(multiplier, 1)
    
    def getLineWin(self, kind:int, symName:str, multiplierKey:str, positions:list) -> List[type]:
        mult = self.addMultipliersInWinningPositions(positions, multiplierKey)
        win = self.config.payTable[(kind, symName)]*mult
        baseWin = self.config.payTable[(kind, symName)]
        return baseWin, win, mult

    def recordLineWin(self, kind:int, symbol:str, mult:int, gameType:str):
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

    def calculateLineWins(self, wildKey:str = 'wild', multiplierKey:str = 'multiplier', recordWins=None):
        returnData = {
            "totalWin": 0,
            "wins": [],
        }
        for lineIndex in self.config.payLines:
            winLine = []
            for reel in range(len(self.board)):
                winLine.append(self.board[reel][self.config.payLines[lineIndex][reel]])
            
            matches, wildMatches = 0, 0
            firstSymNotWild = ""
            finishedWildWins = False 
            for sym in winLine:
                if not(sym.checkAttribute(wildKey)) or finishedWildWins:
                    if firstSymNotWild == "":
                        firstSymNotWild = sym 
                        finishedWildWins = True
                        matches = 1
                    else:
                        if sym.name == firstSymNotWild.name or sym.checkAttribute(wildKey):
                           matches += 1
                        else:
                            break
                elif not(finishedWildWins):
                    wildMatches += 1

            win = 0
            if winLine[0].checkAttribute(wildKey) and ((wildMatches, winLine[0].name) in self.config.payTable):
                "check if all wilds, or first non-wild symbol is not paying"
                if firstSymNotWild == "" or not((wildMatches+matches, firstSymNotWild.name) in self.config.payTable):
                    positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                    baseWin, win, mult = self.getLineWin(wildMatches, firstSymNotWild.name, multiplierKey, positions)
                    mult *= self.globalMultiplier
                    winDict = self.lineWinInfo(winLine[0].name, 
                                               wildMatches, 
                                               win, 
                                               positions, 
                                               {"lineIndex": lineIndex, 
                                                "multiplier": mult, 
                                                "winWithoutMult": baseWin, 
                                                "globalMultiplier": self.globalMultiplier, 
                                                "lineMultiplier": mult/self.globalMultiplier})
                    returnData['wins'].append(winDict)
                    returnData['wins'] += [{"symbol": winLine[0].name, "kind": wildMatches, "win": win, "positions": positions, "meta": {"lineIndex": lineIndex, "multiplier": mult, "winWithoutMult": baseWin}}]
                    if recordWins: self.recordLineWin(wildMatches, winLine[0].name, mult, self.gameType)
                else:
                    if self.config.payTable[(wildMatches, winLine[0].name)] > self.config.payTable[wildMatches+matches, firstSymNotWild.name]:
                        positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches)]
                        baseWin, win, mult = self.getLineWin(wildMatches, firstSymNotWild.name, multiplierKey, positions)
                        mult *= self.globalMultiplier
                        winDict = self.lineWinInfo(winLine[0].name, 
                                                wildMatches, 
                                                win, 
                                                positions, 
                                                {"lineIndex": lineIndex, 
                                                    "multiplier": mult, 
                                                    "winWithoutMult": baseWin, 
                                                    "globalMultiplier": self.globalMultiplier, 
                                                    "lineMultiplier": mult/self.globalMultiplier})
                        returnData['wins'].append(winDict)
                        if recordWins: self.recordLineWin(wildMatches, winLine[0].name, mult, self.gameType)
                    else:
                        positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                        baseWin, win, mult = self.getLineWin(wildMatches+matches, firstSymNotWild.name, multiplierKey, positions)
                        mult *= self.globalMultiplier
                        winDict = self.lineWinInfo(firstSymNotWild.name, 
                                                wildMatches+matches, 
                                                win, 
                                                positions, 
                                                {"lineIndex": lineIndex, 
                                                    "multiplier": mult, 
                                                    "winWithoutMult": baseWin, 
                                                    "globalMultiplier": self.globalMultiplier, 
                                                    "lineMultiplier": mult/self.globalMultiplier})
                        returnData['wins'].append(winDict)
                        if recordWins: self.recordLineWin(wildMatches+matches,firstSymNotWild.name, mult, self.gameType)
            else:
                if firstSymNotWild != "" and (wildMatches+matches, firstSymNotWild.name) in self.config.payTable:
                    positions = [{"reel": reel_, "row": self.config.payLines[lineIndex][reel_]} for reel_ in range(wildMatches+matches)]
                    baseWin, win, mult = self.getLineWin(wildMatches+matches, firstSymNotWild.name, multiplierKey, positions)
                    mult *= self.globalMultiplier
                    winDict = self.lineWinInfo(firstSymNotWild.name, 
                                            wildMatches+matches, 
                                            win, 
                                            positions, 
                                            {"lineIndex": lineIndex, 
                                                "multiplier": mult, 
                                                "winWithoutMult": baseWin, 
                                                "globalMultiplier": self.globalMultiplier, 
                                                "lineMultiplier": mult/self.globalMultiplier})
                    returnData['wins'].append(winDict)
                    if recordWins: self.recordLineWin(wildMatches+matches,firstSymNotWild.name, mult, self.gameType)

            returnData['totalWin'] += win

        self.winData = returnData
        totalLineWin = round(returnData['totalWin'],2)
        if totalLineWin > 0:
            self.updateGameModeWins(totalLineWin)
            self.runningBetWin += totalLineWin
            self.spinWin += totalLineWin