from src.calculations.symbol import Symbol
import json

def generateConfigs(gameState:object, jsonPadding:bool=True, assignProperties:bool=True):
    makeFrontEndConfig(gameState=gameState, jsonPadding=jsonPadding, assignProperties=assignProperties)


def passFeBetmode(betmode):
    modeInfo = {}
    modeInfo['cost'] = betmode.getCost()
    modeInfo['feature'] = betmode.getFeature()
    modeInfo['ante'] = betmode.getEnhancedMode()
    modeInfo['buyBonus'] = betmode.getBuyBonus()
    modeInfo['rtp'] = betmode.getRTP()
    modeInfo['maxWin'] = betmode.getMaxWin()
    modeInfo['description'] = betmode.getDescription()

    return {betmode.getName(): modeInfo}


def makeFrontEndConfig(gameState, jsonPadding=True, assignProperties=True, **kwargs):
    '''
    jsonPadding formats symbols the same as the board {'name': symbol} (default), alternatively an array of strings ['H1',...] is passed
    assignProperties will invode 
    '''
    if assignProperties: assert jsonPadding == True, "jsonPadding must be `True` to invoke symbol properties in padding"

    jsonInfo = {}
    jsonInfo["providerName"] = str(gameState.config.providerName)
    jsonInfo["gameName"] = str(gameState.config.gameName)
    jsonInfo["gameID"] = gameState.config.gameId
    jsonInfo["rtp"] = gameState.config.rtp
    jsonInfo['numReels'] = gameState.config.numReels
    jsonInfo['numRows'] = gameState.config.numRows

    jsonInfo['betModes'] = {}
    for betMode in gameState.config.betModes:
        bmInfo = passFeBetmode(betMode)
        modeName = next(iter(bmInfo))
        jsonInfo['betModes'][modeName] = bmInfo[modeName]

    #Optionally include any custom information
    for key,val in kwargs:
        jsonInfo[key] = val

    try:
        jsonInfo["paylines"] = gameState.config.payLines
    except:
        pass

    symbols = {}
    for sym in gameState.symbolStorage.symbols.values():
        symbols[sym.name] = {}
        specialProperties = []
        for prop in gameState.config.specialSymbols:
            if sym.name in gameState.config.specialSymbols[prop]:
                specialProperties.append(prop)
        
        if sym.payTable is not None:
            symbols[sym.name]['payTable'] = sym.payTable 
        
        if len(specialProperties) >0:
            symbols[sym.name]['specialProperties'] = specialProperties

    jsonInfo["symbols"] = symbols
    reelStripDictionaryJSON = {}
    if jsonPadding:
        for idx,reels in gameState.config.paddingReels.items():
            reelStripDictionaryJSON[idx] = [[] for _ in range(gameState.config.numReels)]
            for c in range(len(reels)):
                column = reels[c]
                for i in range(len(column)):
                    reelStripDictionaryJSON[idx][c].append({'name': column[i]})
                    if len(gameState.symbolStorage.symbols[column[i]].specialFunctions) >0:
                        pass
                        # s = Symbol(gameState.config, column[i])
                        # s.applySpecialFunction()
                        pass
        #TODO: implement special function 
        jsonInfo["paddingReels"] = reelStripDictionaryJSON
    elif not jsonPadding:
        jsonInfo["paddingReels"] = gameState.config.paddingReels
        
    fe_json = open(str.join("/",[gameState.config.configPath,"config_fe_"+str(gameState.config.gameId)+".json"]), 'w')
    fe_json.write(json.dumps(jsonInfo, indent=4))
    fe_json.close()
