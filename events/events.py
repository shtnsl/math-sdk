from events.event_constants import *
from copy import deepcopy

def getSpecialSymbolAttributes(gameState):
    for reel in range(len(gameState.board)):
        for row in range(len(gameState.board[reel])):
            if gameState.board[reel][row].special:
                pass

def revealBoardEvent(gameState):
    boardForClient = []
    for reel in range(len(gameState.board)):
        boardForClient.append([gameState.board[reel][row].name for row in range(len(gameState.board[reel]))])
    if gameState.config.includePaddingSymbols:
        for reel in range(len(boardForClient)):
            boardForClient[reel] = [deepcopy(gameState.topSymbols[reel].name)]+boardForClient[reel]
            boardForClient[reel].append(deepcopy(gameState.bottomSymbols[reel].name))
    
    event = {
        "index": len(gameState.book['events']), 
        "type": REVEAL,
        "board": deepcopy(boardForClient),
        "paddingPositions": deepcopy(gameState.reelPositions),
        "gameType": deepcopy(gameState.gameType),
        "anticipation": deepcopy(gameState.anticipation),
    }

    gameState.book["events"] += [event]

def freeSpinsTriggerEvent(gameState, includePaddingIndex=True, baseGameTrigger=True, freeGameTrigger=False):
    assert baseGameTrigger != freeGameTrigger, "must set either baseGameTrigger or freeSpinTrigger to = True"
    scatterPositions = gameState.specialSymbolsOnBoard['scatter']
    if includePaddingIndex:
        for pos in scatterPositions:
            pos["row"] += 1

    if baseGameTrigger:
        event = {
            "index": len(gameState.book["events"]),
            "type": FREESPINTRIGGER,
            "totalFs": gameState.totFs,
        }
    elif freeGameTrigger:
        event = {
            "index": len(gameState.book["events"]),
            "type": FREESPINRETRIGGER,
            "totalFs": gameState.totFs,
        }

    assert gameState.totFs >0, "total freespins (gameState.totFs) must be >0"
    gameState.book["events"] += [event]

def winInfoEvent(gameState, includePaddingIndex=True):
    """
    includePaddingIndex: starts winning-symbol poasitions at row=1, to account for top/bottom symbol inclusion in board
    """
    winDataCopy = {}    
    winDataCopy["wins"] = gameState.winData["wins"]
    for idx,w in enumerate(gameState.winData["wins"]):
        winDataCopy["wins"][idx]["amount"] = int(min(round(winDataCopy["wins"][idx]["win"]*100,0),gameState.config.winCap*100))
        if includePaddingIndex:
            newPositions = [{"reel":p["reel"], "row": p["row"]+1} for p in w["positions"]]
        else:
            newPositions = w["positions"]

        winDataCopy["wins"][idx]["win"] = int(round(winDataCopy["wins"][idx]["win"]*100,0))
        winDataCopy["wins"][idx]["win"] = int(round(winDataCopy["wins"][idx]["win"]*100,0))
        winDataCopy["wins"][idx]["positions"] = newPositions   
        winDataCopy["wins"][idx]["amount"] = winDataCopy["wins"][idx]["win"],
        winDataCopy["wins"][idx]["meta"] = winDataCopy["wins"][idx]["meta"]
        winDataCopy["wins"][idx]["meta"]["winWithOutMult"] = int(min(round(winDataCopy["wins"][idx]["meta"]["winWithoutMult"]*100,0),gameState.config.winCap*100))
        
        dic = {
            "index": len(gameState.book['events']),
            "type": WIN_DATA,
            "totalWin": min(int(round(gameState.winData['totalWin']*100, 0)),int(round(gameState.config.winCap*100, 0))),
            "wins": winDataCopy["wins"],
        }
        gameState.book['events'] += [dic]