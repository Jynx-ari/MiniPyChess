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

clock = pygame.time.Clock()
AI_DELAY_MS = 3000
ai_thinking = False
ai_think_start = 0

MOVE_ANIMATION_MS = 220
move_animation = None
move_animation_start = 0


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


def start_move_animation():
    global move_animation, move_animation_start

    if not ui.animations_enabled or game.last_move is None:
        move_animation = None
        return False

    move_animation = game.last_move
    move_animation_start = pygame.time.get_ticks()
    return True


def start_ai_thinking():
    global ai_thinking, ai_think_start
    ai_thinking = True
    ai_think_start = pygame.time.get_ticks()


def finish_ai_turn():
    global ai_thinking

    make_ai_move()
    ai_thinking = False

    if game.game_over:
        return "game_over"

    return "game"


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
                    if is_ai_turn():
                        start_ai_thinking()
                elif action == "quit":
                    running = False

            elif app_state == "game":
                if not ai_thinking and move_animation is None:
                    handle_game_click(event.pos)

                    if game.game_over:
                        if ui.animations_enabled and game.last_move is not None:
                            start_move_animation()
                        else:
                            app_state = "game_over"
                    elif game.last_move is not None:
                        if start_move_animation():
                            pass
                        elif is_ai_turn() and not game.is_promotion_pending():
                            start_ai_thinking()

            elif app_state == "game_over":
                action = ui.handle_game_over_click(event.pos)
                if action == "rematch":
                    game.reset()
                    app_state = "game"
                    if is_ai_turn():
                        start_ai_thinking()
                    if is_ai_turn():
                        start_ai_thinking()
                elif action == "menu":
                    game.reset()
                    app_state = "menu"

        if app_state == "game" and move_animation is not None:
            elapsed = pygame.time.get_ticks() - move_animation_start
            progress = min(1.0, elapsed / MOVE_ANIMATION_MS)

            # Smooth ease-out movement.
            progress = 1 - (1 - progress) ** 3
            ui.draw_move_animation(game, move_animation, progress)

            if elapsed >= MOVE_ANIMATION_MS:
                move_animation = None
                if game.game_over:
                    app_state = "game_over"
                elif is_ai_turn() and not game.is_promotion_pending():
                    start_ai_thinking()

        elif app_state == "game" and ai_thinking:
            if pygame.time.get_ticks() - ai_think_start >= AI_DELAY_MS:
                app_state = finish_ai_turn()

        if app_state == "menu":
            ui.draw_menu()
        elif app_state == "game" and move_animation is None:
            if ai_thinking:
                ui.draw_ai_thinking(game)
            else:
                ui.draw_game(game)
        elif app_state == "game_over":
            ui.draw_game_over(game)

        clock.tick(60)

    if ai is not None:
        ai.quit()

    pygame.quit()


if __name__ == "__main__":
    main()
