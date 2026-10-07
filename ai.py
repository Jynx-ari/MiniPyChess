import chess
import chess.engine


STOCKFISH_PATH = "/data/data/com.termux/files/usr/bin/stockfish"


class ChessAI:
    def __init__(self, elo=500):
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.set_elo(elo)

    def set_elo(self, elo):
        elo = max(1, min(2100, elo))

        # MiniPyChess difficulty → Stockfish Skill Level
        skill = min(20, max(0, (elo // 100) - 1))

        self.engine.configure({
            "Skill Level": skill
        })

    def get_move(self, board):
        result = self.engine.play(
            board,
            chess.engine.Limit(depth=12)
        )
        return result.move

    def close(self):
        self.engine.quit()
