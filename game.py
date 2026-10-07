import chess


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.first_select = None
        self.show_moves = True
        self.game_over = False
        self.winner = None
        self.promotion_square = None

    def reset(self):
        self.__init__()

    def clear_selection(self):
        self.first_select = None

    def is_own_piece(self, square):
        piece = self.board.piece_at(square)
        return piece is not None and piece.color == self.board.turn

    def legal_moves_from(self, square):
        return [m for m in self.board.legal_moves if m.from_square == square]

    def select_square(self, square):
        piece = self.board.piece_at(square)
        if self.first_select is None:
            if piece is not None and self.is_own_piece(square):
                self.first_select = square
        elif piece is not None and self.is_own_piece(square):
            self.first_select = square
        else:
            self.try_move(self.first_select, square)

    def try_move(self, start, end, promotion=None):
        piece = self.board.piece_at(start)
        if piece is None:
            return False

        if promotion is None and piece.piece_type == chess.PAWN:
            if chess.square_rank(end) in (0, 7):
                test = chess.Move(start, end, promotion=chess.QUEEN)
                if test in self.board.legal_moves:
                    self.promotion_square = end
                    return False

        move = chess.Move(start, end, promotion=promotion)
        if move not in self.board.legal_moves:
            return False

        self.board.push(move)
        self.clear_selection()
        self.check_game()
        return True

    def choose_promotion(self, piece_type):
        if self.first_select is None or self.promotion_square is None:
            return False

        move = chess.Move(self.first_select, self.promotion_square, promotion=piece_type)
        if move not in self.board.legal_moves:
            return False

        self.board.push(move)
        self.promotion_square = None
        self.clear_selection()
        self.check_game()
        return True

    def check_game(self):
        if self.board.is_checkmate():
            self.game_over = True
            self.winner = "White" if self.board.turn == chess.BLACK else "Black"
            return True
        if self.board.is_stalemate():
            self.game_over = True
            self.winner = None
            return True
        return False

    def is_promotion_pending(self):
        return self.promotion_square is not None
