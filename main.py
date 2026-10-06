import pygame
import chess
import os

pygame.init()


# ============================================================
# ASSETS
# ============================================================

pieceImages = {}

for color in ["white", "black"]:
    for pieceType in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
        path = f"assets/{color}_{pieceType}.png"
        pieceImages[f"{color}_{pieceType}"] = pygame.image.load(path)


# ============================================================
# SETUP
# ============================================================

WIDTH = 640
HEIGHT = 640
TILE = WIDTH // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Chess")

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
font = pygame.font.SysFont(None, 30)

board = chess.Board()


# ============================================================
# BOARD DATA
# ============================================================

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]


# ============================================================
# GAME STATE
# ============================================================

firstSelect = None
secondSelect = None

showMoves = True

invalidSquare = None
invalidS_time = 0

running = True


# ============================================================
# GAME STATE HELPERS
# ============================================================

def clearSelection():
    global firstSelect, secondSelect

    firstSelect = None
    secondSelect = None


def squareFromMouse(position):
    x, y = position

    column = x // TILE
    row = y // TILE

    return chess.square(column, 7 - row)


def isOwnPiece(square):
    piece = board.piece_at(square)

    if piece is None:
        return False

    return piece.color == board.turn


def pieceCheck(position):
    piece = board.piece_at(position)

    if piece is None:
        print("There is no piece there.. blind ahh")
        return None

    print(
        "You grabbed:",
        chess.COLOR_NAMES[piece.color],
        chess.piece_name(piece.piece_type)
    )

    return piece


# ============================================================
# CHESS LOGIC
# ============================================================

def tryMove(start, end):
    global invalidSquare, invalidS_time

    move = chess.Move(start, end)

    if move in board.legal_moves:
        wasCapture = board.is_capture(move)

        board.push(move)

        if wasCapture:
            print("Capture made!")

        else:
            print("Move made!")

        clearSelection()
        return True

    print("Illegal move!")

    invalidSquare = end
    invalidS_time = pygame.time.get_ticks()

    return False


# ============================================================
# INPUT
# ============================================================

def handleKeyPress(key):
    global showMoves

    if key == pygame.K_m:
        showMoves = not showMoves

    elif key == pygame.K_ESCAPE:
        clearSelection()


def handleMouseClick(position):
    global firstSelect, secondSelect

    chessSquare = squareFromMouse(position)
    clickedPiece = pieceCheck(chessSquare)

    # Nothing selected yet.
    if firstSelect is None:

        # Only allow the current player to select their piece.
        if clickedPiece is not None and isOwnPiece(chessSquare):
            firstSelect = chessSquare

    # A piece is selected, so this click is the destination.
    elif secondSelect is None:

        # Clicking another friendly piece switches selection.
        if clickedPiece is not None and isOwnPiece(chessSquare):
            firstSelect = chessSquare
            secondSelect = None

        else:
            secondSelect = chessSquare
            tryMove(firstSelect, secondSelect)

    # This should normally only exist briefly after an invalid move.
    else:

        if clickedPiece is not None and isOwnPiece(chessSquare):
            firstSelect = chessSquare
            secondSelect = None

        else:
            clearSelection()

    print("Clicked:", chess.square_name(chessSquare))
    print("First:", firstSelect)
    print("Second:", secondSelect)


# ============================================================
# DRAW BOARD
# ============================================================

def drawBoard():

    for row in range(8):

        for col in range(8):

            if (row + col) % 2 == 0:
                color = (240, 217, 181)
            else:
                color = (181, 136, 99)

            pygame.draw.rect(
                screen,
                color,
                (
                    col * TILE,
                    row * TILE,
                    TILE,
                    TILE
                )
            )


# ============================================================
# DRAW LABELS
# ============================================================

def drawLabels():

    # FILE LABELS
    for col in range(8):

        text = font.render(
            files[col],
            True,
            (0, 0, 0)
        )

        x = col * TILE + 5
        y = HEIGHT - text.get_height() - 5

        screen.blit(text, (x, y))

    # RANK LABELS
    for row in range(8):

        text = font.render(
            ranks[row],
            True,
            (0, 0, 0)
        )

        x = 5
        y = row * TILE + 5

        screen.blit(text, (x, y))


# ============================================================
# DRAW PIECES
# ============================================================

def drawPieces():

    for row in range(8):

        for col in range(8):

            chessSquare = chess.square(
                col,
                7 - row
            )

            piece = board.piece_at(chessSquare)

            if piece is None:
                continue

            color = chess.COLOR_NAMES[piece.color]
            pieceType = chess.piece_name(piece.piece_type)

            image = pieceImages[
                f"{color}_{pieceType}"
            ]

            x = col * TILE + (TILE - 60) // 2
            y = row * TILE + (TILE - 60) // 2

            screen.blit(image, (x, y))


# ============================================================
# DRAW POSSIBLE MOVES
# ============================================================

def drawMoves():

    if not showMoves or firstSelect is None:
        return

    for move in board.legal_moves:

        if move.from_square != firstSelect:
            continue

        target = move.to_square

        col = chess.square_file(target)
        row = 7 - chess.square_rank(target)

        center = (
            col * TILE + TILE // 2,
            row * TILE + TILE // 2
        )

        if board.is_capture(move):

            pygame.draw.circle(
                overlay,
                (255, 80, 80, 140),
                center,
                30,
                5
            )

        else:

            pygame.draw.circle(
                overlay,
                (50, 50, 50, 100),
                center,
                10
            )


# ============================================================
# DRAW INVALID MOVE
# ============================================================

def drawInvalidHighlight():

    global invalidSquare

    if invalidSquare is None:
        return

    elapsed = pygame.time.get_ticks() - invalidS_time

    blinkCycle = 300
    blinkOnTime = 150
    totalDuration = 3 * blinkCycle

    if elapsed >= totalDuration:
        invalidSquare = None
        return

    if elapsed % blinkCycle < blinkOnTime:

        col = chess.square_file(invalidSquare)
        row = 7 - chess.square_rank(invalidSquare)

        pygame.draw.rect(
            overlay,
            (255, 0, 0, 120),
            (
                col * TILE,
                row * TILE,
                TILE,
                TILE
            )
        )


# ============================================================
# DRAW SELECTIONS
# ============================================================

def drawSelections():

    if firstSelect is not None:

        col = chess.square_file(firstSelect)
        row = 7 - chess.square_rank(firstSelect)

        pygame.draw.rect(
            screen,
            (205, 255, 156),
            (
                col * TILE,
                row * TILE,
                TILE,
                TILE
            ),
            5
        )

    if secondSelect is not None:

        col = chess.square_file(secondSelect)
        row = 7 - chess.square_rank(secondSelect)

        pygame.draw.rect(
            screen,
            (156, 172, 255),
            (
                col * TILE,
                row * TILE,
                TILE,
                TILE
            ),
            5
        )


# ============================================================
# DRAW GAME
# ============================================================

def drawGame():

    drawBoard()
    drawLabels()

    overlay.fill((0, 0, 0, 0))

    drawPieces()
    drawMoves()
    drawInvalidHighlight()

    screen.blit(overlay, (0, 0))

    drawSelections()

    pygame.display.flip()


# ============================================================
# MAIN LOOP
# ============================================================

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            handleKeyPress(event.key)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            handleMouseClick(event.pos)

    drawGame()


pygame.quit()
