from players.player import Player
import random

class RandomPlayer(Player):
    """
    A baseline player that picks a uniformly random legal move.

    Attributes
    
    TYPE_ : str
        Static identifier for this player type ("random").
    """

    TYPE_ = "random"
    
    def __init__(self, name="random"):
        """
        Initialize the random player with a display name.

        Parameters
        
        name : str, optional
            Player name, by default "random".
        """
        
        super().__init__(name)

    def reset(self):
        """
        Reset any internal state.

        This player has no persistent state or metrics to reset, so this
        method is a no-op (kept for API consistency with other players).
        """

        pass
             
    def play(self, board):
        """
        Select and return a random legal move for the current position.

        The method queries the board for all legal moves for this player's
        color using `board.posible_movements(self.tokens.color)`, prints them,
        and returns one move chosen uniformly at random.

        Parameters
        
        board : ReversiBoard
            Current board state (must implement `posible_movements(color)`).

        Returns
        
        tuple[int, int]
            A coordinate pair `(x, y)` representing the chosen move.

        """

        # Print all legal moves (message kept in Spanish for UI consistency)
        print("Movimientos posibles:", board.posible_movements(self.tokens.color))

        # Choose one legal move uniformly at random and return it
        position = random.choice(board.posible_movements(self.tokens.color))
        return position
    
    
if __name__ == "__main__":
    player = RandomPlayer("Alice")
    print(player.name)  # Output: Alice
    print(player.TYPE_)  # Output: human