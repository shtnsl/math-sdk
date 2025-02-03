from collections import defaultdict
from abc import ABC, abstractmethod
class ClusterWins:

    def getNeighbours(self, reel, row, localChecked) -> list:
        neighbours = []
        if reel > 0:
            if (reel-1, row) not in localChecked:
                neighbours += [(reel-1, row)]
                localChecked += [(reel-1, row)]
        if reel < len(self.board)-1:
            if (reel+1, row) not in localChecked:
                neighbours += [(reel+1, row)]
                localChecked += [(reel+1, row)]
        if row > 0:
            if (reel, row-1) not in localChecked:
                neighbours += [(reel, row-1)]
                localChecked += [(reel, row-1)]
        if row < len(self.board[reel])-1:
            if (reel, row+1) not in localChecked:
                neighbours += [(reel, row+1)]
                localChecked += [(reel, row+1)]
        return neighbours

    def inCluster(self, reel: int, row: int, og_symbol: str, wild_key: str='wild') -> bool:
        if self.board[reel][row].check_attribute(wild_key) or og_symbol == self.board[reel][row].name:
            return True

    def checkAllNeighbours(self, alreadyChecked: list, localChecked: list, potentialCluster: list, reel, row, og_symbol: str, wild_key: str='wild'):
        neighbours = self.getNeighbours(reel, row, localChecked)
        for reel_, row_ in neighbours:
            if self.inCluster(reel_, row_, og_symbol, wild_key):
                potentialCluster += [(reel_, row_)]
                alreadyChecked += [(reel_, row_)]
                self.checkAllNeighbours(alreadyChecked, localChecked, potentialCluster, reel_, row_, og_symbol, wild_key)

    def getClusters(self, wild_key: str = "wild") -> dict:
        alreadyChecked = []
        clusters = defaultdict(list)
        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                if not(self.board[reel][row].special) and (reel, row) not in alreadyChecked:
                    potentialCluster = [(reel, row)]
                    alreadyChecked += [(reel, row)]
                    localChecked = [(reel, row)]
                    symbol = self.board[reel][row].name
                    self.checkAllNeighbours(alreadyChecked, localChecked, potentialCluster, reel, row, symbol, wild_key)
                    clusters[symbol].append(potentialCluster)

        return clusters
    
    def evaluateAllClusters(self, clusters:dict, multiplier_key:str = "multiplier", returnData: dict = {"totalWin": 0, "wins": []}) -> type:
        explodingSymbols = []
        totalWin = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                numSymsInCluster = len(cluster)
                if (numSymsInCluster, sym) in self.config.paytable:
                    clusterMult = 0
                    for positions in cluster:
                        if self.board[positions[0]][positions[1]].check_attribute(multiplier_key):
                            if int(self.board[positions[0]][positions[1]].get_attribute(multiplier_key)) > 0:
                                clusterMult += self.board[positions[0]][positions[1]].multiplier
                    clusterMult = max(clusterMult, 1)
                    symWin = self.config.paytable[(numSymsInCluster, sym)]
                    symWinMult = symWin*clusterMult*self.global_multiplier
                    totalWin += symWinMult
                    jsonPositions = [{"reel": p[0], "row": p[1]} for p in cluster]
                    returnData['wins'] += [{"symbol": sym, "clusterSize": numSymsInCluster, "win": symWinMult, "positions": jsonPositions, "meta": {"multiplier": clusterMult, 'winWithoutMult': symWin, "globalMultiplier": self.global_multiplier, "clusterMultiplier": clusterMult}}]

                    for positions in cluster:
                        self.board[positions[0]][positions[1]].explode = True
                        if {'reel':positions[0], 'row':positions[1]} not in explodingSymbols:
                            explodingSymbols.append({"reel": positions[0], "row": positions[1]})
        
        return returnData, explodingSymbols, totalWin


    def getClusterWinData(self, multiplier_key:str = 'multiplier', wild_key:str = 'wild') -> None:
        clusters = self.getClusters(wild_key)
        returnData = {
            "totalWin": 0,
            "wins": [],
        }
        returnData, explodingSymbols, totalWin = self.evaluateAllClusters(clusters, multiplier_key, returnData)

        returnData['totalWin'] += totalWin
        self.clusters = clusters
        self.win_manager.tumble_win = totalWin
        self.explodingSymbols = explodingSymbols

        return returnData
    
    def recordClusterWins(self) -> None:
        for win in self.winData['wins']:
            self.record({
                "clusterSize": win["clusterSize"],
                "symbol": win["symbol"],
                "totalMultiplier": win["meta"]["multiplier"],
                "gameType": self.gametype
            })


