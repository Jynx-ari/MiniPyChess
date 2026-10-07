import chess.engine


STOCKFISH_PATH = "/data/data/com.termux/files/usr/bin/stockfish"


class StockfishAI:
    def __init__(self, elo=500, path=STOCKFISH_PATH):
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.set_elo(elo)

    def set_elo(self, elo):
        elo = max(1, min(2100, int(elo)))

        # MiniPyChess difficulty -> Stockfish Skill Level.
        skill = min(20, max(0, (elo // 100) - 1))

        self.engine.configure({"Skill Level": skill})
        self.elo = elo
        self.skill = skill

    def get_move(self, board, time_limit=0.25):
        result = self.engine.play(
            board,
            chess.engine.Limit(time=time_limit),
        )
        return result.move

    def quit(self):
        self.engine.quit()
