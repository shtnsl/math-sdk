from gamestate import GameConfig, GameState
from src.write_data.write_data import createBooks

if __name__ == "__main__":

    NUM_THREADS = 1
    RUST_THREADS = 20
    batching_size = 5000
    COMPRESSION = False
    profiling = False

    num_sim_args = {
        "base": int(1e2),
    }

    config = GameConfig()
    gamestate = GameState(config)

    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        NUM_THREADS,
        COMPRESSION,
        profiling,
    )
