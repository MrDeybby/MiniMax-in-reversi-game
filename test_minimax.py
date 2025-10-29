from game.reversiGame import ReversiGame
from game.reversiBoard import ReversiBoard
from players.minimax import MinimaxPlayer
from players.badPlayer import BadPlayer
from players.greedy import GreedyPlayer
from game.tokens import StackToken
from players.randomPlayer import RandomPlayer
from concurrent.futures import ProcessPoolExecutor, as_completed
import random
from players.humanPlayer import HumanPlayer


def play_match(player, oponent):
    # Saltar si son el mismo jugador
    if player.name == oponent.name:
        return None

    game = ReversiGame()
    board = ReversiBoard()

    if random.random() > 0.5:
        game.players(player1=player, player2=oponent)
    else:
        game.players(player1=oponent, player2=player)

    player.tokens = StackToken("B")
    oponent.tokens = StackToken("R")

    result = game.play(board)
    return (player.name, oponent.name, result)


if __name__ == "__main__":
    minimax = MinimaxPlayer(
        name="minimax_base",
        max_time=1,
    )

    weights_1 = MinimaxPlayer(
        name="weights_1",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.6785,
                "mob": 0.5875,
                "stable": 0.5912,
                "parity": 0.5108,
                "pos": 0.6347,
            },
            "medio": {
                "corner": 0.3812,
                "mob": 0.5799,
                "stable": 0.3923,
                "parity": 0.4637,
                "pos": 0.5751,
            },
            "final": {
                "corner": 0.5735,
                "mob": 0.4327,
                "stable": 0.7425,
                "parity": 0.7244,
                "pos": 0.5869,
            },
        },
    )

    weights_2 = MinimaxPlayer(
        name="weights_2",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.3226,
                "mob": 0.661,
                "stable": 0.4443,
                "parity": 0.2362,
                "pos": 0.5166,
            },
            "medio": {
                "corner": 0.6096,
                "mob": 0.4591,
                "stable": 0.4478,
                "parity": 0.6536,
                "pos": 0.5919,
            },
            "final": {
                "corner": 0.398,
                "mob": 0.689,
                "stable": 0.1431,
                "parity": 0.6418,
                "pos": 0.3218,
            },
        },
    )

    heuristic_1 = MinimaxPlayer(
        name="heuristic_1",
        max_time=1,
        custom_weights={
            "apertura": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
            "medio": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
            "final": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
        },
    )

    heuristic_2 = MinimaxPlayer(
        name="heuristic_2",
        max_time=1,
        custom_weights={
            "apertura": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
            "medio": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
            "final": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
        },
    )

    heuristic_3 = MinimaxPlayer(
        name="heuristic_3",
        max_time=1,
        custom_weights={
            "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
            "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
            "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
        },
    )

    heuristic_4 = MinimaxPlayer(
        name="heuristic_4",
        max_time=1,
        custom_weights={
            "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
            "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
            "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
        },
    )

    heuristic_5 = MinimaxPlayer(
        name="heuristic_5",
        max_time=1,
        custom_weights={
            "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
            "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
            "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
        },
    )

    time_3 = MinimaxPlayer(
        name="time_3",
        max_time=3,
    )

    time_10 = MinimaxPlayer(
        name="time_10",
        max_time=10,
    )

    greedy = GreedyPlayer(name="greedy")

    bad = BadPlayer(name="bad_player", max_time=1)

    weights_3 = MinimaxPlayer(
        name="weights_3",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.3599,
                "mob": 0.5888,
                "stable": 0.5566,
                "parity": 0.805,
                "pos": 0.4153,
            },
            "medio": {
                "corner": 0.6388,
                "mob": 0.7627,
                "stable": 0.6781,
                "parity": 0.6049,
                "pos": 0.3167,
            },
            "final": {
                "corner": 0.1929,
                "mob": 0.7459,
                "stable": 0.4183,
                "parity": 0.5857,
                "pos": 0.667,
            },
        },
    )

    weights_4 = MinimaxPlayer(
        name="weights_4",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.1141,
                "mob": 0.6328,
                "stable": 0.3379,
                "parity": 0.9211,
                "pos": 0.102,
            },
            "medio": {
                "corner": 0.8077,
                "mob": 0.5559,
                "stable": 0.6918342811648904,
                "parity": 0.4097,
                "pos": 0.3183,
            },
            "final": {
                "corner": 0.1662,
                "mob": 0.831,
                "stable": 0.4163,
                "parity": 0.5333,
                "pos": 0.6764,
            },
        },
    )

    weights_5 = MinimaxPlayer(
        name="weights_5",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.4033,
                "mob": 0.4844,
                "stable": 0.4534,
                "parity": 0.7111,
                "pos": 0.3628,
            },
            "medio": {
                "corner": 0.4561,
                "mob": 0.7731,
                "stable": 0.8084,
                "parity": 0.8716,
                "pos": 0.2125,
            },
            "final": {
                "corner": 0.2062,
                "mob": 0.6556,
                "stable": 0.236,
                "parity": 0.5923,
                "pos": 0.7982,
            },
        },
    )

    weights_6 = MinimaxPlayer(
        name="weights_6",
        max_time=1,
        custom_weights={
            "apertura": {
                "corner": 0.0806,
                "mob": 0.3481,
                "stable": 0.6498,
                "parity": 0.9519,
                "pos": 0.0583,
            },
            "medio": {
                "corner": 0.6825,
                "mob": 0.9393,
                "stable": 0.8581,
                "parity": 0.8179,
                "pos": 0.2365,
            },
            "final": {
                "corner": 0.0209,
                "mob": 0.9103,
                "stable": 0.3316,
                "parity": 0.457,
                "pos": 0.9795,
            },
        },
    )

    random_player = RandomPlayer()
    
    matches = []
    all_players = [weights_1,
        weights_2,
        weights_3,
        weights_4,
        weights_5,
        weights_6,
        heuristic_1,
        heuristic_2,
        heuristic_3,
        heuristic_4,
        heuristic_5,
        time_3,
        time_10,
        
    ]
    oponents = [
        minimax,
        greedy,
        bad,
        random_player,
    ]

    all_oponents = all_players + oponents
    for i in range(len(all_players)):
        for j in range(i + 1, len(all_oponents)):
            matches.append((all_players[i], all_oponents[j]))
            # print(all_players[i].name, "-", all_oponents[j].name)

    results = []

    # Ejecutar en paralelo
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(play_match, player, oponent) for player, oponent in matches
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"{result[0]} vs {result[1]} => {result[2]}")
                results.append(result)

    print("\n--- Todas las partidas completadas ---")

    # all_oponents = all_players + oponents
    # human_player = HumanPlayer(name="Deybby")
    # random.shuffle(all_players)

    # for ai in all_players:
    #     play_match(human_player, ai)
