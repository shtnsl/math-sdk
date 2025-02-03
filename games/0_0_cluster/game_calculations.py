import sys
sys.path.append('./')
from src.executables.executables import Executables

class GameCalculations(Executables):
    """
    This fuction will override the evaluateAllClusters() function in cluster.py
    This is to account for the grid multiplier in winning positions.
    """
    def evaluateAllClusters(self, clusters:dict, multiplier_key:str = "multiplier", returnData: dict = {"totalWin": 0, "wins": []}) -> type:
        explodingSymbols = []
        totalWin = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                numSymsInCluster = len(cluster)
                if (numSymsInCluster, sym) in self.config.paytable:
                    clusterMult = 0
                    for positions in cluster:
                        if self.position_multipliers[positions[0]][positions[1]] > 1:
                            clusterMult += self.position_multipliers[positions[0]][positions[1]]

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