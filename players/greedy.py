import math
from copy import deepcopy
from typing import List, Tuple, Optional
import time
import tracemalloc


from players.player import Player
from game.reversiBoard import ReversiBoard, opponent
from game.tokens import Token


class GreedyPlayer(Player):
    """
    A depth-1 evaluator: picks the move with the best immediate score.

    This player enumerates all legal moves for the current color, applies each
    move to a copy of the board, calls the board evaluator once, and selects
    the move with the highest returned score. No deeper search is performed.

    Attributes
    
    TYPE_ : str
        Static identifier of the player type ("greedy").
    enabled_heuristics : Optional[set[str]]
        If provided, limits the board's evaluation to this subset of heuristics.
    custom_weights : Optional[dict]
        Optional mapping of heuristic names to weight overrides for evaluation.
    ejecution_time : float
        Accumulated time spent choosing moves (seconds).
    nodes_expanded : int
        Accumulated number of child positions evaluated.
    depth_explored : int
        Accumulated deepest depth reached (for greedy, increments by 1 per play).
    turns_played : int
        Number of turns (calls to `play`) executed.
    max_ram_usage : float
        Accumulated peak memory usage (MiB) across plays.
    """
    
    TYPE_ = "greedy"
    
    def __init__(self, name="greedy", 
                enabled_heuristics: Optional[List[str]] = None,
                custom_weights: Optional[dict] = None):
        """Initialize a Greedy player.

        Parameters
        
        name : str, optional
            Player name, by default "greedy".
        enabled_heuristics : Optional[List[str]], optional
            If provided, restrict board evaluation to the listed heuristics.
        custom_weights : Optional[dict], optional
            If provided, custom weight overrides for named heuristics.
        """

        super().__init__(name) 
        # Normalize to a set for efficient membership checks in the board evaluator.
        self.enabled_heuristics = set(enabled_heuristics) if enabled_heuristics else None
        self.custom_weights = custom_weights

        # Telemetry / metrics (aggregated across turns)
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
    def reset(self):
        """Reset all accumulated telemetry/metrics to zero."""
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
        
    def play(self, board: ReversiBoard) -> Tuple[int, int]:
        """
        Main entry point. Finds the best move at depth 1 (greedy).

        The method:

        1) Starts memory tracking (`tracemalloc`) for this move.
        2) Generates all legal moves for the current color.
        3) For each move, applies it on a deep copy of the board and calls
           `board.evaluate(...)` for a single-ply score.
        4) Selects the move with the highest score.
        5) Updates metrics (time, nodes, depth, memory) and returns the move.

        Parameters
        
        board : ReversiBoard
            Current board state.

        Returns
        
        Tuple[int, int]
            The selected `(x, y)` move. If there are no legal moves, returns `None`.

        """

        tracemalloc.start()  # Begin per-move memory profiling

        # Count this as a new turn
        self.turns_played += 1

        # Gather legal moves for our color; if none, pass (return None)
        possible_moves = board.posible_movements(self.tokens.color)
        self.time_start = time.time()
        
        
        if not possible_moves:
            return None
        
        # Initialize best-so-far
        best_move = possible_moves[0]
        best_score = -math.inf

        # Evaluate each legal move in a single-ply lookahead
        for move in possible_moves:
            x, y = move
            
            # Work on a copy to avoid mutating the original board state
            child_board = deepcopy(board)

            # Telemetry: a child position was generated/evaluated
            self.nodes_expanded += 1

            # Apply the candidate move on the copy
            child_board.insert_play(x, y, Token(self.tokens.color))
            
            # Evaluate resulting position from our perspective
            score = child_board.evaluate(self.tokens.color, enabled_heuristics=self.enabled_heuristics,
                        custom_weights=self.custom_weights)
            
            # Keep the highest-scoring move
            if score > best_score:
                best_score = score
                best_move = move

        # For a greedy player, we reached depth 1
        self.depth_explored += 1    

        # Accumulate time spent on this move
        self.ejecution_time += time.time() - self.time_start

        # Record and accumulate peak memory for this move (in MiB)
        _, peak_memory = tracemalloc.get_traced_memory()
        self.max_ram_usage += (peak_memory / 1024**2)
        
        # Stop per-move memory profiling
        tracemalloc.stop()

        print(f"{self.name} elige {best_move} (Puntuación: {best_score:.4f})")
        return best_move
