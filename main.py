import platform
import pygame
import chess

from game import ChessGame
from ui import UI
from ai import StockfishAI


WIDTH = 640
HEIGHT = 640

vsAI = True
aiElo = 500
playerColor = "White"

supported_devices = ["Android", "Linux", "Windows"]
current_device = platform.system() if platform.system() in supported_devices else None

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MiniPyChess")

ui = UI(screen)
game = ChessGame()
ai = StockfishAI(aiElo) if vsAI else None

app_state = "menu"
running = True


def is_ai_turn():
    if not vsAI:
        return False

    if playerColor == "White":
        return game.board.turn == chess.BLACK

    return game.board.turn == chess.WHITE


def make_ai_move():
    if ai is None or game.game_over or game.is_promotion_pending():
        return

    move = ai.get_move(game.board)
    if move is not None:
        game.board.push(move)
        game.check_game()


def handle_game_click(position):
    if is_ai_turn():
        return

    if game.is_promotion_pending():
        ui.handle_promotion_click(position, game)
        return

    square = ui.square_from_mouse(position)
    if square is not None:
        game.select_square(square)


def handle_game_key(key):
    if key == pygame.K_m:
        game.show_moves = not game.show_moves
    elif key == pygame.K_ESCAPE:
        game.clear_selection()


def main():
    global app_state, running

    if current_device:
        print(current_device)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if app_state == "game":
                    handle_game_key(event.key)
                continue

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            if app_state == "menu":
                action = ui.handle_menu_click(event.pos)
                if action == "game":
                    game.reset()
                    app_state = "game"
                elif action == "quit":
                    running = False

            elif app_state == "game":
                handle_game_click(event.pos)

                if game.game_over:
                    app_state = "game_over"
                elif is_ai_turn() and not game.is_promotion_pending():
                    make_ai_move()
                    if game.game_over:
                        app_state = "game_over"

            elif app_state == "game_over":
                action = ui.handle_game_over_click(event.pos)
                if action == "rematch":
                    game.reset()
                    app_state = "game"
                elif action == "menu":
                    game.reset()
                    app_state = "menu"

        if app_state == "menu":
            ui.draw_menu()
        elif app_state == "game":
            ui.draw_game(game)
        elif app_state == "game_over":
            ui.draw_game_over(game)

    if ai is not None:
        ai.quit()

    pygame.quit()


if __name__ == "__main__":
    main()
