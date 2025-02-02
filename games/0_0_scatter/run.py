from gamestate import GameConfig, GameState
from src.write_data.write_data import createBooks
from src.write_data.write_configs import generateConfigs
from src.wins.win_manager import WinManager

if __name__ == '__main__':
    
    numThreads = 1
    rustThreads = 20
    batchingSize = 5000
    compression = True
    profiling = False

    numSimArgs = {
        "base":int(1e2),
        "bonus":int(1e2), 
        }
    
    config = GameConfig()
    winManager = WinManager(config.baseGameType, config.freeGameType)
    gameState = GameState(config)

    createBooks(gameState, config, numSimArgs, batchingSize, numThreads, compression, profiling)
    # generateConfigs(gameState)