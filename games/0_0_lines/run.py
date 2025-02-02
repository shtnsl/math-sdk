
from gamestate import GameConfig, GameState
from src.write_data.write_data import createBooks
from src.write_data.write_configs import generateConfigs

if __name__ == '__main__':
    
    numThreads = 1
    rustThreads = 20
    batchingSize = 50000
    compression = False
    profiling = True

    numSimArgs = {
        "base":int(50),
        "bonus": int(50)
         }
    
    config = GameConfig()
    gameState = GameState(config)

    createBooks(gameState, config, numSimArgs, batchingSize, numThreads, compression, profiling)
    generateConfigs(gameState)