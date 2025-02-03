
UPDATE_TUMBLE_BANNER = "updateTumbleBanner"
BOAD_MULT_INFO = "boardMultiplierInfo"
from src.events.events import *

def send_mult_info_event(gamestate, board_mult:int, mult_info: dict, baseWin:float, updatedWin:float):
    multiplierInfo, winInfo = {}, {}
    multiplierInfo["positions"] = []
    if gamestate.config.include_padding:
        for m in range(len(mult_info)):
            multiplierInfo["positions"].append({'reel': mult_info[m]['reel'], 'row': mult_info[m]['row']+1, 'multiplier': mult_info[m]['value']})
    else:
        for m in range(mult_info):
            multiplierInfo["positions"].append({'reel': mult_info[m]['reel'], 'row': mult_info[m]['row'], 'multiplier': mult_info[m]['value']})

    winInfo["tumbleWin"] = int(round(min(baseWin, gamestate.config.wincap)*100))
    winInfo["board_mult"] = board_mult
    winInfo["totalWin"] = int(round(min(updatedWin, gamestate.config.wincap)*100))

    assert round(updatedWin, 1) == round(baseWin*board_mult, 1)
    event = {
        "index": len(gamestate.book['events']),
        "type": BOAD_MULT_INFO,
        "mult_info": multiplierInfo,
        "winInfo": winInfo
    }
    gamestate.book['events'] += [event]