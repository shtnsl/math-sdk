from gamestate import GameConfig, GameState
from src.write_data.write_data import create_books
from src.write_data.write_configs import generate_configs
from src.wins.win_manager import WinManager

if __name__ == '__main__':
    
    NUM_THREADS = 10
    RUST_THREADS = 20
    BATCHING_SIZE = 5000
    COMPRESSION = True
    PROFILING = False

    num_sim_args = {
        "base":int(1e3),
        "bonus":int(1e3), 
        }
    
    config = GameConfig()
    winManager = WinManager(config.base_game_type, config.free_game_type)
    gamestate = GameState(config)

    create_books(gamestate, config, num_sim_args, BATCHING_SIZE, NUM_THREADS, COMPRESSION, PROFILING)
    generate_configs(gamestate)