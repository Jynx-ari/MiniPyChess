import pygame
import chess


class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

    def draw(self, screen):
        pygame.draw.rect(screen, (230, 230, 230), self.rect, border_radius=10)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2, border_radius=10)
        text = self.font.render(self.text, True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, position):
        return self.rect.collidepoint(position)


class UI:
    WIDTH = 640
    HEIGHT = 640
    TILE = 80
    FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]
    RANKS = ["8", "7", "6", "5", "4", "3", "2", "1"]

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 54)
        self.overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        self.piece_images = {}
        for color in ["white", "black"]:
            for name in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
                self.piece_images[f"{color}_{name}"] = pygame.image.load(
                    f"assets/{color}_{name}.png"
                )

        self.menu_buttons = [
            Button((220, 260, 200, 60), "Play", self.font),
            Button((220, 340, 200, 60), "Quit", self.font),
        ]
        self.game_over_buttons = [
            Button((160, 400, 150, 60), "Rematch", self.font),
            Button((330, 400, 150, 60), "Main Menu", self.font),
        ]
        self.promotion_types = [
            (chess.QUEEN, "queen"),
            (chess.ROOK, "rook"),
            (chess.BISHOP, "bishop"),
            (chess.KNIGHT, "knight"),
        ]

    def square_from_mouse(self, position):
        x, y = position
        col, row = x // self.TILE, y // self.TILE
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        return chess.square(col, 7 - row)

    def handle_menu_click(self, position):
        if self.menu_buttons[0].clicked(position):
            return "game"
        if self.menu_buttons[1].clicked(position):
            return "quit"
        return None

    def handle_game_over_click(self, position):
        if self.game_over_buttons[0].clicked(position):
            return "rematch"
        if self.game_over_buttons[1].clicked(position):
            return "menu"
        return None

    def handle_promotion_click(self, position, game):
        width, gap = 100, 20
        start_x = (self.WIDTH - (width * 4 + gap * 3)) // 2
        y = self.HEIGHT // 2 - 50

        for i, (piece_type, _) in enumerate(self.promotion_types):
            rect = pygame.Rect(start_x + i * (width + gap), y, width, width)
            if rect.collidepoint(position):
                return game.choose_promotion(piece_type)
        return False

    def draw_menu(self):
        self.screen.fill((35, 35, 35))
        title = self.title_font.render("MiniPyChess", True, (245, 245, 245))
        self.screen.blit(title, title.get_rect(center=(320, 150)))
        for button in self.menu_buttons:
            button.draw(self.screen)
        pygame.display.flip()

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(self.screen, color, (col * 80, row * 80, 80, 80))

    def draw_labels(self):
        for col in range(8):
            text = self.font.render(self.FILES[col], True, (0, 0, 0))
            self.screen.blit(text, (col * 80 + 5, 640 - text.get_height() - 5))
        for row in range(8):
            text = self.font.render(self.RANKS[row], True, (0, 0, 0))
            self.screen.blit(text, (5, row * 80 + 5))

    def draw_pieces(self, game):
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = game.board.piece_at(square)
                if piece is None:
                    continue
                color = chess.COLOR_NAMES[piece.color]
                name = chess.piece_name(piece.piece_type)
                image = self.piece_images[f"{color}_{name}"]
                self.screen.blit(image, (col * 80 + 10, row * 80 + 10))

    def draw_moves(self, game):
        if not game.show_moves or game.first_select is None:
            return
        for move in game.legal_moves_from(game.first_select):
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            center = (col * 80 + 40, row * 80 + 40)
            if game.board.is_capture(move):
                pygame.draw.circle(self.overlay, (255, 80, 80, 140), center, 30, 5)
            else:
                pygame.draw.circle(self.overlay, (50, 50, 50, 100), center, 10)

    def draw_selection(self, game):
        if game.first_select is None:
            return
        col = chess.square_file(game.first_select)
        row = 7 - chess.square_rank(game.first_select)
        pygame.draw.rect(self.screen, (205, 255, 156), (col * 80, row * 80, 80, 80), 5)

    def draw_promotion(self, game):
        title = self.title_font.render("Promote Pawn", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(320, 170)))
        width, gap = 100, 20
        start_x = (640 - (width * 4 + gap * 3)) // 2
        y = 270
        color = "white" if game.board.turn == chess.WHITE else "black"

        for i, (_, name) in enumerate(self.promotion_types):
            rect = pygame.Rect(start_x + i * (width + gap), y, width, width)
            pygame.draw.rect(self.screen, (235, 235, 235), rect, border_radius=10)
            image = self.piece_images[f"{color}_{name}"]
            self.screen.blit(image, image.get_rect(center=rect.center))

    def draw_game(self, game, flip=True):
      self.draw_board()
      self.draw_labels()
      self.overlay.fill((0, 0, 0, 0))
    
      self.draw_pieces(game)
      self.draw_moves(game)
    
      self.screen.blit(self.overlay, (0, 0))
      self.draw_selection(game)
    
      if game.is_promotion_pending():
          self.overlay.fill((0, 0, 0, 190))
          self.screen.blit(self.overlay, (0, 0))
          self.draw_promotion(game)
    
      if flip:
          pygame.display.flip()

    def draw_ai_thinking(self, game):
        self.draw_game(game, flip=False)

        self.overlay.fill((0, 0, 0, 150))
        self.screen.blit(self.overlay, (0, 0))

        text = self.title_font.render("AI THINKING...", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(320, 320)))

        pygame.display.flip()

    def draw_game_over(self, game):
        self.draw_game(game, flip=False)

        self.overlay.fill((0, 0, 0, 190))
        self.screen.blit(self.overlay, (0, 0))

        message = "Stalemate" if game.winner is None else f"{game.winner} wins!"
        title = self.title_font.render(message, True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(320, 260)))

        for button in self.game_over_buttons:
            button.draw(self.screen)

        pygame.display.flip()
