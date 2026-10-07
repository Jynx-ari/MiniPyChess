import pygame
import chess


class Button:
    def __init__(self, rect, text, font, primary=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.primary = primary

    def draw(self, screen):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        if self.primary:
            normal = (92, 156, 110)
            hover = (108, 177, 126)
        else:
            normal = (52, 57, 66)
            hover = (66, 72, 82)

        fill = hover if hovered else normal
        pygame.draw.rect(screen, fill, self.rect, border_radius=12)

        border = (145, 151, 161) if hovered else (82, 88, 98)
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=12)

        text = self.font.render(self.text, True, (242, 244, 247))
        screen.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, position):
        return self.rect.collidepoint(position)


class UI:
    WIDTH = 640
    HEIGHT = 640
    TILE = 80

    FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]
    RANKS = ["8", "7", "6", "5", "4", "3", "2", "1"]

    BG = (25, 28, 34)
    PANEL = (34, 38, 46)
    PANEL_LIGHT = (45, 50, 59)
    TEXT = (242, 244, 247)
    MUTED = (165, 171, 181)

    BOARD_LIGHT = (224, 218, 201)
    BOARD_DARK = (116, 142, 108)
    SELECTED = (244, 202, 78)
    MOVE = (35, 45, 42)
    CAPTURE = (210, 78, 78)

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 30)
        self.small_font = pygame.font.SysFont(None, 22)
        self.title_font = pygame.font.SysFont(None, 58)
        self.subtitle_font = pygame.font.SysFont(None, 27)
        self.overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        self.piece_images = {}
        for color in ["white", "black"]:
            for name in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
                self.piece_images[f"{color}_{name}"] = pygame.image.load(
                    f"assets/{color}_{name}.png"
                )

        self.menu_buttons = [
            Button((190, 285, 260, 62), "PLAY", self.font, primary=True),
            Button((190, 365, 260, 62), "QUIT", self.font),
        ]

        self.game_over_buttons = [
            Button((145, 410, 165, 58), "REMATCH", self.font, primary=True),
            Button((330, 410, 165, 58), "MAIN MENU", self.font),
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
        self.screen.fill(self.BG)

        # Decorative panels
        pygame.draw.rect(self.screen, self.PANEL, (70, 70, 500, 500), border_radius=24)
        pygame.draw.rect(self.screen, self.PANEL_LIGHT, (70, 70, 500, 500), 2, border_radius=24)

        title = self.title_font.render("MiniPyChess", True, self.TEXT)
        self.screen.blit(title, title.get_rect(center=(320, 165)))

        subtitle = self.subtitle_font.render("A simple chess game", True, self.MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(320, 205)))

        for button in self.menu_buttons:
            button.draw(self.screen)

        version = self.small_font.render("STOCKFISH EDITION", True, self.MUTED)
        self.screen.blit(version, version.get_rect(center=(320, 535)))

        pygame.display.flip()

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.BOARD_LIGHT if (row + col) % 2 == 0 else self.BOARD_DARK
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * self.TILE, row * self.TILE, self.TILE, self.TILE),
                )

    def draw_labels(self):
        label_font = self.small_font

        for col in range(8):
            light_square = (7 + col) % 2 == 0
            color = self.BOARD_DARK if light_square else self.BOARD_LIGHT
            text = label_font.render(self.FILES[col], True, color)
            self.screen.blit(
                text,
                (col * self.TILE + self.TILE - text.get_width() - 5,
                 self.HEIGHT - text.get_height() - 4),
            )

        for row in range(8):
            light_square = row % 2 == 0
            color = self.BOARD_DARK if light_square else self.BOARD_LIGHT
            text = label_font.render(self.RANKS[row], True, color)
            self.screen.blit(text, (5, row * self.TILE + 4))

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

                self.screen.blit(
                    image,
                    (col * self.TILE + 10, row * self.TILE + 10),
                )

    def draw_moves(self, game):
        if not game.show_moves or game.first_select is None:
            return

        for move in game.legal_moves_from(game.first_select):
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            center = (
                col * self.TILE + self.TILE // 2,
                row * self.TILE + self.TILE // 2,
            )

            if game.board.is_capture(move):
                pygame.draw.circle(
                    self.overlay,
                    (*self.CAPTURE, 150),
                    center,
                    29,
                    5,
                )
            else:
                pygame.draw.circle(
                    self.overlay,
                    (*self.MOVE, 125),
                    center,
                    10,
                )

    def draw_selection(self, game):
        if game.first_select is None:
            return

        col = chess.square_file(game.first_select)
        row = 7 - chess.square_rank(game.first_select)

        pygame.draw.rect(
            self.screen,
            self.SELECTED,
            (
                col * self.TILE + 2,
                row * self.TILE + 2,
                self.TILE - 4,
                self.TILE - 4,
            ),
            4,
        )

    def draw_promotion(self, game):
        title = self.title_font.render("PROMOTE PAWN", True, self.TEXT)
        self.screen.blit(title, title.get_rect(center=(320, 155)))

        subtitle = self.small_font.render(
            "Choose a piece",
            True,
            self.MUTED,
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(320, 190)))

        width, gap = 100, 20
        start_x = (self.WIDTH - (width * 4 + gap * 3)) // 2
        y = 250
        color = "white" if game.board.turn == chess.WHITE else "black"

        for i, (_, name) in enumerate(self.promotion_types):
            rect = pygame.Rect(
                start_x + i * (width + gap),
                y,
                width,
                width,
            )

            hovered = rect.collidepoint(pygame.mouse.get_pos())
            fill = self.PANEL_LIGHT if hovered else self.PANEL

            pygame.draw.rect(screen=self.screen, color=fill, rect=rect, border_radius=14)
            pygame.draw.rect(
                self.screen,
                self.SELECTED if hovered else (80, 86, 96),
                rect,
                2,
                border_radius=14,
            )

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

        self.overlay.fill((0, 0, 0, 155))
        self.screen.blit(self.overlay, (0, 0))

        panel = pygame.Rect(130, 255, 380, 130)
        pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=18)
        pygame.draw.rect(self.screen, self.PANEL_LIGHT, panel, 2, border_radius=18)

        title = self.subtitle_font.render("AI THINKING", True, self.TEXT)
        self.screen.blit(title, title.get_rect(center=(320, 295)))

        dots = "." * ((pygame.time.get_ticks() // 400) % 4)
        thinking = self.small_font.render(
            f"Stockfish is calculating{dots}",
            True,
            self.MUTED,
        )
        self.screen.blit(thinking, thinking.get_rect(center=(320, 335)))

        pygame.display.flip()

    def draw_game_over(self, game):
        self.draw_game(game, flip=False)

        self.overlay.fill((0, 0, 0, 190))
        self.screen.blit(self.overlay, (0, 0))

        panel = pygame.Rect(90, 150, 460, 350)
        pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=22)
        pygame.draw.rect(self.screen, self.PANEL_LIGHT, panel, 2, border_radius=22)

        message = "STALEMATE" if game.winner is None else f"{game.winner.upper()} WINS!"

        title = self.title_font.render(message, True, self.TEXT)
        self.screen.blit(title, title.get_rect(center=(320, 245)))

        subtitle = self.small_font.render(
            "Good game!",
            True,
            self.MUTED,
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(320, 290)))

        for button in self.game_over_buttons:
            button.draw(self.screen)

        pygame.display.flip()
