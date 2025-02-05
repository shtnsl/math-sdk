"""Main file for generating results for sample lines-pay game."""

from gamestate import GameConfig, GameState
from src.write_data.write_data import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    NUM_THREADS = 1
    RUST_THREADS = 20
    batching_size = 50000
    COMPRESSION = False
    profiling = False

    num_sim_args = {"base": int(1e2), "bonus": int(1e2)}

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
    generate_configs(gamestate)
