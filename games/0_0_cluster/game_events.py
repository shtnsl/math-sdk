
from copy import copy, deepcopy
from src.events.events import *

APPLY_TUMBLE_MULTIPLIER = "applyMultiplierToTumble"
UPDATE_GRID = "updateGrid"

def applyMutToTumbleWinEvent(gameState):
    event = {"index": len(gameState.book['events']),
             "type": APPLY_TUMBLE_MULTIPLIER,
             "amount" :int(round(min(gameState.runningBetWin, gameState.config.winCap)*100, 0)),
             "meta": {
                "baseAmount": gameState.tumbleWin,
                "tumbleMultiplier": gameState.globalMult        
             }
    }
    gameState.book["events"] += [deepcopy(event)]

def updateGridMultiplierEvent(gameState):
   event = {
      "index": len(gameState.book['events']),
      "type": UPDATE_GRID,
      "gridMultipliers": gameState.positionMultipliers
   }
   gameState.book["events"] += [deepcopy(event)]
    