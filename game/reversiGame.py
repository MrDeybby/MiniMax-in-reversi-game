from game.reversiBoard import ReversiBoard
from players import humanPlayer, randomPlayer
import os
from game.color import Color
import time
from game.metrics import Metrics
from game.menu import Menu
from players.badPlayer import BadPlayer
from players.greedy import GreedyPlayer
from players.humanPlayer import HumanPlayer
from players.randomPlayer import RandomPlayer
from players.minimax import MinimaxPlayer
from game.control import Control
from game.tokens import StackToken
from multiprocessing import Lock


class ReversiGame:

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.board = None
        self.current_turn = None

    def players(self, player1=None, player2=None):
        self.player1 = player1 if player1 else self.player1
        self.player2 = player2 if player2 else self.player2

    staticmethod

    def select_player(cls, player):
        options = ["Humano", "Minimax", "Greedy", "Aleatorio", "Peor Jugador", "Atras"]
        menu = Menu(options, "Reversi Game")

        choice = menu.select()
        players = {
            0: HumanPlayer(),
            1: MinimaxPlayer(max_time=1),
            2: GreedyPlayer(),
            3: RandomPlayer(),
            4: BadPlayer(max_time=1),
            5: player,
        }
        return players[choice]

    def app(self):
        """
        Presents a menu to the player to either play a game, select players or exit.
        :return: The `app` method is returning `None`.
        """
        if not self.player1:
            self.player1, self.player2 = HumanPlayer(), MinimaxPlayer(max_time=1)

        while True:
            options = ["Jugar", "Seleccionar Jugadores", "Salir"]
            menu = Menu(options, "Reversi Game")
            choice = menu.select()
            if options[choice] == "Salir":
                print("Saliendo del juego...")
                return
            elif options[choice] == "Seleccionar Jugadores":
                options = ["Jugador 1", "Jugador 2", "Atras"]
                menu = Menu(options, "Seleccionar Jugadores")
                choice = menu.select()

                if options[choice] == "Atras":
                    continue
                elif options[choice] == "Jugador 1":
                    self.player1 = self.select_player(self.player1)
                else:
                    self.player2 = self.select_player(self.player2)

                print("Presiona Enter para continuar")
                Control.select({"ENTER": None})
                continue

            self.player1.tokens = StackToken("B")
            self.player2.tokens = StackToken("R")
            board = ReversiBoard()
            self.play(board=board)
            print("Presiona Enter para salir")
            Control.select({"ENTER": None})

    def swap_turn(self):

        self.current_turn = (
            self.player1
            if self.current_turn.tokens == self.player2.tokens
            else self.player2
        )
        self.board.depth += 1

    def play(self, board: ReversiBoard):
        self.board = board
        self.current_turn = self.player1  # Active player reference
        os.system("cls")
        while not self.board.is_terminal():

            available_moves = self.board.posible_movements(
                self.current_turn.token_color
            )
            print(
                f"Turno de {self.current_turn.name} ({self.current_turn.token_color}) Profundidad: {self.board.depth}"
            )
            print(
                f"Puntajes:\n{Color.RED}Rojas{Color.RESET}: {self.board.points()['R']} - {Color.BLUE}Azules{Color.RESET}: {self.board.points()['B']}"
            )

            if self.current_turn.tokens.is_empty():
                print(f"{self.current_turn.name} no tiene fichas para jugar.")
                self.swap_turn()
                time.sleep(1)
                continue
            elif not available_moves:
                print(f"{self.current_turn.name} no tiene movimientos. Cede el turno.")
                self.swap_turn()
                time.sleep(1)
                continue

            print(self.board.show(self.current_turn))

            x, y = self.current_turn.play(self.board)
            if x == None:
                return
            self.board.insert_play(x, y, self.current_turn.tokens.pop())
            os.system("cls")
            # print(f"\n{self.current_turn.name} juega en ({x}, {y})")
            print(f"\nAI juega en ({x}, {y})")
            self.swap_turn()

        print(
            "Puntajes:\n",
            "Rojas:",
            self.board.points()["R"],
            "- Azules:",
            self.board.points()["B"],
        )
        print(self.board.show())
        winner = None
        if self.board.points()["B"] > self.board.points()["R"]:
            print("Ganador: Azul")
            winner = (
                self.player1.name
                if self.player1.token_color == "B"
                else self.player2.name
            )
        elif self.board.points()["R"] > self.board.points()["B"]:
            print("Ganador: Rojo")
            winner = (
                self.player1.name
                if self.player1.token_color == "R"
                else self.player2.name
            )
        else:
            print("Juego empate")

        for player, opponent in (
            (self.player1, self.player2),
            (self.player2, self.player1),
        ):
            try:
                Metrics.generate_report(
                    player,
                    opponent.name,
                    winner,
                    self.board.points()[player.token_color],
                    self.board.points()["R"] + self.board.points()["B"],
                )
                player.reset()
            except:
                pass

    def play_for_algorithms(self, board: ReversiBoard):
        self.board = board
        self.current_turn = self.player1
        while not self.board.is_terminal():

            available_moves = self.board.posible_movements(
                self.current_turn.token_color
            )

            if self.current_turn.tokens.is_empty() or not available_moves:
                self.swap_turn()
                continue

            x, y = self.current_turn.play(self.board)
            self.board.insert_play(x, y, self.current_turn.tokens.pop())
            self.swap_turn()

        winner = None

        if self.board.points()["B"] > self.board.points()["R"]:
            winner = self.player1 if self.player1.token_color == "B" else self.player2
        elif self.board.points()["R"] > self.board.points()["B"]:
            winner = self.player1 if self.player1.token_color == "R" else self.player2
        winner_name = winner.name if winner else None
        winner_points = self.board.points()[winner.token_color] if winner else None

        Metrics.generate_vs_report(
            self.player1.name,
            self.player2.name,
            winner_name,
            winner_points,
            self.board.points()["R"] + self.board.points()["B"],
            self.board.depth,
        )
        return winner_name, self.board.points()["R"] + self.board.points()["B"]


if __name__ == "__main__":
    board = ReversiBoard()
    game = ReversiGame()
    player1 = humanPlayer.HumanPlayer("Alice")
    player2 = randomPlayer.RandomPlayer("Bot")
    game.play(board)
    print(game)
