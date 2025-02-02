
UPDATE_TUMBLE_BANNER = "updateTumbleBanner"
BOAD_MULT_INFO = "boardMultiplierInfo"
from src.events.events import *

def sendBoardMultInfoEvent(gameState, boardMult:int, multInfo: dict, baseWin:float, updatedWin:float):
    multiplierInfo, winInfo = {}, {}
    multiplierInfo["positions"] = []
    if gameState.config.includePadding:
        for m in range(len(multInfo)):
            multiplierInfo["positions"].append({'reel': multInfo[m]['reel'], 'row': multInfo[m]['row']+1, 'multiplier': multInfo[m]['value']})
    else:
        for m in range(multInfo):
            multiplierInfo["positions"].append({'reel': multInfo[m]['reel'], 'row': multInfo[m]['row'], 'multiplier': multInfo[m]['value']})

    winInfo["tumbleWin"] = int(round(min(baseWin, gameState.config.winCap)*100))
    winInfo["boardMult"] = boardMult
    winInfo["totalWin"] = int(round(min(updatedWin, gameState.config.winCap)*100))

    assert round(updatedWin, 1) == round(baseWin*boardMult, 1)
    event = {
        "index": len(gameState.book['events']),
        "type": BOAD_MULT_INFO,
        "multInfo": multiplierInfo,
        "winInfo": winInfo
    }
    gameState.book['events'] += [event]