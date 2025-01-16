import time
import hashlib
import json
import ast
from multiprocessing import Process, Manager
import zstandard
import cProfile
from collections import defaultdict
from warnings import warn
import shutil
from typing import Dict

from src.calculations.statistics import *
from src.config.paths import *


def getSHA256(fileToHash):
    try:
        with open(fileToHash, 'rb') as f:
            sha256_file = hashlib.sha256()
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha256_file.update(data)
        sha256_hexRep = sha256_file.hexdigest()
    except:
        warn(f"{fileToHash} is empty.\nCould not create hash")
        sha256_hexRep = ""
    return sha256_hexRep

def makeForceJson(gameState):
    import os
    import json

    folder_path = gameState.config.forcePath
    force_file_path = str.join("/",[folder_path, "force.json"])
    
    if os.path.isfile(force_file_path) and os.path.getsize(force_file_path) > 0:
        try:
            with open(force_file_path, 'r', encoding='utf-8') as forcefile:
                forceData = json.load(forcefile)
        except json.JSONDecodeError:
            print("Error decoding JSON: The file may be corrupted or empty.")
            forceData = {} 
    else:
        forceData = {}
                    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.json') and filename.startswith('force_for_rob_'):
            with open(file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
                
                modename = filename[len('force_for_rob_'):-len('.json')]
                forceData[modename] = {}
                
                if isinstance(data, list):
                    for item in data:
                        for (key, value) in item['search'].items(): 
                            if key not in forceData[modename]:
                                forceData[modename][key] = []
                            if value not in forceData[modename][key]:
                                forceData[modename][key] += [value]
                else:
                    print("Expected a list, found:", type(data))
    
    with open(force_file_path, 'w', encoding='utf-8') as forcefile:
        json.dump(forceData, forcefile, indent=4)

def getForceResultOptions(forceResults):
    forceKeys = defaultdict(set)
    for force in forceResults.keys():
        for key,val in force:
            forceKeys[str(key)].add(val)
    return {key:list(val) for key,val in forceKeys.items()}

def makeLookUpTable(gameState, name):
    file = open(str.join("/",[gameState.config.tempPath, name]), 'w')
    sims = list(gameState.library.keys())
    sims.sort()
    for sim in sims:
        file.write(str(gameState.library[sim]["id"]) + ",1," + str(gameState.library[sim]["payoutMultiplier"]) + "\n")
    file.close()

def makeLookUpTableIdToCriteria(gameState, name):
    file = open(str.join("/",[gameState.config.tempPath, name]), 'w')
    sims = list(gameState.library.keys())
    sims.sort()
    for sim in sims:
        file.write(str(gameState.library[sim]["id"]) + "," + str(gameState.library[sim]["criteria"]) + "\n")
    file.close()

def makeLookUpTablePaySplit(gameState, name):
    file = open(str.join("/",[gameState.config.tempPath, name]), 'w')
    sims = list(gameState.library.keys())
    sims.sort()
    for sim in sims:
        file.write(str(gameState.library[sim]["id"]) + "," + str(gameState.baseGameWins) + "," + str(gameState.freeGameWins)+"\n")
    file.close()

def writeLibraryEvents(gameState, library, gameType):
    uniqueEvent = []
    eventItems = {}
    for event in library:
        for instance in event['events']:
            libEvent = instance["type"]
            if libEvent not in uniqueEvent:
                uniqueEvent.append(libEvent)
                itemKeys = instance.keys()
                dicDetails = {key: instance[key] for key in itemKeys if key != "index"}
                eventItems[libEvent] = dicDetails
    jsonObject = json.dumps(eventItems, indent=4)
    with open(str.join("/",[gameState.config.configPath,"event_config_"+gameType+".json"]), "w") as f:
        f.write(jsonObject)

def outputLookUpTablesAndForceFiles(threads, batchingSize, gameId, betMode, gameState, numSims=1000000, compress=True):
    print("Saving books for", gameId, "in", betMode)
    numRepeats = max(int(round(numSims/threads/batchingSize, 0)), 1)
    file_list = []
    for repeatIndex in range(numRepeats):
        for thread in range(threads):
            file_list.append(str.join("/",[gameState.config.tempPath, "books_"+betMode+"_"+str(thread)+"_"+str(repeatIndex)+".json" + ".zst"*compress]))

    if compress:
        with open(str.join("/",[gameState.config.compressedBookPath, "books_"+betMode+".json.zst"]), 'wb') as outfile:
            for filename in file_list:
                with open(filename, 'rb') as infile:
                    outfile.write(infile.read())
    else:
        with open(str.join("/",[gameState.config.bookPath,"books_"+betMode+".json"]), 'w') as outfile:
            for filename in file_list:
                with open(filename, 'r') as infile:
                    outfile.write(infile.read())

    print("Saving force files for", gameId, "in", betMode)
    forceResultsDictionary = {}
    file_list = []
    for repeatIndex in range(numRepeats):
        for thread in range(threads):
            file_list.append(str.join("/",[gameState.config.tempPath, "force_"+betMode+"_"+str(thread)+"_"+str(repeatIndex)+".json"]))
            
    for filename in file_list:
        forceChunk = ast.literal_eval(json.load(open(filename, 'r')))
        for key in forceChunk:
            if forceResultsDictionary.get(key) != None:
                forceResultsDictionary[key]["timesTriggered"] += forceChunk[key]["timesTriggered"]
                forceResultsDictionary[key]["bookIds"] += forceChunk[key]["bookIds"]
            else:
                forceResultsDictionary[key] = forceChunk[key]
    
    forceResultsDictionaryJustForRob = []
    for forceCombination in forceResultsDictionary:
        searchDict = {}
        for key in forceCombination:
            searchDict[key[0]] = key[1]
        forceDict = {
            "search": searchDict,
            "timesTriggered": forceResultsDictionary[forceCombination]["timesTriggered"],
            "bookIds": forceResultsDictionary[forceCombination]["bookIds"]
        }
        forceResultsDictionaryJustForRob.append(forceDict)
    json_object_for_rob = json.dumps(forceResultsDictionaryJustForRob, indent=4)
    file = open(str.join("/",[gameState.config.forcePath,"force_for_rob_"+betMode+".json"]), 'w')
    file.write(json_object_for_rob)
    file.close()
    
    forceResultKeys = getForceResultOptions(forceResultsDictionary)
    json_file_path = str.join("/",[gameState.config.forcePath, "force.json"])
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except:
        data = {}
    data[gameState.getCurrentBetMode().getName()] = forceResultKeys
    json_object = json.dumps(data, indent=4)
    file = open(str.join("/",[gameState.config.forcePath, "force.json"]), 'w')
    file.write(json_object)
    file.close()
    weights_plus_wins_file_list = []
    id_to_criteria_file_list = []
    segmented_lut_file_list = []
    print("Saving LUTs for", gameId, "in", betMode)
    for repeatIndex in range(numRepeats):
        for thread in range(threads):
            weights_plus_wins_file_list += [str.join("/",[gameState.config.tempPath,"lookUpTable_"+betMode+"_"+str(thread)+"_"+str(repeatIndex)])]
            id_to_criteria_file_list += [str.join("/",[gameState.config.tempPath,"lookUpTableIdToCriteria_"+betMode+"_"+str(thread)+"_"+str(repeatIndex)])]
            segmented_lut_file_list += [str.join("/",[gameState.config.tempPath,"lookUpTableSegmented_"+betMode+"_"+str(thread)+"_"+str(repeatIndex)])]
    with open(str.join("/",[gameState.config.lookUpPath,"lookUpTable_"+betMode+".csv"]), 'w') as outfile:
        for filename in weights_plus_wins_file_list:
            with open(filename, 'r') as infile:
                outfile.write(infile.read())
    with open(str.join("/",[gameState.config.lookUpPath,"lookUpTableSegmented_"+betMode+".csv"]), 'w') as outfile:
        for filename in segmented_lut_file_list:
            with open(filename, 'r') as infile:
                outfile.write(infile.read())
    with open(str.join("/",[gameState.config.lookUpPath,"lookUpTableIdToCriteria_"+betMode+".csv"]), 'w') as outfile:
        for filename in id_to_criteria_file_list:
            with open(filename, 'r') as infile:
                outfile.write(infile.read())


def writeJsonFile(gameState, library, name, firstFileWrite, lastFileWrite, compress):
   # Convert the list of dictionaries to a JSON-encoded string and compress it in chunks
    chunk = json.dumps(library)
    if not (firstFileWrite):
        chunk = chunk[1:]
    if not (lastFileWrite):
        chunk = chunk[:-1] + ","
    if compress:
        file = open(str.join("/",[gameState.config.libraryPath,name+'.zst']), 'wb')
        compressed_chunk = zstandard.compress(chunk.encode('utf-8'))
        file.write(compressed_chunk)
    else:
        file = open(str.join("/",[gameState.config.libraryPath,name]), 'w')
        file.write(chunk)
    file.close()

def printRecordedWins(gameState, name=""):
    json_object = json.dumps(str(gameState.recordedEvents), indent=4)
    file = open(str.join("/",[gameState.config.tempPath,"force_"+name+".json"]), 'w')
    file.write(json_object)
    file.close()

def createBooks(gameState, config, numSimArgs, batchSize, threads, compress, profiling):
    for ns in numSimArgs.values():
        if all([ns > 0, ns > batchSize*batchSize]):
            assert ns%(threads*batchSize) == 0, "mode-sims/(batch * threads) must be divisible with no remainder"
        
    if not compress and sum(numSimArgs.values())>1e4:
        warn("Generating large number of uncompressed books!")
    
    if profiling and threads > 1:
        raise RuntimeError("Multithread profiling not supported, threads must = 1 with profiling enabled")
    
    startTime = time.time()
    print("\nCreating books...")
    for betModeName in numSimArgs:
        if numSimArgs[betModeName] > 0:
            gameState.betMode = betModeName
            runMultiProcessSims(threads, batchSize, config.gameId, betModeName, gameState, numSims=numSimArgs[betModeName], compress=compress, writeEventList=config.writeEventList, profiling=profiling)
            outputLookUpTablesAndForceFiles(threads, batchSize, config.gameId, betModeName, gameState, numSims=numSimArgs[betModeName], compress=compress)#, writeEventList=config.writeEventList)
    shutil.rmtree(config.tempPath)
    print("\nFinished creating books in", time.time() - startTime, "seconds.\n")

def getSimNumberSplits(gameState: object, numSims: int, betModeName: str) -> Dict[str, int]:
    betModeDistributions = gameState.getBetMode(betModeName).getDistributions()
    numSimsPerCriteria = {
        d._criteria: max(int(numSims * d._quota), 1) for d in betModeDistributions
    }
    totalSims = sum(numSimsPerCriteria.values())
    reduceSims = totalSims > numSims
    listedCriteria = [d._criteria for d in betModeDistributions]
    criteriaWeights = [d._quota for d in betModeDistributions]
    random.seed(0)
    while sum(numSimsPerCriteria.values()) != numSims:
        c = random.choices(listedCriteria, criteriaWeights)[0]
        if reduceSims and numSimsPerCriteria[c] > 1:
            numSimsPerCriteria[c] -= 1
        elif not reduceSims:
            numSimsPerCriteria[c] += 1

    return numSimsPerCriteria

def assignSimsToCriteria(numSimsPerCriteria: Dict[str, int], sims: int) -> Dict[int, str]:
    simAllocation = [
        criteria for criteria, count in numSimsPerCriteria.items() for _ in range(count)
    ]
    random.shuffle(simAllocation)
    return {i: simAllocation[i] for i in range(min(sims, len(simAllocation)))}


def runMultiProcessSims(threads, batchingSize, gameId, betMode, gameState, numSims=1000000, compress=True, writeEventList=False, profiling=False):
    print("\nCreating books for", gameId, "in", betMode)
    numRepeats = max(int(round(numSims/threads/batchingSize, 0)), 1)
    simsPerThread = int(numSims/threads/numRepeats)
    numSimsPerCriteria = getSimNumberSplits(gameState, numSims, betMode)
    simCriteriaAllocation = assignSimsToCriteria(numSimsPerCriteria, numSims)
    for repeat in range(numRepeats):
        print("Batch", repeat+1, "of", numRepeats)
        processes = []
        manager = Manager()
        allBetModesConfigs = manager.list()
        if profiling:
            cProfile.runctx('gameState.runSims(allBetModesConfigs, betMode, simCriteriaAllocation, threads, numRepeats, simsPerThread, 0, repeat, compress, writeEventList)', globals(), locals())
        elif threads == 1:
            gameState.runSims(allBetModesConfigs, betMode, simCriteriaAllocation, threads, numRepeats, simsPerThread, 0, repeat, compress, writeEventList)
        else:
            for thread in range(threads):
                process = Process(target=gameState.runSims, args=(allBetModesConfigs, betMode, simCriteriaAllocation, threads, numRepeats, simsPerThread, thread, repeat, compress, writeEventList))
                print("Started thread", thread)
                process.start()
                processes += [process]
            print('All threads are online.')
            for process in processes:
                process.join()
            print("Finished joining threads.")
            gameState.combine(allBetModesConfigs, betMode)
            gameState.getBetMode(betMode).lockForceKeys()