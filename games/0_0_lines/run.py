
from gamestate import GameConfig, GameState
from src.write_data.write_data import createBooks

if __name__ == '__main__':
    
    numThreads = 10
    rustThreads = 20
    batchingSize = 5000
    compression = True
    profiling = False

    numSimArgs = {
        "base":int(1e4),
         }
    
    config = GameConfig()
    gameState = GameState(config)

    createBooks(gameState, config, numSimArgs, batchingSize, numThreads, compression, profiling)
