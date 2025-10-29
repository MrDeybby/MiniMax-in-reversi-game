from abc import ABC, abstractmethod
from game.tokens import Token
from copy import deepcopy
import math
from game.color import Color

# --- IMPLEMENTACION DE LO QUE HIZO HECTOR EL MORENO MAGICO ---

POSITION_WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, -1, -1, -1, -1, -2, 10],
    [5, -2, -1, -1, -1, -1, -2, 5],
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

    BOARD_SIZE = 8

    def __init__(self, state=None, depth=0, utility=0):
        super().__init__(state, depth, utility)
        self.players_tokens = {"B": 30, "R": 30}
        self.HEURISTICS = {
            "corner": self._corner_occupancy,
            "mob": self._mobility,
            "stable": self._stable_discs,
            "parity": self._coin_parity,
            "pos": self._positional_weights,
        }

        if not state:
            self.create_board()

    def create_board(self):
        self._state = [
            [None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)
        ]
        self._state[3][3] = Token("B")
        self._state[3][4] = Token("R")
        self._state[4][3] = Token("R")
        self._state[4][4] = Token("B")

    def points(self):
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

    def is_terminal(self):
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

    def childrens(self, player_color):
        """
        Generates child board states for all valid moves (used by AI)
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
        return self._state

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, new_depth: int):
        self._depth = new_depth

    def posible_movements(self, color):
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

    def insert_play(self, x, y, token: Token):
        """
        Validates move, places token, flips opponent tokens, decrements token count
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

    def show(self, player=None):
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

    def __str__(self):

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
        """
        Calcula la evaluación usando solo las heurísticas seleccionadas.
        - enabled_heuristics: nombres en {"corner","mob","stable","parity","pos"}.
        Si es None, usa todas.
        - custom_weights: pesos por nombre (se normalizan y prevalecen sobre los de fase).
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
        my_moves = len(self.posible_movements(color))
        op_moves = len(self.posible_movements(opponent(color)))
        if my_moves + op_moves == 0:
            return 0.0
        return 100.0 * (my_moves - op_moves) / (my_moves + op_moves)

    def _corner_occupancy(self, color: str) -> float:
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        my_c = 0
        op_c = 0
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
        if self.state[y][x] is None:
            return False
        color = self.state[y][x].color
        cx, cy = x, y
        ok_to_edge = True
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
        my_s = 0
        op_s = 0
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.state[y][x] is None:
                    continue
                if self._is_stable(x, y):
                    if self.state[y][x].color == color:
                        my_s += 1
                    else:
                        op_s += 1
        if my_s + op_s == 0:
            return 0.0
        return 100.0 * (my_s - op_s) / (my_s + op_s)

    def _positional_weights(self, color: str) -> float:
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
        if empty_cells >= 40:  # Apertura
            base = {
                "corner": 0.20,
                "mob": 0.35,
                "stable": 0.10,
                "parity": 0.05,
                "pos": 0.30,
            }

        elif empty_cells >= 15:  # Medio juego
            base = {
                "corner": 0.25,
                "mob": 0.30,
                "stable": 0.25,
                "parity": 0.05,
                "pos": 0.15,
            }

        else:  # Final
            base = {
                "corner": 0.15,
                "mob": 0.05,
                "stable": 0.40,
                "parity": 0.30,
                "pos": 0.10,
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
