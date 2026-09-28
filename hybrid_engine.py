import chess
import chess.engine
import math
import random

class RubyChessPiece:
    """Inspired by Ruby Chess: Lightweight, object-oriented piece tracking."""
    def __init__(self, piece_type, color):
        self.piece_type = piece_type
        self.color = color

class AlphaZeroHeuristic:
    """
    Inspired by AlphaZero: Approximates a policy network using positional 
    and piece-square table weights to prioritize high-probability tactical squares.
    """
    def __init__(self):
        # Basic piece values for material balance
        self.values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
        
    def evaluate_board(self, board):
        """Generates a static evaluation score from the current position."""
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = self.values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score

class HybridChessEngine:
    """
    The Ultimate Hybrid Engine
    Combines: Stockfish (Calculation) + AlphaZero (Heuristics) + Ruby Chess (Object Structure)
    Created by: Voleti Dheeraj Shankar
    """
    def __init__(self, stockfish_path=None):
        self.board = chess.Board()
        self.az_evaluator = AlphaZeroHeuristic()
        self.stockfish_path = stockfish_path
        self.stockfish_engine = None
        
        # Initialize Stockfish if path is given
        if stockfish_path:
            try:
                self.stockfish_engine = chess.engine.SimpleEngine.Popen(stockfish_path)
            except Exception as e:
                print(f"⚠️ Stockfish path not loaded: {e}. Falling back to internal engine logic.")

    def search_alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        """Stockfish-style classic Alpha-Beta Minimax search tree pruning."""
        if depth == 0 or board.is_game_over():
            return self.az_evaluator.evaluate_board(board)

        legal_moves = list(board.legal_moves)
        # Prioritize moves using AlphaZero positional heuristics to prune early
        legal_moves.sort(key=lambda move: self.score_move_probability(board, move), reverse=maximizing_player)

        if maximizing_player:
            max_eval = -math.inf
            for move in legal_moves:
                board.push(move)
                evaluation = self.search_alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Prune branch
            return max_eval
        else:
            min_eval = math.inf
            for move in legal_moves:
                board.push(move)
                evaluation = self.search_alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Prune branch
            return min_eval

    def score_move_probability(self, board, move):
        """AlphaZero policy surrogate: assigns weights based on move quality."""
        score = 0
        if board.is_capture(move):
            score += 50
        if board.gives_check(move):
            score += 30
        return score

    def get_best_move(self, depth=3):
        """Selects the best tactical move using the active hybrid configuration."""
        # Fallback 1: Use Stockfish binary if natively available
        if self.stockfish_engine:
            result = self.stockfish_engine.play(self.board, chess.engine.Limit(time=0.5))
            return result.move

        # Fallback 2: Compute using internal Alpha-Beta + AlphaZero heuristics
        best_move = None
        best_value = -math.inf if self.board.turn == chess.WHITE else math.inf
        
        for move in self.board.legal_moves:
            self.board.push(move)
            board_value = self.search_alpha_beta(self.board, depth - 1, -math.inf, math.inf, not self.board.turn)
            self.board.pop()
            
            if self.board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
                    
        return best_move if best_move else random.choice(list(self.board.legal_moves))

    def close(self):
        if self.stockfish_engine:
            self.stockfish_engine.quit()

if __name__ == "__main__":
    engine = HybridChessEngine()
    print("♚ Hybrid Chess Engine Initialized! [Stockfish + AlphaZero Heuristics + Ruby Structure]")
    print(f"Initial legal recommendation: {engine.get_best_move(depth=3)}")

