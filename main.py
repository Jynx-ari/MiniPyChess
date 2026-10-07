import pygame
import chess
import platform


# ============================================================
# SETUP
# ============================================================

pygame.init()

WIDTH = 640
HEIGHT = 640
TILE = WIDTH // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Chess")

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
font = pygame.font.SysFont(None, 30)

board = chess.Board()

current_device = None
supportedDevices = ["Android", "Linux", "Windows"]
if platform.system() in supportedDevices:
  current_device = platform.system()
  print(current_device)
  

# ============================================================
# ASSETS
# ============================================================

pieceImages = {}

for color in ["white", "black"]:
    for pieceType in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
        path = f"assets/{color}_{pieceType}.png"
        pieceImages[f"{color}_{pieceType}"] = pygame.image.load(path)


# ============================================================
# BOARD LABELS
# ============================================================

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]


# ============================================================
# GAME STATE
# ============================================================

firstSelect = None
showMoves = True

invalidSquare = None
invalidS_time = 0

gameover = False

# ============================================================
# INPUT HELPERS
# ============================================================

def clearSelection():
    global firstSelect
    firstSelect = None


def squareFromMouse(position):
    x, y = position
    column = x // TILE
    row = y // TILE

    return chess.square(column, 7 - row)


def isOwnPiece(square):
    piece = board.piece_at(square)

    return piece is not None and piece.color == board.turn


def pieceCheck(square):
    piece = board.piece_at(square)

    if piece is None:
        print("There is no piece there.")
        return None

    print(
        "You grabbed:",
        chess.COLOR_NAMES[piece.color],
        chess.piece_name(piece.piece_type)
    )

    return piece


# ============================================================
# MOVE LOGIC
# ============================================================


def checkGame():
  if board.is_checkmate():
    global winner 
    winner = "White" if board.turn == chess.BLACK else "Black"
    print(f"Checkmate! {winner} wins!")
    return True
  if board.is_stalemate():
    print("STALEMATE!!")
    return True

  if board.is_check():
    print("Check!!")
  return False


def showInvalidMove(square):
    global invalidSquare, invalidS_time

    invalidSquare = square
    invalidS_time = pygame.time.get_ticks()


def tryMove(start, end):
    global gameover
    move = chess.Move(start, end)

    if move not in board.legal_moves:
        print("Illegal move!")
        showInvalidMove(end)
        return False

    wasCapture = board.is_capture(move)
    board.push(move)

    if wasCapture:
        print("Capture made!")
    else:
        print("Move made!")
    gameover = checkGame()
    clearSelection()
    return True


def handleMouseClick(position):
    if gameover:
      return
    global firstSelect

    chessSquare = squareFromMouse(position)
    clickedPiece = pieceCheck(chessSquare)

    if firstSelect is None:
        if clickedPiece is not None and isOwnPiece(chessSquare):
            firstSelect = chessSquare

    elif clickedPiece is not None and isOwnPiece(chessSquare):
        firstSelect = chessSquare

    else:
        tryMove(firstSelect, chessSquare)

    print("Clicked:", chess.square_name(chessSquare))
    print("First:", firstSelect)


def handleKeyPress(key):
    global showMoves

    if key == pygame.K_m:
        showMoves = not showMoves

    elif key == pygame.K_ESCAPE:
        clearSelection()


# ============================================================
# DRAWING
# ============================================================

def drawBoard():
    for row in range(8):
        for col in range(8):
            color = (
                (240, 217, 181)
                if (row + col) % 2 == 0
                else (181, 136, 99)
            )

            pygame.draw.rect(
                screen,
                color,
                (col * TILE, row * TILE, TILE, TILE)
            )


def drawLabels():
    for col in range(8):
        text = font.render(files[col], True, (0, 0, 0))
        screen.blit(
            text,
            (col * TILE + 5, HEIGHT - text.get_height() - 5)
        )

    for row in range(8):
        text = font.render(ranks[row], True, (0, 0, 0))
        screen.blit(
            text,
            (5, row * TILE + 5)
        )


def drawPieces():
    for row in range(8):
        for col in range(8):
            chessSquare = chess.square(col, 7 - row)
            piece = board.piece_at(chessSquare)

            if piece is None:
                continue

            color = chess.COLOR_NAMES[piece.color]
            pieceType = chess.piece_name(piece.piece_type)
            image = pieceImages[f"{color}_{pieceType}"]

            x = col * TILE + (TILE - 60) // 2
            y = row * TILE + (TILE - 60) // 2

            screen.blit(image, (x, y))


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


def drawInvalidHighlight():
    if invalidSquare is None:
        return

    elapsed = pygame.time.get_ticks() - invalidS_time

    blinkCycle = 300
    blinkOnTime = 150
    totalDuration = 3 * blinkCycle

    if elapsed >= totalDuration:
        return

    if elapsed % blinkCycle >= blinkOnTime:
        return

    col = chess.square_file(invalidSquare)
    row = 7 - chess.square_rank(invalidSquare)

    pygame.draw.rect(
        overlay,
        (255, 0, 0, 120),
        (col * TILE, row * TILE, TILE, TILE)
    )


def drawSelections():
    if firstSelect is None:
        return

    col = chess.square_file(firstSelect)
    row = 7 - chess.square_rank(firstSelect)

    pygame.draw.rect(
        screen,
        (205, 255, 156),
        (col * TILE, row * TILE, TILE, TILE),
        5
    )


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

def main():
    running = True

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


if __name__ == "__main__":
    main()
