import chess.engine


class StockfishAI:
    def __init__(self, elo=500, path="stockfish"):
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.set_elo(elo)

    def set_elo(self, elo):
        elo = max(100, min(2100, int(elo)))
        skill = min(20, max(0, (elo - 100) // 100))
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
