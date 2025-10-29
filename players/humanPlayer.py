
from players.player import Player
import re


class HumanPlayer(Player):
    """
    A player that queries a human user via the console for moves.

    Attributes
    
    TYPE_ : str
        Static identifier for this player type ("human").
    """
    
    TYPE_ = "human"
    
    def __init__(self, name="human"):
        """
        Initialize the human player with a display name.

        Parameters
        
        name : str, optional
            Player name, by default "human".
        """
        super().__init__(name)
             
    def play(self, board):
        """
        Prompt the user for a legal move and return it.

        The method displays the list of legal moves for the player's color,
        asks the user to input a coordinate in the form of two digits (xy),
        validates the move, and returns it. The special input "salir"
        returns `(None, None)` to signal exit/pass.

        Parameters
        
        board : ReversiBoard
            Current game board. Must implement `posible_movements(color)`.

        Returns
        
        tuple[int, int] | tuple[None, None]
            A legal coordinate `(x, y)`, or `(None, None)` if the user enters "salir".
        """
        # Show all legal moves for the current player color
        print("Movimientos posibles:", board.posible_movements(self.tokens.color))
        print("Que movimiento desea hacer?")

        # Read raw input (kept in Spanish per original UI)
        position = input("Ingrese la coordenada (x,y) [salir] para salir: ").strip().lower()
        
        # Exit/pass if the user types "salir"
        if position == "salir":
            return None, None

        # Accept exactly two digits (e.g., "23") and interpret them as (x, y)
        if re.match(r'^\d{2}$', str(position)):
            x, y = divmod(int(position), 10)
        else:
            # Force an invalid pair to trigger the validation loop
            x, y = -1, -1
            
        # Keep prompting until the user enters a legal move or "salir"
        while (x, y) not in board.posible_movements(self.tokens.color):
            print("Movimiento invalido. Intente de nuevo.")
            position = input("Ingrese la coordenada (x,y) [salir] para salir: ").strip().lower()
        
            if position == "salir":
                return None, None
            if re.match(r'^\d{2}$', str(position)):
                x, y = divmod(int(position), 10)
            else:
                x, y = -1, -1
    
        # Return a validated legal move
        return x, y
        
    


if __name__ == "__main__":
    player = HumanPlayer("Alice")
    print(player.name)  # Output: Alice
    print(player.TYPE_)  # Output: human