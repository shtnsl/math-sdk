from collections import defaultdict

class ClusterWins:

    def getNeighbours(self, reel, row, localChecked):
        neibours = []
        if reel > 0:
            if (reel-1, row) not in localChecked:
                neibours += [(reel-1, row)]
                localChecked += [(reel-1, row)]
        if reel < len(self.board)-1:
            if (reel+1, row) not in localChecked:
                neibours += [(reel+1, row)]
                localChecked += [(reel+1, row)]
        if row > 0:
            if (reel, row-1) not in localChecked:
                neibours += [(reel, row-1)]
                localChecked += [(reel, row-1)]
        if row < len(self.board[reel])-1:
            if (reel, row+1) not in localChecked:
                neibours += [(reel, row+1)]
                localChecked += [(reel, row+1)]
        return neibours

    def inCluster(self, reel, row, og_symbol):
        if self.board[reel][row].hasAttribute("wild") or og_symbol == self.board[reel][row].name:
            return True

    def checkAllNeighbours(self, alreadyChecked, localChecked, potentialCluster, reel, row, og_symbol):
        neibours = self.getNeighbours(reel, row, localChecked)
        for reel_, row_ in neibours:
            if self.inCluster(reel_, row_, og_symbol):
                potentialCluster += [(reel_, row_)]
                alreadyChecked += [(reel_, row_)]
                self.checkAllNeighbours(alreadyChecked, localChecked, potentialCluster, reel_, row_, og_symbol)

    def getClusters(self):
        alreadyChecked = []
        clusters = defaultdict(str)
        for reel in range(len(self.board)):
            for row in range(len(self.board[reel])):
                if not(self.board[reel][row].hasAttribute('special')) and (reel, row) not in alreadyChecked:
                    potentialCluster = [(reel, row)]
                    alreadyChecked += [(reel, row)]
                    localChecked = [(reel, row)]
                    symbol = self.board[reel][row].name
                    self.checkAllNeighbours(alreadyChecked, localChecked, potentialCluster, reel, row, symbol)
                    clusters[symbol].append(potentialCluster)

        return clusters
    
