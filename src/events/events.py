from src.events.event_constants import *
from collections import defaultdict
from copy import deepcopy

def getSpecialSymbolAttributes(gameState):
    for reel in range(len(gameState.board)):
        for row in range(len(gameState.board[reel])):
            if gameState.board[reel][row].special:
                pass

def revealReducedBoardEvent(gameState):
    boardForClient = []
    for reel in range(len(gameState.board)):
        boardForClient.append([gameState.board[reel][row].name for row in range(len(gameState.board[reel]))])
    if gameState.config.includePaddingSymbols:
        for reel in range(len(boardForClient)):
            boardForClient[reel] = [deepcopy(gameState.topSymbols[reel].name)]+boardForClient[reel]
            boardForClient[reel].append(deepcopy(gameState.bottomSymbols[reel].name))
    
    printSpecials = defaultdict(list)
    for prop in gameState.specialSymbolsOnBoard:
        if len(gameState.specialSymbolsOnBoard[prop]) >0:
            for sym in gameState.specialSymbolsOnBoard[prop]:
                if gameState.config.includePadding:
                    if gameState.board[sym['reel']][sym['row']].checkAttribute(prop) and (gameState.board[sym['reel']][sym['row']].getAttribute(prop) == True or type(gameState.board[sym['reel']][sym['row']].getAttribute(prop)) != bool):
                        printSpecials[prop].append({'reel':sym['reel'], 'row':sym['row']+1, str(prop): gameState.board[sym['reel']][sym['row']].getAttribute(prop)})
                else:
                    if gameState.board[sym['reel']][sym['row']].checkAttribute(prop) and (gameState.board[sym['reel']][sym['row']].getAttribute(prop) == True or type(gameState.board[sym['reel']][sym['row']].getAttribute(prop)) != bool):
                        printSpecials[prop].append({'reel':sym['reel'], 'row':sym['row'], str(prop): gameState.board[sym['reel']][sym['row']].getAttribute(prop)})

    event = {
        "index": len(gameState.book['events']), 
        "type": REVEAL,
        "board": deepcopy(boardForClient),
        "specials": deepcopy(printSpecials),
        "paddingPositions": deepcopy(gameState.reelPositions),
        "gameType": deepcopy(gameState.gameType),
        "anticipation": deepcopy(gameState.anticipation),
    }

    gameState.book["events"] += [event]

def jsonReadySymbol(symbol:object, specialAttributes:list=None):
    assert specialAttributes is not None
    printSym = {'name': symbol.name}
    attrs = vars(symbol)
    for key,val in attrs.items():
        if key in specialAttributes and symbol.getAttribute(key) != False:
            printSym[key] = val 
    return printSym

def revealBoardEvent(gameState):
    boardForClient = []
    specialAttributes = list(gameState.config.specialSymbols.keys())
    for reel in range(len(gameState.board)):
        boardForClient.append([])
        for row in range(len(gameState.board[reel])):
            boardForClient[reel].append(jsonReadySymbol(gameState.board[reel][row], specialAttributes))

    if gameState.config.includePaddingSymbols:
        for reel in range(len(boardForClient)):
            boardForClient[reel] = [jsonReadySymbol(gameState.topSymbols[reel],specialAttributes)]+boardForClient[reel]
            boardForClient[reel].append(jsonReadySymbol(gameState.bottomSymbols[reel], specialAttributes))
    
    event = {
        "index": len(gameState.book['events']), 
        "type": REVEAL,
        "board": boardForClient,
        "paddingPositions": gameState.reelPositions,
        "gameType": gameState.gameType,
        "anticipation": gameState.anticipation,
    }

    gameState.book["events"] += [deepcopy(event)]

def freeSpinsTriggerEvent(gameState, includePaddingIndex=True, baseGameTrigger:bool=None, freeGameTrigger:bool=None):
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

def setWinEvent(gameState, winLevelKey: str = "standard"):
    if not(gameState.winCapTriggered):
        event = {"index": len(gameState.book['events']),
                "type": SET_WIN,
                "amount": int(min(round(gameState.winManager.spinWin*100,0), gameState.config.winCap*100)),
                "winLevel": gameState.config.getWinLevel(gameState.winManager.spinWin, winLevelKey)
        }
        gameState.book["events"] += [event]

def setTotalWinEvent(gameState):
    event = {"index": len(gameState.book['events']),
             "type": SET_TOTAL_WIN,
             "amount" :int(round(min(gameState.winManager.runningBetWin, gameState.config.winCap)*100, 0))
    }
    gameState.book["events"] += [event]

def setTumbleWinEvent(gameState):
    event = {"index": len(gameState.book['events']),
             "type": SET_TUMBLE_WIN,
             "amount": int(round(min(gameState.tumbleWin, gameState.config.winCap)*100))
             }
    gameState.book["events"] += [event]

def winCapEvent(gameState):
    event = {
        "index": len(gameState.book['events']), 
        "type": WINCAP,
        "amount": int(round(min(gameState.winManager.runningBetWin, gameState.config.winCap)*100, 0))
    }
    gameState.book["events"] += [event]

def winInfoEvent(gameState, includePaddingIndex=True):
    """
    includePaddingIndex: starts winning-symbol poasitions at row=1, to account for top/bottom symbol inclusion in board
    """
    winDataCopy = {}    
    winDataCopy["wins"] = gameState.winData["wins"]
    for idx,w in enumerate(gameState.winData["wins"]):
        if includePaddingIndex:
            newPositions = []
            for p in w["positions"]:
                newPositions.append({"reel":p["reel"], "row": p["row"]+1})
        else:
            newPositions = w["positions"]

        winDataCopy["wins"][idx]["win"] = int(round(min(winDataCopy["wins"][idx]["win"], gameState.config.winCap)*100,0))
        winDataCopy["wins"][idx]["positions"] = newPositions   
        winDataCopy["wins"][idx]["meta"] = winDataCopy["wins"][idx]["meta"]
        winDataCopy["wins"][idx]["meta"]["winWithoutMult"] = int(round(min(winDataCopy["wins"][idx]["meta"]["winWithoutMult"], gameState.config.winCap)*100, 0))
        
        dictData = {
            "index": len(gameState.book['events']),
            "type": WIN_DATA,
            "totalWin": int(round(min(gameState.winData['totalWin'], gameState.config.winCap)*100, 0)),
            "wins": winDataCopy["wins"],
        }
        gameState.book['events'] += [deepcopy(dictData)]

def updateTumbleWinEvent(gameState):
    event = {
        "index": len(gameState.book['events']),
        "type": UPDATE_TUMBLE_WIN,
        "amount": int(round(min(gameState.winManager.spinWin, gameState.config.winCap)*100, 0))
    }
    gameState.book['events'] += [deepcopy(event)]

def updateFreeSpinEvent(gameState):
    event = {
        "index": len(gameState.book['events']), 
        "type": UPDATE_FS, 
        "amount": int(gameState.fs),
        "total": int(gameState.totFs)}
    gameState.book["events"] += [event]

def freeSpinEndEvent(gameState):
    event = {"index": len(gameState.book['events']), 
             "type": FREE_SPIN_END, 
             "amount": int(round(min(gameState.freeGameWins, gameState.config.winCap)*100, 0))
    }
    gameState.book["events"] += [event]

def finalWinEvent(gameState):
    event = {"index": len(gameState.book['events']), 
             "type": FINAL_WIN,
             "amount": int(round(min(gameState.finalWin, gameState.config.winCap)*100, 0))
    }
    gameState.book["events"] += [event]

def updateGlobalMultEvent(gameState):
    event = {"index": 
             len(gameState.book['events']), 
             "type": UPDATE_GLOBAL_MULT, 
             "globalMult": int(gameState.globalMultiplier)}
    
    gameState.book["events"] += [event]

def tumbleBoardEvent(gameState):
    specialAttributes = list(gameState.config.specialSymbols.keys())
    if gameState.config.includePaddingSymbols:
        exploding = []
        for sym in gameState.explodingSymbols:
            exploding.append({'reel':sym['reel'], "row": sym['row'] + 1})
    else:
        exploding = gameState.explodingSymbols
    
    exploding = sorted(exploding, key=lambda x: x['reel'])

    newSymbols = [[] for _ in range(gameState.config.numReels)]
    for r in range(len(gameState.newSymbolsFromTumble)):
        if len(gameState.newSymbolsFromTumble[r]) > 0:
            newSymbols[r] = [jsonReadySymbol(s, specialAttributes) for s in gameState.newSymbolsFromTumble[r]]

    gameState.book["events"] += [{
        "index": len(gameState.book['events']),
        "type": TUMBLE_BOARD,
        "newSymbols": deepcopy(newSymbols),
        "explodingSymbols": deepcopy(exploding)
    }]