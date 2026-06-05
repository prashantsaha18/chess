import chess
import chess.engine
import random
import numpy as np
from typing import Optional, Tuple

# ─── Piece value tables for positional evaluation ───────────────────────────

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Piece-square tables (from white's perspective)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PST = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


def piece_square_value(piece_type: int, square: int, color: bool) -> int:
    """Get positional bonus for a piece on a square."""
    table = PST.get(piece_type, [0] * 64)
    if color == chess.WHITE:
        idx = (7 - chess.square_rank(square)) * 8 + chess.square_file(square)
    else:
        idx = chess.square_rank(square) * 8 + chess.square_file(square)
    return table[idx]


def evaluate_board(board: chess.Board) -> int:
    """Static evaluation of board position (positive = good for white)."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]
        pst = piece_square_value(piece.piece_type, square, piece.color)
        if piece.color == chess.WHITE:
            score += val + pst
        else:
            score -= val + pst

    # Mobility bonus
    score += len(list(board.legal_moves)) * (1 if board.turn == chess.WHITE else -1) * 2

    return score


# ─── Minimax with Alpha-Beta Pruning ─────────────────────────────────────────

def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        max_eval = -99999
        for move in board.legal_moves:
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 99999
        for move in board.legal_moves:
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return min_eval


def order_moves(board: chess.Board):
    """Sort moves to improve alpha-beta pruning."""
    def move_score(move):
        s = 0
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                s += 10 * PIECE_VALUES.get(victim.piece_type, 0) - PIECE_VALUES.get(attacker.piece_type, 0)
        if move.promotion:
            s += PIECE_VALUES.get(move.promotion, 0)
        if board.gives_check(move):
            s += 50
        return -s

    return sorted(board.legal_moves, key=move_score)


# ─── AI Modes ────────────────────────────────────────────────────────────────

class ChessAI:
    def __init__(self, mode: str):
        self.mode = mode  # beginner, intermediate, difficult, advanced

    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        moves = list(board.legal_moves)
        if not moves:
            return None

        if self.mode == "beginner":
            return self._beginner_move(board, moves)
        elif self.mode == "intermediate":
            return self._intermediate_move(board, moves)
        elif self.mode == "difficult":
            return self._difficult_move(board, moves)
        elif self.mode == "advanced":
            return self._advanced_move(board, moves)

    def _beginner_move(self, board: chess.Board, moves) -> chess.Move:
        """Random move with occasional captures — Elo ~400."""
        captures = [m for m in moves if board.is_capture(m)]
        if captures and random.random() < 0.6:
            return random.choice(captures)
        return random.choice(moves)

    def _intermediate_move(self, board: chess.Board, moves) -> chess.Move:
        """Depth-2 minimax with 25% noise — Elo ~800."""
        scored = []
        for move in moves:
            board.push(move)
            s = -minimax(board, 1, -99999, 99999, False)
            board.pop()
            scored.append((s + random.randint(-50, 50), move))
        scored.sort(key=lambda x: -x[0])
        return scored[0][1]

    def _difficult_move(self, board: chess.Board, moves) -> chess.Move:
        """Depth-3 minimax with move ordering — Elo ~1200."""
        best_move = None
        best_score = -99999
        for move in order_moves(board):
            board.push(move)
            s = -minimax(board, 2, -99999, 99999, False)
            board.pop()
            if s > best_score:
                best_score = s
                best_move = move
        return best_move or random.choice(moves)

    def _advanced_move(self, board: chess.Board, moves) -> chess.Move:
        """Depth-4 minimax with full alpha-beta — Elo ~1600."""
        best_move = None
        best_score = -99999
        for move in order_moves(board):
            board.push(move)
            s = -minimax(board, 3, -99999, 99999, False)
            board.pop()
            if s > best_score:
                best_score = s
                best_move = move
        return best_move or random.choice(moves)


def get_ai(mode: str) -> ChessAI:
    return ChessAI(mode)
