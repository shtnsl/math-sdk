from gamestate import GameConfig, GameState
from write_data.write_data import createBooks
import sys
sys.path.append('./') #Ensure root directory is added to the Python path

if __name__ == '__main__':
    
    numThreads = 1
    rustThreads = 20
    batchingSize = 5000
    compression = True
    profiling = False

    numSimArgs = {
        "base":int(1e3),
         }
    
    config = GameConfig()
    gameState = GameState(config)

    createBooks(gameState, config, numSimArgs, batchingSize, numThreads, compression, profiling)
