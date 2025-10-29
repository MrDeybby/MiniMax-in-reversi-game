import math
from copy import deepcopy
from typing import List, Tuple, Optional
import time
import tracemalloc

from players.player import Player
from game.reversiBoard import ReversiBoard, opponent
from game.tokens import Token


class MinimaxPlayer(Player):
    """
    Reversi player that uses Minimax with Alpha-Beta pruning.

    Attributes
    
    TYPE_ : str
        Static identifier of the player type ("minimax").
    max_depth : float
        Maximum search depth. `math.inf` disables depth limiting (time limit
        will still apply).
    enabled_heuristics : Optional[set[str]]
        Subset of heuristic names to use in `ReversiBoard.evaluate`. If None,
        board decides the default set.
    custom_weights : Optional[dict]
        Optional mapping of heuristic names to custom weights used by the
        board evaluation.
    max_time : float
        Maximum time (seconds) allowed for a single `play` call. `math.inf`
        disables time limiting.
    ejecution_time : float
        Accumulated time (seconds) across plays (kept for metrics).
    nodes_expanded : int
        Accumulated number of nodes expanded across plays.
    depth_explored : int
        Accumulated deepest depth reached across plays.
    turns_played : int
        Number of turns (calls to `play`) executed so far.
    max_ram_usage : float
        Accumulated peak RAM usage (in MiB) across plays.
    """

    TYPE_ = "minimax"
    
    def __init__(self, name="minimax", depth=math.inf, max_time=math.inf, 
                enabled_heuristics: Optional[List[str]] = None,
                custom_weights: Optional[dict] = None):
        """
        Initialize a Minimax player.

        Parameters
        
        name : str, optional
            Player name, by default "minimax".
        depth : float, optional
            Maximum search depth (>=1). Use `math.inf` for no explicit depth
            limit (iterative deepening will still be constrained by `max_time`).
        max_time : float, optional
            Per-move time budget in seconds. Use `math.inf` to disable timing.
        enabled_heuristics : Optional[List[str]], optional
            If provided, restrict board evaluation to the listed heuristics.
        custom_weights : Optional[dict], optional
            If provided, custom weight overides for named heuristics.
        """

        super().__init__(name)
        self.max_depth = depth  
        # Normalize list to a set for O(1) membership checks. If None, defer to board defaults.
        self.enabled_heuristics = set(enabled_heuristics) if enabled_heuristics else None
        self.custom_weights = custom_weights
        self.max_time = max_time

        # Metrics
        self.ejecution_time = 0      # Accumulated wall time
        self.nodes_expanded = 0      # Accumulated expanded nodes
        self.depth_explored = 0      # Accumulated deepest depth reached
        self.turns_played = 0        # Number of turns played
        self.max_ram_usage = 0       # Accumulated peak RAM usage
        
    def reset(self):
        """Reset all acumulated metrics for a fresh evaluation run."""
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
        
    def play(self, board: ReversiBoard) -> Tuple[int, int]:
        """
        Choose the best move for the current board position.

        This is the main entry point called by the game engine. The method
        uses *iterative deepening* with Alpha-Beta pruning, honoring the
        configured `max_time` to stop when time runs out.

        This method:

        1) Start per-move memory profiling with `tracemalloc.start()`.
        2) Increment `turns_played` and collect all legal moves for our color.
           If no moves exist, return `None` (pass).
        3) Initialize root best-so-far score and alpha/beta bounds.
        4) Run an **interative deepening** loop (depth = 2..N):
           4.1) For each legal root move:
                - Clone the board and apply the move.
                - Call `_minimax(child, depth-1, alpha, beta, is_max=False, ...)`.
                - If the returned score improves `best_score`, update `best_move`.
                - Update `alpha` at the root with the best-so-far value.
           4.2) If the time budget is exceeded inside `_minimax`, a `StopIteration`
                is raised and caught here to end the loop cleanly.
        5) Accumulate per-move telemetry: nodes expanded, deepest depth reached,
           and wall-clock time spent.
        6) Record peak memory for this move, add to `max_ram_usage`, and stop
           memory profiling with `tracemalloc.stop()`.
        7) Return the selected `best_move`.

        Parameters
        
        board : ReversiBoard
            Current board state.

        Returns
        
        Tuple[int, int]
            The selected move `(x, y)` in board coordinates. If no move is
            available (pass), returns `None`.

        """
        # Start memory tracking for this move
        tracemalloc.start()

        # Track the deepest depth reached within this move
        self.new_depth = 1
        total_depth = 1
        depth_counter = 1

        # Telemetry: count the turn
        self.turns_played += 1

        # Generate legal moves for our color; if none, return pass (None)
        possible_moves = board.posible_movements(self.tokens.color)
        self.time_start = time.time()
        
        if not possible_moves:
            return None
        
        # Initialize best-so-far (for iterative deepening)
        best_move = possible_moves[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf

        total_nodes_expanded = 0
        total_depth = 0
        
        # Iterative deepening: try increasing depth until time limit hits.
        # Note: `self.max_depth` is not currently enforced in the loop bound,
        # but time budget will still cap the search.
        for depth in range(2, 1000000):
            try:
                # Reset per-iteration counters
                self.turn_nodes_expanded = 0
                self.new_depth = 1

                # Explore all currently legal moves at this root depth.
                for move in possible_moves:
                    x, y = move
                    
                    # Create a child state by applying the move.
                    child_board = deepcopy(board)
                    self.turn_nodes_expanded += 1
                    child_board.insert_play(x, y, Token(self.tokens.color))
                    
                    # Run Minimax from the child position as minimizing player next
                    score = self._minimax(child_board, depth - 1, alpha, beta, False, depth_counter)
                    
                    # Track the best root move based on returned score
                    if score > best_score:
                        best_score = score
                        best_move = move
                    
                    # Alpha update at root
                    alpha = max(alpha, best_score)

                # Collect per-iteration metrics
                total_nodes_expanded = self.turn_nodes_expanded
                total_depth = self.new_depth

            except StopIteration:
                # Time budget exhausted; return best-so-far from the last completed iteration
                break
        
        # Accumulate metrics across turns
        self.nodes_expanded += total_nodes_expanded
        self.depth_explored += total_depth    
        self.ejecution_time += time.time() - self.time_start

        # Record peak memory (MiB) for this move and add to cumulative total
        _, peak_memory = tracemalloc.get_traced_memory()
        self.max_ram_usage += (peak_memory / 1024**2)
        
        # Stop memory tracking
        tracemalloc.stop()

        return best_move

    def _minimax(self, board: ReversiBoard, depth: int, alpha: float, beta: float, is_maximizing_player: bool, depth_counter:int=0) -> float:
        """
        Recursive Minimax with Alpha-Beta pruning.

        Parameters
        
        board : ReversiBoard
            Current node state.
        depth : int
            Remaining depth to search; when it reaches 0 (or at terminal
            states) the evaluator is called.
        alpha : float
            Best already-explored value along the path to the root for the
            maximizing player.
        beta : float
            Best already-explored value along the path to the root for the
            minimizing player.
        is_maximizing_player : bool
            Whether this node is a maximizing (our turn) or minimizing node
            (opponent's turn).
        depth_counter : int, optional
            Tracks depth reached for telemetry purposes.

        Returns

        float
            Heuristic score for the position, from the perspective of this
            player's color (higher is better for us).

        """
        # Enforce time limit (cooperatively abort the search)
        if time.time() - self.time_start >= self.max_time:
            raise StopIteration("Out of time!")
        
        # Terminal node or depth limit reached: evaluate position
        if depth == 0 or board.is_terminal():
            return board.evaluate(self.tokens.color, enabled_heuristics=self.enabled_heuristics,
                                custom_weights=self.custom_weights)
            
        # Track deepest depth reached
        if self.new_depth < depth_counter:
            self.new_depth = depth_counter
        
        if is_maximizing_player:
            # Maximizing branch: our move
            max_eval = -math.inf
            my_color = self.tokens.color
            
            # Expand children for our color
            children_boards = board.childrens(my_color)
            
            if not children_boards:
                # No legal moves: pass turn to opponent (minimizing)
                return self._minimax(board, depth - 1, alpha, beta, False, depth_counter+1)
            
            for child in children_boards:
                # Telemetry: count expansion
                self.turn_nodes_expanded += 1

                # Recurse into minimizing node
                eval = self._minimax(child, depth - 1, alpha, beta, False, depth_counter+1)
                max_eval = max(max_eval, eval)

                # Alpha update and Beta cutoff
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            
            return max_eval
        
        else:
            # Minimizing branch: opponent's move
            min_eval = math.inf
            opponent_color = opponent(self.tokens.color)
            
            # Expand children for opponent color
            children_boards = board.childrens(opponent_color)

            if not children_boards:
                # No opponent moves: pass back to maximizing
                return self._minimax(board, depth - 1, alpha, beta, True, depth_counter+1)

            for child in children_boards:
                # Telemetry: count expansion
                self.turn_nodes_expanded += 1

                # Recurse into maximizing node
                eval = self._minimax(child, depth - 1, alpha, beta, True, depth_counter+1)
                min_eval = min(min_eval, eval)

                # Beta update and Alpha cutoff
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval
        