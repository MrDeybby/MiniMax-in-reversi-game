from abc import ABC, abstractmethod

class Player(ABC):
    """Abstract base class for any Reversi/Othello player.

    Attributes
    
    TYPE_ : str | None
        Class-level identifier (to be overridden by subclasses).
    name : str
        Display name for the player instance.
    _token_color : any
        Cached color of the player's tokens; set when `tokens` is assigned.
    _tokens : any
        Token holder object assigned to this player; provides `.color`.
    """
    
    TYPE_ = None
    
    def __init__(self, name):
        """
        Iniialize the player with a display name.

        Parameters
        
        name : str
            The display name for this player (used in UI/logging).
        """
        self.name = name
        self._token_color = None
        self._tokens = None
        
    @abstractmethod
    def play(self):
        """
        Select and return a move for the current game state.

        Implementations must return a move in the format expected by the
        game engine (commonly a tuple `(x, y)`), or handle passes according
        to the engine's convention.

        Returns
        
        any
            The chosen move (type depends on the concrete implementation).
        """
        pass
    
    @property
    def token_color(self):
        """
        Return the color associated with this player's tokens.

        Returns
        
        any
            The token color (as provided by `tokens.color`), or `None` if
            tokens have not been assigned yet.
        """
        return self._token_color    
    
    @property
    def tokens(self):
        """
        Return the token holder object assigned to this player.

        Returns
        
        any
            The token container/stack object previously assigned, or `None`
            if no tokens have been set yet.
        """
        return self._tokens
    
    @tokens.setter
    def tokens(self, tokens):
        """
        Assign the token holder object and cache its color.

        Parameters
        
        tokens : any
            An object representing the player's tokens; must expose a
            `.color` attribute used to set `_token_color`.
        """
        self._tokens = tokens
        self._token_color = tokens.color
