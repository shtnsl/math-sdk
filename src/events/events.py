from src.events.event_constants import *
from collections import defaultdict
from copy import copy, deepcopy


def reveal_reduced_board_event(gamestate):
    board_client = []
    for reel in range(len(gamestate.board)):
        board_client.append([gamestate.board[reel][row].name for row in range(len(gamestate.board[reel]))])
    if gamestate.config.include_padding:
        for reel in range(len(board_client)):
            board_client[reel] = [gamestate.top_symbols[reel].name]+board_client[reel]
            board_client[reel].append(gamestate.bottom_symbols[reel].name)
    
    print_specials = defaultdict(list)
    for prop in gamestate.special_syms_on_board:
        if len(gamestate.special_syms_on_board[prop]) >0:
            for sym in gamestate.special_syms_on_board[prop]:
                if gamestate.config.include_padding:
                    if gamestate.board[sym['reel']][sym['row']].check_attribute(prop) and (gamestate.board[sym['reel']][sym['row']].get_attribute(prop) == True or type(gamestate.board[sym['reel']][sym['row']].get_attribute(prop)) != bool):
                        print_specials[prop].append({'reel':sym['reel'], 'row':sym['row']+1, str(prop): gamestate.board[sym['reel']][sym['row']].get_attribute(prop)})
                else:
                    if gamestate.board[sym['reel']][sym['row']].check_attribute(prop) and (gamestate.board[sym['reel']][sym['row']].get_attribute(prop) == True or type(gamestate.board[sym['reel']][sym['row']].get_attribute(prop)) != bool):
                        print_specials[prop].append({'reel':sym['reel'], 'row':sym['row'], str(prop): gamestate.board[sym['reel']][sym['row']].get_attribute(prop)})

    event = {
        "index": len(gamestate.book['events']), 
        "type": REVEAL,
        "board": board_client,
        "specials": print_specials,
        "padding_positions": gamestate.reel_positions,
        "gameType": gamestate.gametype,
        "anticipation": gamestate.anticipation,
    }

    gamestate.book["events"] += [deepcopy(event)]

def json_ready_sym(symbol:object, special_attributes:list=None):
    assert special_attributes is not None
    printSym = {'name': symbol.name}
    attrs = vars(symbol)
    for key,val in attrs.items():
        if key in special_attributes and symbol.get_attribute(key) != False:
            printSym[key] = val 
    return printSym

def reveal_event(gamestate):
    board_client = []
    special_attributes = list(gamestate.config.special_symbols.keys())
    for reel in range(len(gamestate.board)):
        board_client.append([])
        for row in range(len(gamestate.board[reel])):
            board_client[reel].append(json_ready_sym(gamestate.board[reel][row], special_attributes))

    if gamestate.config.include_padding:
        for reel in range(len(board_client)):
            board_client[reel] = [json_ready_sym(gamestate.top_symbols[reel],special_attributes)]+board_client[reel]
            board_client[reel].append(json_ready_sym(gamestate.bottom_symbols[reel], special_attributes))
    
    event = {
        "index": len(gamestate.book['events']), 
        "type": REVEAL,
        "board": board_client,
        "padding_positions": gamestate.reel_positions,
        "gameType": gamestate.gametype,
        "anticipation": gamestate.anticipation,
    }

    gamestate.book["events"] += [event]

def fs_trigger_event(gamestate, includePaddingIndex=True, basegame_trigger:bool=None, freeGameTrigger:bool=None):
    assert basegame_trigger != freeGameTrigger, "must set either basegame_trigger or freeSpinTrigger to = True"
    event = {}
    scatterPositions = gamestate.special_syms_on_board['scatter']
    if includePaddingIndex:
        for pos in scatterPositions:
            pos["row"] += 1

    if basegame_trigger:
        event = {
            "index": len(gamestate.book["events"]),
            "type": FREESPINTRIGGER,
            "totalFs": gamestate.totFs,
            "positions": scatterPositions
        }
    elif freeGameTrigger:
        event = {
            "index": len(gamestate.book["events"]),
            "type": FREESPINRETRIGGER,
            "totalFs": gamestate.totFs,
            "positions": scatterPositions
        }

    assert gamestate.totFs >0, "total freespins (gamestate.totFs) must be >0"
    gamestate.book["events"] += [deepcopy(event)]

def set_win_event(gamestate, winLevelKey: str = "standard"):
    if not(gamestate.wincap_triggered):
        event = {"index": len(gamestate.book['events']),
                "type": SET_WIN,
                "amount": int(min(round(gamestate.win_manager.spinWin*100,0), gamestate.config.wincap*100)),
                "win_level": gamestate.config.get_win_level(gamestate.win_manager.spinWin, winLevelKey)
        }
        gamestate.book["events"] += [event]

def set_total_event(gamestate):
    event = {"index": len(gamestate.book['events']),
             "type": SET_TOTAL_WIN,
             "amount" :int(round(min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)*100, 0))
    }
    gamestate.book["events"] += [event]

def set_tumble_event(gamestate):
    event = {"index": len(gamestate.book['events']),
             "type": SET_TUMBLE_WIN,
             "amount": int(round(min(gamestate.tumble_win, gamestate.config.wincap)*100))
             }
    gamestate.book["events"] += [event]

def wincap_event(gamestate):
    event = {
        "index": len(gamestate.book['events']), 
        "type": WINCAP,
        "amount": int(round(min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)*100, 0))
    }
    gamestate.book["events"] += [event]

def win_info_event(gamestate, includePaddingIndex=True):
    """
    includePaddingIndex: starts winning-symbol poasitions at row=1, to account for top/bottom symbol inclusion in board
    """
    win_data_copy = {}    
    win_data_copy["wins"] = deepcopy(gamestate.winData["wins"])
    for idx,w in enumerate(win_data_copy["wins"]):
        if includePaddingIndex:
            new_positions = []
            for p in w["positions"]:
                new_positions.append({"reel":p["reel"], "row": p["row"]+1})
        else:
            new_positions = w["positions"]

        win_data_copy["wins"][idx]["win"] = int(round(min(win_data_copy["wins"][idx]["win"], gamestate.config.wincap)*100,0))
        win_data_copy["wins"][idx]["positions"] = new_positions   
        win_data_copy["wins"][idx]["meta"] = win_data_copy["wins"][idx]["meta"]
        win_data_copy["wins"][idx]["meta"]["winWithoutMult"] = int(round(min(win_data_copy["wins"][idx]["meta"]["winWithoutMult"], gamestate.config.wincap)*100, 0))
        
    dict_data = {
        "index": len(gamestate.book['events']),
        "type": WIN_DATA,
        "totalWin": int(round(min(gamestate.winData['totalWin'], gamestate.config.wincap)*100, 0)),
        "wins": win_data_copy["wins"],
    }
    gamestate.book['events'] += [deepcopy(dict_data)]

def update_tunble_win_event(gamestate):
    event = {
        "index": len(gamestate.book['events']),
        "type": UPDATE_TUMBLE_WIN,
        "amount": int(round(min(gamestate.win_manager.spinWin, gamestate.config.wincap)*100, 0))
    }
    gamestate.book['events'] += [event]

def update_freepsin_event(gamestate):
    event = {
        "index": len(gamestate.book['events']), 
        "type": UPDATE_FS, 
        "amount": int(gamestate.fs),
        "total": int(gamestate.totFs)}
    gamestate.book["events"] += [event]

def freespin_end_event(gamestate):
    event = {"index": len(gamestate.book['events']), 
             "type": FREE_SPIN_END, 
             "amount": int(round(min(gamestate.freegame_wins, gamestate.config.wincap)*100, 0))
    }
    gamestate.book["events"] += [event]

def final_win_event(gamestate):
    event = {"index": len(gamestate.book['events']), 
             "type": FINAL_WIN,
             "amount": int(round(min(gamestate.final_win, gamestate.config.wincap)*100, 0))
    }
    gamestate.book["events"] += [event]

def update_global_mult_event(gamestate):
    event = {"index": 
             len(gamestate.book['events']), 
             "type": UPDATE_GLOBAL_MULT, 
             "globalMult": int(gamestate.global_multiplier)}
    
    gamestate.book["events"] += [event]

def tumeble_board_event(gamestate):
    special_attributes = list(gamestate.config.special_symbols.keys())
    if gamestate.config.include_padding:
        exploding = []
        for sym in gamestate.explodingSymbols:
            exploding.append({'reel':sym['reel'], "row": sym['row'] + 1})
    else:
        exploding = gamestate.explodingSymbols
    
    exploding = sorted(exploding, key=lambda x: x['reel'])

    new_symbols = [[] for _ in range(gamestate.config.num_reels)]
    for r in range(len(gamestate.new_symbols_from_tumble)):
        if len(gamestate.new_symbols_from_tumble[r]) > 0:
            new_symbols[r] = [json_ready_sym(s, special_attributes) for s in gamestate.new_symbols_from_tumble[r]]

    gamestate.book["events"] += deepcopy([{
        "index": len(gamestate.book['events']),
        "type": TUMBLE_BOARD,
        "newSymbols": new_symbols,
        "explodingSymbols": exploding
    }])