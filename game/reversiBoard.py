from abc import ABC, abstractmethod
from game.tokens import Token
from copy import deepcopy
import math
from game.color import Color

# Position evaluation matrix for the Reversi board
# Higher values (100) = strategic positions (corners)
# Negative values (-50) = dangerous positions (near corners)
# Small values (-1, -2) = neutral positions
# This matrix reflects classic Reversi strategy where:
# - Corners are most valuable (100)
# - Positions next to corners are dangerous (-20, -50)
# - Edge positions are moderately good (5-10)
# - Center positions are neutral (-1)
POSITION_WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],  # Corners are best (100)
    [-20, -50, -2, -2, -2, -2, -50, -20],  # Next to corners dangerous
    [10, -2, -1, -1, -1, -1, -2, 10],  # Edges are good
    [5, -2, -1, -1, -1, -1, -2, 5],  # Center is neutral
    [5, -2, -1, -1, -1, -1, -2, 5],
    [10, -2, -1, -1, -1, -1, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100],
]


def opponent(color: str) -> str:
    """Returns the opposite color."""
    return "R" if color == "B" else "B"


class Board(ABC):
    _state = None
    _depth = 0

    def __init__(self, state, depth=0, utility=0):
        self._state = state
        self._depth = depth

    @abstractmethod
    def childrens(self):
        pass


class ReversiBoard(Board):
    """A class representing a Reversi/Othello game board.

    This class implements the game logic for Reversi, including move validation,
    token placement, token flipping, and board state evaluation using various heuristics.

    Attributes:
        BOARD_SIZE (int): Size of the board (8x8 for standard Reversi)
        players_tokens (dict): Number of tokens remaining for each player ('B'lack and 'R'ed)
        HEURISTICS (dict): Available evaluation heuristics for AI decision making
    """

    BOARD_SIZE = 8

    def __init__(self, state=None, depth=0, utility=0):
        """Initialize a new Reversi board.

        Args:
            state (List[List[Token]], optional): Initial board state. If None, creates standard starting position.
            depth (int, optional): Current depth in game tree. Defaults to 0.
            utility (int, optional): Utility value for minimax. Defaults to 0.
        """
        super().__init__(state, depth, utility)
        self.players_tokens = {"B": 30, "R": 30}
        self.HEURISTICS = {
            "corner": self._corner_occupancy,  # Corner control evaluation
            "mob": self._mobility,  # Movement options evaluation
            "stable": self._stable_discs,  # Stable tokens evaluation
            "parity": self._coin_parity,  # Token count difference
            "pos": self._positional_weights,  # Position-based evaluation
        }

        if not state:
            self.create_board()

    def create_board(self):
        """Initialize an empty board with the standard Reversi starting position.

        Creates an 8x8 board with the four center squares occupied by alternating
        black and red tokens in the traditional cross pattern.
        """
        self._state = [
            [None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)
        ]
        self._state[3][3] = Token("B")
        self._state[3][4] = Token("R")
        self._state[4][3] = Token("R")
        self._state[4][4] = Token("B")

    def points(self) -> dict[str, int]:
        """Calculate the current score for both players.

        Counts the number of tokens of each color currently on the board.

        Returns:
            dict: A dictionary with keys 'B' and 'R' containing the number of
                 tokens for each player (Black and Red respectively).
        """
        blue_points = 0
        red_points = 0
        for row in self._state:
            for token in row:
                if token is None:
                    continue

                if token.color == "B":
                    blue_points += 1
                elif token.color == "R":
                    red_points += 1

        return {"B": blue_points, "R": red_points}

    def is_terminal(self) -> bool:
        """Check if the game has reached a terminal (end) state.

        The game is considered finished when:
        1. Neither player can make a valid move
        2. One player has no tokens left and the other has no valid moves
        3. The board is completely full

        Returns:
            bool: True if the game is finished, False otherwise
        """
        # The game ends when neither player can make a valid move
        if not self.posible_movements("B") and not self.posible_movements("R"):
            return True

        # Or when one player has no tokens and the other has no valid moves
        if (
            (self.players_tokens["B"] == 0 and not self.posible_movements("R"))
            or self.players_tokens["R"] == 0
            and not self.posible_movements("B")
        ):
            return True

        # Or when the board is full
        if all(
            self._state[y][x] is not None
            for y in range(self.BOARD_SIZE)
            for x in range(self.BOARD_SIZE)
        ):
            return True
        return False

    def childrens(self, player_color: str) -> list["ReversiBoard"]:
        """Generate all possible next board states for a given player.

        Creates a new board state for each valid move the player can make,
        useful for AI algorithms like Minimax that need to explore the game tree.

        Args:
            player_color (str): The color of the player making the move ('B' or 'R')

        Returns:
            list[ReversiBoard]: A list of new board states, one for each valid move
        """
        options_available = self.posible_movements(player_color)
        children = []

        for x, y in options_available:
            new_state = deepcopy(self._state)
            child = ReversiBoard(new_state, self.depth + 1)
            child.insert_play(x, y, Token(player_color))
            children.append(child)

        return children

    @property
    def state(self):
        """Get the current board state.

        Returns:
            List[List[Token]]: A 2D list representing the board, where None represents
            an empty cell and Token objects represent placed tokens.
        """
        return self._state

    @property
    def depth(self):
        """Get the current depth in the game tree.

        Returns:
            int: The depth of this board state in the game tree.
        """
        return self._depth

    @depth.setter
    def depth(self, new_depth: int):
        """Set the depth of this board state in the game tree.

        Args:
            new_depth (int): The new depth value to set
        """
        self._depth = new_depth

    def posible_movements(self, color: str) -> list[tuple[int, int]]:
        """Find all valid moves for a given player.

        A move is valid if it would flip at least one of the opponent's tokens.
        The method checks in all 8 directions from each empty cell to find valid moves.

        Args:
            color (str): The color of the player ('B' or 'R')

        Returns:
            list[tuple[int, int]]: A list of (x, y) coordinates representing valid moves
        """
        movements = []
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self._state[y][x] is None:
                    # Check all 8 directions
                    directions = [
                        (-1, -1),
                        (-1, 0),
                        (-1, 1),
                        (0, -1),
                        (0, 1),
                        (1, -1),
                        (1, 0),
                        (1, 1),
                    ]
                    for dy, dx in directions:
                        ny, nx = y + dy, x + dx
                        found_opponent = False
                        while 0 <= ny < self.BOARD_SIZE and 0 <= nx < self.BOARD_SIZE:
                            if self._state[ny][nx] is None:
                                break
                            elif self._state[ny][nx].color != color:
                                found_opponent = True
                            elif self._state[ny][nx].color == color:
                                if found_opponent:
                                    movements.append((x, y))
                                break
                            ny += dy
                            nx += dx
        return list(set(movements))

    def insert_play(self, x: int, y: int, token: Token):
        """Place a token on the board and flip opponent's tokens.

        Validates the move, places the token, and flips any opponent's tokens that
        are flanked by the new token. Also updates the token count for the player.

        Args:
            x (int): X-coordinate of the move (0-7)
            y (int): Y-coordinate of the move (0-7)
            token (Token): The token to place (must be valid color)

        Raises:
            ValueError: If the move is not valid for the given color
        """
        if (x, y) not in self.posible_movements(token.color):
            raise ValueError(f"Invalid move at ({x}, {y}) for color {token.color}.")
        self._state[y][x] = token
        self.players_tokens[token.color] -= 1

        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            opponents_found = []

            while 0 <= ny < self.BOARD_SIZE and 0 <= nx < self.BOARD_SIZE:
                if self._state[ny][nx] is None:
                    break
                elif self._state[ny][nx].color == token.color:
                    if opponents_found:
                        for ox, oy in opponents_found:
                            self._state[oy][ox].flip()
                    break

                else:
                    opponents_found.append((nx, ny))
                    ny += dy
                    nx += dx

    def show(self, player=None) -> str:
        """Display the board with colored tokens and available moves.

        Creates a string representation of the board with ASCII art and ANSI colors,
        optionally highlighting valid moves for a specific player.

        Args:
            player (Player, optional): If provided, highlights valid moves for this player

        Returns:
            str: A colored string representation of the board
        """
        avaible_cells = self.posible_movements(player.token_color) if player else []

        board_str = f"    " + "   ".join(str(i) for i in range(self.BOARD_SIZE)) + "\n"
        board_str += f"  {'-'* (self.BOARD_SIZE* 4)}-\n"
        for y in range(self.BOARD_SIZE):
            board_str += f"{y} "
            for x in range(self.BOARD_SIZE):
                if (x, y) in avaible_cells:
                    board_str += f"|{Color.BACKGROUND_GRAY}   {Color.RESET}"
                elif self._state[y][x] == None:
                    board_str += f"|   "
                elif self._state[y][x].color == "B":
                    board_str += f"| {Color.BLUE}O{Color.RESET} "
                else:
                    board_str += f"| {Color.RED}O{Color.RESET} "
            board_str += f"|\n"
            board_str += f"  {'-'* (self.BOARD_SIZE* 4)}-\n"

        return board_str

    def __str__(self) -> str:
        """Convert the board to a simple ASCII string representation.

        Creates a plain text representation of the board using ASCII characters,
        suitable for console output without colors.

        Returns:
            str: An ASCII art representation of the current board state
        """
        board_str = f"  {'-'* (self.BOARD_SIZE* 4)}-\n"
        for y in range(self.BOARD_SIZE):
            board_str += f"{y} "
            for x in range(self.BOARD_SIZE):
                board_str += (
                    f"| {self._state[y][x] if self._state[y][x] != None else ' '} "
                )
            board_str += "|\n"
            board_str += f"  {'-'* (self.BOARD_SIZE* 4)}-\n"
        board_str += f"    " + "   ".join(str(i) for i in range(self.BOARD_SIZE)) + "\n"

        return board_str

    def __repr__(self):
        return f"ReversiBoard(state={self._state}, depth={self.depth})"

    # --- OTRA PARTE DEL CÓDIGO DEL HECTOR MAGICO ---

    def _normalize(self, W: dict) -> dict:
        """Normalize weights to sum to 1.0 while preserving relative proportions."""
        total = sum(abs(v) for v in W.values())
        if total == 0:
            return {k: 0.0 for k in W}
        return {k: (v / total) for k, v in W.items()}

    def evaluate(
        self,
        color: str,
        enabled_heuristics: list[str] | set[str] | None = None,
        custom_weights: dict[str, float] | None = None,
    ) -> float:
        """Calculate board evaluation score using selected heuristics.

        Combines multiple evaluation heuristics with weights that change based on
        game phase (opening, midgame, endgame). Available heuristics:
        - corner: Control of corner positions
        - mob: Player mobility (number of possible moves)
        - stable: Number of stable discs that can't be flipped
        - parity: Raw disc count difference
        - pos: Position-based evaluation using POSITION_WEIGHTS

        Args:
            color: Player color to evaluate for ('B' or 'R')
            enabled_heuristics: Which heuristics to use, or None for all
            custom_weights: Override default phase-based weights
        """

        if self.is_terminal():
            pts = self.points()
            myc, opc = pts[color], pts[opponent(color)]
            if myc > opc:
                return math.inf
            if opc > myc:
                return -math.inf
            return 0.0

        # Determina heurísticas activas
        if enabled_heuristics is None:
            enabled = set(self.HEURISTICS.keys())
        else:
            enabled = {h for h in enabled_heuristics if h in self.HEURISTICS}
            if not enabled:
                return 0.0

        # Calcula valores h_* solo para las activas
        h_vals = {name: self.HEURISTICS[name](color) for name in enabled}

        if custom_weights is not None:

            # APERTURA, MEDIO, FINAL
            if (
                "apertura" in custom_weights
                and "medio" in custom_weights
                and "final" in custom_weights
            ):
                e = self._empty_count()

                if e >= 40:  # Apertura
                    W = custom_weights["apertura"]
                elif e >= 15:  # Medio
                    W = custom_weights["medio"]
                else:  # Final
                    W = custom_weights["final"]

                W = {k: v for k, v in W.items() if k in enabled}
                W = self._normalize(W)

            elif any(k in enabled for k in custom_weights):
                W = {k: v for k, v in custom_weights.items() if k in enabled}
                W = self._normalize(W)

            else:
                e = self._empty_count()
                W = self._phase_weights(e, enabled)

        else:
            e = self._empty_count()
            W = self._phase_weights(e, enabled)

        return sum(W[name] * h_vals[name] for name in enabled)

    def _empty_count(self) -> int:
        return sum(
            1
            for y in range(self.BOARD_SIZE)
            for x in range(self.BOARD_SIZE)
            if self.state[y][x] is None
        )

    def _coin_parity(self, color: str) -> float:
        pts = self.points()
        myc = pts[color]
        opc = pts[opponent(color)]
        total = myc + opc
        if total == 0:
            return 0.0
        return 100.0 * (myc - opc) / total

    def _mobility(self, color: str) -> float:
        """Calculate relative mobility (freedom of movement) advantage.

        Mobility is the number of legal moves available. Higher mobility:
        - Gives more strategic options
        - Restricts opponent's choices
        - Often indicates better board control

        Returns normalized difference: (my_moves - opp_moves)/(my_moves + opp_moves)
        """
        my_moves = len(self.posible_movements(color))  # Count my legal moves
        op_moves = len(self.posible_movements(opponent(color)))  # Count opponent moves

        # Avoid division by zero if no moves available
        if my_moves + op_moves == 0:
            return 0.0
        return 100.0 * (my_moves - op_moves) / (my_moves + op_moves)

    def _corner_occupancy(self, color: str) -> float:
        """Calculate relative advantage in corner control.

        Corner positions are strategically vital because:
        - Tokens in corners can never be flipped
        - They allow building stable lines of tokens
        - They deny the opponent key strategic positions

        Returns normalized difference: (my_corners - opp_corners)/(total_corners)
        """
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]  # Corner coordinates
        my_c = 0  # Count of my corners
        op_c = 0  # Count of opponent's corners

        for x, y in corners:
            t = self.state[y][x]
            if t is None:
                continue
            if t.color == color:
                my_c += 1
            else:
                op_c += 1
        if my_c + op_c == 0:
            return 0.0
        return 100.0 * (my_c - op_c) / (my_c + op_c)

    def _line_stable_in_direction(self, x, y, dx, dy) -> bool:
        """Check if a line of tokens is stable in a given direction.

        A line is stable if all tokens from the starting position to the board edge
        are the same color. This helps identify tokens that cannot be flipped.

        Args:
            x, y: Starting position
            dx, dy: Direction vector to check
        Returns:
            bool: True if the line is stable (all same color to edge)
        """
        # Empty cells can't be stable
        if self.state[y][x] is None:
            return False

        color = self.state[y][x].color
        cx, cy = x, y  # Current position
        ok_to_edge = True  # Track if we reach the edge with same color

        # Follow the direction vector until we hit edge or different color
        while 0 <= cx < self.BOARD_SIZE and 0 <= cy < self.BOARD_SIZE:
            t = self.state[cy][cx]
            if t is None or t.color != color:
                ok_to_edge = False
                break
            cx += dx
            cy += dy
        return ok_to_edge

    def _is_stable(self, x, y) -> bool:
        if self.state[y][x] is None:
            return False
        dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in dirs:
            if not (
                self._line_stable_in_direction(x, y, dx, dy)
                or self._line_stable_in_direction(x, y, -dx, -dy)
            ):
                return False
        return True

    def _stable_discs(self, color: str) -> float:
        """Calculate relative advantage in stable discs.

        A stable disc is one that cannot be flipped for the remainder of the game.
        This typically includes:
        - Corner pieces
        - Discs in completed lines connected to corners
        - Discs surrounded by stable discs of the same color

        Returns normalized difference: (my_stable - opp_stable)/(my_stable + opp_stable)
        """
        my_s = 0  # Count of player's stable discs
        op_s = 0  # Count of opponent's stable discs

        # Check each board position
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.state[y][x] is None:
                    continue
                # If position is stable, increment appropriate counter
                if self._is_stable(x, y):
                    if self.state[y][x].color == color:
                        my_s += 1
                    else:
                        op_s += 1

        # Normalize to percentage difference
        if my_s + op_s == 0:
            return 0.0
        return 100.0 * (my_s - op_s) / (my_s + op_s)

    def _positional_weights(self, color: str) -> float:
        """Evaluate board position using predefined position weights.

        Uses POSITION_WEIGHTS matrix to score each token based on its location.
        Strategic positions (corners, edges) are worth more than center positions.
        Adds weight if player's color, subtracts if opponent's color.

        Returns normalized score based on maximum possible score from weights."""
        score = 0
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                t = self.state[y][x]
                if t is None:
                    continue
                w = POSITION_WEIGHTS[y][x]
                score += w if t.color == color else -w
        # El valor máximo absoluto es la suma de todos los pesos positivos
        max_abs = sum(abs(w) for row in POSITION_WEIGHTS for w in row)
        if max_abs == 0:
            return 0.0  # Evitar división por cero
        return 100.0 * score / max_abs

    def _phase_weights(self, empty_cells: int, enabled: set[str]) -> dict:
        """Get appropriate heuristic weights based on game phase.

        The importance of different strategies changes throughout the game:
        - Opening (≥40 empty): Focus on mobility and positioning
        - Midgame (15-39 empty): Balanced approach with emphasis on corners
        - Endgame (<15 empty): Focus on stable discs and raw token count

        Args:
            empty_cells: Number of empty cells on board
            enabled: Set of enabled heuristic names
        """
        if empty_cells >= 40:  # Opening phase
            base = {
                "corner": 0.20,  # Corners less critical early
                "mob": 0.35,  # Mobility is key in opening
                "stable": 0.10,  # Few stable discs early
                "parity": 0.05,  # Token count matters little
                "pos": 0.30,  # Position strategy important
            }

        elif empty_cells >= 15:  # Midgame phase
            base = {
                "corner": 0.25,  # Corners become more important
                "mob": 0.30,  # Mobility still crucial
                "stable": 0.25,  # Stable discs more relevant
                "parity": 0.05,  # Count still secondary
                "pos": 0.15,  # Less focus on position
            }

        else:  # Endgame phase
            base = {
                "corner": 0.15,  # Corners less important late
                "mob": 0.05,  # Few moves available
                "stable": 0.40,  # Stable discs crucial
                "parity": 0.30,  # Final count matters a lot
                "pos": 0.10,  # Position less relevant
            }

        # Filtra a solo las activas y normaliza
        filtered = {k: v for k, v in base.items() if k in enabled}
        return self._normalize(filtered)


if __name__ == "__main__":
    board = ReversiBoard()
    print(board)
    print("Movimientos posibles para 'B':", board.posible_movements("B"))
    print("Evaluación para 'B':", board.evaluate("B"))
    print("Evaluación para 'R':", board.evaluate("R"))
