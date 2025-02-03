from src.calculations.symbol import Symbol
import json

def generate_configs(gamestate:object, jsonPadding:bool=True, assignProperties:bool=True):
    makeFrontEndConfig(gamestate=gamestate, jsonPadding=jsonPadding, assignProperties=assignProperties)


def passFeBetmode(betmode):
    modeInfo = {}
    modeInfo['cost'] = betmode.getCost()
    modeInfo['feature'] = betmode.getFeature()
    modeInfo['ante'] = betmode.getEnhancedMode()
    modeInfo['buyBonus'] = betmode.getBuyBonus()
    modeInfo['rtp'] = betmode.getRTP()
    modeInfo['max_win'] = betmode.getMaxWin()
    modeInfo['description'] = betmode.getDescription()

    return {betmode.getName(): modeInfo}


def makeFrontEndConfig(gamestate, jsonPadding=True, assignProperties=True, **kwargs):
    '''
    jsonPadding formats symbols the same as the board {'name': symbol} (default), alternatively an array of strings ['H1',...] is passed
    assignProperties will invode 
    '''
    if assignProperties: assert jsonPadding == True, "jsonPadding must be `True` to invoke symbol properties in padding"

    jsonInfo = {}
    jsonInfo["providerName"] = str(gamestate.config.provider_name)
    jsonInfo["gameName"] = str(gamestate.config.game_name)
    jsonInfo["gameID"] = gamestate.config.game_id
    jsonInfo["rtp"] = gamestate.config.rtp
    jsonInfo['numReels'] = gamestate.config.num_reels
    jsonInfo['numRows'] = gamestate.config.num_rows

    jsonInfo['betModes'] = {}
    for bet_mode in gamestate.config.bet_modes:
        bmInfo = passFeBetmode(bet_mode)
        modeName = next(iter(bmInfo))
        jsonInfo['betModes'][modeName] = bmInfo[modeName]

    #Optionally include any custom information
    for key,val in kwargs:
        jsonInfo[key] = val

    try:
        jsonInfo["paylines"] = gamestate.config.pay_lines
    except:
        pass

    symbols = {}
    for sym in gamestate.symbolStorage.symbols.values():
        symbols[sym.name] = {}
        special_properties = []
        for prop in gamestate.config.special_symbols:
            if sym.name in gamestate.config.special_symbols[prop]:
                special_properties.append(prop)
        
        if sym.paytable is not None:
            symbols[sym.name]['paytable'] = sym.paytable 
        
        if len(special_properties) >0:
            symbols[sym.name]['special_properties'] = special_properties

    jsonInfo["symbols"] = symbols
    reelStripDictionaryJSON = {}
    if jsonPadding:
        for idx,reels in gamestate.config.padding_reels.items():
            reelStripDictionaryJSON[idx] = [[] for _ in range(gamestate.config.num_reels)]
            for c in range(len(reels)):
                column = reels[c]
                for i in range(len(column)):
                    reelStripDictionaryJSON[idx][c].append({'name': column[i]})
                    if len(gamestate.symbolStorage.symbols[column[i]].special_functions) >0:
                        pass
                        # s = Symbol(gamestate.config, column[i])
                        # s.applySpecialFunction()
                        pass
        #TODO: implement special function 
        jsonInfo["paddingReels"] = reelStripDictionaryJSON
    elif not jsonPadding:
        jsonInfo["paddingReels"] = gamestate.config.paddingReels
        
    fe_json = open(str.join("/",[gamestate.config.configPath,"config_fe_"+str(gamestate.config.game_id)+".json"]), 'w')
    fe_json.write(json.dumps(jsonInfo, indent=4))
    fe_json.close()
