import math
from copy import deepcopy
from typing import List, Tuple, Optional
import time
import tracemalloc

from players.player import Player
from game.reversiBoard import ReversiBoard, opponent
from game.tokens import Token


class BadPlayer(Player):
    """
    A deliberately weak Minimax player (chooses lower-scoring root moves).

    Attributes
    
    TYPE_ : str
        Static identifier of the player type ("Bad").
    max_depth : float
        Maximum search depth. `math.inf` disables explicit depth limiting.
    enabled_heuristics : Optional[set[str]]
        Optional subset of heuristic names to use during board evaluation.
    custom_weights : Optional[dict]
        Optional mapping of heuristic names to custom weight overrides.
    max_time : float
        Maximum wall-clock time (seconds) allowed per call to `play`.
    ejecution_time : float
        Accumulated time (seconds) spent choosing moves across plays.
    nodes_expanded : int
        Total number of expanded nodes accumulated across plays.
    depth_explored : int
        Accumulated deepest depth reached across plays.
    turns_played : int
        Number of moves (calls to `play`) executed.
    max_ram_usage : float
        Accumulated peak memory usage (MiB) across plays.
    """
    
    TYPE_ = "Bad"
    
    def __init__(self, name="Bad", depth=math.inf, max_time=math.inf, 
                enabled_heuristics: Optional[List[str]] = None,
                custom_weights: Optional[dict] = None):
        """Inicialize a BadPlayer.

        Parameters
        
        name : str, optional
            Player name, by default "Bad".
        depth : float, optional
            Maximum search depth (>=1). Use `math.inf` to disable explicit
            depth limiting (time limiting may still stop search).
        max_time : float, optional
            Per-move wall-clock time budget (seconds). Use `math.inf` to disable.
        enabled_heuristics : Optional[List[str]], optional
            If provided, restrict board evaluation to the listed heuristics.
        custom_weights : Optional[dict], optional
            If provided, weight overrides for named heuristics.
        """
        super().__init__(name)
        self.max_depth = depth  
        # Normalize list to a set for efficient membership checks. If None, the board uses its defaults.
        self.enabled_heuristics = set(enabled_heuristics) if enabled_heuristics else None
        self.custom_weights = custom_weights
        self.max_time = max_time

        # Metrics
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
    def reset(self):
        """Reset accumulated metrics to zero."""
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
        
    def play(self, board: ReversiBoard) -> Tuple[int, int]:
        """
        Main entry point: search and choose a (deliberaly worse) move.

        This method:
        1) Starts memory tracking (via `tracemalloc`) for this move.
        2) Generates all legal moves for the current color.
        3) Runs an iterative-deepening loop over Minimax (with Alpha-Beta).
        4) At the root, updates the chosen move when a **lower** score is found
           (note the inverted comparison), intentionally degrading performance.
        5) Updates time, node, depth, and memory metrics, and prints the choice.

        Parameters
        
        board : ReversiBoard
            Current board state.

        Returns
        
        Tuple[int, int]
            The selected `(x, y)` move. If there are no legal moves, returns `None`.

        Raises
        
        StopIteration
            Propagated internally to end search when the time budget is exceeded.
        """
        tracemalloc.start()  # Begin per-move memory profiling

        # Track latest depth reached within this move (for telemetry only)
        self.new_depth = 1
        total_depth = None
        depth_counter = 1

        # Count this as a new turn
        self.turns_played += 1

        # Generate legal moves for our color; if none, pass (return None)
        possible_moves = board.posible_movements(self.tokens.color)
        self.time_start = time.time()
        
        
        if not possible_moves:
            return None
        
        # Initialize best-so-far (intentionally picking worse scores)
        best_move = possible_moves[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf
        
        total_nodes_expanded = 0
        total_depth = 0

        # Iterative deepening: increase depth until time limit triggers StopIteration
        self.turn_nodes_expanded = 0
        for depth in range(2, 1000000):
            try:
                # Reset per-iteration counters
                self.turn_nodes_expanded = 0
                self.new_depth = 1

                # Explore all current legal moves from the root
                for move in possible_moves:
                    x, y = move
                    
                    # Create a child state by applying the move.
                    child_board = deepcopy(board)
                    self.turn_nodes_expanded += 1
                    child_board.insert_play(x, y, Token(self.tokens.color))
                    
                    # Minimax from the child position (opponent to play)
                    score = self._minimax(child_board, depth - 1, alpha, beta, False, depth_counter)
                    
                    # NOTE: Deliberately worse selection: keep move if score is LOWER
                    if score < best_score:
                        best_score = score
                        best_move = move
                    
                    # Alpha update at root
                    alpha = max(alpha, best_score)

                # Collect per-iteration metrics
                total_nodes_expanded = self.turn_nodes_expanded
                total_depth = self.new_depth
            except StopIteration:
                # Time budget exhausted; return best-so-far
                break
        
        # Accumulate metrics across turns
        self.nodes_expanded += total_nodes_expanded
        self.depth_explored += total_depth    
        self.ejecution_time += time.time() - self.time_start

        # Record and acumulate peak memory for this move (in MiB)
        _, peak_memory = tracemalloc.get_traced_memory()
        self.max_ram_usage += (peak_memory / 1024**2)
        
        tracemalloc.stop()  # End per-move memory profiling

        print(f"{self.name} elige {best_move} (Puntuación: {best_score:.4f})")
        return best_move

    def _minimax(self, board: ReversiBoard, depth: int, alpha: float, beta: float, is_maximizing_player: bool, depth_counter:int=0) -> float:
        """Recursive Minimax with Alpha-Beta pruning.

        Parameters
        
        board : ReversiBoard
            Current node (board) state.
        depth : int
            Remaining depth to search; when it reaches 0 (or at terminal states)
            the evaluator is called.
        alpha : float
            Best value along the path to the root for the maximizing player.
        beta : float
            Best value along the path to the root for the minimizing player.
        is_maximizing_player : bool
            Whether this node is a maximizing node (our turn) or minimizing node
            (opponent's turn).
        depth_counter : int, optional
            Tracks depth reached for telemetry updates.

        Returns
        
        float
            Heuristic score for the position from **this player's** perspective.

        Raises
        
        StopIteration
            If the allotted time budget is exceeded during search.
        """
        # Coperative time check; abort search if out of time
        if time.time() - self.time_start >= self.max_time:
            raise StopIteration("Out of time!")
        
        # Depth cutoff or terminal node: return evaluation
        if depth == 0 or board.is_terminal():
            return board.evaluate(self.tokens.color, enabled_heuristics=self.enabled_heuristics,
                                custom_weights=self.custom_weights)
            
        # Track deepest depth reached in this move
        if self.new_depth < depth_counter:
            self.new_depth = depth_counter
        
        if is_maximizing_player:
            # NOTE: In this branch the code computes a MIN value (intentionally inverted)
            min_eval = math.inf
            my_color = self.tokens.color

            # Expand children for our color
            children_boards = board.childrens(my_color)
            
            if not children_boards:
                # No legal moves: pass turn to opponent (minimizing)
                return self._minimax(board, depth - 1, alpha, beta, False, depth_counter+1)

            for child in children_boards:
                # Telemetry: count node expansion
                self.turn_nodes_expanded += 1

                # Recurse into minimizing node
                eval = self._minimax(child, depth - 1, alpha, beta, False, depth_counter+1)
                min_eval = min(min_eval, eval)

                # Beta update and Alpha cut-off
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return min_eval
            
        else:
            # Opponent branch (treated as maximizing in this implementation)
            max_eval = -math.inf
            
            opponent_color = opponent(self.tokens.color)
            # Expand children for the opponent color
            children_boards = board.childrens(opponent_color)
            
            if not children_boards:
                # No opponent moves: pass back to maximizing branch
                return self._minimax(board, depth - 1, alpha, beta, True, depth_counter+1)
            
            for child in children_boards:
                # Telemetry: count node expansion
                self.turn_nodes_expanded += 1

                # Recurse into maximizing node
                eval = self._minimax(child, depth - 1, alpha, beta, True, depth_counter+1)
                max_eval = max(max_eval, eval)

                # Alpha update and Beta cut-off
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta pruning
            
            return max_eval
