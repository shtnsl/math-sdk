
UPDATE_TUMBLE_BANNER = "updateTumbleBanner"
BOAD_MULT_INFO = "boardMultiplierInfo"
from src.events.events import *

def updateTumbleBoardBanner(gameState):
    event = {
        "index": len(gameState.book['events']),
        "type": UPDATE_TUMBLE_BANNER,
        "amount": int(round(min(gameState.spinWin, gameState.config.winCap)*100, 0))
    }
    gameState.book['events'] += [deepcopy(event)]

def sendBoardMultInfo(gameState, boardMult:int, multInfo: dict):
    multEventInfo = []
    if gameState.config.includePadding:
        for m in range(multInfo):
            multEventInfo.append({'positions': [{'reel': multInfo[m]['reel'], 'row': multInfo[m]['row']+1, 'multiplier': multInfo[m]['value']}]})
    else:
        for m in range(multInfo):
            multEventInfo.append({'positions': [{'reel': multInfo[m]['reel'], 'row': multInfo[m]['row'], 'multiplier': multInfo[m]['value']}]})
            
    event = {
        "index": len(gameState.book['events']),
        "type": BOAD_MULT_INFO,
        "totalMult": deepcopy(boardMult),
        "multInfo": deepcopy(multEventInfo)
    }
    gameState.book['events'] += [event]