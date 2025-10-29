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
import ast


class ReversiGame:
    """A class managing a Reversi/Othello game session.

    This class handles:
    - Player management (human and AI players)
    - Game loop and turn control
    - Board state and move validation
    - Game UI and player interaction
    - Score tracking and winner determination

    The game supports multiple player types including:
    - Human players
    - Minimax AI with custom heuristics
    - Greedy AI
    - Random AI
    - Bad player AI (for testing)
    """

    def __init__(self):
        """Initialize a new game session with empty state."""
        self.player1 = None  # First player (Blue tokens)
        self.player2 = None  # Second player (Red tokens)
        self.board = None  # Game board state
        self.current_turn = None  # Reference to active player

    def players(self, player1=None, player2=None):
        """Set or update the players for the game.

        Args:
            player1: First player (Blue), keeps current if None
            player2: Second player (Red), keeps current if None

        This method allows changing one or both players without
        creating a new game instance.
        """
        self.player1 = player1 if player1 else self.player1
        self.player2 = player2 if player2 else self.player2

    @staticmethod
    def select_player(cls, player):
        """Interactive menu for selecting and configuring a player.

        Provides options to create:
        - Human player with custom name
        - Minimax AI with optional custom heuristics
        - Greedy AI for aggressive play
        - Random AI for unpredictable moves
        - Bad player AI for testing

        Args:
            cls: Class reference (unused, for staticmethod)
            player: Current player instance to keep as fallback option

        Returns:
            Player: New configured player instance
        """
        # Define available player types
        options = ["Humano", "Minimax", "Greedy", "Aleatorio", "Peor Jugador", "Atras"]
        menu = Menu(options, "Reversi Game")

        choice = menu.select()
        # Map menu choices to player instances
        players = {
            1: MinimaxPlayer(),  # Smart AI using minimax algorithm
            2: GreedyPlayer(),  # AI that maximizes immediate gain
            3: RandomPlayer(),  # AI making random valid moves
            4: BadPlayer(max_time=1),  # AI making intentionally poor choices
            5: player,  # Keep current player as fallback
        }

        if choice == 1:
            options = ["Heuristica Personalizada", "Base"]
            menu = Menu(options, "Minimax")
            choice = menu.select()

            if choice == 0:
                Control.clean_input_keys()
                try:
                    heuristic_value = input(
                        "Inserte el diccionario con las heuristicas: "
                    )
                    heuristic = ast.literal_eval(heuristic_value)

                    name = input("Nombre del Minimax: ")
                    player = MinimaxPlayer(
                        name=name, max_time=1, custom_weights=heuristic
                    )
                    Control.clean_input_keys()
                    print("Heuristica cargada")

                    return player
                except:
                    print("El diccionario debe ser valido")

        elif choice == 0:
            Control.clean_input_keys()
            name = input("Nombre: ")
            return HumanPlayer(name=name)

        return players[choice]

    def app(self):
        """Main application loop with menu-driven interface.

        Provides the following options:
        1. Play Game: Start a new game with current players
        2. Select Players: Configure player 1 (Blue) and player 2 (Red)
        3. Exit: Terminate the application

        The menu keeps track of current player names and types.
        Default players are Human vs Minimax AI if not configured.
        """
        # Set default players if none configured
        if not self.player1:
            self.player1 = HumanPlayer()  # Blue player defaults to human
            self.player2 = MinimaxPlayer(max_time=1)  # Red player defaults to AI

        while True:
            print()
            # Main menu options
            options = ["Jugar", "Seleccionar Jugadores", "Salir"]
            # Display menu with current player information
            menu = Menu(
                options,
                f"Jugador 1: {self.player1.name}, Jugador 2: {self.player2.name} ===\n=== Reversi Game",
            )
            choice = menu.select()

            # Handle exit option
            if options[choice] == "Salir":
                Control.clean_input_keys()
                print("Saliendo del juego...")
                return
            elif options[choice] == "Seleccionar Jugadores":
                # Player selection submenu
                options = ["Jugador 1", "Jugador 2", "Atras"]
                menu = Menu(options, "Seleccionar Jugadores")
                choice = menu.select()

                # Handle player selection or return to main menu
                if options[choice] == "Atras":
                    continue
                elif options[choice] == "Jugador 1":
                    # Configure Blue player (Player 1)
                    self.player1 = self.select_player(self.player1)
                else:
                    # Configure Red player (Player 2)
                    self.player2 = self.select_player(self.player2)

                # Wait for user acknowledgment
                print("Presiona Enter para continuar")
                Control.select({"ENTER": None})
                continue

            # Initialize new game
            Control.clean_input_keys()

            # Set up player tokens
            self.player1.tokens = StackToken("B")  # Blue tokens for Player 1
            self.player2.tokens = StackToken("R")  # Red tokens for Player 2

            # Create fresh game board
            board = ReversiBoard()

            # Start the game
            self.play(board=board)

    def swap_turn(self):
        """Switch the active player and increment game depth.

        Alternates between player1 and player2 based on token color.
        Increments board depth to track game progression and for AI depth calculations.
        """
        # Switch to the other player based on current token color
        self.current_turn = (
            self.player1
            if self.current_turn.tokens == self.player2.tokens
            else self.player2
        )
        self.board.depth += 1  # Increment game tree depth

    def play(self, board: ReversiBoard):
        """Main game loop handling the flow of a complete game.

        Manages:
        - Turn alternation
        - Move validation
        - Board display
        - Score tracking
        - Game termination
        - Winner determination

        Args:
            board: Initial game board configuration
        """
        # Initialize game state
        self.board = board
        self.current_turn = self.player1  # Blue player starts
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

            # Display board with highlighted valid moves
            print(self.board.show(self.current_turn))

            # Get move from current player (human or AI)
            x, y = self.current_turn.play(self.board)
            if x == None:  # Player requested to exit
                return

            # Execute the move and update game state
            self.board.insert_play(x, y, self.current_turn.tokens.pop())
            os.system("cls")  # Clear screen for next turn
            print(f"\n{self.current_turn.name} juega en ({x}, {y})")
            self.swap_turn()

        # Game over - display final scores
        print(
            "Puntajes:\n",
            "Rojas:",
            self.board.points()["R"],
            "- Azules:",
            self.board.points()["B"],
        )
        print(self.board.show())

        # Determine winner based on final score
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
        print("Presiona ESC para salir")
        Control.select({"ESC": None})
        # Generate performance metrics for both players
        for player, opponent in (
            (self.player1, self.player2),
            (self.player2, self.player1),
        ):
            try:
                # Record game statistics for analysis
                Metrics.generate_report(
                    player,  # Current player
                    opponent.name,  # Opponent name
                    winner,  # Game winner
                    self.board.points()[player.token_color],  # Player's score
                    self.board.points()["R"] + self.board.points()["B"],  # Total tokens
                )
                # Reset player state for next game
                player.reset()
            except:
                # Skip metrics if there's an error (player is human or random)
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
