
from gamestate import GameConfig, GameState
from src.write_data.write_data import create_books

if __name__ == '__main__':
    
    NUM_THREADS = 1
    RUST_THREADS = 20
    BATCHING_SIZE = 5000
    COMPRESSION = False
    PROFILING = False

    num_sim_args = {
        "base":int(1e2),
         }
    
    config = GameConfig()
    gamestate = GameState(config)

    create_books(gamestate, config, num_sim_args, BATCHING_SIZE, NUM_THREADS, COMPRESSION, PROFILING)
