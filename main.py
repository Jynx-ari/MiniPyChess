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

overlay = pygame.Surface(
    (WIDTH, HEIGHT),
    pygame.SRCALPHA
)

font = pygame.font.SysFont(None, 30)

board = chess.Board()


# ============================================================
# BOARD LABELS
# ============================================================

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]


# ============================================================
# GAME STATE
# ============================================================

firstSelect = None
secondSelect = None

currentHandPiece = None

showMoves = True

invalidSquare = None
invalidS_time = 0

running = True


# ============================================================
# PIECE CHECK
# ============================================================

def pieceCheck(position):

    WhatPiece = board.piece_at(position)

    if WhatPiece is None:

        print("There is no piece there.. blind ahh")

    else:

        pieceInfo = {
            "Color": chess.COLOR_NAMES[WhatPiece.color],
            "Type": WhatPiece.piece_type,
            "Name": chess.piece_name(WhatPiece.piece_type)
        }

        print(
            "You grabbed:",
            chess.COLOR_NAMES[WhatPiece.color],
            chess.piece_name(WhatPiece.piece_type)
        )

        return WhatPiece


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

        screen.blit(
            text,
            (x, y)
        )


    # RANK LABELS
    for row in range(8):

        text = font.render(
            ranks[row],
            True,
            (0, 0, 0)
        )

        x = 5
        y = row * TILE + 5

        screen.blit(
            text,
            (x, y)
        )


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

            if piece is not None:

                color = chess.COLOR_NAMES[piece.color]

                pieceType = chess.piece_name(
                    piece.piece_type
                )

                image = pieceImages[
                    f"{color}_{pieceType}"
                ]

                x = col * TILE + (TILE - 60) // 2
                y = row * TILE + (TILE - 60) // 2

                screen.blit(
                    image,
                    (x, y)
                )


# ============================================================
# DRAW POSSIBLE MOVES
# ============================================================

def drawMoves():

    if not showMoves:
        return

    if firstSelect is None:
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

        # CAPTURE
        if board.is_capture(move):

            pygame.draw.circle(
                overlay,
                (255, 80, 80, 140),
                center,
                30,
                5
            )

        # NORMAL MOVE
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

    elif elapsed % blinkCycle < blinkOnTime:

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

    # FIRST SELECTED TILE
    if firstSelect is not None:

        col = chess.square_file(
            firstSelect
        )

        row = 7 - chess.square_rank(
            firstSelect
        )

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


    # SECOND SELECTED TILE
    if secondSelect is not None:

        col = chess.square_file(
            secondSelect
        )

        row = 7 - chess.square_rank(
            secondSelect
        )

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
# MAIN LOOP
# ============================================================

while running:

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_m:

                showMoves = not showMoves


            if event.key == pygame.K_ESCAPE:

                firstSelect = None
                secondSelect = None
                currentHandPiece = None


        # ----------------------------------------------------
        # MOUSE
        # ----------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            x, y = event.pos

            ValColumn = x // TILE
            ValRow = y // TILE

            # Convert Pygame coordinates
            # into a python-chess square

            chessSquare = chess.square(
                ValColumn,
                7 - ValRow
            )

            currentHandPiece = pieceCheck(
                chessSquare
            )


            # =================================================
            # NOTHING SELECTED
            # =================================================

            if firstSelect is None:

                if currentHandPiece is not None:

                    firstSelect = chessSquare


            # =================================================
            # FIRST PIECE SELECTED
            # =================================================

            elif secondSelect is None:

                if currentHandPiece is not None:

                    # Click another piece
                    # Switch selection

                    firstSelect = chessSquare
                    secondSelect = None

                else:

                    # Click empty square
                    # This becomes destination

                    secondSelect = chessSquare

                    move = chess.Move(
                        firstSelect,
                        secondSelect
                    )


                    # -----------------------------------------
                    # VALID MOVE
                    # -----------------------------------------

                    if move in board.legal_moves:

                        board.push(move)

                        print("Move made!")

                        firstSelect = None
                        secondSelect = None
                        currentHandPiece = None


                    # -----------------------------------------
                    # INVALID MOVE
                    # -----------------------------------------

                    else:

                        print("Illegal move!")

                        invalidSquare = secondSelect

                        invalidS_time = pygame.time.get_ticks()


            # =================================================
            # BOTH SELECTIONS EXIST
            # =================================================

            else:

                if currentHandPiece is not None:

                    # Start a new selection

                    firstSelect = chessSquare
                    secondSelect = None

                else:

                    # Cancel selections

                    firstSelect = None
                    secondSelect = None


            print(
                "Clicked:",
                chess.square_name(chessSquare)
            )

            print(
                "First:",
                firstSelect
            )

            print(
                "Second:",
                secondSelect
            )


    # ========================================================
    # DRAW
    # ========================================================

    drawBoard()

    drawLabels()

    overlay.fill(
        (0, 0, 0, 0)
    )

    drawPieces()

    drawMoves()

    drawInvalidHighlight()

    screen.blit(
        overlay,
        (0, 0)
    )

    drawSelections()

    pygame.display.flip()


pygame.quit()